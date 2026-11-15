"""MAYORDOMO de la tienda (Minotauro Mayordomo).

Trabaja solo una vez al dia desde GitHub Actions. No necesita claves ni IA de pago:
todo sale del catalogo (redesign/catalog.json) y de guias.html.

Cada jornada:
  1. Rehace los rankings "Top 10 por categoria" (carpeta top/) con el catalogo actual.
  2. Crea el PIN DEL DIA (imagen vertical 1000x1500 en pins/auto/): tres dias un ranking,
     el cuarto una de las guias digitales propias.
  3. Lo anade a feed.xml (RSS). Pinterest puede publicar solo desde ese feed.
  4. Actualiza sitemap.xml.
  5. Revisa la web: enlaces de Amazon sin codigo de afiliado y enlaces internos rotos.
  6. Escribe el informe en mayordomo/diario.md y mayordomo/ultimo.md.

Uso:
  python scripts/mayordomo.py                 -> jornada de hoy (si ya se hizo, no repite)
  python scripts/mayordomo.py --fecha 2026-11-20 --forzar
  python scripts/mayordomo.py --avisar        -> comprueba que la web publicada responde y avisa a
                                                 los buscadores (IndexNow) de las paginas nuevas

Reglas: solo decimos lo que figura en el catalogo (titulo y puesto en ventas). No se inventan
precios, descuentos ni opiniones. No se usan fotos de Amazon ni de terceros.
"""
import argparse
import datetime as dt
import html
import json
import os
import pathlib
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from email.utils import format_datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
TAG = "trendpulsesho-21"
BASE = "https://pantoas13.github.io/trendpulseshop/"
NETLIFY = "https://trendpulseshop-es.netlify.app/"
MARCA = "CompraFaro"
CLAVE_INDEXNOW = "1ffa39a9d60bb4af3ddbba97ff9d9ecf"

CATALOGO = ROOT / "redesign" / "catalog.json"
TOP = ROOT / "top"
PINS = ROOT / "pins" / "auto"
DATOS = ROOT / "mayordomo"
ESTADO = DATOS / "estado.json"
DIARIO = DATOS / "diario.md"
ULTIMO = DATOS / "ultimo.md"
FEED = ROOT / "feed.xml"
SITEMAP = ROOT / "sitemap.xml"
FUENTES = pathlib.Path(__file__).resolve().parent / "fonts"

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]

# Orden de los pines: primero lo que mas se regala y se busca; el resto del catalogo va detras.
PRIORIDAD = [
    "Juguetes", "Auriculares y audio portátil", "Videojuegos", "Belleza", "Dispositivos Amazon",
    "Hogar y cocina", "Móviles y accesorios", "Electrónica", "Deporte", "Tablets",
    "Electrodomésticos", "Mascotas", "Moda", "Bebé", "Informática", "TV y home cinema",
    "Iluminación", "Coche y moto", "Portátiles", "Salud", "Almacenamiento", "Oficina",
    "Fotografía y vídeo", "Bricolaje", "Jardín", "Monitores", "Pilas y cargadores",
    "Redes y wifi", "Audio y Hi-Fi", "Instrumentos musicales", "Libros",
    "Accesorios de informática", "Componentes de PC", "Electrónica para coche", "Impresoras",
    "Grandes electrodomésticos", "Handmade", "Reacondicionados", "Ordenadores de sobremesa",
    "Industria y ciencia",
]
# Colores de los pines (fondo de la banda, texto de la banda). Van rotando.
PALETA = [("#003cff", "#ffffff"), ("#101c3c", "#ffffff"), ("#0a6b4a", "#ffffff"), ("#b3261e", "#ffffff")]


# ------------------------------------------------------------------ utilidades
def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def e(texto):
    return html.escape(str(texto), quote=True)


def leer_json(ruta, defecto):
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return defecto


def titulo_limpio(t):
    """Los titulos del catalogo vienen cortados a 90 caracteres: se cierran en palabra entera."""
    t = " ".join(t.split())
    if len(t) >= 88:
        t = t[:t.rfind(" ")].rstrip(" ,;:|-(/") + "…"
    return t


