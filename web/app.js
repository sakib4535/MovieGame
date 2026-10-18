'use strict';
const $ = (s) => document.querySelector(s);
const main = $('#main');
const locale = window.MovieLocale;
const n = value => locale.number(value);
const t = value => locale.t(value);
const downloadUrl = url => {const link=new URL(url,location.origin);link.searchParams.set('download','1');return link.pathname+link.search;};
const esc = (s) => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const labels = {all:'All cinema', hollywood:'Hollywood', bangladeshi:'Bangladeshi', anime:'Japanese anime'};
const fresh = (mode='story') => ({edition:2, mode, seed:crypto.randomUUID(), answers:{}, step:0, category:'all', key:null, result:null, displayName:'', share:null});
let state = fresh(), survey = null, busy = false, routeId = 0;
let library = {q:'', category:'all', page:1}, searchTimer;
try { const saved = JSON.parse(sessionStorage.getItem('moviegame') || 'null'); if (saved?.answers && Number.isInteger(saved.step) && saved.step >= 0 && saved.step < 15) state = saved.edition===2 || saved.result ? {...fresh(saved.mode || 'story'), ...saved} : fresh(); } catch {}
delete state.localizedResult;
function save() { try { const {localizedResult,...saved}=state; sessionStorage.setItem('moviegame', JSON.stringify(saved)); } catch {} }
function notify(text) { $('#toast').textContent = t(text); clearTimeout(notify.timer); notify.timer = setTimeout(() => $('#toast').textContent = '', 4000); }
function go(route) { if (location.hash === route) render(); else location.hash = route; }
function focusMain() { main.focus({preventScroll:true}); window.scrollTo({top:0, behavior:'instant'}); }
async function request(url, options={}) {
  const response = await fetch(url, {...options, signal: options.signal || AbortSignal.timeout(12000)});
  const data = await response.json();
  if (!response.ok) {
    const error = new Error(typeof data.detail === 'string' ? data.detail : 'That request could not be completed. Please try again.');
    error.status = response.status; error.retry = Number(response.headers.get('Retry-After') || 2); throw error;
  }
  return data;
}
async function getSurvey() {
  const mode=state.mode, seed=state.seed, language=locale.lang;
  if (!survey || survey.mode!==mode || survey.seed!==seed || survey.language!==language) {
    const next=await locale.localizeSurvey(await request(`/api/v1/survey?mode=${mode}&seed=${encodeURIComponent(seed)}&lang=${language}`),language);
    if(state.mode!==mode || state.seed!==seed || locale.lang!==language) return getSurvey();
    if(state.surveyVersion && (state.surveyVersion!==next.version || state.catalogVersion!==next.catalog_version) && !state.result) {
      state.answers={}; state.step=0; state.key=null; notify('A new edition is here. Start a fresh story.');
    }
    survey=next;
  }
  state.surveyVersion=survey.version; state.catalogVersion=survey.catalog_version; save();
  return survey;
}
const filmImage = movie => {
  const fallback=`/api/v1/posters/${encodeURIComponent(movie.id)}.svg?lang=${locale.lang}`;
  const src=movie.image?.kind==='illustrated-cover'?fallback:movie.image?.url || fallback;
  return `<figure class="movie-artwork"><img src="${esc(src)}" data-fallback="${esc(fallback)}" alt="${esc(movie.title)} — ${movie.image?.kind==='reference-artwork'?'reference artwork':'original MovieGame cover'}" loading="lazy" decoding="async" referrerpolicy="no-referrer" width="360" height="510"><figcaption>${movie.image?.kind==='reference-artwork'?`<a href="${esc(movie.image.file_page || movie.image.source_url)}" target="_blank" rel="noopener noreferrer">Artwork source ↗</a>`:'Original MovieGame cover art'}</figcaption></figure>`;
};
const pills = (active, attr) => Object.entries(labels).map(([key,label]) => `<button class="pill ${active===key?'active':''}" ${attr}="${key}" aria-pressed="${active===key}">${label}</button>`).join('');
const tags = (items) => `<div class="tags">${items.map(t=>`<span class="tag">${esc(t)}</span>`).join('')}</div>`;
const art = '<div class="art art-orbit" aria-hidden="true"><span>✧</span></div>';

