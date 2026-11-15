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
7. **Publicación**: lanza la publicación en Netlify, comprueba que las dos direcciones responden
   y avisa a los buscadores (IndexNow: Bing, Yandex y otros).

## Lo único que tienes que hacer tú (una vez, desde un ordenador)

Conectar el feed en Pinterest para que los pines se publiquen solos:

1. Entra en Pinterest con tu cuenta de empresa, desde un ordenador (en el móvil no aparece).
2. Ajustes → **Crear Pines en bloque** (o «Reclamar») → **Publicación automática** → conectar feed RSS.
3. Pega esta dirección: `https://trendpulseshop-es.netlify.app/feed.xml`
4. Elige el tablero «Ofertas Amazon España» y guarda.

Pinterest tarda hasta 24 horas en crear los primeros pines. Solo acepta el feed de la dirección
que tienes reclamada (la de Netlify); por eso el feed de Netlify es el que hay que pegar.

## Cambiar cosas

- **Orden de las categorías o colores de los pines**: listas `PRIORIDAD` y `PALETA` al principio de
  `scripts/mayordomo.py`.
- **Lanzarlo a mano**: pestaña Actions → «Mayordomo diario» → Run workflow.
- **Pararlo**: pestaña Actions → «Mayordomo diario» → botón «…» → Disable workflow.

## Lo que NO hace

No compra, no cobra, no entra en tus cuentas, no inventa precios ni descuentos y no usa fotos de
Amazon ni de terceros. No garantiza ventas: consigue que tu web tenga contenido nuevo y pines
cada día; las ventas dependen de que la gente llegue y compre.
