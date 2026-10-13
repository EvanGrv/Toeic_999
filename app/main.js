import {icon} from './icons.js';

const $ = (s) => document.querySelector(s);
const esc = (v) => String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const modeNames={daily:'Séance du jour',practice:'Entraînement ciblé',diagnostic:'Diagnostic',exam:'Examen complet','reading-exam':'Examen Reading',review:'Révision des erreurs',challenge:'Défi avancé'};
const partNames={1:'Photographies',2:'Questions-réponses',3:'Conversations',4:'Courts exposés',5:'Phrases incomplètes',6:'Textes à compléter',7:'Compréhension écrite'};
const state={dashboard:null,session:null,lessons:[],cards:[],errors:[],drafts:[],selected:{},confidence:{},route:'dashboard',filter:'all',cardFlipped:false,activeSeconds:0,lastActivity:Date.now(),busy:false,offset:0,audioEnabled:false,examSet:1};
const programme=[
 ['Prendre vos repères','word-forms',5,2,'Diagnostic 30 min · analyse 25 min · cours 15 min · Reading 30 min · écoute 20 min'],
 ['La précision avant la vitesse','word-forms',5,2],['Relier les idées','connectors',6,3],['Les temps qui font la différence','tenses',5,4],
 ['Chercher une preuve dans le texte','detail',7,3],['Lire entre les lignes','inference',7,2],['Premier examen complet',null,null,null,'Examen série 01 · 120 min'],
 ['Transformer les erreurs en acquis','agreement',5,4],['Croiser deux ou trois documents','synthesis',7,3],['Automatiser les associations','prepositions',5,2],
 ['Comprendre les intentions','intent',6,3],['Lire sous contrainte de temps','detail',7,4],['Consolider avant le bilan','vocabulary',7,2],['Faire le point sur deux semaines',null,null,null,'Examen série 08 · 120 min']
];
let player=null, playingGroup=null, routeVersion=0, pollBusy=false;

async function api(path,body) {
 const res=await fetch('/api'+path,{method:body===undefined?'GET':'POST',headers:body===undefined?{}:{'Content-Type':'application/json','X-TOEIC-Client':'1'},body:body===undefined?undefined:JSON.stringify(body)});
 const data=await res.json();
 if(!res.ok) throw new Error(data.error||'Impossible de joindre le serveur.');
 return data;
}
function notify(message,error=false){const n=$('#notifications');n.innerHTML=`<div class="toast ${error?'error':''}">${icon(error?'info':'check')}<span>${esc(message)}</span><button data-action="dismiss-toast" aria-label="Fermer le message">${icon('cross',16)}</button></div>`;if(!error)setTimeout(()=>n.replaceChildren(),4500);}
function dateLabel(ts){return new Date(ts*1000).toLocaleDateString('fr-FR',{day:'numeric',month:'short',timeZone:'Europe/Paris'});}
function duration(seconds){const s=Math.max(0,Math.floor(seconds));return `${Math.floor(s/60).toString().padStart(2,'0')}:${(s%60).toString().padStart(2,'0')}`;}
function tag(text,cls=''){return `<span class="tag ${cls}">${esc(text)}</span>`;}
function button(text,action,cls='primary',attrs=''){return `<button class="btn ${cls}" data-action="${action}" ${attrs}>${text}</button>`;}
function progress(value,cls=''){return `<div class="progress ${cls}" role="progressbar" aria-valuenow="${Math.round(value)}" aria-valuemin="0" aria-valuemax="100"><span style="width:${Math.min(100,Math.max(0,value))}%"></span></div>`;}
function empty(title,text,action='train',label='Choisir un exercice'){return `<div class="empty">${icon('leaf',34)}<h3>${esc(title)}</h3><p>${esc(text)}</p>${action?`<a class="btn secondary" href="#${action}">${esc(label)} ${icon('arrow',16)}</a>`:''}</div>`;}
function heading(kicker,title,desc,extra=''){return `<div class="page-heading"><div><div class="eyebrow">${esc(kicker)}</div><h1 tabindex="-1">${esc(title)}</h1><p>${esc(desc)}</p></div>${extra}</div>`;}
function sectionHead(title,link='',label='Tout voir'){return `<div class="section-head"><h2>${title}</h2>${link?`<a href="#${link}" class="text-link">${label} ${icon('arrow',16)}</a>`:''}</div>`;}
function skillName(id){return state.dashboard?.skills.find(s=>s.id===id)?.name||id;}
function stopAudio(){if(player){player.pause();player=null;}playingGroup=null;}
function goto(route){if(location.hash.slice(1)===route)loadRoute();else location.hash=route;}

function shell(content){
 const d=state.dashboard,p=d.profile;
 const nav=[['dashboard','home','Vue d’ensemble'],['plan','path','Mon parcours'],['train','target','Entraînement'],['lessons','book','Cours & stratégies'],['exams','clock','Examens blancs'],['cards','cards','Flashcards'],['errors','repeat','Carnet d’erreurs'],['stats','chart','Ma progression']];
 const current=state.route.split('/')[0];
 $('#app').innerHTML=`<aside class="sidebar" aria-label="Navigation principale"><button class="sidebar-close" data-action="menu" aria-label="Fermer le menu">${icon('cross',20)}</button><a href="#dashboard" class="brand"><span class="brand-mark">${icon('book',25)}</span><span>TOEIC <strong>990<span class="plus">+</span></strong><small>VOTRE AMBITION, VOTRE PARCOURS</small></span></a><div class="workspace-label">MON ESPACE</div><nav>${nav.map(([route,i,label])=>`<a href="#${route}" class="nav-link ${current===route?'active':''}" ${current===route?'aria-current="page"':''}>${icon(i)}<span>${label}</span>${route==='errors'&&d.dueQuestions?`<b class="nav-count">${d.dueQuestions}</b>`:''}</a>`).join('')}</nav><div class="sidebar-grow"></div><a class="lab-link" href="#lab">${icon('spark')}<div>Atelier d’exercices<small>Créer. Vérifier. Progresser.</small></div>${icon('chevron',15)}</a><nav class="lower-nav"><a href="#resources" class="nav-link ${current==='resources'?'active':''}">${icon('globe')}Ressources & méthode</a><a href="#settings" class="nav-link ${current==='settings'?'active':''}">${icon('settings')}Mes préférences</a></nav><a href="#settings" class="profile-mini"><span class="avatar">${esc(p.name.slice(0,1).toUpperCase())}</span><span><b>${esc(p.name)}</b><small>Objectif ${p.target} · puis 990</small></span>${icon('chevron',15)}</a></aside><div class="workspace"><header class="topbar"><div class="breadcrumbs"><button class="mobile-menu" data-action="menu" aria-label="Ouvrir le menu">${icon('menu')}</button><span>Mon espace</span>${icon('chevron',13)}<strong>${esc(nav.find(x=>x[0]===current)?.[2]||({settings:'Mes préférences',lab:'Atelier d’exercices',resources:'Ressources',session:'Séance en cours',lesson:'Cours'}[current]||'Mon parcours'))}</strong></div><div class="topbar-right"><span class="save-status"><i></i> Sauvegarde locale</span><span class="streak">${icon('flame',17)} ${d.stats.streak} jour${d.stats.streak>1?'s':''}</span></div></header><main id="main" class="main" tabindex="-1">${content}</main><footer>TOEIC 990+ AI <span>Votre progression, votre rythme.</span><a href="#resources">Application indépendante · Contenus originaux</a></footer></div>`;
}