function home() {
  const total = survey?.movie_count || 1126;
  main.innerHTML = `<section class="hero"><div><span class="eyebrow"><i></i> YOUR NEXT PLOT TWIST IS YOU</span><h1>You have<br>main character<br><em>energy.</em></h1><p class="intro">Somewhere in the movies, there’s a character who sees the world a little like you. Let’s find them.</p><button class="button" data-start>Meet my character <span>↗</span></button><div class="hero-meta"><div class="avatars" aria-hidden="true"><span>✳</span><span>✧</span><span>✷</span></div><span>15 questions</span><span>·</span><span>About 3 minutes</span><span>·</span><span>100% you</span></div></div><div class="stage" aria-label="Original illustrated cards representing dreamers, explorers, and everyday heroes"><span class="spark" aria-hidden="true">✳</span><span class="spark small" aria-hidden="true">✧</span><div class="poster poster-left"><span class="poster-top">THE INNER UNIVERSE</span><div class="art art-sun"></div><div><h3>THE<br>DREAMER</h3><div class="poster-foot"><span>IMAGINE MORE</span><span>01</span></div></div></div><div class="poster poster-right"><span class="poster-top">A WORLD OF POSSIBILITIES</span><div class="art art-mountain"></div><div><h3>THE<br>EXPLORER</h3><div class="poster-foot"><span>GO A LITTLE FURTHER</span><span>03</span></div></div></div><div class="poster poster-center"><span class="poster-top">SOME STORIES FIND YOU</span>${art}<div><h3>THE<br>EVERYDAY<br>HERO</h3><div class="poster-foot"><span>IT COULD BE YOU</span><span>02</span></div></div></div><span class="stage-label"><span>✦</span> EVERY CHARACTER HAS A LITTLE OF US.</span></div></section><div class="ticker" aria-label="Game features"><span><b>✦</b> ${total} FILMS. ENDLESS POSSIBILITIES.</span><span><b>✦</b> HOLLYWOOD TO DHAKA</span><span><b>✦</b> A LITTLE ANIME MAGIC</span><span><b>✦</b> YOUR STORY STARTS HERE</span></div><section class="section"><div class="section-head"><div><span class="eyebrow">ONE QUIZ. DIFFERENT WORLDS.</span><h2>Where do you belong?</h2></div><p>Big-screen legends, stories close to home, and worlds beyond imagination.</p></div><div class="worlds"><button class="world-card" data-world="hollywood"><small>01 / THE BIG SCREEN</small><span class="symbol">✳</span><h3>Hollywood</h3><p>For the bold, the brilliant, and the beautifully human. ↗</p></button><button class="world-card" data-world="bangladeshi"><small>02 / STORIES CLOSE TO HOME</small><span class="symbol">আ</span><h3>Bangladeshi cinema</h3><p>Familiar streets. Unforgettable hearts. ↗</p></button><button class="world-card" data-world="anime"><small>03 / BEYOND THE ORDINARY</small><span class="symbol">✧</span><h3>Japanese anime</h3><p>A little wonder. A whole lot of possibility. ↗</p></button></div><div class="character-game-section"><div><span class="eyebrow">A DIFFERENT WAY TO FIND YOURSELF</span><h2>Character Game.</h2><p class="quiet">A separate survey about your instincts, decisions, and relationships. Discover your character across every movie in the library.</p></div><button class="button" data-character-start>Play Character Game <span>↗</span></button></div><div class="how"><p>A few choices.<br>A familiar kind of magic.</p><div class="steps"><div><b>01</b><h3>Follow your instinct</h3><p>15 varied everyday moments. Different ways to respond. No right answers.</p></div><div><b>02</b><h3>Meet your match</h3><p>Find the character whose story energy feels closest to yours.</p></div><div><b>03</b><h3>See the connection</h3><p>Five reasons, drawn from your choices. Then share your reveal.</p></div></div></div></section>`;
}