def nombre_corto(t, maximo=46):
    """Nombre breve para el pin: hasta la primera coma o barra y, si sigue largo, palabras enteras."""
    t = " ".join(t.split())
    t = re.sub(r"^(\[[^\]]*\]|\([^)]*\)|【[^】]*】)\s*", "", t)
    corto = re.split(r"\s[|\-–]\s|,(?!\d)|\(|\[", t)[0].strip()
    if len(corto) < 16:
        corto = t
    corto = corto[:1].upper() + corto[1:]
    if len(corto) > maximo:
        corto = corto[:maximo + 1]
        corto = corto[:corto.rfind(" ")].rstrip(" ,;:-|(") + "…"
    return corto


def enlace_amazon(asin):
    return f"https://www.amazon.es/dp/{asin}?tag={TAG}"


# ------------------------------------------------------------------ datos
def cargar_catalogo():
    c = json.loads(CATALOGO.read_text(encoding="utf-8"))
    por_cat = {}
    for p in c["products"]:
        if re.fullmatch(r"[A-Z0-9]{10}", p.get("asin", "")) and p.get("title"):
            por_cat.setdefault(p["category"], []).append(p)
    for lista in por_cat.values():
        lista.sort(key=lambda p: p.get("rank", 999))
    return c.get("updated", ""), {k: v for k, v in por_cat.items() if len(v) >= 10}


def cargar_guias():
    """Guias digitales propias, leidas de guias.html (titulo, texto, portada y categoria)."""
    try:
        src = (ROOT / "guias.html").read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    guias = []
    for m in re.finditer(r'<a class="card" data-c="([^"]*)" href="([^"]+)"><img src="([^"]+)"[^>]*>'
                         r'.*?<h4>(.*?)</h4><p>(.*?)</p>', src, re.S):
        cat, href, img, tit, desc = (html.unescape(x) for x in m.groups())
        if (ROOT / img).exists():
            guias.append({"cat": cat, "href": href, "img": img, "titulo": tit, "desc": desc,
                          "slug": slug(href.rstrip("/").split("/")[-1])})
    return guias


def orden_categorias(por_cat):
    primero = [c for c in PRIORIDAD if c in por_cat]
    return primero + sorted(c for c in por_cat if c not in primero)


