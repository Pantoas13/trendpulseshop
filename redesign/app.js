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
try { const stored=JSON.parse(localStorage.getItem('comprafaro-saved')||'[]'); if(Array.isArray(stored)) saved=new Set(stored.filter(x=>typeof x==='string')); } catch {}
function updateSaved(){ $('#saved-count').textContent=saved.size; try{localStorage.setItem('comprafaro-saved',JSON.stringify([...saved]));}catch{} }
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
function makeCard(product){
 const card=document.createElement('article');card.className='card';
 const href='https://www.amazon.es/dp/'+encodeURIComponent(product.asin)+'?tag=trendpulsesho-21';
 const picture=document.createElement('a');picture.className='picture';picture.href=href;picture.target='_blank';picture.rel='sponsored noopener';picture.setAttribute('aria-label','Ver fotos de '+product.title+' en Amazon');
 const fallback=document.createElement('span');fallback.className='photo-placeholder';
 const icon=document.createElement('span');icon.textContent='▧';icon.setAttribute('aria-hidden','true');const note=document.createElement('span');note.textContent='Ver foto en Amazon →';fallback.append(icon,note);picture.append(fallback);
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
