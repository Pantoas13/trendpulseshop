"""Genera las páginas comparativas "Los mejores X" a partir del catálogo de index.html.

Uso: python3 scripts/gen_comparativas.py
El puesto en ventas y el precio aproximado salen de index.html; los textos, de este archivo.
Regla: solo decimos lo que figura en la ficha del producto (título del fabricante) y su
posición en ventas. No inventamos opiniones, pruebas ni descuentos.
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = (ROOT / "index.html").read_text(encoding="utf-8")
TAG = "trendpulsesho-21"
BASE = "https://pantoas13.github.io/trendpulseshop/"

rows = re.search(r"const DATA\s*=\s*`(.*?)`", SRC, re.S).group(1).strip().split("\n")
CAT = {}
for line in rows:
    p = line.split("|")
    CAT.setdefault(p[1], {"cat": p[0], "rank": int(p[2]), "price": float(p[-1])})
PRICE_DATE = re.search(r'PRICE_DATE\s*=\s*"([^"]+)"', SRC).group(1)

PAGES = [
    {
        "slug": "mejores-fire-tv-stick",
        "short": "Fire TV Stick",
        "title": "Qué Fire TV Stick comprar en 2026: los 5 modelos comparados",
        "desc": "Fire TV Stick HD, 4K Select, 4K, 4K Plus o 4K Max: diferencias, para qué tele es cada uno y cuál comprar. Comparativa con los modelos más vendidos de Amazon España.",
        "lead": "Si tu tele es Full HD, el Fire TV Stick HD es suficiente. Si es 4K, el 4K Plus es el más equilibrado: añade Wi-Fi 6 y Dolby Vision sin llegar al precio del Max.",
        "pick": "B0F7ZFWVTC",
        "pick_why": "Es 4K, es compatible con Wi-Fi 6 y Dolby Vision, y está entre los 3 dispositivos de Amazon más vendidos. Para la mayoría de teles modernas es el punto justo.",
        "items": [
            ("B0DJGCX6Q2", "Fire TV Stick HD", "Resolución HD y TV en directo", "Teles Full HD o una segunda tele", "No reproduce en 4K: si tu tele es 4K, mira los modelos siguientes."),
            ("B0CN41GMDK", "Fire TV Stick 4K Select", "El modelo 4K de entrada", "Quien quiere 4K gastando lo mínimo", "Es la opción 4K más básica de la gama."),
            ("B0GSH6FCBN", "Fire TV Stick 4K", "Streaming 4K sencillo", "Teles 4K y uso normal de plataformas", "Para Wi-Fi 6 o Dolby Vision, el 4K Plus."),
            ("B0F7ZFWVTC", "Fire TV Stick 4K Plus", "4K, Wi-Fi 6 y Dolby Vision", "La mayoría de teles 4K modernas", "Cuesta algo más que el 4K normal."),
            ("B0CW4HD359", "Fire TV Stick 4K Max", "El más completo de los Stick", "Quien quiere lo máximo de la gama", "Es el más caro de los cinco."),
        ],
        "guide": [
            ("Mira la resolución de tu tele", "Con una tele Full HD no notarás la diferencia del 4K. Con una 4K, elige un modelo 4K."),
            ("Tu wifi importa", "Si tu router tiene Wi-Fi 6, los modelos compatibles aprovechan mejor la conexión."),
            ("Dolby Vision y HDR", "Solo se notan si tu tele también es compatible: compruébalo en su manual."),
            ("Hace falta una entrada HDMI libre", "Todos se conectan al HDMI de la tele y a la corriente."),
        ],
        "faq": [
            ("¿Qué Fire TV Stick es mejor para una tele normal?", "Para una tele Full HD, el Fire TV Stick HD. Si la tele es 4K, el 4K Plus es el más equilibrado."),
            ("¿Necesito Prime para usar el Fire TV Stick?", "No. Puedes usar Netflix, YouTube, Disney+ y otras apps con sus propias suscripciones. Prime solo hace falta para Prime Video."),
            ("¿Cuándo baja de precio?", "Suele estar en oferta en el Black Friday (27 de noviembre de 2026) y el Cyber Monday. El precio de hoy está siempre en Amazon."),
        ],
    },
    {
        "slug": "mejores-auriculares-inalambricos-baratos",
        "short": "auriculares baratos",
        "title": "Los 5 mejores auriculares inalámbricos baratos de 2026",
        "desc": "Comparativa de auriculares inalámbricos baratos entre los más vendidos de Amazon España: Xiaomi Redmi Buds, Sony WH-CH520, Sony WH-CH720N y Soundcore de Anker.",
        "lead": "Por menos de 20 € los Xiaomi Redmi Buds 8 Active son los más vendidos. Si quieres cancelación de ruido sin gastar mucho, mira los Soundcore de Anker.",
        "pick": "B08N5ZV798",
        "pick_why": "Son de los auriculares más vendidos de Amazon España, anuncian 37 horas de batería con el estuche y cuestan menos de 20 €.",
        "items": [
            ("B08N5ZV798", "Xiaomi Redmi Buds 8 Active", "37 h de batería, botón semiintraural", "Gastar poco: diario, gimnasio, regalo", "No anuncian cancelación de ruido."),
            ("B0BTJD6LCL", "Sony WH-CH520", "Diadema inalámbrica Bluetooth, diseño ligero", "Quien prefiere cascos sobre la oreja", "Son de diadema: abultan más para llevar."),
            ("B0CRTYZG5C", "Soundcore P30i de Anker", "Cancelación de ruido, 45 h", "Transporte público y oficina", "Cuestan más del doble que los Redmi."),
            ("B0FNWCYLZN", "Soundcore P31i de Anker", "Cancelación de ruido", "Quien quiere el modelo más reciente de Soundcore", "Precio similar al P30i."),
            ("B0BTDX26B2", "Sony WH-CH720N", "Diadema con cancelación de ruido", "Viajes largos y concentrarse", "Los más caros de esta lista."),
        ],
        "guide": [
            ("Botón o diadema", "Los de botón caben en el bolsillo. Los de diadema suelen ser más cómodos durante horas."),
            ("Cancelación de ruido", "Útil en metro, avión u oficina. Si los usas en casa o haciendo deporte, puedes ahorrártela."),
            ("Batería", "Fíjate en si la cifra es solo de los auriculares o sumando el estuche."),
            ("Compatibilidad", "Todos son Bluetooth y funcionan con Android y iPhone."),
        ],
        "faq": [
            ("¿Cuáles son los auriculares inalámbricos más baratos que merecen la pena?", "Entre los más vendidos, los Xiaomi Redmi Buds 8 Active, por menos de 20 €."),
            ("¿Merece la pena la cancelación de ruido?", "Si viajas en transporte público o trabajas en sitios con ruido, sí. Para casa o deporte no es imprescindible."),
            ("¿Sirven para iPhone?", "Sí, todos los de esta lista son Bluetooth y funcionan con iPhone y Android."),
        ],
    },
    {
        "slug": "mejores-smartwatch-calidad-precio",
        "short": "smartwatch",
        "title": "Los 5 mejores smartwatch calidad-precio de 2026",
        "desc": "Comparativa de relojes inteligentes y pulseras de actividad calidad-precio entre los más vendidos de Amazon España: Xiaomi Redmi Watch, Huawei, Amazfit.",
        "lead": "Si buscas autonomía, los Xiaomi Redmi Watch 6 anuncian hasta 24 días. Para correr con GPS, el Amazfit Bip 6.",
        "pick": "B0GQL9JZS7",
        "pick_why": "Anuncia hasta 24 días de batería, sirve para hombre y mujer y está en un precio medio dentro de esta lista.",
        "items": [
            ("B0H8TCWZYF", "Xiaomi Redmi Watch 6 Lite", "Hasta 18 días de autonomía", "Primer smartwatch con poco presupuesto", "Versión Lite: menos funciones que el Redmi Watch 6."),
            ("B0GQL9JZS7", "Xiaomi Redmi Watch 6", "Hasta 24 días de batería", "Uso diario sin cargar a menudo", "Cuesta más que la versión Lite."),
            ("B0GGHLQGKB", "HUAWEI Band 11", "Pantalla AMOLED de 1,62\"", "Quien prefiere una pulsera fina", "Pantalla más pequeña que un reloj."),
            ("B0DYP9R6YT", "Amazfit Bip 6", "GPS, 14 días, AMOLED de 1,97\"", "Correr o caminar con GPS", "Menos batería que los Xiaomi."),
            ("B0F29Y67ZR", "HUAWEI Watch FIT 4", "Pantalla con brillo de hasta 2.000 nits", "Ver bien la pantalla al sol", "El más caro de los cinco."),
        ],
        "guide": [
            ("Pulsera o reloj", "Una pulsera es más fina y ligera. Un reloj tiene más pantalla y se lee mejor."),
            ("Batería", "Los días anunciados son con uso típico: con el GPS encendido duran menos."),
            ("GPS integrado", "Si sales a correr sin el móvil, busca GPS en el propio reloj."),
            ("Tu móvil", "Comprueba en la ficha que su app es compatible con tu Android o iPhone."),
        ],
        "faq": [
            ("¿Cuál es el smartwatch con más batería?", "En esta lista, el Xiaomi Redmi Watch 6, que anuncia hasta 24 días."),
            ("¿Qué smartwatch es mejor para correr?", "El Amazfit Bip 6, porque incluye GPS."),
            ("¿Son compatibles con iPhone?", "Normalmente sí, a través de la app de cada marca, pero conviene comprobarlo en la ficha de Amazon."),
        ],
    },
    {
        "slug": "mejores-camaras-vigilancia-wifi",
        "short": "cámaras de vigilancia",
        "title": "Las 5 mejores cámaras de vigilancia WiFi de 2026 para casa",
        "desc": "Comparativa de cámaras de vigilancia WiFi para interior y exterior entre las más vendidas de Amazon España: Tapo C200, Tapo C210, Blink Mini 2K+, Ring y Tapo C510W.",
        "lead": "Para interior, la Tapo C200 gira 360º y es de las más vendidas. Para exterior, la Tapo C510W también gira 360º y graba en 2K.",
        "pick": "B095CLQ1PT",
        "pick_why": "Gira 360º, graba en 2K (3 MP) y cuesta casi lo mismo que la C200, que es Full HD.",
        "items": [
            ("B07XLML2YS", "Tapo C200", "Interior, 360º, 1080p", "Vigilar una habitación gastando poco", "Full HD: la C210 da más resolución."),
            ("B095CLQ1PT", "Tapo C210", "Interior, 360º, 2K 3 MP", "Ver más detalle por poco más", "Solo para interior."),
            ("B0F3BDBWK2", "Blink Mini 2K+", "Cámara mini 2K+ de Amazon", "Quien ya tiene Alexa en casa", "No gira: plano fijo."),
            ("B0B6GKHS2S", "Ring Cámara interior (2.ª gen.)", "Cámara interior de Ring", "Quien usa otros aparatos Ring", "Funciones extra con suscripción de Ring."),
            ("B0BZMLKXL4", "Tapo C510W", "Exterior, 360º, 2K 3 MP, detección IA", "Vigilar entrada, jardín o garaje", "Necesita enchufe cerca y buena wifi fuera."),
        ],
        "guide": [
            ("Interior o exterior", "Las de exterior están preparadas para lluvia y polvo. No pongas fuera una de interior."),
            ("Que gire o fija", "Una cámara que gira 360º cubre la habitación entera con un solo aparato."),
            ("Grabación", "Revisa si guarda vídeo en tarjeta microSD o solo en la nube con suscripción."),
            ("Privacidad", "Instálala solo en tu propiedad y avisa si graba zonas comunes."),
        ],
        "faq": [
            ("¿Qué cámara de vigilancia WiFi es mejor para casa?", "Para interior, la Tapo C210: gira 360º y graba en 2K por poco dinero."),
            ("¿Hace falta pagar suscripción?", "Depende de la marca: las Tapo graban en tarjeta microSD. Ring y Blink ofrecen funciones extra con suscripción."),
            ("¿Funcionan con Alexa?", "Blink y Ring son de Amazon y funcionan con Alexa. Las Tapo también indican compatibilidad en su ficha."),
        ],
    },
    {
        "slug": "mejores-altavoces-bluetooth",
        "short": "altavoces",
        "title": "Los 5 mejores altavoces Bluetooth e inteligentes de 2026",
        "desc": "Comparativa de altavoces Bluetooth portátiles e inteligentes con Alexa entre los más vendidos de Amazon España: Echo Dot, Echo Dot Max, JBL GO 5 y Anker Soundcore.",
        "lead": "Para casa y Alexa, el Echo Dot. Para llevar a todas partes, el JBL GO 5 o el Anker SoundCore 2.",
        "pick": "B09B94956P",
        "pick_why": "Es el más vendido de esta lista (Nº 2 en Audio y Hi-Fi): wifi y Bluetooth, con Alexa para música, radio, recordatorios y domótica.",
        "items": [
            ("B09B94956P", "Echo Dot (última generación)", "Altavoz inteligente wifi y Bluetooth, con Alexa", "Casa: música, radio y domótica por voz", "Necesita enchufe: no es portátil."),
            ("B0DKLFHZDH", "Echo Dot Max", "Echo Dot con sonido más potente", "Quien quiere más sonido en el salón", "Necesita enchufe."),
            ("B0GPPRPRM5", "JBL GO 5", "Bluetooth ultraportátil, graves fuertes", "Llevar en la mochila o la playa", "Sin Alexa ni wifi."),
            ("B01MTB55WH", "Anker SoundCore 2", "24 h de batería, protección contra el agua", "Mucha batería por poco dinero", "Modelo con años en el mercado."),
            ("B0DB1753RZ", "Soundcore Select 4 Go", "Mini, 20 h, apto para la ducha", "Ducha, bici o bolsillo", "Pequeño: sonido para espacios cortos."),
        ],
        "guide": [
            ("Inteligente o portátil", "Un Echo funciona con wifi y Alexa en casa. Uno portátil funciona con batería y Bluetooth donde vayas."),
            ("Batería", "Para viajes o playa, busca 20 horas o más."),
            ("Resistencia al agua", "Si lo vas a usar en la ducha o en la piscina, que lo indique la ficha."),
            ("Tamaño y sonido", "Cuanto más pequeño, menos graves: para fiestas, uno más grande."),
        ],
        "faq": [
            ("¿Qué altavoz con Alexa comprar?", "El Echo Dot es el más vendido de esta lista. Si quieres más potencia, el Echo Dot Max."),
            ("¿Cuál es el mejor altavoz Bluetooth barato?", "Entre los más vendidos, el Anker SoundCore 2, con 24 horas de batería."),
            ("¿El Echo Dot funciona sin wifi?", "Necesita wifi para Alexa. También puede usarse como altavoz Bluetooth del móvil."),
        ],
    },
    {
        "slug": "mejores-power-bank",
        "short": "power bank",
        "title": "Los 5 mejores power bank y baterías externas de 2026",
        "desc": "Comparativa de baterías externas (power bank) entre las más vendidas de Amazon España: INIU, UGREEN Nexode y modelos magnéticos inalámbricos.",
        "lead": "Para viajar, un power bank de 20.000 mAh y 45 W carga el móvil varias veces y rápido. Para el día a día, uno de 10.000 mAh pesa menos.",
        "pick": "B0DCYR5VNR",
        "pick_why": "Es el power bank más vendido de esta lista: 20.000 mAh, carga rápida de 45 W y cable USB-C integrado.",
        "items": [
            ("B0DCYR5VNR", "INIU 20.000 mAh 45 W", "Carga rápida y cable USB-C integrado", "Viajes y días largos fuera de casa", "Pesa más que uno de 10.000 mAh."),
            ("B0HDQK4LM6", "Power Bank 20.000 mAh 22,5 W", "Carga rápida PD 20 W", "Mucha capacidad por poco dinero", "Carga más lenta que los de 45 W."),
            ("B0DSPVDYQ9", "UGREEN Nexode 45 W 20.000 mAh", "Apto para avión, carga rápida", "Viajar en avión", "Similar en precio al INIU."),
            ("B0DQD457KX", "INIU 10.000 mAh Ultra Mini 45 W", "Muy pequeño, cable USB-C desmontable", "Llevar en el bolsillo a diario", "Menos capacidad: 1 o 2 cargas de móvil."),
            ("B0FLPCM6CB", "INIU 10.000 mAh magnético", "Inalámbrico magnético, fino", "Móviles con carga magnética", "La carga inalámbrica es más lenta que con cable."),
        ],
        "guide": [
            ("Capacidad", "10.000 mAh da para 1 o 2 cargas de móvil; 20.000 mAh, para 3 o 4, según el modelo."),
            ("Potencia", "Con 20 W cargas un móvil rápido. Con 45 W también puedes cargar tablets y algunos portátiles."),
            ("Avión", "Las aerolíneas permiten power bank en cabina hasta cierto límite: revísalo con tu aerolínea."),
            ("Cable integrado", "Un cable incorporado evita olvidarse el cable en casa."),
        ],
        "faq": [
            ("¿Cuántos mAh necesito?", "Para el día a día, 10.000 mAh. Para viajes o varios aparatos, 20.000 mAh."),
            ("¿Se puede llevar un power bank en el avión?", "Sí, en el equipaje de mano, dentro del límite de la aerolínea. Nunca en la maleta facturada."),
            ("¿Cuál carga más rápido?", "En esta lista, los modelos de 45 W: INIU y UGREEN Nexode."),
        ],
    },
]


def esc(s):
    return html.escape(s, quote=True)


def price(asin):
    p = CAT[asin]["price"]
    return f"{p:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def link(asin):
    return f"https://www.amazon.es/dp/{asin}?tag={TAG}"


def page(cfg):
    items = [i for i in cfg["items"] if i[0] in CAT]
    missing = [i[0] for i in cfg["items"] if i[0] not in CAT]
    if missing:
        print("  aviso: fuera del catálogo", missing)
    pick = next(i for i in items if i[0] == cfg["pick"])
    rows_html = "".join(
        f'<tr{" class=pick" if a == cfg["pick"] else ""}><td><a href="{link(a)}" target="_blank" rel="sponsored nofollow noopener"><b>{esc(n)}</b></a>'
        f'{"<span class=badge>Nuestra elección</span>" if a == cfg["pick"] else ""}<small>Nº {CAT[a]["rank"]} en {esc(CAT[a]["cat"])}</small></td>'
        f"<td>{esc(k)}</td><td>{esc(f)}</td><td class=pr>≈ {price(a)} €</td>"
        f'<td><a class="btn" href="{link(a)}" target="_blank" rel="sponsored nofollow noopener">Ver precio en Amazon</a></td></tr>'
        for a, n, k, f, t in items
    )
    cards = "".join(
        f'<article class="item" id="p{idx}"><div class="ih"><span class="num">{idx}</span><div><h3>{esc(n)}</h3>'
        f'<small>Nº {CAT[a]["rank"]} en ventas en {esc(CAT[a]["cat"])} · ≈ {price(a)} € aprox.</small></div></div>'
        f"<p><b>Lo que ofrece:</b> {esc(k)}.</p><p><b>Ideal para:</b> {esc(f)}.</p><p><b>Ten en cuenta:</b> {esc(t)}</p>"
        f'<a class="btn" href="{link(a)}" target="_blank" rel="sponsored nofollow noopener">Ver opiniones y precio en Amazon</a></article>'
        for idx, (a, n, k, f, t) in enumerate(items, 1)
    )
    guide = "".join(f"<li><b>{esc(h)}.</b> {esc(b)}</li>" for h, b in cfg["guide"])
    faq = "".join(f"<h3>{esc(q)}</h3><p>{esc(a)}</p>" for q, a in cfg["faq"])
    others = "".join(
        f'<a href="{o["slug"]}.html">Mejores {esc(o["short"])}</a>' for o in PAGES if o["slug"] != cfg["slug"]
    )
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "FAQPage", "mainEntity": [
                {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in cfg["faq"]]},
            {"@type": "ItemList", "name": cfg["title"], "itemListElement": [
                {"@type": "ListItem", "position": i, "name": n, "url": link(a)} for i, (a, n, *_r) in enumerate(items, 1)]},
        ],
    }
    url = f'{BASE}{cfg["slug"]}.html'
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(cfg["title"])} · TrendPulseShop</title>
<meta name="description" content="{esc(cfg["desc"])}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:title" content="{esc(cfg["title"])}"><meta property="og:description" content="{esc(cfg["desc"])}">
<meta property="og:image" content="{BASE}og.png"><meta property="og:url" content="{url}"><meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<link rel="stylesheet" href="comparativa.css">
<link rel="stylesheet" href="marca/diseno.css"><script data-goatcounter="https://trendpulseshop.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script></head><body>
<header><a class="logo" href="./">Trend<b>Pulse</b>Shop</a><nav><a href="./">Lo más vendido</a><a href="buscador-regalos.html">Buscador de regalos</a><a href="regalos-black-friday.html">Regalos &lt;30 €</a></nav></header>
<main class="w">
<p class="crumb"><a href="./">Inicio</a> › Comparativas › {esc(cfg["short"][0].upper() + cfg["short"][1:])}</p>
<h1>{esc(cfg["title"])}</h1>
<p class="lead">{esc(cfg["lead"])}</p>
<p class="meta">Actualizado en noviembre de 2026 · Elegidos entre los más vendidos de Amazon España (ranking del {PRICE_DATE}). No los hemos probado: comparamos lo que indica cada fabricante y su posición en ventas.</p>
<div class="tablewrap"><table><thead><tr><th>Producto</th><th>Lo más destacado</th><th>Ideal para</th><th>Precio aprox.</th><th></th></tr></thead><tbody>{rows_html}</tbody></table></div>
<p class="note">Precios aproximados del {PRICE_DATE}. El precio de hoy, las ofertas del Black Friday y el envío con Prime se ven en Amazon.</p>
<section class="pickbox"><span class="badge">Nuestra elección</span><h2>{esc(pick[1])}</h2><p>{esc(cfg["pick_why"])}</p>
<a class="btn big" href="{link(pick[0])}" target="_blank" rel="sponsored nofollow noopener">Comprobar disponibilidad en Amazon</a></section>
<h2>Los 5 comparados uno a uno</h2>
{cards}
<section class="box"><h2>Qué mirar antes de comprar</h2><ul>{guide}</ul></section>
<section class="box"><h2>Preguntas frecuentes</h2>{faq}</section>
<a class="prime" href="https://www.amazon.es/prime?tag={TAG}" target="_blank" rel="sponsored nofollow noopener"><span>⚡ ¿Sin Prime? Pruébalo gratis: envío rápido y ofertas exclusivas del Black Friday</span><span class="pb">Probar gratis</span></a>
<section class="box"><h2>Más comparativas</h2><div class="others">{others}<a href="buscador-regalos.html">🎯 Buscador de regalos</a></div></section>
</main>
<footer><div class="w"><p>TrendPulseShop participa en el Programa de Afiliados de Amazon EU, un programa de publicidad para afiliados diseñado para ofrecer a sitios web un modo de obtener comisiones por publicidad, publicitando e incluyendo enlaces a Amazon.es. Como afiliado de Amazon, obtengo ingresos por las compras adscritas que cumplen los requisitos aplicables. <a href="privacidad.html">Privacidad</a></p></div></footer>
</body></html>
"""


