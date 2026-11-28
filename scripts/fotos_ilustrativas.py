#!/usr/bin/env python3
"""Fotos ilustrativas por tipo de producto (mientras la API de Amazon no da las fotos oficiales).

Busca en Openverse (el buscador de imágenes con licencia libre de WordPress) UNA foto por tipo de producto
(auriculares, cafetera, smartwatch...) con licencia que permite uso comercial: CC0, dominio público o CC BY.
No usa fotos de Amazon ni de tiendas: las normas de afiliados lo prohíben.

En la web se muestran con la etiqueta "Imagen ilustrativa": enseñan el tipo de producto, no el modelo exacto.
Los autores y licencias quedan en creditos-imagenes.html (CC BY obliga a citar al autor).

Las fotos se eligen a ojo, nunca solas (las automáticas salían mal: pilas en una foto de guerra...):
  1. --candidatos auriculares cafe ...   (o "todos")  descarga hasta 8 opciones por tipo en img/candidatos/
  2. Claude (o Iván) mira las opciones y elige:  --elegir auriculares=1,4,6 cafe=2
     Cada tipo puede tener varias fotos; cada producto usa siempre la misma (según su ASIN), así las tarjetas varían.
  3. Sin argumentos: solo rehace tipos.json y la página de créditos.
Todo producto tiene foto: si su tipo no tiene, usa la de su categoría y, si tampoco, la de "compras".
Lo ejecuta GitHub (.github/workflows/fotos-ilustrativas.yml) porque desde la nube de Claude no se llega a Openverse.

Escribe:
  img/tipos/<tipo>.webp          la foto, 640x480
  redesign/tipos.json            reglas para que app.js sepa qué foto va con cada producto
  creditos-imagenes.html         autores, licencias y enlaces a la foto original
"""
import argparse
import html
import io
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageOps

RAIZ = Path(__file__).resolve().parent.parent
CARPETA = RAIZ / "img" / "tipos"
REGLAS = RAIZ / "redesign" / "tipos.json"
CREDITOS = CARPETA / "creditos.json"
CANDIDATOS = RAIZ / "img" / "candidatos"
PAGINA = RAIZ / "creditos-imagenes.html"
API = "https://api.openverse.org/v1/images/"
UA = "TrendPulseShop/1.0 (fotos ilustrativas; https://trendpulseshop-es.netlify.app)"
LICENCIAS = "cc0,pdm,by"

