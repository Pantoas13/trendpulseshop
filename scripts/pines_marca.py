"""Pines de Pinterest con la marca TrendPulseShop (1000x1500), hechos con HTML y Playwright.

    python3 scripts/pines_marca.py            # genera todos en promo/ig/
    python3 scripts/pines_marca.py gta6       # solo uno

Usa las fuentes y colores de marca/diseno.css. Sin fotos ni logotipos de terceros.
"""
import html
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "promo" / "ig"

PINES = {
    "gamers_tps_1": {
        "eyebrow": "GUÍA DE REGALOS · NAVIDAD",
        "titulo": "Regalos<br>para gamers",
        "sub": "13 ideas de lo más vendido en Amazon.es, según su consola o su PC",
        "chips": [("CONSOLA", "Switch 2"), ("CONSOLA", "PS5 · Xbox"), ("PC", "Ratón · teclado"), ("SETUP", "Monitor · LED")],
        "boton": "Ver la guía →",
    },
    "gamers_tps_2": {
        "eyebrow": "ANTES DE REGALAR",
        "titulo": "¿Regalo para<br>un gamer?",
        "sub": "Primero mira dónde juega. Luego elige en nuestra guía de 13 ideas.",
        "chips": [("PASO 1", "Mandos"), ("PASO 2", "Ratón y cascos"), ("PASO 3", "Monitor y SSD"), ("EXTRA", "Tarjeta regalo")],
        "boton": "13 ideas →",
    },
    "gta6": {
        "eyebrow": "GUÍA PARA JUGADORES · PS5 Y XBOX",
        "titulo": "GTA 6: qué<br>necesitas",
        "sub": "Mandos, cascos y espacio para instalarlo, de lo más vendido en Amazon.es",
        "chips": [("MANDO", "PS5 · Xbox"), ("CASCOS", "Con o sin cable"), ("ESPACIO", "SSD interno o USB"), ("GRABAR", "Capturadora 4K")],
        "boton": "Ver la guía →",
    },
    "teletrabajo_tps_1": {
        "eyebrow": "GUÍA DE REGALOS · NAVIDAD",
        "titulo": "Regalos para<br>quien teletrabaja",
        "sub": "12 ideas para su despacho en casa, de lo más vendido en Amazon.es",
        "chips": [("PANTALLA", "Monitor 23,8\""), ("POSTURA", "Soporte portátil"), ("REUNIONES", "Webcam 1080p"), ("CONCENTRACIÓN", "Cascos con ANC")],
        "boton": "Ver la guía →",
    },
    "teletrabajo_tps_2": {
        "eyebrow": "IDEAS PARA EL DESPACHO",
        "titulo": "¿Trabaja<br>desde casa?",
        "sub": "Regálale un despacho mejor: 12 ideas de lo más vendido en Amazon.es",
        "chips": [("ESCRITORIO", "Teclado y ratón"), ("CONEXIONES", "Hub USB-C"), ("ENERGÍA", "Cargador USB-C"), ("ORGANIZAR", "Agenda y pizarra")],
        "boton": "12 ideas →",
    },
}

PLANTILLA = """<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
@font-face{{font-family:B;font-weight:800;src:url({f}/bricolage-grotesque-latin-800-normal.woff2)}}
@font-face{{font-family:I;font-weight:500;src:url({f}/inter-latin-500-normal.woff2)}}
@font-face{{font-family:I;font-weight:700;src:url({f}/inter-latin-700-normal.woff2)}}
*{{box-sizing:border-box;margin:0}}body{{width:1000px;height:1500px;background:#F6F3EE;font-family:I,sans-serif;color:#15171C;overflow:hidden}}
.top{{height:760px;background:#0A3DFF;color:#fff;padding:80px;position:relative;overflow:hidden}}
.logo{{display:flex;align-items:center;gap:18px;font:800 40px B}}.logo i{{width:62px;height:62px;border-radius:14px;background:#fff;display:grid;place-items:center}}
.eb{{margin-top:70px;font:700 28px I;letter-spacing:6px;opacity:.85}}
h1{{margin-top:26px;font:800 132px/1.0 B;letter-spacing:-3px}}
.pad{{position:absolute;right:-60px;bottom:-60px;width:430px;height:260px;border:22px solid rgba(255,255,255,.22);border-radius:130px}}
.bot{{padding:70px 80px}}.sub{{font:800 46px/1.25 B;letter-spacing:-.5px}}
.chips{{display:grid;grid-template-columns:1fr 1fr;gap:22px;margin-top:50px}}
.chip{{background:#fff;border:3px solid #E4DED3;border-radius:22px;padding:24px 30px}}.chip b{{display:block;color:#0A3DFF;font:700 22px I;letter-spacing:4px}}.chip span{{font:700 34px I}}
.pie{{position:absolute;left:80px;right:80px;bottom:60px;display:flex;justify-content:space-between;align-items:center}}
.pie p{{color:#5B6170;font:500 26px/1.35 I}}.btn{{background:#15171C;color:#fff;font:700 32px I;padding:24px 34px;border-radius:16px}}
</style></head><body>
<div class="top"><div class="logo"><i><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#0A3DFF" stroke-width="3.2" stroke-linecap="round"><path d="M7 17L17 7M9 7h8v8"/></svg></i>TrendPulseShop</div>
<p class="eb">{eyebrow}</p><h1>{titulo}</h1><div class="pad"></div></div>
<div class="bot"><p class="sub">{sub}</p><div class="chips">{chips}</div></div>
<div class="pie"><p>Precio de hoy en Amazon<br>#publicidad</p><span class="btn">{boton}</span></div>
</body></html>"""


def html_pin(datos):
    chips = "".join(f'<div class="chip"><b>{html.escape(a)}</b><span>{html.escape(b)}</span></div>' for a, b in datos["chips"])
    return PLANTILLA.format(f=(RAIZ / "marca" / "fuentes").as_uri(), eyebrow=html.escape(datos["eyebrow"]),
                            titulo=datos["titulo"], sub=html.escape(datos["sub"]), chips=chips,
                            boton=html.escape(datos["boton"]))


def generar(nombres):
    from playwright.sync_api import sync_playwright
    SALIDA.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pag = nav.new_page(viewport={"width": 1000, "height": 1500})
        for n in nombres:
            tmp = SALIDA / f".pin_{n}.html"
            tmp.write_text(html_pin(PINES[n]), encoding="utf-8")
            pag.goto(tmp.as_uri())
            pag.wait_for_timeout(300)
            pag.screenshot(path=str(SALIDA / f"pin_{n}.png"))
            tmp.unlink()
            print("creado", SALIDA / f"pin_{n}.png")
        nav.close()


if __name__ == "__main__":
    generar(sys.argv[1:] or list(PINES))