function quiz() {
  const question = survey.questions[state.step];
  const selected = state.answers[question.id];
  main.innerHTML = `<section class="quiz-shell"><div class="quiz-top"><button class="text-button" data-home>← Back to the lobby</button><span>SCENE ${String(state.step+1).padStart(2,'0')} / 15</span></div><div class="progress-track" role="progressbar" aria-label="Quiz progress" aria-valuemin="0" aria-valuemax="15" aria-valuenow="${Object.keys(state.answers).length}"><span style="width:${(state.step+1)/15*100}%"></span></div><span class="eyebrow">${state.mode==='character'?'CHARACTER GAME · ':''}${state.step<5?'THE OPENING CHAPTER':state.step<10?'THE PLOT THICKENS':'YOUR FINAL ACT'}</span><h1 id="question-title">${esc(question.text)}</h1><p class="quiet">Choose what feels most like you. Every listed answer belongs here.</p>${state.step===0 && state.mode==='story'?`<div class="category-pills" aria-label="Choose your cinema">${pills(state.category,'data-quiz-category')}</div>`:''}<fieldset class="options" aria-labelledby="question-title">${question.options.map((o,i)=>`<label class="option"><input type="radio" name="answer" value="${o.id}" ${selected===o.id?'checked':''} ${busy?'disabled':''}><span>${esc(o.text)}</span><span class="letter" aria-hidden="true">${locale.lang==='bn'?'কখগঘঙচছজঝঞ'[i]:String.fromCharCode(65+i)}</span></label>`).join('')}</fieldset><div class="quiz-actions"><button class="text-button" id="back-question" ${state.step===0||busy?'disabled':''}>← Previous scene</button><button class="button" id="next-question" ${selected===undefined||busy?'disabled':''}>${busy?'Finding your character…':state.step===14?'Reveal my character':'Next scene'} <span>↗</span></button></div><div id="quiz-error" class="error" role="alert"></div><p class="quiet">${labels[state.category]} · Progress is saved in this tab. ${state.step>0?'<button class="text-button" data-restart>Start over</button>':''}</p></section>`;
}

async function submit() {
  if (busy) return;
  busy = true; state.key ||= crypto.randomUUID(); save(); quiz();
  const submissionKey = state.key;
  const payload = {survey_version:state.surveyVersion, catalog_version:state.catalogVersion, category:state.category, mode:state.mode, seed:state.seed, answers:{...state.answers}};
  try {
    let result;
    for (let attempt=0;attempt<3;attempt++) {
      try {
        result = await request('/api/v1/matches', {method:'POST', headers:{'Content-Type':'application/json','Idempotency-Key':submissionKey}, body:JSON.stringify(payload)});
        break;
      } catch(error) {
        if (attempt===2 || (error.status && error.status!==503 && error.status!==502 && error.status!==504)) throw error;
        await new Promise(resolve => setTimeout(resolve, Math.min(error.retry || 2, 5)*1000 + Math.random()*500));
      }
    }
    state.result = result; state.localizedResult=null; state.share=null; save(); busy=false; go('#result');
  } catch(error) {
    busy=false;
    if (location.hash==='#quiz' || location.hash==='#character') {quiz(); $('#quiz-error').textContent=error.status?error.message:'Connection interrupted. Your answers are safe in this tab. Try the reveal again.';}
    else notify('Your result could not be saved. Return to the quiz to retry.');
  }
}

function profileOwner(escaped=true) {
  const owner=state.displayName || '';
  const label=locale.lang==='bn' ? (owner?owner+' — বৈশিষ্ট্যের প্রোফাইল':'আপনার বৈশিষ্ট্যের প্রোফাইল') : (owner?owner+'’s trait profile':'Your trait profile');
  return escaped?esc(label):label;
}

