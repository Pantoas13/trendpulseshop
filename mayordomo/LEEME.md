# El Mayordomo de la tienda

Trabaja solo cada día a las 06:23 (hora de Polonia y España en invierno) desde GitHub Actions.
No necesita claves, no usa IA de pago y no cuesta dinero.

## Qué hace cada día

1. **Rankings al día**: rehace las páginas «Los 10 más vendidos en…» de la carpeta `top/`
   (una por categoría) con el catálogo actual (`redesign/catalog.json`).
2. **Pin del día**: dibuja una imagen vertical (1000×1500) en `pins/auto/`. Tres días toca un
   ranking; el cuarto, una de tus guías digitales de `guias.html`.
3. **Feed RSS** (`feed.xml`): añade el pin. Pinterest puede publicar solo desde ese feed.
4. **Sitemap**: añade las páginas nuevas para Google.
5. **Revisión**: comprueba que todos los enlaces a Amazon llevan tu código de afiliado y que
   no hay enlaces internos rotos.
6. **Informe**: lo deja en `mayordomo/diario.md`, en la pestaña Actions y como comentario en el
   issue «Informe diario del Mayordomo».
7. **Publicación**: GitHub Pages publica la web sola; el mayordomo comprueba que responde y
   avisa a los buscadores (IndexNow: Bing, Yandex y otros).

La dirección que se actualiza cada día es https://pantoas13.github.io/trendpulseshop/
La copia de Netlify no se actualiza a diario (cada publicación allí gasta créditos).

## Lo único que tienes que hacer tú (una vez, desde un ordenador)

Conectar el feed en Pinterest para que los pines se publiquen solos. En el móvil no aparece la opción.

**Paso 1. Reclamar la dirección de GitHub Pages** (Pinterest solo acepta feeds de una web reclamada):

1. Pinterest (cuenta de empresa) → Ajustes → **Cuentas reclamadas** → Sitios web → **Reclamar**.
2. Elige «Añadir etiqueta HTML», pulsa Continuar y escribe: `https://pantoas13.github.io/trendpulseshop/`
3. Pulsa Verificar. La portada ya lleva tu etiqueta de Pinterest. Si Pinterest te da una etiqueta
   distinta, pásasela a Claude y la pone.

**Paso 2. Conectar el feed:**

1. Ajustes → **Crear Pines en bloque** → **Publicación automática** (conectar feed RSS).
2. Pega: `https://pantoas13.github.io/trendpulseshop/feed.xml`
3. Elige el tablero «Ofertas Amazon España» y guarda.

Pinterest tarda hasta 24 horas en crear los primeros pines y después sigue solo, cada día.

## Cambiar cosas

- **Orden de las categorías o colores de los pines**: listas `PRIORIDAD` y `PALETA` al principio de
  `scripts/mayordomo.py`.
- **Lanzarlo a mano**: pestaña Actions → «Mayordomo diario» → Run workflow.
- **Pararlo**: pestaña Actions → «Mayordomo diario» → botón «…» → Disable workflow.

## Lo que NO hace

No compra, no cobra, no entra en tus cuentas, no inventa precios ni descuentos y no usa fotos de
Amazon ni de terceros. No garantiza ventas: consigue que tu web tenga contenido nuevo y pines
cada día; las ventas dependen de que la gente llegue y compre.
