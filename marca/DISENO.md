# Sistema de diseño de TrendPulseShop

Una sola capa, `marca/diseno.css`, que se carga la última en todas las páginas (después de su estilo propio).
Antes cada parte de la web tenía su estilo (portada azul con Georgia, guías tipo Amazon negro y amarillo,
rankings con otro azul): ahora todo se ve como una sola marca.

Hecho el 28-11-2026 siguiendo las reglas de tres skills de diseño de código abierto (taste-skill, MIT;
ui-ux-pro-max, MIT; impeccable, Apache 2.0): nada de degradados morados, un solo estilo de botón y de tarjeta,
letras propias, zonas de toque de 44 px y revisión con capturas en móvil y ordenador.

## Reglas
- **Letras:** Bricolage Grotesque (titulares, 700/800) e Inter (texto, 400-700). Guardadas en `marca/fuentes/`
  con su licencia SIL OFL; no dependen de Google Fonts.
- **Colores:** papel `#F6F3EE`, tarjeta `#FFFFFF`, tinta `#15171C`, gris `#5B6170`, línea `#E4DED3`.
  Azul de marca `#0A3DFF` solo para enlaces y el estado "al pasar". Naranja `#E8501E` solo para ofertas,
  etiquetas y "nuestra elección". Modo oscuro con los mismos papeles.
- **Botones:** uno principal (píldora de tinta que se vuelve azul al pasar) y uno de texto subrayado.
- **Tarjetas:** borde fino, radio 16 px, sombra suave, suben 2 px al pasar.
- **Sin fotos de producto** (hasta que la API de Amazon las dé): bloque del color de la categoría con su icono
  y la marca del producto, nunca "Ver foto real en Amazon".
- **Nunca:** violeta o morado, degradados de fondo, emojis como iconos de interfaz, letras del sistema
  (Arial, Georgia), dos estilos de botón en la misma página.

## Páginas nuevas
Añadir antes de `</head>`: `<link rel="stylesheet" href="marca/diseno.css">` (en `top/`: `../marca/diseno.css`).
Los generadores (`scripts/gen_comparativas.py`, `scripts/mayordomo.py`, `scripts/buscador_template.html`)
ya lo ponen solos.
