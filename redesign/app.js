'use strict';
const technology=['Informática','Electrónica','Dispositivos Amazon','Videojuegos','Móviles y accesorios','Auriculares y audio portátil','Audio y Hi-Fi','TV y home cinema','Fotografía y vídeo','Pilas y cargadores','Portátiles','Tablets','Monitores','Componentes de PC','Almacenamiento','Redes y wifi','Impresoras','Accesorios de informática','Ordenadores de sobremesa','Reacondicionados','Software'];
const $=selector=>document.querySelector(selector);
const scriptURL=new URL(document.currentScript?.src||'/redesign/app.js',location.href);
const siteBase=new URL('../',scriptURL);
// The same source runs at the Netlify domain root and GitHub Pages project path.
for(const anchor of document.querySelectorAll('a[href]')){
 const href=anchor.getAttribute('href');
 if(['/guias','/buscador-regalos','/privacidad'].includes(href)) anchor.href=new URL(href.slice(1)+'.html',siteBase).href;
}
const normalize=text=>String(text).toLocaleLowerCase('es').normalize('NFD').replace(/[\u0300-\u036f]/g,'');
const state={products:[],category:'Todas',query:'',shown:24,sort:'recommended',savedOnly:false};
let saved=new Set();
try { const stored=JSON.parse(localStorage.getItem('trendpulseshop-saved')||'[]'); if(Array.isArray(stored)) saved=new Set(stored.filter(x=>typeof x==='string')); } catch {}
function updateSaved(){ $('#saved-count').textContent=saved.size; try{localStorage.setItem('trendpulseshop-saved',JSON.stringify([...saved]));}catch{} }
function imageURL(value){
  try { const url=new URL(value); return url.protocol==='https:'&&(['m.media-amazon.com','images-eu.ssl-images-amazon.com','images-na.ssl-images-amazon.com'].includes(url.hostname))?url.href:null; }catch{return null;}
}
function selectCategory(category){state.category=category;state.shown=24;$('#category').value=category;render();}
function matching(){
 const query=normalize(state.query);
 const products=state.products.filter(p=>(!state.savedOnly||saved.has(p.asin))&&(state.category==='Todas'||(state.category==='Tecnología'?technology.includes(p.category):p.category===state.category))&&(!query||normalize(p.title+' '+p.category).includes(query)));
 if(state.sort==='title') products.sort((a,b)=>a.title.localeCompare(b.title,'es'));
 return products;
}