function dashboard(){
 const d=state.dashboard,p=d.profile,total=p.reading+p.listening;
 const active=d.sessions.find(s=>s.status==='active');
 const weak=[...d.skills].filter(s=>s.n>0).sort((a,b)=>a.mastery-b.mastery).slice(0,3);
 const priorities=weak.length?weak:[d.skills.find(s=>s.id==='word-forms'),d.skills.find(s=>s.id==='connectors'),d.skills.find(s=>s.id==='synthesis')];
 const day=new Date().toLocaleDateString('fr-FR',{weekday:'long',day:'numeric',month:'long',timeZone:'Europe/Paris'});
 return `${heading(day,`Un pas de plus, ${p.name}.`,'Les grands scores se construisent une séance à la fois.',`<a class="btn secondary" href="#plan">${icon('calendar',17)} Mon programme</a>`)}
 <div class="dashboard-grid"><div class="dashboard-left"><section class="daily-hero"><div class="hero-copy"><div class="hero-eyebrow">${icon('spark',15)} VOTRE SÉANCE PERSONNALISÉE</div><h2>Faites du Reading<br>votre point fort.</h2><p>Un entraînement qui s’ajuste à vos réponses.<br>Aujourd’hui, chaque exercice a une raison d’être.</p><div class="hero-meta"><span>${icon('clock',16)} ${Math.min(d.dailyGoal||p.dailyMinutes,60)} min de pratique</span><span>${icon('target',16)} ${d.allocation.reading} % Reading</span></div>${button(`${active?'Reprendre ma séance':'Commencer ma séance'} ${icon('arrow',18)}`,active?'resume':'start','light',active?`data-id="${active.id}"`:'data-mode="daily"')}</div><div class="hero-visual" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="hero-numeral">990<span>+</span></div><div class="orbit-dot"></div><div class="hero-caption">L’AMBITION SE TRAVAILLE.</div></div></section>
 <div class="metric-row"><div class="metric"><span>${icon('target',17)} Questions travaillées</span><strong>${d.stats.answered}<small>${d.stats.unique} distinctes</small></strong></div><div class="metric"><span>${icon('check',17)} Taux de réussite</span><strong>${d.stats.accuracy===null?'—':d.stats.accuracy+' %'}<small>${d.stats.answered?'sur vos réponses':'Première séance à venir'}</small></strong></div><div class="metric"><span>${icon('clock',17)} Temps de pratique</span><strong>${d.stats.minutes}<small>minutes cumulées</small></strong></div></div>
 <section class="section">${sectionHead('Vos prochains leviers','stats','Voir mes compétences')}<div class="priority-list">${priorities.map((s,i)=>`<a class="priority-row" href="#lesson/${s.id}"><span class="priority-icon ${['sage','sand','lavender'][i]}">${icon(['book','path','folder'][i],23)}</span><div><div class="priority-name">${esc(s.name)} ${tag(i===0?'Prioritaire':i===1?'Consolider':'Approfondir',i===0?'warm':'muted')}</div><p>${s.n?`${s.accuracy} % de réussite · ${s.n} questions distinctes`:'Point de départ proposé · À confirmer par la pratique'}</p></div><span class="priority-end">${s.n?`${s.mastery} %`:'Explorer'} ${icon('chevron',17)}</span></a>`).join('')}</div></section>
 <section class="section">${sectionHead('Un peu chaque jour','stats','Voir mon activité')}<div class="activity-panel"><div><h3>${d.stats.streak?'Gardez votre élan.':'Votre première série commence ici.'}</h3><p>${d.stats.streak?`${d.stats.streak} jour${d.stats.streak>1?'s':''} de pratique consécutive.`:'Pas besoin d’une journée parfaite. Juste d’un premier exercice.'}</p></div><div class="week-activity">${d.days.slice(-7).map(day=>`<div title="${day.date} · ${day.count} réponses"><span>${new Date(day.date+'T12:00:00').toLocaleDateString('fr-FR',{weekday:'narrow'})}</span><b class="day-circle ${day.count?'done':''} ${day.date===d.today.date?'today':''}">${day.count?icon('check',15):'·'}</b></div>`).join('')}</div></div></section>
 </div><aside class="dashboard-right"><section class="card score-card"><div class="section-head"><h2>Votre cap</h2>${icon('trophy',19)}</div><div class="score-main"><strong>${total}</strong><span>/ 990</span></div><p class="score-label">Votre dernier score officiel</p><div class="score-track"><span style="left:${total/990*100}%" class="score-dot"></span><span class="target-marker" style="left:${p.target/990*100}%"></span></div><div class="score-track-labels"><span>Point de départ</span><strong>Objectif ${p.target}</strong></div><div class="score-breakdown"><div>${icon('headphones',17)}<span>Listening <small>B2 déclaré</small></span><b>${p.listening}<small>/495</small></b></div><div>${icon('book',17)}<span>Reading <small>B1 déclaré</small></span><b>${p.reading}<small>/495</small></b></div></div><a href="#settings" class="text-link">Ajuster mon objectif ${icon('arrow',15)}</a></section>
 <section class="card focus-card"><div class="section-head"><h2>Le bon équilibre</h2>${tag(d.allocation.adaptive?'Adaptatif':'Point de départ','green')}</div><div class="split-bar"><span style="width:${d.allocation.reading}%"></span></div><div class="split-labels"><span><i class="legend-dot green-dot"></i>Reading <b>${d.allocation.reading} %</b></span><span><i class="legend-dot sand-dot"></i>Listening <b>${d.allocation.listening} %</b></span></div><p>Votre Reading a le plus de marge de progression. La répartition évoluera avec vos résultats.</p></section>
 <a class="revision-callout" href="#cards"><span class="revision-icon">${icon('cards',24)}</span><div><h3>${d.dueCards} cartes vous attendent</h3><p>Quelques minutes pour ancrer vos acquis.</p></div>${icon('arrow',18)}</a>
 <div class="quiet-note">${icon('leaf',18)}<p>La régularité fait la différence.<br>La perfection viendra avec la pratique.</p></div></aside></div>`;
}

function training(){
 const d=state.dashboard;
 const parts=d.parts.filter(p=>state.filter==='all'||(state.filter==='reading'?p.part>=5:p.part<5));
 return `${heading('LA PRATIQUE QUI FAIT PROGRESSER','À vous de jouer.','Travaillez une partie précise ou laissez votre parcours choisir le prochain défi.')}
 <div class="training-banner"><div class="circle-icon">${icon('spark',26)}</div><div><h2>Le bon exercice, au bon moment.</h2><p>Faiblesses, nouveautés et révisions se combinent dans votre séance.</p></div>${button(`Lancer ma séance ${icon('arrow',17)}`,'start','primary','data-mode="daily"')}</div>
 <div class="toolbar"><div class="tabs" role="group" aria-label="Filtrer les parties">${[['all','Toutes les parties'],['reading','Reading'],['listening','Listening']].map(([key,name])=>`<button class="${state.filter===key?'active':''}" data-action="filter" data-filter="${key}" aria-pressed="${state.filter===key}">${name}</button>`).join('')}</div><span class="muted">${d.bankCount} questions · ${d.originalCount} initiales + ${d.variantCount} variantes${d.bankCount>d.originalCount+d.variantCount?` + ${d.bankCount-d.originalCount-d.variantCount} ajout(s)`:""}</span></div>
 <div class="parts-grid">${parts.map(p=>`<article class="card part-card"><div class="part-card-top"><span class="part-number">PART ${p.part}</span><span class="circle-icon ${p.part<5?'sand':'sage'}">${icon(p.part<5?'headphones':'book',24)}</span></div><h2>${p.name}</h2><p>${{1:'Observer les détails, reconnaître la bonne description.',2:'Saisir une question et comprendre une réponse implicite.',3:'Suivre un échange, ses détails et ses intentions.',4:'Comprendre les annonces et les présentations.',5:'Grammaire, vocabulaire et précision en contexte.',6:'Retrouver la logique et la cohérence d’un texte.',7:'Lire, déduire et croiser plusieurs documents.'}[p.part]}</p><div class="part-card-meta">${tag(p.part>=5?'Reading':'Listening',p.part>=5?'green':'warm')}<span>${p.count} questions</span></div><div class="part-progress">${p.accuracy===null?'<span>À découvrir</span>':`<span>${p.accuracy} % de réussite</span><span>${p.attempts} réponses</span>`}</div>${progress(p.accuracy||0)}${button(`S’entraîner ${icon('arrow',17)}`,'start','secondary full',`data-mode="practice" data-part="${p.part}"`)}</article>`).join('')}</div>
 <section class="challenge-strip"><span class="circle-icon">${icon(d.challengeReady?'bolt':'lock',25)}</span><div><h2>Au-delà du TOEIC</h2><p>Nuances C1–C2, inversions et inférences exigeantes. Déblocage : 40 questions B2/C1 distinctes, au moins 85 % de réussite.</p></div>${button('Relever le défi','start','secondary',`data-mode="challenge" ${!d.challengeReady?'disabled':''}`)}</section>`;
}

