/* TrendPulseShop · Amazon según el país del visitante
 * Detecta el país (zona horaria e idioma del navegador, sin cookies ni servicios externos)
 * y cambia los enlaces de Amazon.es a la Amazon de ese país.
 *
 * IMPORTANTE: Amazon solo paga comisión en cada tienda si tienes un código de afiliado de ESA tienda.
 * Cuando consigas un código nuevo, añádelo abajo en TAGS (una línea) y la web lo usará sola.
 * Si un país no tiene código, el enlace se queda en Amazon.es (donde sí cobras).
 */
(function () {
  var TAGS = {
    'amazon.es': 'trendpulsesho-21'
    // 'amazon.com':    'TU-CODIGO-20',   // EE. UU. y Latinoamérica
    // 'amazon.co.uk':  'TU-CODIGO-21',   // Reino Unido e Irlanda
    // 'amazon.de':     'TU-CODIGO-21',   // Alemania, Austria, Suiza
    // 'amazon.fr':     'TU-CODIGO-21',
    // 'amazon.it':     'TU-CODIGO-21',
    // 'amazon.pl':     'TU-CODIGO-21',
    // 'amazon.nl':     'TU-CODIGO-21',
    // 'amazon.se':     'TU-CODIGO-21',
    // 'amazon.com.be': 'TU-CODIGO-21',
    // 'amazon.ca':     'TU-CODIGO-20',
    // 'amazon.com.mx': 'TU-CODIGO-20',
    // 'amazon.com.br': 'TU-CODIGO-20',
  };

  var C = {
    es: ['España', 'amazon.es'], pt: ['Portugal', 'amazon.es'], ad: ['Andorra', 'amazon.es'],
    de: ['Alemania', 'amazon.de'], at: ['Austria', 'amazon.de'], ch: ['Suiza', 'amazon.de'],
    fr: ['Francia', 'amazon.fr'], lu: ['Luxemburgo', 'amazon.fr'], it: ['Italia', 'amazon.it'],
    gb: ['Reino Unido', 'amazon.co.uk'], ie: ['Irlanda', 'amazon.co.uk'], nl: ['Países Bajos', 'amazon.nl'],
    be: ['Bélgica', 'amazon.com.be'], se: ['Suecia', 'amazon.se'], pl: ['Polonia', 'amazon.pl'],
    us: ['Estados Unidos', 'amazon.com'], ca: ['Canadá', 'amazon.ca'], mx: ['México', 'amazon.com.mx'],
    br: ['Brasil', 'amazon.com.br'], co: ['Colombia', 'amazon.com'], ar: ['Argentina', 'amazon.com'],
    cl: ['Chile', 'amazon.com'], pe: ['Perú', 'amazon.com'], ec: ['Ecuador', 'amazon.com'],
    ve: ['Venezuela', 'amazon.com'], uy: ['Uruguay', 'amazon.com'], py: ['Paraguay', 'amazon.com'],
    bo: ['Bolivia', 'amazon.com'], cr: ['Costa Rica', 'amazon.com'], pa: ['Panamá', 'amazon.com'],
    do: ['Rep. Dominicana', 'amazon.com'], gt: ['Guatemala', 'amazon.com'], jp: ['Japón', 'amazon.co.jp'],
    au: ['Australia', 'amazon.com.au'], in: ['India', 'amazon.in'], ae: ['Emiratos Árabes', 'amazon.ae'],
    sa: ['Arabia Saudí', 'amazon.sa'], tr: ['Turquía', 'amazon.com.tr'], sg: ['Singapur', 'amazon.sg'],
    eg: ['Egipto', 'amazon.eg']
  };

  var TZ = {
    'Europe/Madrid': 'es', 'Atlantic/Canary': 'es', 'Africa/Ceuta': 'es', 'Europe/Lisbon': 'pt', 'Atlantic/Madeira': 'pt',
    'Atlantic/Azores': 'pt', 'Europe/Andorra': 'ad', 'Europe/Berlin': 'de', 'Europe/Vienna': 'at', 'Europe/Zurich': 'ch',
    'Europe/Paris': 'fr', 'Europe/Luxembourg': 'lu', 'Europe/Rome': 'it', 'Europe/London': 'gb', 'Europe/Dublin': 'ie',
    'Europe/Amsterdam': 'nl', 'Europe/Brussels': 'be', 'Europe/Stockholm': 'se', 'Europe/Warsaw': 'pl',
    'America/Toronto': 'ca', 'America/Vancouver': 'ca', 'America/Edmonton': 'ca', 'America/Winnipeg': 'ca',
    'America/Halifax': 'ca', 'America/Mexico_City': 'mx', 'America/Monterrey': 'mx', 'America/Tijuana': 'mx',
    'America/Cancun': 'mx', 'America/Sao_Paulo': 'br', 'America/Bogota': 'co', 'America/Argentina/Buenos_Aires': 'ar',
    'America/Santiago': 'cl', 'America/Lima': 'pe', 'America/Guayaquil': 'ec', 'America/Caracas': 've',
    'America/Montevideo': 'uy', 'America/Asuncion': 'py', 'America/La_Paz': 'bo', 'America/Costa_Rica': 'cr',
    'America/Panama': 'pa', 'America/Santo_Domingo': 'do', 'America/Guatemala': 'gt', 'Asia/Tokyo': 'jp',
    'Asia/Kolkata': 'in', 'Asia/Calcutta': 'in', 'Asia/Dubai': 'ae', 'Asia/Riyadh': 'sa', 'Europe/Istanbul': 'tr',
    'Asia/Singapore': 'sg', 'Africa/Cairo': 'eg'
  };

  function safeGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function safeSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

  function detect() {
    var q = (location.search.match(/[?&]pais=([a-z]{2})/i) || [])[1];
    if (q && C[q.toLowerCase()]) { safeSet('tp-pais', q.toLowerCase()); return q.toLowerCase(); }
    var saved = safeGet('tp-pais');
    if (saved && C[saved]) return saved;
    var tz = '';
    try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) {}
    if (TZ[tz]) return TZ[tz];
    if (/^America\//.test(tz)) return 'us';
    if (/^Australia\//.test(tz)) return 'au';
    var langs = navigator.languages || [navigator.language || ''];
    for (var i = 0; i < langs.length; i++) {
      var m = /-([A-Za-z]{2})$/.exec(langs[i] || '');
      if (m && C[m[1].toLowerCase()]) return m[1].toLowerCase();
    }
    return 'es';
  }

  var country = detect();
  var wanted = C[country] ? C[country][1] : 'amazon.es';
  var store = TAGS[wanted] ? wanted : 'amazon.es';
  var en = !/^es/i.test(navigator.language || 'es');

  function fix(a) {
    if (!a || !a.href || a.href.indexOf('amazon.es') === -1) return;
    var u;
    try { u = new URL(a.href); } catch (e) { return; }
    if (!/(^|\.)amazon\.es$/.test(u.hostname) && !/(^|\.)amazon\./.test(u.hostname)) return;
    u.hostname = 'www.' + store;
    u.searchParams.set('tag', TAGS[store]);
    if (a.href !== u.toString()) a.href = u.toString();
  }
  function fixAll(root) {
    if (store === 'amazon.es') return;
    var list = (root || document).querySelectorAll('a[href*="amazon.es"]');
    for (var i = 0; i < list.length; i++) fix(list[i]);
  }

  // Cambia el enlace justo al hacer clic (sirve también para productos que se cargan después)
  ['click', 'auxclick', 'touchstart'].forEach(function (ev) {
    document.addEventListener(ev, function (e) {
      if (store === 'amazon.es') return;
      var a = e.target && e.target.closest ? e.target.closest('a[href*="amazon.es"]') : null;
      if (a) fix(a);
    }, true);
  });

  function banner() {
    if (country === 'es' || safeGet('tp-banner-off') === country) return;
    var name = C[country] ? C[country][0] : '';
    var local = store !== 'amazon.es';
    var msg = local
      ? (en ? '🌍 We send you to <b>' + store + '</b>, the Amazon store of your country. Prices on this site are approximate euro prices from Amazon.es; you will see the real price on Amazon.'
            : '🌍 Te llevamos a <b>' + store + '</b>, la Amazon de ' + name + '. Los precios de esta web son aproximados de Amazon.es en euros: el precio real lo verás en Amazon.')
      : (en ? '🌍 You are visiting from ' + name + '. Links go to <b>Amazon.es</b> (Spain), which ships many products abroad: check on Amazon whether it delivers to you.'
            : '🌍 Nos visitas desde ' + name + '. Los enlaces van a <b>Amazon.es</b> (España), que envía muchos productos al extranjero: comprueba en Amazon si llega a tu país.');
    var opts = Object.keys(C).sort(function (a, b) { return C[a][0].localeCompare(C[b][0], 'es'); })
      .map(function (k) { return '<option value="' + k + '"' + (k === country ? ' selected' : '') + '>' + C[k][0] + '</option>'; }).join('');
    var d = document.createElement('div');
    d.id = 'tp-geo';
    d.setAttribute('role', 'region');
    d.setAttribute('aria-label', en ? 'Your country' : 'Tu país');
    d.innerHTML = '<style>#tp-geo{background:#232F3E;color:#fff;font:14px/1.45 Arial,Helvetica,sans-serif;padding:10px 16px;display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;justify-content:center}#tp-geo b{color:#FFD814}#tp-geo select{font:inherit;padding:3px 6px;border-radius:6px;border:0;color:#0F1111;background:#fff}#tp-geo button{background:none;border:0;color:#ccc;font-size:20px;line-height:1;cursor:pointer;padding:0 4px}</style>'
      + '<span>' + msg + '</span><label>' + (en ? 'Country: ' : 'País: ') + '<select>' + opts + '</select></label>'
      + '<button type="button" aria-label="' + (en ? 'Close' : 'Cerrar') + '">×</button>';
    document.body.insertBefore(d, document.body.firstChild);
    d.querySelector('select').addEventListener('change', function () { safeSet('tp-pais', this.value); location.reload(); });
    d.querySelector('button').addEventListener('click', function () { safeSet('tp-banner-off', country); d.remove(); });
  }

  function start() {
    fixAll();
    banner();
    if (store !== 'amazon.es' && 'MutationObserver' in window) {
      new MutationObserver(function (ms) {
        ms.forEach(function (m) { m.addedNodes.forEach(function (n) { if (n.nodeType === 1) { if (n.matches && n.matches('a[href*="amazon.es"]')) fix(n); else fixAll(n); } }); });
      }).observe(document.body, { childList: true, subtree: true });
    }
    document.documentElement.setAttribute('data-tp-pais', country);
    document.documentElement.setAttribute('data-tp-tienda', store);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();

  window.TrendPulseGeo = { pais: country, tienda: store };
})();