# (tipo, palabras del título en español (regex), búsqueda en inglés, nombre para el texto alternativo)
TIPOS = [
    ("mando", r"mando|gamepad|controller", "gamepad controller", "un mando de videojuegos"),
    ("consola", r"nintendo|switch|playstation|ps5|ps4|xbox|consola", "playstation console", "una consola"),
    ("auriculares", r"auricular|cascos|headphone|earbuds|airpods|buds", "wireless headphones", "unos auriculares"),
    ("smartwatch", r"smartwatch|reloj inteligente|pulsera de actividad|smartband|watch", "smartwatch wrist", "un reloj inteligente"),
    ("altavoz", r"altavoz|speaker|barra de sonido|echo dot|echo pop", "bluetooth speaker", "un altavoz"),
    ("powerbank", r"power ?bank|bater[ií]a externa", "power bank charging phone", "una batería externa"),
    ("cargador", r"cargador|cable usb|cable lightning|adaptador de corriente", "usb charger cable", "un cargador"),
    ("pilas", r"\bpilas?\b|bater[ií]as? (aa|aaa|alcalin)|cr2032", "aa batteries", "unas pilas"),
    ("movil", r"smartphone|m[oó]vil|iphone|galaxy|redmi|poco|xiaomi.*gb", "smartphone in hand", "un teléfono móvil"),
    ("tablet", r"tablet|ipad|fire hd|kindle", "tablet computer", "una tablet"),
    ("portatil", r"ordenador port[aá]til|laptop|notebook|chromebook|macbook|port[aá]til.*(intel|amd|ryzen|core i|\bram\b|ssd)", "laptop on desk", "un portátil"),
    ("pc", r"ordenador de sobremesa|mini pc|\bnuc\b|torre gaming|pc gaming", "desktop computer", "un ordenador de sobremesa"),
    ("monitor", r"monitor", "computer monitor desk", "un monitor"),
    ("raton", r"rat[oó]n|mouse", "computer mouse", "un ratón"),
    ("teclado", r"teclado|keyboard", "mechanical keyboard", "un teclado"),
    ("almacenamiento", r"\bssd\b|disco duro|pendrive|memoria usb|tarjeta (micro ?)?sd", "ssd drive", "un disco de almacenamiento"),
    ("router", r"router|wifi mesh|repetidor|extensor wifi", "wifi router", "un router"),
    ("tv", r"\btv\b|televisor|smart tv|fire tv|chromecast|google tv", "television living room", "un televisor"),
    ("camara", r"c[aá]mara|webcam|gopro|dashcam", "digital camera lens", "una cámara"),
    ("cafetera", r"cafetera", "coffee machine", "una cafetera"),
    ("cafe", r"caf[eé]|c[aá]psulas|nespresso|dolce gusto|espresso", "coffee beans cup", "café"),
    ("freidora", r"freidora", "air fryer appliance", "una freidora de aire"),
    ("aspirador", r"aspirador|robot aspirador|roomba", "vacuum cleaner appliance", "un aspirador"),
    ("cocina", r"sart[eé]n|olla|cuchill|batidora|robot de cocina|tostadora|microondas|hervidor", "kitchen utensils wooden", "utensilios de cocina"),
    ("iluminacion", r"bombilla|linterna|l[aá]mpara|tira led|luz led|foco", "led light bulb", "una bombilla"),
    ("juguete", r"lego|juguete|mu[nñ]eca|peluche|playmobil|puzzle|juego de mesa", "colorful toys", "juguetes"),
    ("libro", r"libro|novela|tapa blanda|tapa dura", "books stack", "libros"),
    ("belleza", r"crema|s[eé]rum|s[eé]rum|maquillaje|rimel|m[aá]scara de pesta|labial|perfume|colonia|champ[uú]|cosm", "skincare products", "productos de belleza"),
    ("afeitado", r"afeitad|depiladora|recortadora|oneblade", "electric razor", "una afeitadora"),
    ("deporte", r"mancuerna|esterilla|yoga|bicicleta est|cinta de correr|balón|pelota|fitness|gimnasio", "dumbbells gym", "material de deporte"),
    ("mascotas", r"perro|gato|mascota|pienso|arena para", "dog and cat", "mascotas"),
    ("bebe", r"pa[nñ]al|beb[eé]|toallitas", "baby bottle pacifier", "productos para bebé"),
    ("herramientas", r"taladro|destornillador|llave|herramienta|bricolaje|sierra", "power tools", "herramientas"),
    ("coche", r"coche|moto|neum[aá]tico|aceite motor|limpiaparabrisas", "car interior accessories", "accesorios de coche"),
    ("leche", r"leche|bebida (vegetal|de avena|de almendra)", "glass of milk", "leche"),
    ("cerveza", r"cerveza|lager", "beer glass", "cerveza"),
    ("refresco", r"refresco|\bcola\b|zumo|agua mineral|t[oó]nica", "soda cans", "refrescos"),
    ("alimentacion", r"chocolate|turr[oó]n|galleta|aceite de oliva|pasta|arroz|conserva", "grocery basket vegetables", "alimentos"),
    ("oficina", r"impresora|cartucho|t[oó]ner|papel a4|bol[ií]grafo|cuaderno|agenda", "office supplies pens notebook", "material de oficina"),
    ("salud", r"tensi[oó]metro|term[oó]metro|vitamina|suplemento|mascarilla", "first aid kit", "productos de salud"),
    ("moda", r"zapatilla|camiseta|sudadera|mochila|bolso|cartera|gafas de sol", "fashion accessories", "moda"),
    ("jardin", r"jard[ií]n|manguera|cortac[eé]sped|planta|maceta", "garden tools shovel", "jardín"),
    ("vinilo", r"vinilo|\bcd\b|[aá]lbum", "vinyl records", "discos de música"),
    ("pelicula", r"blu-?ray|dvd|pel[ií]cula|temporada", "movie film reel", "una película"),
    ("software", r"antivirus|software|licencia|office 20|windows 1", "software on computer screen", "programas de ordenador"),
    ("regalo", r"personalizad|regalo|handmade|hecho a mano", "gift box wrapped", "un regalo"),
    ("musica", r"guitarra|piano|teclado musical|ukelele|micr[oó]fono", "acoustic guitar", "instrumentos musicales"),
    ("compras", r"$^", "shopping bags gifts", "productos variados"),
]