function plan(){
 const d=state.dashboard,p=d.profile;
 const daysLeft=p.examDate?Math.ceil((new Date(p.examDate+'T23:59:59+02:00')-Date.now())/86400000):null;
 const weak=[...d.skills].filter(s=>s.n>0).sort((a,b)=>a.mastery-b.mastery)[0]||d.skills[0];
 return `${heading('VOTRE FEUILLE DE ROUTE','Un parcours qui vous ressemble.','Vos résultats guident les priorités. Votre planning donne le rythme.',`<a class="btn secondary" href="#settings">${icon('settings',17)} Adapter mon rythme</a>`)}
 <div class="plan-summary"><div><span>Premier objectif</span><strong>${p.target}<small>/ 990</small></strong></div><div><span>Temps aujourd’hui</span><strong>${d.dailyGoal}<small>min</small></strong></div><div><span>Examen</span><strong>${daysLeft===null?'À définir':daysLeft<0?'Date passée':'J − '+daysLeft}</strong></div></div>
 <div class="two-columns"><section class="card"><div class="section-head"><h2>Votre séance en 3 temps</h2>${tag('Aujourd’hui','green')}</div><div class="timeline"><div><span>01</span><div><h3>Réactiver vos acquis</h3><p>${d.dueCards} cartes et ${d.dueQuestions} erreurs à revoir. Retrouvez la réponse avant d’afficher la correction.</p><a class="text-link" href="#cards">Réviser mes cartes ${icon('arrow',15)}</a></div></div><div><span>02</span><div><h3>Faire avancer votre Reading</h3><p>Priorité proposée : ${esc(weak.name.toLowerCase())}. Les passages restent complets, même si le nombre de questions varie légèrement.</p>${button('Commencer la séance','start','primary','data-mode="daily"')}</div></div><div><span>03</span><div><h3>Comprendre, puis réessayer</h3><p>Analysez chaque distracteur. Une erreur ou une réponse incertaine rejoint automatiquement vos révisions espacées.</p><a class="text-link" href="#errors">Ouvrir mon carnet ${icon('arrow',15)}</a></div></div></div></section><section class="card"><h2>Votre semaine, à votre rythme</h2><div class="week-plan">${p.weekMinutes.map((min,i)=>`<div><span>${['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche'][i]}</span><div class="mini-bar"><b style="width:${min/180*100}%"></b></div><strong>${min?min+' min':'Repos'}</strong></div>`).join('')}</div><div class="note">${icon('info',18)}<p>Les durées incluent cours et révisions. Les séances de questions sont découpées en blocs de 60 minutes maximum.</p></div></section></div>
 <section class="card section"><h2>Pourquoi cette répartition ?</h2><p>${esc(d.allocation.reason)}</p><div class="allocation-large"><b>${d.allocation.reading}% <span>Reading</span></b><b>${d.allocation.listening}% <span>Listening</span></b></div><p class="muted">La maîtrise affichée est un indicateur pédagogique lissé. Elle ne constitue ni un niveau CECR certifié ni une estimation officielle de score.</p></section>
 <section class="section">${sectionHead('14 jours pour installer une vraie dynamique')}<div class="programme-intro"><strong>28 heures <span>de préparation</span></strong><p>${d.bankCount.toLocaleString('fr-FR')} questions, ${d.cardCount} cartes et 8 séries complètes. Ce programme est une proposition : si une compétence reste fragile, votre parcours adaptatif lui donne la priorité.</p></div><div class="programme-grid">${programme.map(([title,course,reading,listening,custom],i)=>`<article class="card programme-day"><div class="section-head">${tag('JOUR '+String(i+1).padStart(2,'0'),i===6||i===13?'green':'muted')}<span class="muted">120 min</span></div><h3>${title}</h3><p>${custom||'Cartes 15 min · cours 15 min · Reading 45 min · Listening 30 min · correction 15 min'}</p><div class="programme-actions">${i===6||i===13?button(`Examen · série ${i===6?'01':'08'}`,'programme-exam','primary',`data-set="${i===6?1:8}"`):`${i===0?button('Diagnostic','exam-info','secondary','data-mode="diagnostic"'):`<a class="btn secondary" href="#cards">Cartes</a>`}<a class="btn secondary" href="#lesson/${course}">Cours</a>${button('Reading','start','secondary',`data-mode="practice" data-part="${reading}" data-minutes="${i===0?30:45}"`)}${button('Listening','start','secondary',`data-mode="practice" data-part="${listening}" data-minutes="${i===0?20:30}"`)}<a class="text-link" href="#errors">Correction ${icon('arrow',14)}</a>`}</div></article>`).join('')}</div></section>`;
}

function lessons(){
 const done=state.dashboard.lessonsDone;
 return `${heading('COMPRENDRE POUR MIEUX RÉPONDRE','Les bons réflexes s’apprennent.','Des cours courts, des exemples utiles et une mise en pratique immédiate.')}
 <div class="lesson-grid">${state.lessons.map((l,i)=>`<a href="#lesson/${l.id}" class="card lesson-tile"><div class="lesson-top"><span class="lesson-number">${String(i+1).padStart(2,'0')}</span>${done.includes(l.id)?tag('Lu','green'):tag(l.level,'muted')}</div><h2>${esc(l.title)}</h2><p>${esc(l.subtitle)}</p><div class="lesson-bottom"><span>${icon('clock',15)} ${l.minutes} min</span>${icon('arrow',20)}</div></a>`).join('')}</div>`;
}
function lesson(id){
 const l=state.lessons.find(x=>x.id===id);
 if(!l)return empty('Cours introuvable','Retrouvez les cours dans la bibliothèque.','lessons');
 return `<a class="back-link" href="#lessons">← Tous les cours</a>${heading(l.level,l.title,l.subtitle)}<div class="lesson-layout"><article class="card lesson-body">${l.sections.map(([title,body],i)=>`<section><span class="lesson-index">${String(i+1).padStart(2,'0')}</span><h2>${esc(title)}</h2><p>${esc(body).replace(/\n/g,'<br>')}</p></section>`).join('')}<div class="lesson-actions">${button(`${icon('check',17)} Marquer comme lu`,'complete-lesson','secondary',`data-id="${l.id}"`)}${button(`Mettre en pratique ${icon('arrow',17)}`,'start','primary',`data-mode="practice" data-skill="${l.id}"`)}</div></article><aside class="card lesson-aside"><span class="circle-icon sage">${icon('leaf',25)}</span><h3>Faites une pause active.</h3><p>Fermez les yeux quelques secondes. Pouvez-vous reformuler une règle et inventer un exemple ?</p><p class="muted">Lire donne un repère. Retrouver la règle sans aide l’installe dans la durée.</p><span class="muted">${l.minutes} minutes de lecture</span></aside></div>`;
}

function exams(){
 return `${heading('MESURER SANS SE RACONTER D’HISTOIRES','Le rendez-vous avec vos acquis.','Un diagnostic pour orienter la pratique. Des examens pour travailler la durée.')}
 <div class="exam-set-selector"><label>Série à utiliser<select id="exam-set">${state.dashboard.examSets.map(s=>`<option value="${s.id}" ${state.examSet===s.id?'selected':''}>${s.name} · ${s.kind}${s.completed?' · effectuée':''}</option>`).join('')}</select></label><p>8 séries de 200 questions. Les séries 02 à 08 sont des variantes contrôlées ; les six photos sont partagées. Les questions déjà rencontrées restent possibles en examen.</p></div>
 <div class="exam-grid">${[
  ['diagnostic','Votre point de départ','30 min maximum','≈ 20 questions','Un premier échantillon de compétences. Les corrections sont disponibles à la fin. Aucun score TOEIC prédit.','target'],
  ['reading-exam','Le défi Reading','75 minutes','100 questions','Parties 5, 6 et 7. Navigation libre dans la section, questions à marquer et chronomètre continu.','book'],
  ['exam','Le format classique','120 minutes','200 questions','Listening : 45 min. Reading : 75 min. Écoute cadencée, sans retour en arrière ; correction à la fin.','headphones']
 ].map(([mode,title,timing,count,desc,i])=>`<article class="card exam-card ${mode==='exam'?'featured':''}"><span class="circle-icon ${mode==='exam'?'sage':'sand'}">${icon(i,26)}</span>${tag(mode==='exam'?'FORMAT 2 HEURES':mode==='diagnostic'?'POUR COMMENCER':'VOTRE PRIORITÉ',mode==='exam'?'green':'muted')}<h2>${title}</h2><div class="exam-numbers">${timing}<span>${count}</span></div><p>${desc}</p>${button(`Commencer ${icon('arrow',17)}`,'exam-info',mode==='exam'?'primary full':'secondary full',`data-mode="${mode}"`)}</article>`).join('')}</div>
 <div class="note wide-note">${icon('info',22)}<div><b>Un simulateur d’entraînement indépendant.</b><p>Les questions et photographies sont originales, les voix sont synthétiques. Le format reproduit la structure du test classique ; les pauses audio sont adaptées aux enregistrements. Les séries partagent des familles de situations et ne constituent pas des formes psychométriquement étalonnées. Les pourcentages ne sont pas convertis en score officiel. La version Multistage Adaptive d’une heure n’est pas simulée.</p></div></div>
 ${sessionHistory()}`;
}
function sessionHistory(){
 const sessions=state.dashboard.sessions;
 return `<section class="section">${sectionHead('Vos dernières séances')}${sessions.length?`<div class="card session-history">${sessions.map(s=>`<a href="#session/${s.id}"><span class="history-icon">${icon(s.mode.includes('exam')?'clock':'target',20)}</span><div><b>${modeNames[s.mode]}</b><small>${dateLabel(s.created)} · ${s.count} questions</small></div><span>${s.status==='active'?tag('En cours','warm'):tag(`${s.result.correct}/${s.result.total} réponses correctes`,'green')}</span>${icon('chevron',18)}</a>`).join('')}</div>`:empty('Chaque séance laissera une trace.','Vos résultats apparaîtront ici dès votre premier entraînement.','train','Démarrer un entraînement')}</section>`;
}

