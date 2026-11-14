# CompraFaro

Portada pública renovada y copia en /redesign/. Identificador de afiliado conservado: trendpulsesho-21. El dominio se mantiene.

Funciones: búsqueda, 45 categorías de referencia, guardados locales, orden alfabético, paginación y modo oscuro. El catálogo de referencia es del 15/11/2026 (los más vendidos de Amazon.es ese día); el ranking cambia a diario.

## Imágenes oficiales de Amazon

La portada carga /productos-api.js antes de iniciar. El flujo de Creators API actualiza este archivo cada seis horas e incluye API_UPDATED_AT. Solo se muestran imágenes de dominios oficiales aprobados y con menos de 24 horas desde la actualización. Las imágenes se solicitan directamente a Amazon, sin descargarlas al repositorio. Productos con imagen oficial se muestran primero. Las fichas sin imagen ofrecen acceso a la foto en Amazon; no usan fotografías genéricas.

Configurar CREATORS_CLIENT_ID y CREATORS_CLIENT_SECRET en Settings > Secrets and variables > Actions > Repository secrets, en Pantoas13/trendpulseshop. PARTNER_TAG es opcional. Ejecutar Actualizar productos desde Amazon y verificar su resultado. Su finalización correcta dispara Publicar en Netlify, también cuando el commit del catálogo procede de GITHUB_TOKEN.

No incluir secretos en archivos ni en el chat. No necesita acceso al servidor Minotauro.

## Publicación y reversión

El flujo Publicar en Netlify utiliza la configuración existente. La portada anterior puede recuperarse del historial Git anterior al merge de la PR 1. La copia /redesign/ permanece como acceso alternativo.

## Verificación

node --check redesign/app.js
python3 -m py_compile scripts/actualizar_productos.py
python3 -m http.server 8080

En local, abrir http://localhost:8080/. Los productos oficiales requieren un productos-api.js válido y reciente.