function resultView() {
  const result = locale.lang==='bn' ? state.localizedResult : state.result;
  if (!result?.matches?.length) return;
  const best = result.matches[0], c = best.character, movie=best.movie;
  main.innerHTML = `<section class="result-header"><span class="eyebrow">THE REVEAL</span><h1>${locale.lang==='bn'?`আপনার গল্পে <em>${esc(c.name.split(' ')[0])}-এর ছোঁয়া।</em>`:`Your story has a little <em>${esc(c.name.split(' ')[0])}.</em>`}</h1><p class="quiet">Different worlds. A familiar way of being.</p></section><section class="result-layout"><div class="result-character"><article class="character-card"><div class="affinity"><span>YOUR STORY AFFINITY</span><strong>${best.affinity}%</strong></div>${filmImage(movie)}<span class="eyebrow">${esc(labels[movie.category])} / ${movie.year}</span><h2>${esc(c.name)}</h2><div class="movie-title">${esc(movie.title)}</div><p class="identity">${esc(c.identity)}<br>${esc(c.description)}</p>${tags(movie.themes)}<a class="reference" href="${esc(movie.source_url)}" target="_blank" rel="noopener noreferrer">Film reference ↗</a></article><p class="quiet">Affinity is a playful similarity score, not a scientific measure. ${movie.source_verified?'Source checked.':'Reference supplied; editorial verification pending.'}</p></div><section class="profile-card" aria-labelledby="profile-owner"><div class="profile-card-top"><div><span class="eyebrow">YOUR STORY AFFINITY</span><h3 id="profile-owner" class="profile-owner" data-i18n-skip>${profileOwner()}</h3></div><strong class="profile-affinity">${n(best.affinity)}%</strong></div><p class="profile-character" data-i18n-skip>${esc(c.name)}<small>${esc(movie.title)} (${n(movie.year)})</small></p><div class="trait-bars">${Object.entries(result.profile).map(([trait,value])=>`<div><div class="trait-label"><span>${t(trait)}</span><span>${n(value)}</span></div><div class="bar"><span style="width:${value}%"></span></div></div>`).join('')}</div><span class="profile-signature">moviegame ✦</span></section><div class="result-details"><span class="eyebrow">THE THINGS THAT CONNECT YOU</span><h2>Five reasons this feels like you.</h2>${result.close_match?'<p class="quiet">A few characters share your story energy. Explore the alternatives below as well.</p>':''}${best.reasons.map((r,i)=>`<article class="reason"><span class="number">0${i+1}</span><div><h3>${esc(r.trait)}</h3><blockquote>“${esc(r.answer)}”</blockquote><p>${esc(r.text)}</p></div></article>`).join('')}<section class="share-panel" aria-labelledby="share-heading"><h3 id="share-heading">Share your character & trait bars</h3><label class="quiet" for="share-name">Name on your shared result (optional)</label><input class="search-input" id="share-name" maxlength="48" value="${esc(state.displayName || '')}" placeholder="Your name or nickname" autocomplete="nickname"><p class="quiet">Sharing creates a public link with this name, your character, and the eight trait bars. Your full answers stay private.</p><div class="share-buttons"><button class="button small" data-share="facebook">Facebook ↗</button><button class="button secondary small" data-share="instagram">Instagram ↗</button><button class="button secondary small" data-share="copy">Copy Link</button></div><p id="share-status" class="quiet" role="status"></p><img id="share-preview" class="share-card-preview" ${state.share?'':'hidden'} ${state.share?`src="${esc(state.share.image_url)}"`:''} alt="Your named character result with eight trait bars" width="1200" height="630"><a id="download-card" class="reference" ${state.share?`href="${esc(downloadUrl(state.share.image_url))}"`:'hidden'} download="moviegame-result.png">Save result image</a></section><div class="result-actions"><button class="button secondary" data-restart>Play another story</button><a class="reference" href="#character">Try Character Game ↗</a></div><h2 style="margin-top:38px">Also in your universe</h2><div class="alternatives">${result.matches.slice(1).map(m=>`<article class="alternative">${esc(m.character.name)}<small>${esc(m.movie.title)} (${m.movie.year})</small><small>${m.affinity}% story affinity · ${esc(labels[m.movie.category])}</small></article>`).join('')}</div><p class="quiet">Curious about the cast? <a class="reference" href="#catalog">Explore the character library ↗</a></p></div></section>`;
}

async function libraryView(id) {
  main.innerHTML = `<section class="library"><span class="eyebrow">A WHOLE WORLD OF CHARACTERS</span><h1>The character library.</h1><p class="quiet">Discover the stories behind your match. Character identities are factual; themes and personality profiles are editorial interpretations.</p><div class="search-row"><label class="sr-only" for="search">Search films, characters, or themes</label><input class="search-input" id="search" type="search" placeholder="Search films, characters, or themes…" value="${esc(library.q)}" maxlength="100"></div><div class="category-pills">${pills(library.category,'data-filter')}</div><p id="catalog-count" class="quiet" role="status">Opening the library…</p><div class="catalog-grid" id="catalog-grid" aria-live="polite"></div><div class="pagination" id="pagination"></div></section>`;
  await loadLibrary(id);
}