function cards(){
 const due=state.cards.filter(c=>c.due<=Date.now()/1000).sort((a,b)=>(a.due===0)-(b.due===0)||a.due-b.due);
 const c=due[0];
 return `${heading('RETROUVER AVANT DE RETOURNER','Un mot de plus, pour longtemps.','La répétition espacée remet les mots difficiles au bon moment.')}
 <div class="flash-meta"><span>${due.length} carte${due.length>1?'s':''} à revoir</span><span>${state.cards.length} mots et expressions</span></div>
 ${c?`<div class="flashcard ${state.cardFlipped?'flipped':''}"><div class="eyebrow">${esc(skillName(c.skill))}</div><span class="flash-language">ANGLAIS → FRANÇAIS</span><h2>${esc(c.front)}</h2>${state.cardFlipped?`<div class="flash-answer"><h3>${esc(c.back)}</h3><p lang="en">${esc(c.example)}</p></div>`:'<p>Retrouvez le sens et imaginez un exemple.</p>'}<button class="text-link flash-flip" data-action="flip">${icon('repeat',17)} ${state.cardFlipped?'Masquer la réponse':'Révéler la réponse'}</button></div>${state.cardFlipped?`<div class="rating-buttons">${button('À revoir <small>Dans 10 min</small>','rate-card','secondary',`data-id="${c.id}" data-rating="again"`)}${button('Retrouvé <small>Intervalle progressif</small>','rate-card','primary',`data-id="${c.id}" data-rating="good"`)}${button('Facile <small>Espacer davantage</small>','rate-card','secondary',`data-id="${c.id}" data-rating="easy"`)}</div>`:'<p class="center muted">Ne retournez la carte qu’après avoir essayé de répondre.</p>'}`:empty('Tout est à jour.','Vos cartes reviendront automatiquement à leur prochaine échéance.','train','Continuer à pratiquer')}
 <div class="note flash-note">${icon('leaf',18)}<p>« À revoir » si la réponse est venue après lecture. « Retrouvé » si vous l’avez rappelée sans aide. « Facile » si vous pouvez aussi l’utiliser en contexte.</p></div>`;
}

function errors(){
 const now=Date.now()/1000,due=state.errors.filter(e=>e.due<=now);
 return `${heading('L’ERREUR EST UNE INFORMATION','Votre carnet de progrès.','Les erreurs et les réponses incertaines reviennent après un délai.',button(`Revoir ${due.length} question${due.length>1?'s':''} ${icon('repeat',17)}`,'start','primary',`data-mode="review" ${!due.length?'disabled':''}`))}
 ${!state.errors.length?empty('Un carnet prêt à vous aider.','Après un exercice, vos erreurs et réponses incertaines apparaîtront ici.'):state.errors.map(e=>`<details class="card error-item"><summary><span class="circle-icon ${e.last_correct?'sage':'sand'}">${icon(e.last_correct?'check':'repeat',20)}</span><div><span class="eyebrow">PART ${e.part} · ${esc(skillName(e.question.skill))}</span><h3 lang="en">${esc(e.question.stem)}</h3></div>${tag(e.due<=now?'À revoir':`Révision le ${dateLabel(e.due)}`,e.due<=now?'warm':'muted')}</summary><div class="error-detail"><p><b>Bonne réponse :</b> ${esc(e.question.choices[e.question.answer])}</p><p>${esc(e.question.explanation)}</p><a class="text-link" href="#lesson/${e.question.skill}">Revoir la règle ${icon('arrow',15)}</a></div></details>`).join('')}`;
}

function stats(){
 const d=state.dashboard;
 const max=Math.max(1,...d.days.map(x=>x.count));
 return `${heading('DES REPÈRES, PAS DES PROMESSES','La progression se voit dans les détails.','Vos données réelles, par partie et par compétence.')}
 <div class="stats-overview"><div class="card"><span>Réponses enregistrées</span><strong>${d.stats.answered}</strong><small>${d.stats.unique} questions distinctes</small></div><div class="card"><span>Réussite globale</span><strong>${d.stats.accuracy===null?'—':d.stats.accuracy+' %'}</strong><small>Sur vos entraînements</small></div><div class="card"><span>Pratique cumulée</span><strong>${d.stats.minutes}<small> min</small></strong><small>Temps actif sur les questions</small></div><div class="card"><span>Régularité</span><strong>${d.stats.streak}<small> jours</small></strong><small>Série actuelle</small></div></div>
 <section class="card section"><div class="section-head"><h2>Votre activité sur 14 jours</h2><span class="muted">Questions répondues</span></div><div class="bar-chart" role="img" aria-label="Activité quotidienne : ${d.days.map(x=>x.date+': '+x.count+' réponses').join(', ')}">${d.days.map(x=>`<div class="chart-column"><span class="bar-value">${x.count||''}</span><div class="bar-area"><b style="height:${Math.max(2,x.count/max*100)}%" class="${x.count?'has-data':''}"></b></div><small>${new Date(x.date+'T12:00:00').getDate()}</small></div>`).join('')}</div>${!d.stats.answered?'<p class="center muted">Vos premières réponses feront apparaître votre activité.</p>':''}</section>
 <div class="two-columns"><section class="card"><h2>Par partie</h2><div class="part-stats">${d.parts.map(p=>`<div><div><span><b>${p.part}</b> ${p.name}</span><strong>${p.accuracy===null?'—':p.accuracy+' %'}</strong></div>${progress(p.accuracy||0)}<small>${p.attempts} réponse${p.attempts>1?'s':''}</small></div>`).join('')}</div></section><section class="card"><h2>Les compétences à consolider</h2><div class="skill-stats">${[...d.skills].sort((a,b)=>a.mastery-b.mastery).map(s=>`<a href="#lesson/${s.id}"><div><strong>${esc(s.name)}</strong><small>${s.n} questions distinctes · ${s.confidence}${s.n?' · '+s.average_seconds+' s/question':''}</small></div><b>${s.n?s.mastery+' %':'—'}</b></a>`).join('')}</div></section></div><p class="muted methodology">Maîtrise = (réponses correctes distinctes + 2) / (questions distinctes + 4). Ce lissage limite l’effet d’un petit échantillon. Les niveaux des exercices sont éditoriaux ; aucun score TOEIC ou niveau CECR n’est certifié.</p>${sessionHistory()}`;
}

function settings(){
 const p=state.dashboard.profile;
 return `${heading('VOTRE PRÉPARATION, VOS RÈGLES','Ajustez votre rythme.','Les préférences sont enregistrées sur cet ordinateur et utilisées dès la prochaine séance.')}
 <form id="settings-form" class="settings-layout"><section class="card"><h2>Votre objectif</h2><div class="form-grid"><label>Prénom<input name="name" value="${esc(p.name)}" maxlength="40" required></label><label>Date de l’examen<input type="date" name="examDate" value="${esc(p.examDate)}"></label><label>Premier score cible<input type="number" name="target" min="10" max="990" step="5" value="${p.target}" required></label><label>Durée habituelle par jour (min)<input type="number" name="dailyMinutes" min="30" max="180" value="${p.dailyMinutes}" required></label><label>Dernier Listening officiel<input type="number" name="listening" min="5" max="495" step="5" value="${p.listening}" required></label><label>Dernier Reading officiel<input type="number" name="reading" min="5" max="495" step="5" value="${p.reading}" required></label></div><p class="field-help">Objectif final conservé : 990. Les scores saisis sont vos résultats déclarés, pas des estimations de l’application.</p><h2 class="form-subtitle">Vos préférences d’entraînement</h2><div class="form-grid"><label>Intensité<select name="intensity">${[['gentle','Progressive'],['balanced','Soutenue'],['intensive','Intensive']].map(([v,l])=>`<option value="${v}" ${p.intensity===v?'selected':''}>${l}</option>`).join('')}</select></label><label>Préférence<select name="preference">${[['balanced','Suivre le moteur adaptatif'],['reading','Favoriser le Reading'],['listening','Favoriser le Listening']].map(([v,l])=>`<option value="${v}" ${p.preference===v?'selected':''}>${l}</option>`).join('')}</select></label><label>Voix privilégiées à l’entraînement<select name="accent">${[['mixed','Varier les accents'],['US','Dominante américaine'],['UK','Dominante britannique'],['AU','Dominante australienne']].map(([v,l])=>`<option value="${v}" ${p.accent===v?'selected':''}>${l}</option>`).join('')}</select></label></div><p class="field-help">Les dialogues peuvent mêler plusieurs voix. Les examens conservent une variété d’accents.</p></section><section class="card"><h2>Votre temps disponible</h2><p class="muted">Personnalisez chaque jour, de 0 à 180 minutes.</p><div class="daily-inputs">${p.weekMinutes.map((v,i)=>`<label>${['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche'][i]}<span><input name="day${i}" type="number" min="0" max="180" value="${v}" required> min</span></label>`).join('')}</div><button class="btn secondary full" type="button" data-action="apply-daily">Appliquer la durée habituelle aux 7 jours</button><div class="note"><p>Un jour à 0 minute représente un repos prévu. Vous pouvez toujours lancer un exercice librement.</p></div></section><div class="settings-submit"><p id="form-message" role="status"></p><button class="btn primary" type="submit">${icon('check',17)} Enregistrer mes préférences</button></div></form>
 <section class="card section backup-card"><div><h2>Vos données vous appartiennent.</h2><p>Exportez votre profil, vos réponses, vos séances et vos révisions dans un fichier JSON.</p></div>${button(`${icon('download',17)} Exporter mes données`,'export','secondary')}</section>`;
}