# ------------------------------------------------------------------ paginas de ranking
CABECERA = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:title" content="{ogtitle}"><meta property="og:description" content="{desc}">
<meta property="og:image" content="{ogimg}"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#003cff"><link rel="icon" href="../redesign/assets/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{marca} · Novedades" href="../feed.xml">
{jsonld}<link rel="stylesheet" href="top.css">
</head><body>
<div class="ribbon">{marca} · Descubre buenas compras · Compra en Amazon.es</div>
<header><div class="w"><a class="logo" href="../"><span aria-hidden="true">↗</span>{marca}</a><nav aria-label="Secciones"><a href="../">Catálogo</a><a href="./">Rankings</a><a href="../buscador-regalos.html">Ideas de regalo</a><a href="../guias.html">Guías</a></nav></div></header>
<main class="w">
"""
PIE = """</main>
<footer><div class="w"><p>Como Afiliado de Amazon, {marca} obtiene ingresos por las compras adscritas que cumplen los requisitos aplicables, sin coste adicional para ti. {marca} es una web independiente. El pago y el pedido se gestionan en Amazon. <a href="../privacidad.html">Privacidad y cookies</a></p></div></footer>
<script src="../geo-amazon.js" defer></script>
</body></html>
"""


def fecha_catalogo(fecha_cat, hoy):
    """Fecha del catalogo (dd/mm/aaaa) como date; si no se entiende, hoy."""
    try:
        d, m, a = (int(x) for x in fecha_cat.split("/"))
        return dt.date(a, m, d)
    except ValueError:
        return hoy


def pagina_categoria(cat, productos, fecha_cat, ref, vecinas):
    s = slug(cat)
    url = f"{BASE}top/{s}.html"
    mes = f"{MESES[ref.month - 1]} de {ref.year}"
    title = f"Los 10 más vendidos en {cat} · Amazon España ({mes})"
    top3 = ", ".join(nombre_corto(p["title"], 34) for p in productos[:3])
    desc = (f"Ranking de los 10 productos más vendidos de {cat} en Amazon.es: {top3} y más. "
            f"Consulta el precio de hoy en Amazon.")[:300]
    jsonld = {"@context": "https://schema.org", "@type": "ItemList", "name": title,
              "itemListElement": [{"@type": "ListItem", "position": i + 1,
                                   "name": titulo_limpio(p["title"]), "url": enlace_amazon(p["asin"])}
                                  for i, p in enumerate(productos[:10])]}
    out = [CABECERA.format(title=e(title), desc=e(desc), url=url, ogtitle=e(f"Los 10 más vendidos en {cat}"),
                           ogimg=f"{BASE}og.png", marca=MARCA,
                           jsonld='<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False) + "</script>\n")]
    out.append(f'<p class="crumb"><a href="../">Inicio</a> › <a href="./">Rankings</a> › {e(cat)}</p>\n')
    out.append('<p class="eyebrow">LOS MÁS VENDIDOS · AMAZON.ES</p>\n')
    out.append(f"<h1>Los 10 más vendidos en {e(cat)}</h1>\n")
    out.append(f'<p class="lead">Lo que más se está comprando en {e(cat)} en Amazon España, por orden de ventas. '
               "Pulsa en cualquiera para ver fotos, precio de hoy y opiniones en Amazon.</p>\n")
    out.append(f'<p class="meta">Ranking de referencia del {e(fecha_cat)}. '
               "El orden de ventas cambia cada día. No hemos probado estos productos: mostramos su puesto en ventas.</p>\n")
    out.append('<p class="disc">Enlaces de afiliado: si compras desde aquí podemos recibir una comisión, sin coste adicional para ti.</p>\n')
    out.append('<ol class="rank">\n')
    for i, p in enumerate(productos[:10], 1):
        t = e(titulo_limpio(p["title"]))
        out.append(f'<li><span class="n" aria-hidden="true">{i}</span><div><h3>{t}</h3>'
                   f"<p>Puesto n.º {i} en ventas de {e(cat)} · Precio y disponibilidad en Amazon</p>"
                   f'<a class="go" href="{enlace_amazon(p["asin"])}" target="_blank" rel="sponsored noopener" '
                   f'aria-label="Ver {t} en Amazon (se abre en otra pestaña)">Ver en Amazon →</a></div></li>\n')
    out.append("</ol>\n")
    resto = productos[10:20]
    if resto:
        out.append(f"<h2>Del puesto 11 al {10 + len(resto)}</h2>\n<ul class=\"more\">\n")
        for i, p in enumerate(resto, 11):
            out.append(f'<li><b>{i}</b><a href="{enlace_amazon(p["asin"])}" target="_blank" rel="sponsored noopener">'
                       f"{e(titulo_limpio(p['title']))}</a></li>\n")
        out.append("</ul>\n")
    out.append("<h2>Antes de comprar</h2>\n<ul class=\"tips\">"
               "<li><b>Mira el precio de hoy.</b> En Amazon cambia a menudo; aquí no lo mostramos para no darte un dato viejo.</li>"
               "<li><b>Lee las opiniones recientes</b> y fíjate en las de compra verificada.</li>"
               "<li><b>Comprueba quién lo vende y la devolución.</b> Aparece en la ficha, junto al botón de compra.</li>"
               "<li><b>Más vendido no siempre es el mejor para ti.</b> Compara dos o tres antes de decidir.</li></ul>\n")
    out.append("<h2>Otros rankings</h2>\n<ul class=\"chips\">")
    for v in vecinas:
        out.append(f'<li><a href="{slug(v)}.html">{e(v)}</a></li>')
    out.append('<li><a href="./">Ver todos →</a></li></ul>\n')
    out.append(PIE.format(marca=MARCA))
    (TOP / f"{s}.html").write_text("".join(out), encoding="utf-8")
    return {"url": url, "titulo": title, "desc": desc}


def pagina_indice(por_cat, orden, fecha_cat):
    url = f"{BASE}top/"
    title = f"Rankings: los más vendidos de Amazon España por categoría · {MARCA}"
    desc = f"{len(orden)} rankings con los 10 productos más vendidos de cada categoría de Amazon.es. Elige categoría y consulta el precio de hoy en Amazon."
    out = [CABECERA.format(title=e(title), desc=e(desc), url=url, ogtitle=e("Los más vendidos por categoría"),
                           ogimg=f"{BASE}og.png", marca=MARCA, jsonld="")]
    out.append('<p class="crumb"><a href="../">Inicio</a> › Rankings</p>\n<p class="eyebrow">RANKINGS POR CATEGORÍA</p>\n')
    out.append("<h1>Los más vendidos de Amazon España, por categoría</h1>\n")
    out.append(f'<p class="lead">Elige una categoría y mira sus 10 productos más vendidos.</p>\n'
               f'<p class="meta">Ranking de referencia del {e(fecha_cat)}. El orden de ventas cambia cada día.</p>\n<ul class="grid">\n')
    for c in sorted(orden, key=lambda x: slug(x)):
        n1 = nombre_corto(por_cat[c][0]["title"], 40)
        out.append(f'<li><a href="{slug(c)}.html"><b>{e(c)}</b><span>N.º 1: {e(n1)}</span></a></li>\n')
    out.append("</ul>\n" + PIE.format(marca=MARCA))
    (TOP / "index.html").write_text("".join(out), encoding="utf-8")


# ------------------------------------------------------------------ imagenes (pines)
def fuente(nombre, tam):
    from PIL import ImageFont
    return ImageFont.truetype(str(FUENTES / nombre), tam)


def partir(draw, texto, f, ancho, max_lineas):
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = (actual + " " + palabra).strip()
        if draw.textlength(prueba, font=f) <= ancho:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    if len(lineas) > max_lineas:
        lineas = lineas[:max_lineas]
        while lineas[-1] and draw.textlength(lineas[-1] + "…", font=f) > ancho:
            lineas[-1] = lineas[-1][:-1]
        lineas[-1] = lineas[-1].rstrip(" ,;:-") + "…"
    return lineas


def titular(draw, texto, ancho, tamanos, max_lineas, nombre="Inter-ExtraBold.otf"):
    """Elige el tamano de letra mas grande con el que el titular cabe sin cortarse."""
    for tam in tamanos:
        f = fuente(nombre, tam)
        lineas = partir(draw, texto, f, ancho, 99)
        if len(lineas) <= max_lineas and all(draw.textlength(l, font=f) <= ancho for l in lineas):
            return f, lineas, tam
    f = fuente(nombre, tamanos[-1])
    return f, partir(draw, texto, f, ancho, max_lineas), tamanos[-1]


def base_pin(color, color_txt, etiqueta):
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (1000, 1500), "#fcfaf7")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 1000, 150], fill=color)
    d.rounded_rectangle([60, 43, 124, 107], 14, fill=color_txt)
    d.line([78, 89, 106, 61], fill=color, width=7)
    d.line([84, 61, 106, 61], fill=color, width=7)
    d.line([106, 61, 106, 83], fill=color, width=7)
    d.text((146, 75), MARCA, font=fuente("Inter-ExtraBold.otf", 46), fill=color_txt, anchor="lm")
    f = fuente("Inter-SemiBold.otf", 24)
    d.text((940, 75), etiqueta, font=f, fill=color_txt, anchor="rm")
    return img, d


def boton(d, texto, color, color_txt, y):
    d.rounded_rectangle([60, y, 940, y + 112], 24, fill=color)
    d.text((500, y + 56), texto, font=fuente("Inter-ExtraBold.otf", 40), fill=color_txt, anchor="mm")


def pin_categoria(cat, productos, fecha_cat, ruta, n):
    color, ctxt = PALETA[n % len(PALETA)]
    img, d = base_pin(color, ctxt, "AMAZON.ES")
    d.text((60, 212), "LOS MÁS VENDIDOS · TOP 10", font=fuente("Inter-ExtraBold.otf", 30), fill=color)
    f, lineas, tam = titular(d, cat, 880, [112, 96, 84, 72, 62], 2)
    y = 268
    for l in lineas:
        d.text((60, y), l, font=f, fill="#101c3c")
        y += int(tam * 1.08)
    y += 34
    fila = min(150, (1238 - y) // 5)
    fn, ft = fuente("Inter-ExtraBold.otf", 40), fuente("Inter-SemiBold.otf", 34)
    for i, p in enumerate(productos[:5], 1):
        d.rounded_rectangle([60, y, 940, y + fila - 16], 22, fill="#ffffff", outline="#e4e4e7", width=2)
        cy = y + (fila - 16) // 2
        d.ellipse([84, cy - 38, 160, cy + 38], fill=color if i <= 3 else "#f3f5fc")
        d.text((122, cy), str(i), font=fn, fill=ctxt if i <= 3 else color, anchor="mm")
        ls = partir(d, nombre_corto(p["title"], 60), ft, 730, 2)
        yy = cy - (len(ls) * 42) // 2
        for l in ls:
            d.text((186, yy + 21), l, font=ft, fill="#101c3c", anchor="lm")
            yy += 42
        y += fila
    boton(d, "Ver el ranking completo →", color, ctxt, 1272)
    d.text((500, 1432), f"Ranking de referencia del {fecha_cat} · Enlaces de afiliado", font=fuente("Inter-Regular.otf", 24),
           fill="#586070", anchor="mm")
    img.save(ruta, optimize=True)


def pin_guia(g, ruta, n):
    from PIL import Image, ImageDraw
    color, ctxt = PALETA[n % len(PALETA)]
    img, d = base_pin(color, ctxt, "GUÍA DIGITAL")
    portada = Image.open(ROOT / g["img"]).convert("RGB").resize((640, 640), Image.LANCZOS)
    mascara = Image.new("L", (640, 640), 0)
    ImageDraw.Draw(mascara).rounded_rectangle([0, 0, 640, 640], 32, fill=255)
    d.rounded_rectangle([172, 202, 828, 858], 40, fill="#e4e4e7")
    img.paste(portada, (180, 210), mascara)
    d.text((500, 912), g["cat"].upper(), font=fuente("Inter-ExtraBold.otf", 28), fill=color, anchor="mm")
    f, lineas, tam = titular(d, g["titulo"], 880, [70, 62, 54, 48], 2)
    y = 950
    for l in lineas:
        d.text((500, y + tam // 2), l, font=f, fill="#101c3c", anchor="mm")
        y += int(tam * 1.12)
    fd = fuente("Inter-Regular.otf", 32)
    y += 14
    for l in partir(d, g["desc"], fd, 860, 2):
        d.text((500, y + 20), l, font=fd, fill="#586070", anchor="mm")
        y += 44
    boton(d, "Ver la guía →", color, ctxt, 1292)
    d.text((500, 1446), "Guía digital en PDF · Material educativo", font=fuente("Inter-Regular.otf", 24),
           fill="#586070", anchor="mm")
    img.save(ruta, optimize=True)


# ------------------------------------------------------------------ feed RSS y sitemap
def escribir_feed(entradas):
    items = []
    for x in entradas[-40:][::-1]:
        fecha = dt.datetime.fromisoformat(x["fecha"] + "T07:00:00+00:00")
        img = BASE + x["imagen"]
        peso = (ROOT / x["imagen"]).stat().st_size if (ROOT / x["imagen"]).exists() else 0
        items.append(
            "<item>"
            f"<title>{e(x['titulo'])}</title>"
            f"<link>{e(x['enlace'])}</link>"
            f"<guid isPermaLink=\"false\">{e(x['id'])}</guid>"
            f"<pubDate>{format_datetime(fecha)}</pubDate>"
            f"<description>{e(x['texto'])}</description>"
            f"<enclosure url=\"{e(img)}\" length=\"{peso}\" type=\"image/png\"/>"
            f"<media:content url=\"{e(img)}\" medium=\"image\" type=\"image/png\" width=\"1000\" height=\"1500\"/>"
            f"<content:encoded><![CDATA[<p><img src=\"{img}\" alt=\"{e(x['titulo'])}\" width=\"1000\" height=\"1500\"></p><p>{e(x['texto'])}</p>]]></content:encoded>"
            "</item>")
    ahora = format_datetime(dt.datetime.now(dt.timezone.utc))
    FEED.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:content="http://purl.org/rss/1.0/modules/content/" '
        'xmlns:atom="http://www.w3.org/2005/Atom">\n<channel>\n'
        f"<title>{MARCA} · Novedades</title>\n<link>{BASE}</link>\n"
        f'<atom:link href="{BASE}feed.xml" rel="self" type="application/rss+xml"/>\n'
        "<description>Rankings de lo más vendido en Amazon España y guías digitales.</description>\n"
        f"<language>es</language>\n<lastBuildDate>{ahora}</lastBuildDate>\n"
        + "\n".join(items) + "\n</channel>\n</rss>\n", encoding="utf-8")


def actualizar_sitemap(urls, fecha):
    """Anade las paginas que falten y pone la fecha del catalogo a las de rankings. No borra nada."""
    src = SITEMAP.read_text(encoding="utf-8")
    nuevas = 0
    for u in urls:
        linea = f"  <url><loc>{u}</loc><lastmod>{fecha}</lastmod><changefreq>weekly</changefreq></url>"
        patron = re.compile(r"[ \t]*<url><loc>" + re.escape(u) + r"</loc>.*?</url>")
        if patron.search(src):
            src = patron.sub(lambda m: linea, src, count=1)
        else:
            src = src.replace("</urlset>", linea + "\n</urlset>")
            nuevas += 1
    SITEMAP.write_text(src, encoding="utf-8")
    return nuevas


# ------------------------------------------------------------------ revision de la web
def revisar_web():
    paginas = sorted(list(ROOT.glob("*.html")) + list(TOP.glob("*.html")) + list((ROOT / "redesign").glob("*.html")))
    sin_tag, rotos, n_amazon = [], [], 0
    for p in paginas:
        src = p.read_text(encoding="utf-8", errors="ignore")
        rel = p.relative_to(ROOT).as_posix()
        for href in re.findall(r'href="([^"]+)"', src):
            href = html.unescape(href)
            if re.match(r"https?://(www\.)?amazon\.[a-z.]+/", href):
                n_amazon += 1
                if "tag=" + TAG not in href:
                    sin_tag.append(f"{rel}: {href[:90]}")
            elif href.startswith("/") and not href.startswith("//"):
                # la web vive en una subcarpeta en GitHub Pages: un enlace que empieza por "/" alli no existe
                rotos.append(f"{rel} → {href[:80]} (empieza por «/»: falla en GitHub Pages)")
            elif not re.match(r"(https?:|mailto:|tel:|javascript:|data:|#|/)", href):
                destino = href.split("#")[0].split("?")[0]
                if not destino:
                    continue
                d = (p.parent / destino)
                if destino.endswith("/") or d.is_dir():
                    d = d / "index.html"
                if not d.exists():
                    rotos.append(f"{rel} → {href[:80]}")
    return {"paginas": len(paginas), "amazon": n_amazon, "sin_tag": sin_tag, "rotos": rotos}


def responde(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MayordomoCompraFaro/1.0"})
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read(400000).decode("utf-8", "ignore")
    except urllib.error.HTTPError as err:
        return err.code, ""
    except Exception as err:  # sin red, DNS, tiempo agotado...
        return 0, str(err)[:80]


def avisar():
    """Tras publicar: comprueba que las dos direcciones responden y avisa a los buscadores (IndexNow)."""
    estado = leer_json(ESTADO, {})
    ultimo = (estado.get("entradas") or [{}])[-1]
    lineas = []
    for nombre, raiz in (("GitHub Pages", BASE),):
        cod, cuerpo = responde(raiz + "feed.xml")
        al_dia = ultimo.get("id", "¿?") in cuerpo
        if cod == 200 and al_dia:
            lineas.append(f"- ✅ {nombre}: publicado y al día ({raiz}feed.xml)")
        elif cod == 200:
            lineas.append(f"- ⏳ {nombre}: responde, pero aún no muestra el pin de hoy (puede tardar unos minutos)")
        else:
            lineas.append(f"- ⚠️ {nombre}: no responde (código {cod}). Mira la pestaña Actions del repositorio.")
        if cod != 200:
            continue
        host = raiz.split("/")[2]
        urls = [raiz + "top/", raiz + "feed.xml"]
        if ultimo.get("pagina"):
            urls.append(ultimo["pagina"].replace(BASE, raiz))
        cuerpo = json.dumps({"host": host, "key": CLAVE_INDEXNOW, "keyLocation": f"{raiz}{CLAVE_INDEXNOW}.txt",
                             "urlList": urls}).encode()
        try:
            req = urllib.request.Request("https://api.indexnow.org/indexnow", data=cuerpo,
                                         headers={"Content-Type": "application/json; charset=utf-8"})
            with urllib.request.urlopen(req, timeout=25) as r:
                lineas.append(f"- 🔔 Aviso a buscadores (IndexNow) para {nombre}: aceptado ({r.status})")
        except urllib.error.HTTPError as err:
            lineas.append(f"- 🔕 Aviso a buscadores para {nombre}: no aceptado (código {err.code})")
        except Exception as err:
            lineas.append(f"- 🔕 Aviso a buscadores para {nombre}: sin conexión ({str(err)[:50]})")
    texto = "\n### Publicación\n" + "\n".join(lineas) + "\n"
    with ULTIMO.open("a", encoding="utf-8") as f:
        f.write(texto)
    print(texto)


# ------------------------------------------------------------------ jornada
def jornada(hoy, forzar=False):
    for carpeta in (TOP, PINS, DATOS):
        carpeta.mkdir(parents=True, exist_ok=True)
    estado = leer_json(ESTADO, {"jornadas": 0, "entradas": []})
    fecha = hoy.isoformat()
    if not forzar and any(x["fecha"] == fecha for x in estado["entradas"]):
        print(f"La jornada del {fecha} ya estaba hecha. Nada que repetir.")
        return False

    fecha_cat, por_cat = cargar_catalogo()
    orden = orden_categorias(por_cat)
    guias = cargar_guias()
    ref = fecha_catalogo(fecha_cat, hoy)

    # 1) rankings al dia con el catalogo
    paginas = {}
    for i, cat in enumerate(orden):
        vecinas = [orden[(i + k) % len(orden)] for k in range(1, 7)]
        paginas[cat] = pagina_categoria(cat, por_cat[cat], fecha_cat, ref, vecinas)
    pagina_indice(por_cat, orden, fecha_cat)

    # 2) pin del dia: 3 rankings y 1 guia propia, en rueda
    previa = next((x for x in estado["entradas"] if x["fecha"] == fecha), None)
    n = previa.get("n", max(estado["jornadas"] - 1, 0)) if previa else estado["jornadas"]
    utm = f"utm_source=pinterest&utm_medium=social&utm_campaign=mayordomo&utm_content={fecha}"
    if guias and n % 4 == 3:
        g = guias[(n // 4) % len(guias)]
        imagen = f"pins/auto/{fecha}-guia-{g['slug']}.png"
        pin_guia(g, ROOT / imagen, n)
        entrada = {"tipo": "guia", "nombre": g["titulo"],
                   "titulo": f"{g['titulo']} · Guía digital en español"[:100],
                   "texto": f"{g['desc']} Guía digital en PDF de la colección {MARCA}: {g['cat'].lower()}. "
                            "Material educativo, sin promesas de resultados. #guiadigital #aprender",
                   "enlace": f"{BASE}guias.html?g={g['slug']}&{utm}", "pagina": f"{BASE}guias.html"}
    else:
        cat = orden[(n - n // 4 if guias else n) % len(orden)]
        imagen = f"pins/auto/{fecha}-top-{slug(cat)}.png"
        pin_categoria(cat, por_cat[cat], fecha_cat, ROOT / imagen, n)
        top3 = ", ".join(nombre_corto(p["title"], 34) for p in por_cat[cat][:3])
        mes = f"{MESES[ref.month - 1]} {ref.year}"
        entrada = {"tipo": "ranking", "nombre": cat,
                   "titulo": f"Los 10 más vendidos en {cat} · Amazon España ({mes})"[:100],
                   "texto": f"Lo que más se compra ahora en {cat} en Amazon España: {top3} y 7 más. "
                            f"Ranking completo y precio de hoy en el enlace. Contiene enlaces de afiliado. "
                            f"#publicidad #amazonespaña #{slug(cat).replace('-', '')}"[:480],
                   "enlace": f"{paginas[cat]['url']}?{utm}", "pagina": paginas[cat]["url"]}
    entrada.update({"fecha": fecha, "n": n, "id": f"mayordomo-{fecha}-{slug(entrada['nombre'])}", "imagen": imagen})
    estado["entradas"] = [x for x in estado["entradas"] if x["fecha"] != fecha] + [entrada]
    estado["entradas"].sort(key=lambda x: x["fecha"])
    estado["jornadas"] = max(estado["jornadas"], n + 1)

    # 3) feed y 4) sitemap
    escribir_feed(estado["entradas"])
    nuevas = actualizar_sitemap([f"{BASE}top/"] + [paginas[c]["url"] for c in orden], ref.isoformat())

    # 5) revision
    rev = revisar_web()
    ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=1), encoding="utf-8")

    # 6) informe
    manana_n = n + 1
    if guias and manana_n % 4 == 3:
        manana = "guía «" + guias[(manana_n // 4) % len(guias)]["titulo"] + "»"
    else:
        manana = "ranking de " + orden[(manana_n - manana_n // 4 if guias else manana_n) % len(orden)]
    inf = [f"## {hoy.day} de {MESES[hoy.month - 1]} de {hoy.year} · Jornada n.º {n + 1}", "",
           f"- 📌 **Pin del día** ({entrada['tipo']}): {entrada['titulo']}",
           f"  - Imagen: {BASE}{imagen}",
           f"  - Lleva a: {entrada['pagina']}",
           f"- 📄 Rankings al día: {len(orden)} categorías (catálogo del {fecha_cat})"
           + (f", {nuevas} páginas nuevas en el sitemap" if nuevas else ""),
           f"- 📰 Feed RSS: {min(len(estado['entradas']), 40)} pines publicados en {BASE}feed.xml",
           f"- 🔎 Revisión: {rev['paginas']} páginas y {rev['amazon']} enlaces a Amazon comprobados"]
    if rev["sin_tag"]:
        inf.append(f"- ⚠️ **{len(rev['sin_tag'])} enlaces a Amazon SIN tu código de afiliado** (no cobrarías por ellos):")
        inf += [f"  - {x}" for x in rev["sin_tag"][:8]]
    else:
        inf.append("- ✅ Todos los enlaces a Amazon llevan tu código de afiliado")
    if rev["rotos"]:
        inf.append(f"- ⚠️ {len(rev['rotos'])} enlaces internos rotos:")
        inf += [f"  - {x}" for x in rev["rotos"][:8]]
    else:
        inf.append("- ✅ Sin enlaces internos rotos")
    inf.append(f"- ⏭️ Mañana: {manana}")
    texto = "\n".join(inf) + "\n"
    ULTIMO.write_text(texto, encoding="utf-8")
    cab = "# Diario del Mayordomo\n\nLo que hizo cada día, lo más reciente arriba.\n\n"
    previo = DIARIO.read_text(encoding="utf-8").replace(cab, "", 1) if DIARIO.exists() else ""
    dias = [b for b in re.split(r"(?m)^(?=## )", previo) if b.strip() and not b.startswith(inf[0])]
    DIARIO.write_text(cab + texto + "\n" + "".join(dias[:90]), encoding="utf-8")
    print(texto)
    return True


def main():
    ap = argparse.ArgumentParser(description="Mayordomo diario de la tienda")
    ap.add_argument("--fecha", help="AAAA-MM-DD (por defecto, hoy en hora de Madrid/Varsovia)")
    ap.add_argument("--forzar", action="store_true", help="rehacer aunque la jornada de ese dia ya exista")
    ap.add_argument("--avisar", action="store_true", help="comprobar la publicacion y avisar a los buscadores")
    a = ap.parse_args()
    if a.avisar:
        avisar()
        return
    if a.fecha:
        hoy = dt.date.fromisoformat(a.fecha)
    else:
        hoy = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(hours=1)).date()
    hecho = jornada(hoy, a.forzar)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"hecho={'true' if hecho else 'false'}\n")


if __name__ == "__main__":
    sys.exit(main())