let libraryRequest=0;
async function loadLibrary(id=routeId) {
  const requestId=++libraryRequest;
  try {
    const params=new URLSearchParams({...library, limit:12, lang:locale.lang});
    const data=await request(`/api/v1/catalog?${params}`);
    if (id!==routeId || requestId!==libraryRequest || !$('#catalog-grid')) return;
    $('#catalog-count').textContent=`${data.total} films in this collection`;
    $('#catalog-grid').innerHTML=data.items.length?data.items.map(m=>`<article class="film-card" data-category="${m.category}">${filmImage(m)}<span class="film-category">${esc(labels[m.category])} / ${m.year}</span><h2>${esc(m.title)}</h2><p>${esc(m.description)}</p>${m.characters.map(c=>`<p><span class="character-name">${esc(c.name)}</span> — ${esc(c.identity)}</p>`).join('')}${tags(m.themes)}<a class="reference" href="${esc(m.source_url)}" target="_blank" rel="noopener noreferrer">${m.source_verified?'Source checked':'Film reference'} ↗</a></article>`).join(''):'<p class="empty">No stories found. Try another title, character, or theme.</p>';
    const pages=Math.max(1,Math.ceil(data.total/12));
    $('#pagination').innerHTML=`<button class="button secondary small" data-page="${library.page-1}" ${library.page===1?'disabled':''}>← Previous</button><span>Page ${library.page} of ${pages}</span><button class="button secondary small" data-page="${library.page+1}" ${library.page>=pages?'disabled':''}>Next →</button>`;
  } catch(error) {if(id===routeId && requestId===libraryRequest && $('#catalog-count')) $('#catalog-count').textContent='The library could not load. Change a filter to retry.';}
}

async function render() {
  const id=++routeId;
  const route=location.hash || '#home';
  if (route==='#home') {home(); focusMain(); return;}
  if (route==='#catalog') {await libraryView(id); focusMain(); return;}
  if (route==='#character') {if(busy) return go('#quiz'); if(state.mode!=='character' || state.result) {state=fresh('character'); survey=null; save();}}
  if (route==='#result' && state.result) {
    if(locale.lang==='bn' && !state.localizedResult) {
      main.innerHTML='<div class="loading" role="status">Getting your story ready…</div>';
      try {
        const key=state.key;
        const translated=await request('/api/v1/results/current?lang=bn',{headers:{'Idempotency-Key':key}});
        if(state.key!==key || id!==routeId) return;
        state.localizedResult=translated; save();
      } catch(error) {
        if(id===routeId) main.innerHTML=`<section class="loading"><p>${esc(t(error.status?error.message:'Please check your connection, then try again.'))}</p><button class="button" data-start>Try again ↗</button></section>`;
        return;
      }
    }
    if(id===routeId) {resultView(); focusMain();} return;
  }
  main.innerHTML='<div class="loading" role="status">Getting your story ready…</div>';
  try {await getSurvey(); if(id===routeId) {quiz(); focusMain();}}
  catch {if(id===routeId) main.innerHTML='<section class="loading"><h1>The cinema is taking a moment.</h1><p class="quiet">Please check your connection, then try again.</p><button class="button" data-start>Try again ↗</button></section>';}
}

document.addEventListener('click', async event => {
  const target=event.target.closest('button'); if(!target) return;
  if (target.hasAttribute('data-start')) {go(state.result?'#result':'#quiz');}
  if (target.hasAttribute('data-character-start') && !busy) go('#character');
  if (target.hasAttribute('data-home')) go('#home');
  if (target.hasAttribute('data-world') && !busy) {state=fresh(); survey=null; state.category=target.dataset.world; save(); go('#quiz');}
  if (target.hasAttribute('data-restart') && !busy) {state=fresh(state.mode); survey=null; save(); go('#quiz');}
  if (target.hasAttribute('data-quiz-category') && !busy) {state.category=target.dataset.quizCategory;state.key=null;save();quiz();}
  if (target.id==='back-question' && state.step>0 && !busy) {state.step--;save();quiz();focusMain();}
  if (target.id==='next-question' && !busy) {
    if(state.answers[survey.questions[state.step].id]===undefined) return;
    if(state.step===14) await submit(); else {state.step++;save();quiz();focusMain();}
  }
  if (target.hasAttribute('data-filter')) {library.category=target.dataset.filter;library.page=1;await libraryView(routeId);}
  if (target.hasAttribute('data-page')) {library.page=Number(target.dataset.page);await loadLibrary();$('#search').scrollIntoView({block:'start',behavior:'smooth'});}
  if (target.hasAttribute('data-share')) await shareResult(target.dataset.share);
});
main.addEventListener('change', event=>{if(event.target.name==='answer' && !busy) {state.answers[survey.questions[state.step].id]=Number(event.target.value);state.key=null;state.result=null;save();$('#next-question').disabled=false;}});
main.addEventListener('input', event=>{if(event.target.id==='share-name') {state.displayName=event.target.value;state.share=null;save();if($('#profile-owner')) $('#profile-owner').textContent=profileOwner(false);if($('#share-preview')) $('#share-preview').hidden=true;if($('#download-card')) $('#download-card').hidden=true;} if(event.target.id==='search') {library.q=event.target.value;library.page=1;clearTimeout(searchTimer);searchTimer=setTimeout(()=>loadLibrary(),250);}});
$('#about-button').addEventListener('click',()=>$('#about').showModal());
$('#close-about').addEventListener('click',()=>$('#about').close());
window.addEventListener('hashchange',render);
window.addEventListener('moviegame:languagechange',()=>{survey=null;state.share=null;save();render();});
render();
getSurvey().then(()=>{if(!location.hash || location.hash==='#home') home();}).catch(()=>{});