function lab(){
 const d=state.dashboard;
 return `${heading('UN CONTENU QUI PEUT GRANDIR','L’atelier d’exercices.','Générez ou importez des questions de partie 5, vérifiez-les, puis ajoutez-les à la banque.')}
 <div class="two-columns"><form id="generate-form" class="card"><div class="section-head"><h2>Créer un exercice</h2>${tag(d.aiConfigured?'IA configurée':'Mode local disponible','green')}</div><p class="muted">Chaque proposition reste un brouillon jusqu’à votre relecture.</p><div class="form-grid"><label>Mode<select name="provider"><option value="local">Gabarits locaux · sans clé</option value="openai" ${!d.aiConfigured?'disabled':''}>OpenAI · génération + second contrôle</option></select></label><label>Difficulté souhaitée<select name="level"><option>B2</option><option>B1</option><option>C1</option><option>C2</option></select></label><label class="full-label">Compétence<select name="skill">${d.skills.slice(0,6).map(s=>`<option value="${s.id}">${s.name}</option>`).join('')}</select></label></div><p class="field-help">En mode local, la difficulté dépend du gabarit. En mode IA, le niveau demandé reste une appréciation éditoriale.</p><button class="btn primary full" type="submit">${icon('spark',17)} Générer un brouillon</button><p id="generation-status" role="status"></p></form>
 <section class="card"><h2>Comment un exercice entre dans la banque</h2><ol class="quality-steps"><li><b>Structure vérifiée</b><span>Quatre réponses distinctes, un seul blanc, une explication et une compétence.</span></li><li><b>Réponse contrôlée</b><span>Gabarit contraint en local ; seconde résolution sans la clé fournie en mode IA.</span></li><li><b>Relecture explicite</b><span>Vérifiez l’unicité de la réponse et chaque distracteur avant publication.</span></li></ol><p class="field-help">Pour activer OpenAI : définir OPENAI_API_KEY dans l’environnement du serveur, puis le relancer. La clé n’est jamais envoyée au navigateur. Deux appels sont effectués par question ; aucun appel payant au démarrage.</p></section></div>
 <details class="card import-box section"><summary>${icon('upload',19)} Importer une question originale ou autorisée</summary><form id="import-form"><label>Question au format JSON<textarea name="json" rows="10" required placeholder='{"stem":"… ____ …", "choices":["A","B","C","D"], "answer":0, "explanation":"…", "skill":"word-forms", "level":"B2"}'></textarea></label><label class="checkbox"><input type="checkbox" name="rights" required>Je dispose des droits nécessaires pour réutiliser ce contenu.</label><button class="btn secondary" type="submit">Vérifier et importer en brouillon</button></form></details>
 <section class="section">${sectionHead('Vos propositions')}<div class="draft-list">${d && state.drafts.length?state.drafts.map(g=>{const q=g.questions[0];return `<article class="card draft"><div class="section-head">${tag(g.status==='published'?'Publié':g.status==='rejected'?'Écarté':'À relire',g.status==='published'?'green':'warm')}<span class="muted">${g.source==='local'?'Gabarit local':g.source==='openai'?'Génération IA':'Import'} · ${q.level}</span></div><h3 lang="en">${esc(q.stem)}</h3><div class="draft-options">${q.choices.map((c,i)=>`<div class="${i===q.answer?'correct':''}"><b>${'ABCD'[i]}</b>${esc(c)}${i===q.answer?icon('check',16):''}</div>`).join('')}</div><p>${esc(q.explanation)}</p><div class="note"><p>${esc(g.review.note)}</p></div>${g.status==='draft'?`<label class="checkbox"><input type="checkbox" id="reviewed-${g.id}">J’ai vérifié qu’une seule réponse est correcte et que l’explication est exacte.</label><div class="draft-actions">${button('Écarter','draft','ghost',`data-id="${g.id}" data-decision="reject"`)}${button('Publier dans ma banque','draft','primary',`data-id="${g.id}" data-decision="publish"`)}</div>`:''}</article>`;}).join(''):empty('L’atelier est prêt.','Votre premier brouillon apparaîtra ici. Une question publiée devient disponible dans les séances ciblées.','', '')}</div></section>`;
}

function resources(){
 return `${heading('DES BASES TRANSPARENTES','La méthode et les sources.','Comprendre le format, connaître les limites, compléter votre pratique.')}
 <div class="two-columns"><section class="card"><h2>Compléter votre entraînement</h2><div class="resource-links">${[
 ['Le format Listening & Reading','Structure classique et durée des sections','https://www.ets.org/toeic/about/listening-reading.html'],
 ['Préparation et exemples ETS','Exemples officiels, audios et guide du candidat','https://www.ets.org/toeic/test-takers/prepare.html'],
 ['Le guide officiel du candidat','Consignes, compétences, notation et conditions','https://www.ets.org/content/dam/ets-org/pdfs/toeic/toeic-listening-reading-test-examinee-handbook.pdf'],
 ['Les outils officiels ETS Global','Application, tests et préparation complète de l’éditeur','https://www.etsglobal.org/gp/en/landing-page/preparation-for-the-toeic-test'],
 ['Exam English','Entraînements en ligne par partie','https://www.examenglish.com/TOEIC/'],
 ['EnglishClub','Exemples des sept parties et explications','https://www.englishclub.com/esl-exams/ets-toeic-practice.php'],
 ['TOEIC Training','Pratique externe et présentation d’un test complet','https://www.toeic-training.com/toeic-test/'],
 ['La version classique et le Multistage Adaptive','Comprendre la différence entre les formats','https://www.etsglobal.org/fr/fr/test-type-family/test-toeic-listening-and-reading']
 ].map(([title,desc,url])=>`<a href="${url}" target="_blank" rel="noopener noreferrer"><div><b>${title}</b><small>${desc}</small></div>${icon('external',18)}</a>`).join('')}</div></section><section class="card"><h2>Ce que vos résultats signifient</h2><p>Votre score de départ est celui que vous avez déclaré : Listening ${state.dashboard.profile.listening}, Reading ${state.dashboard.profile.reading}. Les exercices mesurent ensuite votre réussite, vos temps et vos points à consolider.</p><p>La conversion officielle dépend de la forme du test et de son étalonnage. Cette application n’annonce donc pas un score TOEIC à partir d’un simple pourcentage.</p><p>Les niveaux B1 à C2 servent à organiser la difficulté. Les défis avancés ne prétendent pas certifier un niveau C2.</p></section></div>
 <section class="card section"><h2>Apprendre, retrouver, espacer</h2><div class="method-grid"><div><h3>Rappel actif</h3><p>Répondre avant de voir la correction, rappeler un mot avant de retourner la carte.</p></div><div><h3>Répétition espacée</h3><p>Réviser les erreurs après dix minutes, puis espacer progressivement les réussites.</p></div><div><h3>Pratique alternée</h3><p>Mélanger les compétences tout en conservant les documents et conversations complets.</p></div><div><h3>Adaptation prudente</h3><p>Conserver des seuils de données avant de modifier les priorités ou débloquer les défis.</p></div></div></section>
 <section class="card section"><h2>Les recherches du projet</h2><div class="research-links">${[['990prep.md','Analyse de 990prep'],['globalexam.md','Analyse de GlobalExam'],['toeic-format.md','Format officiel'],['learning-science.md','Méthodes pédagogiques'],['content-sources.md','Sources et réutilisation'],['two-week-program.md','Programme de 28 heures']].map(([path,title])=>`<a class="btn secondary" href="/docs/research/${path}" target="_blank" rel="noopener">${icon('book',16)} ${title}</a>`).join('')}</div><p class="field-help">Recherche réalisée le 13 octobre 2026 sur les pages publiques. Les fonctionnalités réservées aux comptes n’ont pas été testées. Aucun test propriétaire n’a été importé.</p></section>`;
}