CSS = """:root{--bg:#EAEDED;--surface:#fff;--ink:#0F1111;--muted:#565959;--line:#D5D9D9;--nav:#131921;--link:#007185;--btn:#FFD814;--btn-b:#FCD200;--btn-h:#F7CA00;--best:#C45500;--accent:#FF9900;--soft:#F7FAFA;--pick:#FFF8E1;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#131A22;--surface:#1D2530;--ink:#E7ECEE;--muted:#9AA4AD;--line:#3A4553;--link:#56C2D6;--soft:#222c38;--pick:#33301f;color-scheme:dark}}
*{box-sizing:border-box;margin:0}body{background:var(--bg);color:var(--ink);font:16px/1.55 Arial,Helvetica,sans-serif}a{color:var(--link)}
header{background:var(--nav);padding:12px 20px;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}header .logo{color:#fff;text-decoration:none;font-weight:800;font-size:20px}header .logo b{color:var(--accent)}header nav a{color:#fff;text-decoration:none;font-size:14px;margin-left:14px}
.w{max-width:1000px;margin:0 auto;padding:0 16px}.crumb{font-size:13px;color:var(--muted);margin:18px 0 6px}
h1{font-size:clamp(26px,4.4vw,38px);line-height:1.12}.lead{font-size:18px;margin-top:10px;max-width:70ch}.meta{font-size:13px;color:var(--muted);margin:8px 0 16px}
.tablewrap{overflow-x:auto;background:var(--surface);border:1px solid var(--line);border-radius:12px}
table{width:100%;border-collapse:collapse;font-size:14.5px;min-width:720px}th{text-align:left;font-size:12.5px;text-transform:uppercase;color:var(--muted);padding:10px 12px;border-bottom:1px solid var(--line)}
td{padding:12px;border-bottom:1px solid var(--line);vertical-align:middle}tr:last-child td{border-bottom:0}tr.pick td{background:var(--pick)}
td small{display:block;color:var(--muted);font-size:12px;margin-top:2px}td b{font-size:15px}td.pr{font-weight:700;white-space:nowrap}
.badge{display:inline-block;background:var(--accent);color:#0F1111;font-size:11.5px;font-weight:700;padding:2px 8px;border-radius:999px;margin-left:6px;vertical-align:middle}
.btn{display:inline-block;text-align:center;background:var(--btn);border:1px solid var(--btn-b);border-radius:999px;padding:9px 16px;font-weight:700;font-size:14px;color:#0F1111;text-decoration:none;white-space:nowrap}.btn:hover{background:var(--btn-h)}.btn.big{font-size:16px;padding:12px 22px;margin-top:12px}
.note{font-size:13px;color:var(--muted);margin:8px 0 0}
.pickbox{background:var(--pick);border:2px solid var(--accent);border-radius:14px;padding:20px;margin:22px 0}.pickbox .badge{margin:0 0 8px}.pickbox h2{font-size:24px}.pickbox p{margin-top:6px;max-width:65ch}
main>h2{font-size:24px;margin:28px 0 12px}
.item{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:18px;margin-bottom:12px}.item p{margin-top:6px}.item .btn{margin-top:12px}
.ih{display:flex;gap:12px;align-items:center}.num{flex:none;width:36px;height:36px;border-radius:50%;background:var(--nav);color:#fff;display:grid;place-items:center;font-weight:700}.ih h3{font-size:19px}.ih small{color:var(--muted);font-size:13px}
.box{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:20px;margin:22px 0}.box h2{font-size:21px;margin-bottom:10px}.box ul{padding-left:20px}.box li{margin:6px 0}.box h3{font-size:16px;margin:12px 0 2px}.box p{color:var(--muted)}
.others{display:flex;flex-wrap:wrap;gap:8px}.others a{background:var(--soft);border:1px solid var(--line);border-radius:999px;padding:7px 13px;text-decoration:none;font-size:14px}
.prime{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;background:var(--btn);border-radius:12px;padding:14px 18px;text-decoration:none;color:#0F1111;font-weight:700}.prime .pb{background:#0F1111;color:#fff;border-radius:999px;padding:7px 14px;font-size:14px}
footer{border-top:1px solid var(--line);padding:22px 0 40px;color:var(--muted);font-size:13px;margin-top:24px}
"""

(ROOT / "comparativa.css").write_text(CSS, encoding="utf-8")
for cfg in PAGES:
    (ROOT / f'{cfg["slug"]}.html').write_text(page(cfg), encoding="utf-8")
    print("ok", cfg["slug"])
json.dump([{"slug": c["slug"], "short": c["short"], "title": c["title"]} for c in PAGES],
          open(ROOT / "scripts" / "comparativas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