/* Ilustraciones propias por categoría (sin fotos de Amazon ni de terceros) */
const ART_ICONS={
 audio:'<path d="M14 34v-6a18 18 0 0 1 36 0v6" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round"/><rect x="10" y="32" width="10" height="18" rx="5" fill="#fff"/><rect x="44" y="32" width="10" height="18" rx="5" fill="#fff"/>',
 pc:'<rect x="12" y="14" width="40" height="27" rx="3" fill="none" stroke="#fff" stroke-width="4"/><path d="M6 48h52l-5 5H11z" fill="#fff"/>',
 phone:'<rect x="21" y="8" width="22" height="48" rx="5" fill="none" stroke="#fff" stroke-width="4"/><circle cx="32" cy="48" r="2.5" fill="#fff"/>',
 tv:'<rect x="8" y="14" width="48" height="31" rx="3" fill="none" stroke="#fff" stroke-width="4"/><path d="M22 54h20M32 45v9" stroke="#fff" stroke-width="4" stroke-linecap="round"/>',
 home:'<path d="M8 30 32 10l24 20" fill="none" stroke="#fff" stroke-width="4.5" stroke-linejoin="round" stroke-linecap="round"/><path d="M15 28v26h34V28" fill="none" stroke="#fff" stroke-width="4.5" stroke-linejoin="round"/><rect x="27" y="38" width="10" height="16" fill="#fff"/>',
 bulb:'<path d="M32 8a16 16 0 0 0-9 29c2 2 3 4 3 7h12c0-3 1-5 3-7A16 16 0 0 0 32 8z" fill="none" stroke="#fff" stroke-width="4"/><path d="M26 50h12M28 56h8" stroke="#fff" stroke-width="4" stroke-linecap="round"/>',
 game:'<rect x="6" y="20" width="52" height="26" rx="13" fill="none" stroke="#fff" stroke-width="4"/><path d="M19 28v10M14 33h10" stroke="#fff" stroke-width="4" stroke-linecap="round"/><circle cx="43" cy="30" r="3" fill="#fff"/><circle cx="49" cy="36" r="3" fill="#fff"/>',
 car:'<path d="M8 38l5-14h38l5 14v10H8z" fill="none" stroke="#fff" stroke-width="4" stroke-linejoin="round"/><circle cx="19" cy="48" r="5" fill="#fff"/><circle cx="45" cy="48" r="5" fill="#fff"/>',
 ball:'<circle cx="32" cy="32" r="22" fill="none" stroke="#fff" stroke-width="4"/><path d="M32 10v44M10 32h44M16 16c8 8 8 24 0 32M48 16c-8 8-8 24 0 32" fill="none" stroke="#fff" stroke-width="3"/>',
 book:'<path d="M8 14h20a4 4 0 0 1 4 4v34a4 4 0 0 0-4-4H8zM56 14H36a4 4 0 0 0-4 4v34a4 4 0 0 1 4-4h20z" fill="none" stroke="#fff" stroke-width="4" stroke-linejoin="round"/>',
 heart:'<path d="M32 54C10 38 8 24 16 17c6-5 13-3 16 3 3-6 10-8 16-3 8 7 6 21-16 37z" fill="none" stroke="#fff" stroke-width="4.5" stroke-linejoin="round"/>',
 paw:'<ellipse cx="32" cy="42" rx="12" ry="10" fill="#fff"/><circle cx="16" cy="28" r="5" fill="#fff"/><circle cx="26" cy="19" r="5" fill="#fff"/><circle cx="38" cy="19" r="5" fill="#fff"/><circle cx="48" cy="28" r="5" fill="#fff"/>',
 tool:'<path d="M14 50 40 24" stroke="#fff" stroke-width="7" stroke-linecap="round"/><path d="M38 10a12 12 0 0 0-8 15l9 9a12 12 0 0 0 15-8l-8 3-6-6 3-8z" fill="#fff"/>',
 bag:'<path d="M12 22h40l-3 32H15z" fill="none" stroke="#fff" stroke-width="4" stroke-linejoin="round"/><path d="M22 22v-4a10 10 0 0 1 20 0v4" fill="none" stroke="#fff" stroke-width="4"/>',
 note:'<path d="M24 46V14l26-6v32" fill="none" stroke="#fff" stroke-width="4" stroke-linejoin="round"/><circle cx="18" cy="46" r="7" fill="#fff"/><circle cx="44" cy="40" r="7" fill="#fff"/>',
 leaf:'<path d="M12 52C10 28 24 10 54 10c0 28-14 42-34 42" fill="none" stroke="#fff" stroke-width="4.5" stroke-linejoin="round"/><path d="M12 52 36 28" stroke="#fff" stroke-width="4" stroke-linecap="round"/>',
 cam:'<path d="M8 22h12l4-6h16l4 6h12v32H8z" fill="none" stroke="#fff" stroke-width="4" stroke-linejoin="round"/><circle cx="32" cy="37" r="9" fill="none" stroke="#fff" stroke-width="4"/>',
 box:'<path d="M8 20 32 8l24 12v26L32 58 8 46z" fill="none" stroke="#fff" stroke-width="4" stroke-linejoin="round"/><path d="M8 20l24 12 24-12M32 32v26" fill="none" stroke="#fff" stroke-width="4"/>'
};
const ART_MAP={'Alimentación':['leaf','#1f8a4c'],'Bebé':['heart','#e0709a'],'Belleza':['heart','#b94fa0'],'Bricolaje':['tool','#c2661a'],'Coche y moto':['car','#2d4a7a'],'Deporte':['ball','#d4552b'],'Dispositivos Amazon':['box','#1f6fb5'],'Electrónica':['phone','#003cff'],'Electrodomésticos':['home','#2f7d86'],'Hogar y cocina':['home','#a86a3a'],'Iluminación':['bulb','#d49a1a'],'Informática':['pc','#4a4fd4'],'Instrumentos musicales':['note','#7a3fb5'],'Jardín':['leaf','#3f8f2f'],'Juguetes':['game','#e0562b'],'Moda':['bag','#c23a6a'],'Oficina':['pc','#4f6b8a'],'Mascotas':['paw','#a5682d'],'Salud':['heart','#1f9a8a'],'Videojuegos':['game','#5b3fd4'],'Libros':['book','#8a4f2f'],'Móviles y accesorios':['phone','#1f5fd4'],'Auriculares y audio portátil':['audio','#003cff'],'Audio y Hi-Fi':['audio','#5a3fb5'],'TV y home cinema':['tv','#1f3a8a'],'Fotografía y vídeo':['cam','#3a3f4a'],'Electrónica para coche':['car','#3a5a7a'],'Pilas y cargadores':['bulb','#c27a1a'],'Portátiles':['pc','#003cff'],'Tablets':['phone','#2f6fd4'],'Monitores':['tv','#2a4fb5'],'Componentes de PC':['pc','#5a5fd4'],'Almacenamiento':['box','#4a6a8a'],'Redes y wifi':['bulb','#1f7ab5'],'Impresoras':['box','#6a6f7a'],'Accesorios de informática':['pc','#3f6fa5'],'Ordenadores de sobremesa':['pc','#3a3fb5'],'Reacondicionados':['box','#2f8a5a'],'Software':['pc','#5a4fd4'],'Grandes electrodomésticos':['home','#2a7a8a'],'Industria y ciencia':['tool','#5a6a7a'],'Películas y series':['tv','#8a2f4a'],'CD y vinilos':['note','#4a3f6a'],'Handmade':['heart','#b5683a'],'eBooks Kindle':['book','#1f6fb5']};
function categoryArt(category){
 const m=ART_MAP[category]||['box','#003cff'];
 const svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-hidden="true"><rect width="64" height="64" rx="12" fill="'+m[1]+'"/>'+ART_ICONS[m[0]]+'</svg>';
 return 'data:image/svg+xml;utf8,'+encodeURIComponent(svg);
}
function makeCard(product){
 const card=document.createElement('article');card.className='card';
 const href='https://www.amazon.es/dp/'+encodeURIComponent(product.asin)+'?tag=trendpulsesho-21';
 const picture=document.createElement('a');picture.className='picture';picture.href=href;picture.target='_blank';picture.rel='sponsored noopener';picture.setAttribute('aria-label','Ver fotos de '+product.title+' en Amazon');
 const fallback=document.createElement('span');fallback.className='photo-placeholder';
 const icon=document.createElement('img');icon.src=categoryArt(product.category);icon.alt='';icon.width=96;icon.height=96;icon.className='cat-art';icon.setAttribute('aria-hidden','true');const note=document.createElement('span');note.textContent='Ver foto real en Amazon →';fallback.append(icon,note);picture.append(fallback);
 const src=imageURL(product.img);
 if(src){ const img=document.createElement('img');img.src=src;img.alt=product.title;img.loading='lazy';img.width=400;img.height=300;img.addEventListener('load',()=>{fallback.hidden=true;});img.addEventListener('error',()=>{img.remove();fallback.hidden=false;});picture.append(img); }
 const favorite=document.createElement('button');favorite.className='favorite';favorite.textContent=saved.has(product.asin)?'♥':'♡';favorite.setAttribute('aria-pressed',String(saved.has(product.asin)));favorite.setAttribute('aria-label','Guardar '+product.title);favorite.addEventListener('click',()=>{saved.has(product.asin)?saved.delete(product.asin):saved.add(product.asin);updateSaved();render();});
 const visual=document.createElement('div');visual.className='visual';visual.append(picture,favorite);
 const body=document.createElement('div');body.className='card-body';const category=document.createElement('span');category.className='cat';category.textContent=product.category;
 const heading=document.createElement('h3');heading.textContent=product.title;
 const detail=document.createElement('p');detail.className='product-detail';detail.textContent='Precio y disponibilidad en Amazon';
 const link=document.createElement('a');link.className='product-link';link.href=href;link.target='_blank';link.rel='sponsored noopener';link.textContent='Ver en Amazon →';link.setAttribute('aria-label','Ver '+product.title+' en Amazon (se abre en otra pestaña)');
 body.append(category,heading,detail,link);card.append(visual,body);return card;
}
function render(){
 const list=matching();$('#grid').replaceChildren();$('#status').textContent=`${list.length.toLocaleString('es-ES')} productos${state.savedOnly?' guardados':''}${state.query?' para «'+state.query+'»':''}`;
 $('#more').hidden=list.length<=state.shown;$('#clear').hidden=state.category==='Todas'&&!state.query&&!state.savedOnly;
 document.querySelectorAll('[data-filter]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.filter===state.category)));
 $('#saved-toggle').setAttribute('aria-pressed',String(state.savedOnly));
 if(!list.length){const message=document.createElement('p');message.className='empty';message.textContent=state.savedOnly?'Todavía no hay productos guardados que coincidan. Pulsa el corazón de un producto para guardarlo.':'No encontramos productos con esos filtros. Prueba con otra palabra o categoría.';$('#grid').append(message);return;}
 const fragment=document.createDocumentFragment();list.slice(0,state.shown).forEach(product=>fragment.append(makeCard(product)));$('#grid').append(fragment);
}
$('#q').addEventListener('input',event=>{state.query=event.target.value.trim();state.shown=24;render();});
$('#search').addEventListener('submit',event=>{event.preventDefault();$('#catalogo').scrollIntoView({behavior:'smooth'});});
$('#category').addEventListener('change',event=>selectCategory(event.target.value));
$('#sort').addEventListener('change',event=>{state.sort=event.target.value;state.shown=24;render();});
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>selectCategory(button.dataset.filter)));
document.querySelectorAll('[data-category],[data-group]').forEach(link=>link.addEventListener('click',()=>selectCategory(link.dataset.category||link.dataset.group)));
$('#more').addEventListener('click',()=>{const previous=state.shown;state.shown+=24;render();$('#grid').children[previous]?.querySelector('.product-link')?.focus({preventScroll:true});});
$('#clear').addEventListener('click',()=>{state.query='';state.savedOnly=false;$('#q').value='';selectCategory('Todas');});
$('#saved-toggle').addEventListener('click',event=>{event.preventDefault();state.savedOnly=!state.savedOnly;state.shown=24;render();$('#catalogo').scrollIntoView({behavior:'smooth'});});
function theme(dark){document.documentElement.dataset.theme=dark?'dark':'light';$('#theme').setAttribute('aria-pressed',String(dark));$('#theme').setAttribute('aria-label',dark?'Activar modo claro':'Activar modo oscuro');}
try{theme(localStorage.getItem('trendpulse-clone-theme')==='dark');}catch{theme(false);}
$('#theme').addEventListener('click',()=>{const dark=document.documentElement.dataset.theme!=='dark';theme(dark);try{localStorage.setItem('trendpulse-clone-theme',dark?'dark':'light');}catch{}});
updateSaved();
const started=Date.now();
const officialDate=Date.parse(window.API_UPDATED_AT||'');
const fresh=Number.isFinite(officialDate)&&started>=officialDate&&started-officialDate<24*60*60*1000;
const official=Array.isArray(window.API_PRODUCTS)&&fresh?window.API_PRODUCTS.filter(p=>/^[A-Z0-9]{10}$/.test(p.asin)&&p.title&&imageURL(p.img)).map(p=>({...p,category:p.cat||p.category})):[];
fetch(new URL('catalog.json',scriptURL)).then(response=>{if(!response.ok)throw Error('catalog');return response.json();}).then(data=>{
 const byASIN=new Map();official.forEach(product=>byASIN.set(product.asin,product));
 data.products.forEach(product=>{if(!byASIN.has(product.asin))byASIN.set(product.asin,product);});
 state.products=[...byASIN.values()];$('#updated').textContent=data.updated;
 $('#feed-status').textContent=official.length?`${official.length} productos con foto oficial de Amazon. Imágenes actualizadas: ${new Date(officialDate).toLocaleString('es-ES')}.`:'Consulta las fotos reales en la ficha de Amazon de cada producto.';
 const group=document.createElement('option');group.value='Tecnología';group.textContent='Tecnología (todas)';$('#category').append(group);
 [...new Set(state.products.map(p=>p.category))].sort((a,b)=>a.localeCompare(b,'es')).forEach(category=>{const option=document.createElement('option');option.value=category;option.textContent=category;$('#category').append(option);});$('#category').value=state.category;render();
 // Never keep displaying cached API image URLs beyond their 24-hour lifetime.
 if(official.length)setTimeout(()=>{state.products=state.products.map(p=>({...p,img:null}));$('#feed-status').textContent='Consulta las fotos actuales en Amazon.';render();},Math.max(0,24*60*60*1000-(Date.now()-officialDate)));
}).catch(()=>{$('#status').textContent='No se ha podido cargar el catálogo. Recarga la página para intentarlo de nuevo.';});