function stimulus(g,revealed=false){
 return `${g.image!==undefined?`<div class="photo-atlas photo-${g.image}" role="img" aria-label="Photographie de la question ${g.questions[0].id.split('-').at(-1)}"></div><p class="caption">Photographie de synthèse originale · support d’entraînement</p>`:''}
 ${g.documents?.map(doc=>`<article class="document"><div class="document-title">${icon('folder',17)} ${esc(doc.title)}</div><div class="document-body" lang="en">${esc(doc.body).replace(/\n/g,'<br>').replace(/\[(\d)\]/g,'<span class="blank-number">[$1]</span>')}</div></article>`).join('')||''}
 ${g.graphic?`<table class="stimulus-table"><caption>Support de la question</caption><thead><tr>${g.graphic.headers.map(h=>`<th>${esc(h)}</th>`).join('')}</tr></thead><tbody>${g.graphic.rows.map(row=>`<tr>${row.map(v=>`<td>${esc(v)}</td>`).join('')}</tr>`).join('')}</tbody></table>`:''}
 ${g.part<5?`<div class="audio-player"><button class="audio-play" data-action="play-audio" data-id="${g.id}" aria-label="Écouter l’audio">${icon(player&&!player.paused&&playingGroup===g.id?'pause':'play',20)}</button><div class="audio-info"><b>${g.part<=2?'Écoutez les propositions':'Écoutez le passage'}</b><span>Voix synthétiques · ${g.accent||'US'}${g.dialogue?' · conversation':''}</span><div class="audio-progress"><span id="audio-fill"></span></div></div><span id="audio-time">${player&&playingGroup===g.id?duration(player.currentTime):'00:00'}</span>${state.session?.mode==='exam'&&state.session?.status==='active'?'':`<label class="audio-speed"><span class="sr-only">Vitesse de lecture</span><select id="audio-speed"><option value="0.85">0,85×</option><option value="1" selected>1×</option><option value="1.15">1,15×</option></select></label>`}</div><p class="caption">${state.session?.mode==='exam'&&state.session.status==='active'?'Écoute cadencée : une reprise repart au temps courant, sans rembobinage.':'Écoutez d’abord sans transcription. Vous pourrez réécouter après la correction.'}</p>`:''}
 ${g.transcript?`<details class="transcript"><summary>Lire la transcription</summary><p lang="en">${esc(g.transcript).replace(/\n/g,'<br>')}</p>${g.part<=2?g.questions.map(q=>`<ol type="A">${q.choices.map(c=>`<li>${esc(c)}</li>`).join('')}</ol>`).join(''):''}</details>`:''}`;
}

function questionCard(q,g,number){
 const s=state.session,a=s.answers[q.id],graded=q.answer!==undefined;
 const selected=state.selected[q.id]??a?.choice;
 return `<article class="question-card" id="question-${q.id}"><div class="question-top"><span class="eyebrow">QUESTION ${number} ${tag(q.level,'muted')}</span><button class="icon-button ${s.flags.includes(q.id)?'flagged':''}" data-action="flag" data-id="${q.id}" aria-label="${s.flags.includes(q.id)?'Retirer le repère':'Marquer la question'}" aria-pressed="${s.flags.includes(q.id)}">${icon('flag',18)}</button></div><h2 lang="en">${esc(q.stem).replace(/____/g,'<span class="sentence-blank">________</span>')}</h2><div class="options" role="group" aria-label="Choix pour la question ${number}">${q.choices.map((choice,i)=>{const cls=graded?(i===q.answer?'correct':i===a?.choice?'incorrect':''):selected===i?'selected':'';return `<button class="option ${cls}" data-action="choose" data-qid="${q.id}" data-choice="${i}" ${graded?'disabled':''} aria-pressed="${selected===i}"><span class="option-letter">${'ABCD'[i]}</span><span lang="en">${esc(choice)}</span>${graded&&i===q.answer?icon('check',18):graded&&i===a?.choice?icon('cross',18):''}</button>`;}).join('')}</div>${graded?`<div class="correction ${a?.choice===q.answer?'correct':'incorrect'}"><strong>${icon(a?.choice===q.answer?'check':'info',18)} ${a?.choice===q.answer?'Bien joué.':a?'À retenir pour la prochaine fois.':'Question non répondue.'}</strong><p>${esc(q.explanation)}</p><a href="#lesson/${q.skill}" class="text-link">Revoir la règle ${icon('arrow',14)}</a></div>`:`<label class="confidence"><input type="checkbox" data-confidence="${q.id}" ${state.confidence[q.id]?'checked':''}> Je suis incertain : à revoir, même si ma réponse est juste.</label>`}</article>`;
}

function session(){
 const s=state.session;
 if(s.status==='completed')return result();
 const g=s.groups[s.index],total=s.groups.reduce((n,g)=>n+g.questions.length,0),offset=s.groups.slice(0,s.index).reduce((n,g)=>n+g.questions.length,0);
 const isListening=s.mode==='exam'&&g.part<5,immediate=!['exam','reading-exam','diagnostic'].includes(s.mode);
 const allAnswered=g.questions.every(q=>q.id in s.answers);
 return `<div class="session-top"><a href="#dashboard" class="back-link">← Mon espace</a><div class="session-status"><span>${icon('check',15)} Réponses sauvegardées</span>${s.deadline?`<b class="timer" id="timer" role="timer">${icon('clock',18)} <span></span></b>`:'<b class="timer">À votre rythme</b>'}</div></div><div class="session-title"><div><div class="eyebrow">${modeNames[s.mode]} · ${g.part<5?'LISTENING':'READING'}</div><h1 tabindex="-1">${partNames[g.part]}</h1></div><span>${Object.keys(s.answers).length} / ${total} réponses</span></div>${progress(Object.keys(s.answers).length/total*100,'session-progress')}
 ${isListening?`<div class="note exam-listening-note">${icon('volume',19)}<p>Passage ${s.index+1} / ${s.schedule.length}. Le passage suivant s’affichera automatiquement. <b id="slot-timer"></b></p>${!state.audioEnabled?button('Activer l’écoute','enable-audio','secondary'):''}</div>`:''}
 <div class="exercise-layout ${!g.documents?.length&&g.image===undefined&&!g.graphic&&g.part>=5?'single-question':''}"><div class="stimulus-column">${stimulus(g)}</div><div class="questions-column">${g.questions.map((q,i)=>questionCard(q,g,offset+i+1)).join('')}
 <div class="exercise-actions">${!isListening&&s.index>0&&!(s.mode==='exam'&&s.groups[s.index-1].part<5)?button('← Précédent','navigate','ghost',`data-index="${s.index-1}"`):'<span></span>'}${immediate&&!allAnswered?button(`Valider ${g.questions.length>1?'les réponses':'ma réponse'} ${icon('check',17)}`,'validate','primary'):!isListening?(s.index<s.groups.length-1?button(`Passage suivant ${icon('arrow',17)}`,'next','primary'):button('Terminer la séance','finish-info','primary')):button('Enregistrer mes réponses','validate','primary')}</div>
 ${!immediate&&!isListening?`<div class="exam-save-row">${button('Enregistrer mes choix','validate','secondary')}${button('Terminer maintenant','finish-info','ghost')}</div>`:''}
 ${immediate?`<div class="center">${button('Terminer cette séance','finish-info','ghost small')}</div>`:''}</div></div>
 ${!isListening?`<details class="question-nav"><summary>Navigation dans la séance · ${s.flags.length} repère${s.flags.length>1?'s':''}</summary><div>${s.groups.map((group,i)=>s.mode==='exam'&&group.part<5?'':`<button class="${i===s.index?'current':''} ${group.questions.every(q=>q.id in s.answers)?'answered':''} ${group.questions.some(q=>s.flags.includes(q.id))?'marked':''}" data-action="navigate" data-index="${i}" aria-label="Passage ${i+1}, partie ${group.part}">${i+1}${group.questions.some(q=>s.flags.includes(q.id))?' ⚑':''}</button>`).join('')}</div></details>`:''}`;
}

