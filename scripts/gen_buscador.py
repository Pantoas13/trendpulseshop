"""Genera buscador-regalos.html a partir del catálogo de index.html.

Uso: python3 scripts/gen_buscador.py
Vuelve a ejecutarlo cada vez que se actualice el catálogo de index.html.
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
html = (ROOT / "index.html").read_text(encoding="utf-8")

data = re.search(r"const DATA\s*=\s*`(.*?)`", html, re.S).group(1).strip().split("\n")
icons = json.loads(re.search(r"const ICONS\s*=\s*(\{[^}]*\})", html).group(1))
date_m = re.search(r"PRICE_DATE\s*=\s*\"([^\"]+)\"", html)
ranking_date = date_m.group(1) if date_m else "octubre de 2026"

EXCLUDE_CATS = {
    "Alimentación", "Industria y ciencia", "Software", "Reacondicionados",
    "Pilas y cargadores", "Componentes de PC", "Impresoras", "Oficina",
    "Grandes electrodomésticos", "Almacenamiento", "Ordenadores de sobremesa",
    "Monitores", "Informática",
}
BAD_WORDS = re.compile(
    r"pañal|toallita|wipes|detergente|papel higi|bolsas? de basura|lavavajillas|suavizante|"
    r"lejía|insecticida|recambio|filtro|cápsula|capsula|pack ahorro|limpiador|"
    r"preservativo|test de|tampón|compresa|cartucho|tóner|toner",
    re.I,
)

products = []
for line in data:
    p = line.split("|")
    cat, asin, rank, title, price = p[0], p[1], int(p[2]), " ".join(p[3:-1]), float(p[-1])
    if cat in EXCLUDE_CATS or BAD_WORDS.search(title) or price <= 0:
        continue
    products.append([cat, asin, rank, title.strip(" -,"), price])

payload = json.dumps({"p": products, "i": icons}, ensure_ascii=False, separators=(",", ":"))
template = (ROOT / "scripts" / "buscador_template.html").read_text(encoding="utf-8")
out = template.replace("__DATA__", payload).replace("__FECHA__", ranking_date)
(ROOT / "buscador-regalos.html").write_text(out, encoding="utf-8")
print(f"{len(products)} productos -> buscador-regalos.html (ranking {ranking_date})")
