#!/usr/bin/env python3
"""
TrendPulseShop - actualiza productos desde la API oficial de Amazon (Creators API).

Escribe el archivo productos-api.js, que index.html carga automáticamente.
Lo ejecuta solo GitHub cada semana (.github/workflows/actualizar-productos.yml).

Necesita estos "secrets" en GitHub (Settings > Secrets and variables > Actions):
  CREATORS_CLIENT_ID      -> Client ID de la Creators API
  CREATORS_CLIENT_SECRET  -> Client Secret de la Creators API
  (opcional) PARTNER_TAG  -> tu tag de afiliado; por defecto trendpulsesho-21

Si los secrets no existen todavía, el script no cambia nada y termina sin error.
Solo usa la librería estándar de Python (no hay que instalar nada).
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

# ---------------- CONFIGURACIÓN ----------------
TOKEN_URL = "https://api.amazon.co.uk/auth/o2/token"        # región Europa (incluye España)
API_BASE = "https://creatorsapi.amazon"
SEARCH_PATH = "/catalog/v1/searchItems"
MARKETPLACE = "www.amazon.es"
PAGINAS_POR_BUSQUEDA = 2     # 10 productos por página (máximo de Amazon: 10 páginas)
PAUSA_SEGUNDOS = 1.2         # para respetar el límite de peticiones por segundo
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "productos-api.js")

# (SearchIndex de Amazon.es, categoría como se ve en tu tienda, palabras clave)
BUSQUEDAS = [
    ("Electronics", "Electrónica", ["auriculares bluetooth", "smartwatch", "power bank", "altavoz bluetooth"]),
    ("Computers", "Informática", ["portátil", "ratón inalámbrico", "teclado gaming", "ssd"]),
    ("VideoGames", "Videojuegos", ["consola retro portátil", "nintendo switch", "mando ps5"]),
    ("HomeAndKitchen", "Hogar y cocina", ["freidora de aire", "cafetera", "robot aspirador"]),
    ("Appliances", "Grandes electrodomésticos", ["lavadora", "frigorífico"]),
    ("ToysAndGames", "Juguetes", ["lego", "juego de mesa"]),
    ("Beauty", "Belleza", ["sérum facial", "secador de pelo"]),
    ("HealthPersonalCare", "Salud", ["creatina", "proteína", "báscula"]),
    ("SportsAndOutdoors", "Deporte", ["mancuernas", "esterilla yoga", "bicicleta estática"]),
    ("Baby", "Bebé", ["pañales", "vigilabebés"]),
    ("PetSupplies", "Mascotas", ["pienso perro", "arena gato"]),
    ("Automotive", "Coche y moto", ["accesorios coche", "casco moto"]),
    ("ToolsAndHomeImprovement", "Bricolaje", ["taladro", "caja de herramientas"]),
    ("GardenAndOutdoor", "Jardín", ["manguera", "barbacoa"]),
    ("OfficeProducts", "Oficina", ["silla de oficina", "impresora"]),
    ("Lighting", "Iluminación", ["bombilla inteligente", "tira led"]),
    ("Fashion", "Moda", ["zapatillas", "mochila"]),
    ("Books", "Libros", ["novela", "libro infantil"]),
    ("GroceryAndGourmetFood", "Alimentación", ["café en grano", "aceite de oliva"]),
    ("MusicalInstruments", "Instrumentos musicales", ["guitarra", "teclado piano"]),
]
RECURSOS = [
    "itemInfo.title",
    "offersV2.listings.price",
    "images.primary.large",
    "images.primary.medium",
]
# -----------------------------------------------


def post_json(url, body, headers):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    for k, v in headers.items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def obtener_token(client_id, client_secret):
    r = post_json(TOKEN_URL, {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "creatorsapi::default",
    }, {})
    return r["access_token"]


def buscar(token, tag, search_index, palabras, pagina):
    return post_json(API_BASE + SEARCH_PATH, {
        "partnerTag": tag,
        "marketplace": MARKETPLACE,
        "searchIndex": search_index,
        "keywords": palabras,
        "itemCount": 10,
        "itemPage": pagina,
        "sortBy": "Featured",
        "languagesOfPreference": ["es_ES"],
        "resources": RECURSOS,
    }, {
        "Authorization": "Bearer " + token,
        "x-marketplace": MARKETPLACE,
    })


def leer_item(it, categoria, puesto):
    asin = it.get("asin")
    titulo = ((it.get("itemInfo") or {}).get("title") or {}).get("displayValue")
    precio = None
    for l in ((it.get("offersV2") or {}).get("listings") or []):
        m = ((l.get("price") or {}).get("money") or {})
        if m.get("amount") is not None:
            precio = float(m["amount"])
            break
    prim = ((it.get("images") or {}).get("primary") or {})
    foto = (prim.get("large") or prim.get("medium") or {}).get("url", "")
    if not (asin and titulo and precio and precio > 0):
        return None
    return {"cat": categoria, "asin": asin, "rank": puesto,
            "title": titulo[:140], "price": round(precio, 2), "img": foto}


def main():
    cid = os.environ.get("CREATORS_CLIENT_ID", "").strip()
    csec = os.environ.get("CREATORS_CLIENT_SECRET", "").strip()
    tag = os.environ.get("PARTNER_TAG", "").strip() or "trendpulsesho-21"
    if not cid or not csec:
        print("Aún no hay credenciales de la Creators API. No se cambia nada.")
        return 0

    try:
        token = obtener_token(cid, csec)
    except urllib.error.HTTPError as e:
        print("ERROR al obtener el token:", e.code, e.read().decode("utf-8", "ignore")[:500])
        return 1

    productos, vistos, errores = [], set(), 0
    for search_index, categoria, lista in BUSQUEDAS:
        puesto = 0
        for palabras in lista:
            for pagina in range(1, PAGINAS_POR_BUSQUEDA + 1):
                try:
                    r = buscar(token, tag, search_index, palabras, pagina)
                except urllib.error.HTTPError as e:
                    errores += 1
                    print(f"  aviso {categoria}/{palabras} p{pagina}: HTTP {e.code} {e.read().decode('utf-8','ignore')[:200]}")
                    time.sleep(PAUSA_SEGUNDOS)
                    break
                items = ((r.get("searchResult") or {}).get("items")) or []
                for it in items:
                    p = leer_item(it, categoria, puesto + 1)
                    if p and p["asin"] not in vistos:
                        puesto += 1
                        p["rank"] = puesto
                        vistos.add(p["asin"])
                        productos.append(p)
                time.sleep(PAUSA_SEGUNDOS)
                if len(items) < 10:
                    break
        print(f"{categoria}: {puesto} productos")

    if not productos:
        print("La API no devolvió productos; se deja el archivo como estaba.")
        return 1 if errores else 0

    fecha = datetime.now(timezone.utc).strftime("%d/%m/%Y")
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("/* Generado automáticamente desde la Creators API de Amazon. No editar a mano. */\n")
        f.write("window.API_PRICE_DATE = " + json.dumps(fecha) + ";\n")
        f.write("window.API_PRODUCTS = " + json.dumps(productos, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print(f"Listo: {len(productos)} productos guardados en productos-api.js ({fecha}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