function result(){
 const s=state.session,r=s.result,accuracy=Math.round(r.correct/r.total*100);
 return `${heading('UNE SÉANCE DE PLUS VERS VOTRE OBJECTIF','Prenez un instant pour comprendre.',`${modeNames[s.mode]} · ${dateLabel(s.created)}`,`<a class="btn secondary" href="#dashboard">Retour à mon espace ${icon('arrow',17)}</a>`)}
 <section class="result-hero"><div class="result-ring" style="--value:${accuracy}%"><strong>${accuracy}<small>%</small></strong></div><div><h2>${r.correct} réponse${r.correct>1?'s':''} correcte${r.correct>1?'s':''} sur ${r.total}.</h2><p>${Object.keys(s.answers).length} question${Object.keys(s.answers).length>1?'s':''} répondue${Object.keys(s.answers).length>1?'s':''} · ${Math.round(r.seconds/60)} minutes de pratique active.</p><div class="result-sections">${Object.entries(r.sections).map(([name,v])=>`<span>${icon(name==='reading'?'book':'headphones',18)} ${name==='reading'?'Reading':'Listening'} <b>${v.correct}/${v.total}</b></span>`).join('')}</div></div></section><div class="note"><p>Ce résultat mesure votre réussite sur cette sélection. Il ne constitue pas une estimation officielle de score TOEIC. Les questions non répondues comptent dans le total ; seules les réponses enregistrées enrichissent les séances libres.</p></div>
 <div class="result-actions"><a class="btn primary" href="#errors">Comprendre mes erreurs ${icon('arrow',17)}</a><a class="btn secondary" href="#plan">Retrouver mon parcours</a></div><section class="section">${sectionHead('La correction complète')}<div class="result-corrections">${s.groups.map(g=>`<details class="card result-group"><summary><span>${tag('PART '+g.part,'muted')} ${esc(g.title)}</span><b>${g.questions.filter(q=>s.answers[q.id]?.choice===q.answer).length}/${g.questions.length} ${icon('chevron',16)}</b></summary><div class="result-group-content">${stimulus(g,true)}${g.questions.map(q=>`<div class="review-question"><h3 lang="en">${esc(q.stem)}</h3><p class="${s.answers[q.id]?.choice===q.answer?'text-green':'text-red'}">Votre réponse : ${esc(q.choices[s.answers[q.id]?.choice]||'Non répondue')}</p><p><b>Réponse correcte : ${esc(q.choices[q.answer])}</b></p><p>${esc(q.explanation)}</p><a href="#lesson/${q.skill}" class="text-link">Revoir ${esc(skillName(q.skill).toLowerCase())} ${icon('arrow',14)}</a></div>`).join('')}</div></details>`).join('')}</div></section>`;
}

function syncSidebarAccessibility(){
 const sidebar=$('.sidebar');if(!sidebar)return;
 const open=sidebar.classList.contains('open');
 sidebar.inert=matchMedia('(max-width: 760px)').matches&&!open;
 $('.mobile-menu')?.setAttribute('aria-expanded',String(open));
}
function render(){
 const [route,id]=state.route.split('/');
 const pages={dashboard,train:training,plan,lessons,lesson:()=>lesson(id),exams,cards,errors,stats,settings,lab,resources,session};
 shell((pages[route]||dashboard)());
 syncSidebarAccessibility();updateTimers();
}

async function loadRoute(){
 const version=++routeVersion;
 const route=location.hash.slice(1)||'dashboard';
 const [name,id]=route.split('/');
 const oldGroup=state.session?.groups[state.session.index]?.id;
 if(!route.startsWith('session/'))stopAudio();
 try{
  const requests=[api('/dashboard')];
  if(name==='session')requests.push(api('/sessions/'+encodeURIComponent(id)));
  if(['lesson','lessons'].includes(name))requests.push(api('/lessons'));
  if(name==='cards')requests.push(api('/cards'));
  if(name==='errors')requests.push(api('/errors'));
  if(name==='lab')requests.push(api('/drafts'));
  const data=await Promise.all(requests);
  if(version!==routeVersion)return;
  state.dashboard=data[0];state.route=route;
  if(name==='session') { state.session=data[1];state.offset=state.session.server_time*1000-Date.now();state.activeSeconds=0;state.selected={};state.confidence={}; }
  if(['lesson','lessons'].includes(name))state.lessons=data[1];
  if(name==='cards'){state.cards=data[1];state.cardFlipped=false;}
  if(name==='errors')state.errors=data[1];
  if(name==='lab')state.drafts=data[1];
  render();window.scrollTo({top:0,behavior:'instant'});$('h1')?.focus({preventScroll:true});
  if(name==='session'&&state.session.mode==='exam'&&state.session.status==='active'&&state.session.groups[state.session.index].part<5&&state.audioEnabled&&playingGroup!==state.session.groups[state.session.index].id)await playAudio(state.session.groups[state.session.index].id);
 }catch(err){if(!state.dashboard){$('#app').innerHTML=`<div class="boot"><h1>Le serveur ne répond pas.</h1><p>${esc(err.message)}</p><button class="btn primary" data-action="retry">Réessayer</button></div>`;}else notify(err.message,true);}
}

function updateTimers(){
 const s=state.session;
 if(!state.route.startsWith('session/')||!s||s.status!=='active')return;
 const now=(Date.now()+state.offset)/1000;
 const target=s.mode==='exam'&&now<s.listening_end?s.listening_end:s.deadline;
 const timer=$('#timer span');if(timer)timer.textContent=duration(target-now);
 if($('#timer'))$('#timer').classList.toggle('urgent',target-now<300);
 const slot=s.schedule?.[s.index];
 if($('#slot-timer')&&slot)$('#slot-timer').textContent=`Suite dans ${duration(slot.end-now)}.`;
 if((s.deadline&&now>=s.deadline)||(s.mode==='exam'&&slot&&now>=slot.end))syncTimedSession();
 if(player&&$('#audio-fill')){const ratio=player.duration?player.currentTime/player.duration*100:0;$('#audio-fill').style.width=ratio+'%';if($('#audio-time'))$('#audio-time').textContent=duration(player.currentTime);}
}
async function syncTimedSession(){
 if(pollBusy)return;pollBusy=true;
 try{const prev=state.session.groups[state.session.index]?.id;state.session=await api('/sessions/'+state.session.id);state.offset=state.session.server_time*1000-Date.now();const next=state.session.groups[state.session.index]?.id;
  if(prev!==next||state.session.status==='completed'){stopAudio();state.activeSeconds=0;state.selected={};render();window.scrollTo({top:0,behavior:'instant'});if(state.session.status==='active'&&state.session.groups[state.session.index].part<5&&state.audioEnabled)await playAudio(next);}
 }catch(err){notify(err.message,true);}finally{pollBusy=false;}
}

async function playAudio(id){
 const strict=state.session?.mode==='exam'&&state.session.status==='active';
 if(player&&playingGroup===id&&!player.paused){if(strict){notify('L’écoute continue pendant la section chronométrée.');return;}player.pause();render();return;}
 if(player&&playingGroup===id&&player.paused&&!strict&&player.currentTime<player.duration){await player.play();render();return;}
 const res=await api('/sessions/'+state.session.id+'/audio',{groupId:id});
 stopAudio();player=new Audio(res.url);playingGroup=id;
 const thisPlayer=player;
 player.preload='auto';
 player.addEventListener('loadedmetadata',()=>{if(thisPlayer!==player)return;player.currentTime=Math.min(res.offset,Math.max(0,player.duration-.05));});
 player.addEventListener('error',()=>notify('Cet audio n’a pas pu être chargé. Vérifiez les fichiers audio du projet.',true));
 player.addEventListener('ended',()=>{const b=$('.audio-play');if(b)b.innerHTML=icon('play',20);});
 try{await player.play();state.audioEnabled=true;const b=$('.audio-play');if(b)b.innerHTML=icon(strict?'volume':'pause',20);}catch{state.audioEnabled=false;notify('Cliquez sur Écouter pour autoriser la lecture audio dans ce navigateur.',true);}
}

async function start(mode,extra={}){
 stopAudio();
 const s=await api('/sessions',{mode,...extra});
 state.session=s;state.selected={};state.activeSeconds=0;
 goto('session/'+s.id);
}

async function saveChoices(){
 const s=state.session,g=s.groups[s.index];
 const pending=g.questions.filter(q=>state.selected[q.id]!==undefined&&q.answer===undefined);
 if(!pending.length){if(g.questions.every(q=>q.id in s.answers))return;throw new Error('Sélectionnez au moins une réponse avant de valider.');}
 const each=state.activeSeconds/pending.length;
 for(const q of pending){state.session=await api('/sessions/'+s.id+'/answer',{questionId:q.id,choice:state.selected[q.id],seconds:Math.min(each,1800),confidence:state.confidence[q.id]?'unsure':'sure'});}
 state.activeSeconds=0;render();
}
async function navigate(index){
 const s=state.session,g=s.groups[s.index];
 const pending=g.questions.some(q=>state.selected[q.id]!==undefined&&q.answer===undefined&&state.selected[q.id]!==s.answers[q.id]?.choice);
 if(pending)await saveChoices();
 stopAudio();state.session=await api('/sessions/'+s.id+'/navigate',{index});state.selected={};state.confidence={};state.activeSeconds=0;render();window.scrollTo({top:0,behavior:'instant'});$('h1')?.focus({preventScroll:true});
}