# Búsquedas de más para tener opciones al elegir
EXTRA = {
    "aspirador": ["vacuum cleaner", "robot vacuum"], "bebe": ["baby bottle", "baby toys rattle"],
    "pilas": ["batteries closeup", "rechargeable batteries"], "freidora": ["air fryer", "deep fryer kitchen"],
    "router": ["wireless router antennas", "internet router"], "consola": ["game console", "nintendo switch"],
    "mando": ["video game controller", "xbox controller"], "salud": ["thermometer", "vitamins pills bottle"],
    "jardin": ["gardening tools", "watering can garden"], "compras": ["shopping bags", "gift boxes"],
}

# Si ninguna palabra del título encaja, foto por categoría de la tienda
CATEGORIA = {
    "Auriculares y audio portátil": "auriculares", "Audio y Hi-Fi": "altavoz", "Electrónica": "cargador",
    "Dispositivos Amazon": "altavoz", "Informática": "portatil", "Portátiles": "portatil", "Monitores": "monitor",
    "Componentes de PC": "almacenamiento", "Almacenamiento": "almacenamiento", "Accesorios de informática": "raton",
    "Redes y wifi": "router", "Impresoras": "oficina", "Oficina": "oficina", "Tablets": "tablet",
    "Móviles y accesorios": "movil", "TV y home cinema": "tv", "Fotografía y vídeo": "camara",
    "Videojuegos": "mando", "Juguetes": "juguete", "Libros": "libro", "eBooks Kindle": "libro",
    "Hogar y cocina": "cocina", "Electrodomésticos": "cocina", "Grandes electrodomésticos": "cocina",
    "Iluminación": "iluminacion", "Belleza": "belleza", "Salud": "salud", "Deporte": "deporte",
    "Mascotas": "mascotas", "Bebé": "bebe", "Bricolaje": "herramientas", "Industria y ciencia": "herramientas",
    "Coche y moto": "coche", "Electrónica para coche": "coche", "Alimentación": "alimentacion", "Moda": "moda",
    "Jardín": "jardin", "Instrumentos musicales": "musica", "Pilas y cargadores": "pilas",
    "CD y vinilos": "vinilo", "Películas y series": "pelicula", "Software": "software", "Handmade": "regalo",
    "Ordenadores de sobremesa": "pc", "Reacondicionados": "portatil",
}


def pedir(url, intentos=3):
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=40) as r:  # nosec B310 (URLs https de Openverse y sus fuentes)
                return r.read()
        except Exception as e:
            if i == intentos - 1:
                raise
            print(f"   reintento por {e}")
            time.sleep(5 * (i + 1))


def buscar(consulta, saltar=0):
    q = urllib.parse.urlencode({"q": consulta, "license": LICENCIAS, "category": "photograph", "mature": "false",
                                "page_size": 20, "extension": "jpg,png"})
    datos = json.loads(pedir(f"{API}?{q}"))
    buenos = [r for r in datos.get("results", [])
              if (r.get("width") or 0) >= 800 and (r.get("height") or 0) >= 500 and r.get("url")]
    return buenos[saltar:]