main.addEventListener('error',event=>{const img=event.target;if(img.tagName==='IMG' && img.dataset.fallback && img.src!==new URL(img.dataset.fallback,location.origin).href) {img.src=img.dataset.fallback;const credit=img.closest('figure')?.querySelector('figcaption');if(credit) credit.textContent='Original MovieGame cover art';}},true);
async function prepareShare() {
  if(!state.share || state.share.snapshot?.language!==locale.lang) {
    const sourceKey=state.key;
    const shared=await request('/api/v1/shares',{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':sourceKey},body:JSON.stringify({display_name:state.displayName || '',language:locale.lang})});
    if(state.key!==sourceKey) throw new Error('Your game changed. Share the result of the current quiz instead.');
    state.share=shared;
    save();
  }
  const preview=$('#share-preview'), download=$('#download-card');
  if(preview) {preview.src=state.share.image_url;preview.hidden=false;}
  if(download) {download.href=downloadUrl(state.share.image_url);download.hidden=false;}
  return state.share;
}
let sharing=false;
async function shareResult(destination) {
  if(sharing) return;
  sharing=true;
  const nameInput=$('#share-name');if(nameInput) nameInput.disabled=true;
  const languageControl=$('#language-switcher');if(languageControl) languageControl.disabled=true;
  let popup=destination==='facebook'?window.open('about:blank','_blank'):null;
  if(popup) popup.opener=null;
  const status=$('#share-status');
  if(status) status.textContent='Preparing your named result and trait bars…';
  try {
    const shared=await prepareShare();
    const url=new URL(shared.share_url,location.origin).href;
    if(destination==='copy') {
      try {await navigator.clipboard.writeText(url);if(status) status.textContent='Result link copied, including your name and trait bars.';}
      catch {if(status) {status.textContent='Copy this result link: ';const link=document.createElement('a');link.href=url;link.textContent=url;status.append(link);}}
    } else if(destination==='facebook') {
      const facebook='https://www.facebook.com/sharer/sharer.php?u='+encodeURIComponent(url);
      if(popup) popup.location.href=facebook;else location.href=facebook;
      if(status) status.textContent='Facebook can preview your name and trait bars when this game is on a public HTTPS domain.';
    } else {
      const response=await fetch(shared.image_url);
      if(!response.ok) throw new Error('The result image could not be loaded. Try again.');
      const file=new File([await response.blob()],'moviegame-result.png',{type:'image/png'});
      if(navigator.canShare?.({files:[file]})) {
        await navigator.share({files:[file],title:t('My MovieGame character')});
        if(status) status.textContent='Choose Instagram in your device share sheet. The image includes your name and all eight bars.';
      } else {
        const download=$('#download-card');download?.click();
        if(status) status.textContent='Your result image is ready to save. Add it to an Instagram story or post from the Instagram app.';
      }
    }
  } catch(error) {
    if(popup) popup.close();
    const fallback='Sharing could not open. Use Save result image, then share it in Instagram.';
    const message=error.name==='AbortError'?'Sharing cancelled. Your result image is still ready.':error.message || fallback;
    if(status) status.textContent=locale.lang==='bn' && /[A-Za-z]/.test(t(message)) ? t(fallback) : t(message);
  } finally {sharing=false;if(nameInput) nameInput.disabled=false;if(languageControl) languageControl.disabled=false;}
}