function showModal(content){const dialog=$('#modal');dialog.innerHTML=content;dialog.showModal();}
function closeModal(){$('#modal').close();}
function examInfo(mode){
 const full=mode==='exam';
 showModal(`<div class="modal-body"><span class="circle-icon sage">${icon(full?'headphones':'clock',26)}</span><h2>${modeNames[mode]}</h2><p>${full?'200 questions, 45 minutes d’écoute puis 75 minutes de lecture.':'reading-exam'===mode?'100 questions de Reading et 75 minutes.':'Un premier diagnostic de 30 minutes maximum, sans estimation officielle de score.'}</p><ul><li>Le chronomètre continue si vous quittez ou rechargez la page.</li><li>Les réponses sont sauvegardées au fur et à mesure.</li><li>Les corrections seront disponibles après la fin.</li>${full?'<li>L’écoute avance automatiquement. Vous ne pourrez pas revenir à un passage précédent.</li><li>Les photographies sont synthétiques et les voix artificielles. Les pauses sont adaptées à nos enregistrements.</li>':''}</ul>${full?button(`${icon('volume',18)} Tester mon son`,'test-sound','secondary full'):''}<div class="modal-actions">${button('Plus tard','close-modal','ghost')}${button('Commencer maintenant','begin-exam','primary',`data-mode="${mode}"`)}</div></div>`);
}

async function action(el){
 const a=el.dataset.action;
 if(a==='dismiss-toast'){$('#notifications').replaceChildren();return;}
 if(a==='retry')return loadRoute();
 if(a==='menu'){const open=$('.sidebar').classList.toggle('open');syncSidebarAccessibility();$(open?'.sidebar-close':'.mobile-menu')?.focus();return;}
 if(a==='close-modal'){closeModal();return;}
 if(a==='filter'){state.filter=el.dataset.filter;render();return;}
 if(a==='resume')return goto('session/'+el.dataset.id);
 if(a==='start')return start(el.dataset.mode,{...(el.dataset.part?{part:Number(el.dataset.part)}:{}),...(el.dataset.skill?{skill:el.dataset.skill}:{}),...(el.dataset.minutes?{minutes:Number(el.dataset.minutes)}:{})});
 if(a==='exam-info')return examInfo(el.dataset.mode);
 if(a==='programme-exam'){state.examSet=Number(el.dataset.set);return examInfo('exam');}
 if(a==='begin-exam'){if(el.dataset.mode==='exam'&&!state.audioEnabled)throw new Error('Testez le son avant de lancer les 45 minutes d’écoute.');closeModal();await start(el.dataset.mode,{examSet:state.examSet});return;}
 if(a==='test-sound'){stopAudio();player=new Audio('/audio/p2-001.wav');await player.play();state.audioEnabled=true;el.innerHTML=icon('check',17)+' Son activé';return;}
 if(a==='choose'){
  const id=el.dataset.qid,choice=Number(el.dataset.choice);state.selected[id]=choice;
  if(state.session.mode==='exam'||state.session.mode==='reading-exam'){
   state.session=await api('/sessions/'+state.session.id+'/answer',{questionId:id,choice,seconds:Math.min(state.activeSeconds,1800),confidence:state.confidence[id]?'unsure':'sure'});
   state.activeSeconds=0;delete state.selected[id];
  }
  render();$(`[data-qid="${id}"][data-choice="${choice}"]`)?.focus({preventScroll:true});return;
 }
 if(a==='validate')return saveChoices();
 if(a==='next')return navigate(state.session.index+1);
 if(a==='navigate')return navigate(Number(el.dataset.index));
 if(a==='flag'){state.session=await api('/sessions/'+state.session.id+'/flag',{questionId:el.dataset.id});render();return;}
 if(a==='play-audio')return playAudio(el.dataset.id);
 if(a==='enable-audio'){state.audioEnabled=true;await playAudio(state.session.groups[state.session.index].id);render();return;}
 if(a==='finish-info'){const s=state.session,n=s.groups.reduce((n,g)=>n+g.questions.length,0)-Object.keys(s.answers).length;showModal(`<div class="modal-body"><h2>Terminer cette séance ?</h2><p>${n?n+' question(s) ne sont pas encore enregistrées. Les choix sélectionnés sur cette page seront sauvegardés.':'Toutes vos réponses sont enregistrées.'} La correction sera ensuite disponible.</p><div class="modal-actions">${button('Continuer','close-modal','ghost')}${button('Terminer et voir la correction','finish','primary')}</div></div>`);return;}
 if(a==='finish'){const g=state.session.groups[state.session.index];if(g.questions.some(q=>state.selected[q.id]!==undefined&&q.answer===undefined))await saveChoices();stopAudio();state.session=await api('/sessions/'+state.session.id+'/finish',{});state.dashboard=await api('/dashboard');closeModal();render();window.scrollTo({top:0,behavior:'instant'});return;}
 if(a==='flip'){state.cardFlipped=!state.cardFlipped;render();return;}
 if(a==='rate-card'){await api('/cards/rate',{id:el.dataset.id,rating:el.dataset.rating});state.cards=await api('/cards');state.dashboard=await api('/dashboard');state.cardFlipped=false;render();return;}
 if(a==='complete-lesson'){await api('/lessons/complete',{id:el.dataset.id});state.dashboard=await api('/dashboard');notify('Cours marqué comme lu. Place à la pratique.');return;}
 if(a==='apply-daily'){const min=$('[name="dailyMinutes"]').value;for(let i=0;i<7;i++)$(`[name="day${i}"]`).value=min;return;}
 if(a==='export'){const data=await api('/export');const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download='toeic-990-progression-'+new Date().toISOString().slice(0,10)+'.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);notify('Vos données ont été exportées.');return;}
 if(a==='draft'){const reviewed=$('#reviewed-'+el.dataset.id)?.checked||false;await api('/drafts/'+el.dataset.id,{action:el.dataset.decision,reviewed});await loadRoute();notify(el.dataset.decision==='publish'?'Exercice ajouté à votre banque.':'Proposition écartée.');return;}
}

document.addEventListener('click',async e=>{
 if(e.target.closest('a.skip')){e.preventDefault();$('#main')?.focus();return;}
 const el=e.target.closest('[data-action]');if(!el||el.disabled)return;
 if(state.busy)return;
 state.busy=true;el.setAttribute('aria-busy','true');
 try{await action(el);}catch(err){notify(err.message,true);}finally{state.busy=false;el.removeAttribute('aria-busy');}
});
document.addEventListener('change',async e=>{
 if(e.target.dataset.confidence){
  const id=e.target.dataset.confidence;state.confidence[id]=e.target.checked;
  if(['exam','reading-exam'].includes(state.session?.mode)&&state.session.answers[id]){
   try{state.session=await api('/sessions/'+state.session.id+'/answer',{questionId:id,choice:state.session.answers[id].choice,seconds:0,confidence:e.target.checked?'unsure':'sure'});}
   catch(err){notify(err.message,true);}
  }
 }
 if(e.target.id==='audio-speed'&&player)player.playbackRate=Number(e.target.value);
 if(e.target.id==='exam-set')state.examSet=Number(e.target.value);
});
document.addEventListener('submit',async e=>{
 const form=e.target;if(!['settings-form','generate-form','import-form'].includes(form.id))return;
 e.preventDefault();if(state.busy)return;state.busy=true;
 const submit=form.querySelector('[type="submit"]');submit.disabled=true;
 const values=Object.fromEntries(new FormData(form));
 try{
  if(form.id==='settings-form'){
   const data={...values};for(const k of ['dailyMinutes','target','listening','reading'])data[k]=Number(values[k]);data.weekMinutes=Array.from({length:7},(_,i)=>Number(values['day'+i]));await api('/profile',data);state.dashboard=await api('/dashboard');$('#form-message').textContent='Préférences enregistrées.';notify('Votre rythme a été mis à jour.');
  }else if(form.id==='generate-form'){
   $('#generation-status').textContent=values.provider==='openai'?'Génération puis vérification indépendante en cours…':'Création et contrôle du gabarit…';
   await api('/generate',values);await loadRoute();notify('Brouillon prêt pour votre relecture.');
  }else{
   let question;try{question=JSON.parse(values.json);}catch{throw new Error('Le JSON n’est pas valide. Vérifiez les guillemets et les virgules.');}
   await api('/drafts/import',{question,rightsConfirmed:values.rights==='on'});await loadRoute();notify('Question importée en brouillon.');
  }
 }catch(err){notify(err.message,true);if($('#generation-status'))$('#generation-status').textContent=err.message;}
 finally{state.busy=false;submit.disabled=false;}
});
for(const event of ['pointerdown','keydown','scroll'])window.addEventListener(event,()=>state.lastActivity=Date.now(),{passive:true});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&$('.sidebar')?.classList.contains('open')){$('.sidebar').classList.remove('open');syncSidebarAccessibility();$('.mobile-menu')?.focus();}});
window.addEventListener('resize',syncSidebarAccessibility);
window.addEventListener('hashchange',loadRoute);
window.addEventListener('online',()=>notify('Connexion rétablie.'));
window.addEventListener('pagehide',stopAudio);
setInterval(()=>{if(state.route.startsWith('session/')&&state.session?.status==='active'&&!document.hidden&&(Date.now()-state.lastActivity<90000||player&&!player.paused))state.activeSeconds++;updateTimers();},1000);
loadRoute();