def guardar_foto(resultado, destino):
    crudo = pedir(resultado["url"])
    im = Image.open(io.BytesIO(crudo)).convert("RGB")
    im = ImageOps.fit(im, (640, 480), Image.LANCZOS, centering=(0.5, 0.5))
    im.save(destino, "WEBP", quality=78, method=6)


def pagina_creditos(creditos):
    filas = []
    for tipo, c in sorted(creditos.items()):
        for f in c.get("fotos", []):
            autor = html.escape(f.get("autor") or "autor desconocido")
            filas.append(f'<li><img src="img/tipos/{f["archivo"]}" alt="" width="120" height="90" loading="lazy">'
                         f'<div><b>{html.escape(c["nombre"].capitalize())}</b><br>«{html.escape(f.get("titulo") or "sin título")}», de {autor}. '
                         f'Licencia <a href="{html.escape(f.get("licencia_url") or "")}" rel="nofollow">{html.escape(f.get("licencia") or "")}</a>. '
                         f'<a href="{html.escape(f.get("fuente") or "")}" rel="nofollow">Ver original</a>. Recortada y reducida.</div></li>')
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Créditos de las imágenes · TrendPulseShop</title><meta name="robots" content="noindex">
<link rel="icon" href="redesign/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="top/top.css">
<style>ul.cred{{list-style:none;padding:0;display:grid;gap:12px}}ul.cred li{{display:flex;gap:14px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px}}ul.cred img{{border-radius:10px;object-fit:cover;flex:none}}</style>
<link rel="stylesheet" href="marca/diseno.css"><script data-goatcounter="https://trendpulseshop.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script></head><body>
<header><div class="w"><a class="logo" href="index.html"><span>↗</span>TrendPulseShop</a></div></header>
<main class="w"><h1>Créditos de las imágenes</h1>
<p class="lead">Las fotos de producto de la tienda son <b>ilustrativas</b>: muestran el tipo de producto, no el modelo exacto.
Son fotos con licencia libre (CC0, dominio público o CC BY) encontradas en Openverse. El producto real, su foto y su precio se ven en Amazon.</p>
<ul class="cred">{''.join(filas)}</ul></main>
<footer><div class="w"><a href="index.html">Volver a la tienda</a></div></footer></body></html>
"""


def info_de(r):
    return {"titulo": r.get("title"), "autor": r.get("creator"),
            "licencia": f"{(r.get('license') or '').upper()} {r.get('license_version') or ''}".strip(),
            "licencia_url": r.get("license_url") or "https://creativecommons.org/",
            "fuente": r.get("foreign_landing_url") or r.get("url"), "openverse_id": r.get("id")}


def migrar(creditos):
    """Formato antiguo (una foto por tipo) -> {"nombre", "fotos": [...]}."""
    nombres = {t: n for t, _, _, n in TIPOS}
    for tipo, c in list(creditos.items()):
        if "fotos" in c:
            continue
        if c.get("vetado"):
            creditos[tipo] = {"nombre": nombres.get(tipo, tipo), "fotos": []}
            continue
        viejo = CARPETA / f"{tipo}.webp"
        nuevo = CARPETA / f"{tipo}-1.webp"
        if viejo.exists():
            viejo.rename(nuevo)
        foto = {k: c.get(k) for k in ("titulo", "autor", "licencia", "licencia_url", "fuente", "openverse_id")}
        foto["archivo"] = nuevo.name
        creditos[tipo] = {"nombre": c.get("nombre", nombres.get(tipo, tipo)), "fotos": [foto] if nuevo.exists() else []}
    return creditos


def candidatos(tipos, n):
    consultas = {t: q for t, _, q, _ in TIPOS}
    for tipo in tipos:
        carpeta = CANDIDATOS / tipo
        carpeta.mkdir(parents=True, exist_ok=True)
        vistos, opciones = set(), []
        for consulta in [consultas[tipo]] + EXTRA.get(tipo, []):
            try:
                resultados = buscar(consulta)
            except Exception as e:
                print(f"⚠️ {tipo}: búsqueda «{consulta}» falló ({e})")
                continue
            for r in resultados:
                if len(opciones) >= n:
                    break
                if r.get("id") in vistos:
                    continue
                vistos.add(r.get("id"))
                k = len(opciones) + 1
                try:
                    guardar_foto(r, carpeta / f"{k}.webp")
                except Exception as e:
                    print(f"   descarga fallida: {e}")
                    continue
                opciones.append(info_de(r) | {"archivo": f"{k}.webp", "consulta": consulta})
            time.sleep(1.2)
            if len(opciones) >= n:
                break
        (carpeta / "info.json").write_text(json.dumps(opciones, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"🔎 {tipo}: {len(opciones)} opciones")


def elegir(creditos, elecciones):
    nombres = {t: n for t, _, _, n in TIPOS}
    for e in elecciones:
        tipo, _, nums = e.partition("=")
        info = json.loads((CANDIDATOS / tipo / "info.json").read_text(encoding="utf-8"))
        for viejo in CARPETA.glob(f"{tipo}-*.webp"):
            viejo.unlink()
        fotos = []
        for i, k in enumerate([int(x) for x in nums.split(",") if x.strip()], 1):
            op = info[k - 1]
            destino = CARPETA / f"{tipo}-{i}.webp"
            destino.write_bytes((CANDIDATOS / tipo / op["archivo"]).read_bytes())
            fotos.append({x: op.get(x) for x in ("titulo", "autor", "licencia", "licencia_url", "fuente", "openverse_id")} | {"archivo": destino.name})
        creditos[tipo] = {"nombre": nombres.get(tipo, tipo), "fotos": fotos}
        print(f"✅ {tipo}: {len(fotos)} fotos elegidas")
    return creditos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidatos", nargs="*", help="tipos (o 'todos') de los que bajar opciones a img/candidatos/")
    ap.add_argument("--n", type=int, default=8, help="opciones por tipo")
    ap.add_argument("--elegir", nargs="*", default=[], help="tipo=1,4,6 ... (números de img/candidatos/<tipo>/)")
    ap.add_argument("--quitar", nargs="*", default=[], help="tipos que se quedan sin foto propia")
    ap.add_argument("--limpiar", action="store_true", help="borrar img/candidatos/ al terminar")
    a = ap.parse_args()
    CARPETA.mkdir(parents=True, exist_ok=True)
    creditos = migrar(json.loads(CREDITOS.read_text(encoding="utf-8")) if CREDITOS.exists() else {})
    if a.candidatos:
        tipos = [t for t, _, _, _ in TIPOS] if a.candidatos == ["todos"] else a.candidatos
        candidatos(tipos, a.n)
    if a.elegir:
        creditos = elegir(creditos, a.elegir)
    for tipo in a.quitar:
        for viejo in CARPETA.glob(f"{tipo}-*.webp"):
            viejo.unlink()
        creditos[tipo] = {"nombre": creditos.get(tipo, {}).get("nombre", tipo), "fotos": []}
    if a.limpiar and CANDIDATOS.exists():
        import shutil
        shutil.rmtree(CANDIDATOS)
    CREDITOS.write_text(json.dumps(creditos, ensure_ascii=False, indent=1), encoding="utf-8")
    fotos = {t: [f["archivo"] for f in c.get("fotos", []) if (CARPETA / f["archivo"]).exists()] for t, c in creditos.items()}
    reglas = {"tipos": [{"tipo": t, "re": r, "nombre": n, "fotos": fotos.get(t, [])} for t, r, _, n in TIPOS],
              "categorias": {c: t for c, t in CATEGORIA.items() if fotos.get(t)},
              "respaldo": "compras" if fotos.get("compras") else None}
    REGLAS.write_text(json.dumps(reglas, ensure_ascii=False, indent=1), encoding="utf-8")
    PAGINA.write_text(pagina_creditos(creditos), encoding="utf-8")
    print(f"Tipos con foto: {sum(1 for v in fotos.values() if v)}/{len(TIPOS)} · fotos: {sum(len(v) for v in fotos.values())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
