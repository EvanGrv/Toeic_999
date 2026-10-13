#!/usr/bin/env python3
"""Local single-user application. Python 3.10+, standard library only."""
from collections import Counter
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import copy
import json
import mimetypes
import os
from pathlib import Path
import sqlite3
import threading
import time
import traceback
from urllib.parse import urlparse, unquote
import uuid
from zoneinfo import ZoneInfo

from server.content import GROUPS, PARTS, SKILLS, LESSONS, FLASHCARDS
from server.engine import allocation, mastery, challenge_ready, select_groups, schedule_review, validate_question
from server.generation import generate

ROOT = Path(__file__).resolve().parents[1]
DB = Path(os.environ.get('TOEIC_DB', ROOT / 'data' / 'toeic.sqlite3'))
LOCK = threading.RLock()
TZ = ZoneInfo('Europe/Paris')
DEFAULT_PROFILE = {'name':'Evan','listening':405,'reading':310,'target':900,'finalTarget':990,
    'examDate':'','dailyMinutes':120,'intensity':'intensive','preference':'balanced',
    'accent':'mixed','weekMinutes':[120,120,120,120,120,120,120]}

class APIError(Exception):
    def __init__(self, message, status=400):
        self.message, self.status = message, status

def connect():
    db = sqlite3.connect(DB, timeout=10)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    return db

def init_db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    with connect() as db:
        db.executescript('''
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS sessions (id TEXT PRIMARY KEY, mode TEXT NOT NULL, created REAL NOT NULL, status TEXT NOT NULL, data TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS attempts (id INTEGER PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id), question_id TEXT NOT NULL, part INTEGER NOT NULL, skill TEXT NOT NULL, level TEXT NOT NULL, correct INTEGER NOT NULL, choice INTEGER, seconds REAL NOT NULL, confidence TEXT NOT NULL, created REAL NOT NULL, UNIQUE(session_id,question_id));
        CREATE TABLE IF NOT EXISTS reviews (id TEXT PRIMARY KEY, kind TEXT NOT NULL, data TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS drafts (id TEXT PRIMARY KEY, data TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS lesson_progress (id TEXT PRIMARY KEY, completed REAL NOT NULL);
        ''')
        db.execute('INSERT OR IGNORE INTO settings VALUES (?,?)', ('profile',json.dumps(DEFAULT_PROFILE)))

def profile(db):
    return {**DEFAULT_PROFILE, **json.loads(db.execute("SELECT value FROM settings WHERE key='profile'").fetchone()[0])}

def attempts(db):
    return [dict(r) for r in db.execute('SELECT * FROM attempts ORDER BY created,id')]

def bank(db):
    result = list(GROUPS)
    for row in db.execute('SELECT data FROM drafts'):
        group = json.loads(row[0])
        if group['status'] == 'published':
            result.append(group)
    return result

def review_rows(db, kind=None):
    return {r['id']:json.loads(r['data']) for r in db.execute('SELECT * FROM reviews') if not kind or r['kind']==kind}

def get_session(db, id):
    row = db.execute('SELECT * FROM sessions WHERE id=?',(id,)).fetchone()
    if not row:
        raise APIError('Séance introuvable.',404)
    result = json.loads(row['data'])
    result.update(id=row['id'],mode=row['mode'],created=row['created'],status=row['status'])
    return result

def save_session(db, s):
    db.execute('UPDATE sessions SET status=?,data=? WHERE id=?', (s['status'],json.dumps(s,ensure_ascii=False),s['id']))

def record(db, s, group, item, answer):
    if db.execute('SELECT 1 FROM attempts WHERE session_id=? AND question_id=?',(s['id'],item['id'])).fetchone():
        return
    correct = answer.get('choice') == item['answer']
    db.execute('INSERT INTO attempts(session_id,question_id,part,skill,level,correct,choice,seconds,confidence,created) VALUES(?,?,?,?,?,?,?,?,?,?)',
        (s['id'],item['id'],group['part'],item['skill'],item['level'],int(correct),answer.get('choice'),answer.get('seconds',0),answer.get('confidence','sure'),time.time()))
    review_row = db.execute("SELECT data FROM reviews WHERE id=? AND kind='question'",(item['id'],)).fetchone()
    previous = json.loads(review_row[0]) if review_row else {}
    if not correct or previous or answer.get('confidence') == 'unsure':
        review = schedule_review(previous, 'good' if correct and answer.get('confidence') != 'unsure' else 'again')
        review.update(question_id=item['id'],group_id=group['id'],last_correct=bool(correct),mistake=answer.get('choice'))
        db.execute('INSERT OR REPLACE INTO reviews VALUES(?,?,?)',(item['id'],'question',json.dumps(review)))

def finish(db, s):
    if s['status'] == 'completed':
        return
    if s['mode'] in ('exam','reading-exam','diagnostic'):
        for g in s['groups']:
            for item in g['questions']:
                record(db,s,g,item,s['answers'].get(item['id'],{}))
    s['status'], s['finished'] = 'completed', time.time()
    save_session(db,s)

def sync_session(db, s):
    now = time.time()
    if s['status'] != 'active':
        return s
    if s.get('deadline') and now >= s['deadline']:
        finish(db,s)
    elif s['mode'] == 'exam':
        if now < s['listening_end']:
            s['index'] = next((i for i, slot in enumerate(s['schedule']) if now < slot['end']), len(s['schedule'])-1)
        elif s['index'] < len(s['schedule']):
            s['index'] = len(s['schedule'])
        save_session(db,s)
    return s

def public_session(s):
    result = copy.deepcopy(s)
    reveal_all = s['status'] == 'completed'
    immediate = s['mode'] not in ('exam','reading-exam','diagnostic')
    for group in result['groups']:
        all_done = all(q['id'] in s['answers'] for q in group['questions'])
        if not reveal_all and not (immediate and all_done):
            group.pop('transcript',None)
            group.pop('dialogue',None)
        for item in group['questions']:
            visible = reveal_all or (immediate and item['id'] in s['answers'])
            if not visible:
                item.pop('answer',None)
                item.pop('explanation',None)
                if group['part'] <= 2:
                    if group['part'] == 2:
                        item['stem'] = 'Écoutez la question et choisissez la meilleure réponse.'
                    item['choices'] = ['Réponse '+x for x in 'ABCD'[:len(item['choices'])]]
    result['server_time'] = time.time()
    if reveal_all:
        result['result'] = session_result(s)
    return result

def session_result(s):
    sections = {}
    for section in ('reading','listening'):
        items = [q for g in s['groups'] if (g['part'] >= 5) == (section=='reading') for q in g['questions']]
        if items:
            correct = sum(s['answers'].get(q['id'],{}).get('choice') == q['answer'] for q in items)
            answered = sum(q['id'] in s['answers'] for q in items)
            sections[section] = {'total':len(items),'correct':correct,'answered':answered,'accuracy':round(correct/len(items)*100)}
    return {'sections':sections,'total':sum(x['total'] for x in sections.values()),'correct':sum(x['correct'] for x in sections.values()),
            'seconds':sum(a.get('seconds',0) for a in s['answers'].values())}

def dashboard(db):
    for row in db.execute("SELECT id FROM sessions WHERE status='active'").fetchall():
        sync_session(db,get_session(db,row['id']))
    rows = attempts(db)
    p = profile(db)
    now = datetime.now(TZ)
    today = now.date()
    days = []
    for n in range(13,-1,-1):
        day = today-timedelta(days=n)
        day_rows = [a for a in rows if datetime.fromtimestamp(a['created'],TZ).date()==day]
        days.append({'date':day.isoformat(),'count':len(day_rows),'minutes':round(sum(a['seconds'] for a in day_rows)/60,1),
                     'accuracy':round(sum(a['correct'] for a in day_rows)/len(day_rows)*100) if day_rows else None})
    practiced = {datetime.fromtimestamp(a['created'],TZ).date() for a in rows}
    cursor = today if today in practiced else today-timedelta(days=1)
    streak = 0
    while cursor in practiced:
        streak += 1
        cursor -= timedelta(days=1)
    skill_data = mastery(rows)
    reviews = review_rows(db)
    sessions = [get_session(db,r['id']) for r in db.execute('SELECT id FROM sessions ORDER BY created DESC LIMIT 12')]
    completed_sets = {json.loads(r[0]).get('exam_set') for r in db.execute("SELECT data FROM sessions WHERE status='completed' AND mode='exam'")}
    inventory = bank(db)
    seen_ids = {a['question_id'] for a in rows}
    exam_seen = {i:len(seen_ids & {q['id'] for g in inventory if g.get('exam_set')==i for q in g['questions']}) for i in range(1,9)}
    return {'profile':p,'allocation':allocation(rows),'skills':list(skill_data.values()),'challengeReady':challenge_ready(rows),
        'stats':{'answered':len(rows),'unique':len({a['question_id'] for a in rows}),
                 'accuracy':round(sum(a['correct'] for a in rows)/len(rows)*100) if rows else None,
                 'minutes':round(sum(a['seconds'] for a in rows)/60),'streak':streak},
        'today':days[-1],'dailyGoal':p['weekMinutes'][today.weekday()], 'days':days,
        'dueQuestions':sum(r.get('due',0)<=time.time() for r in review_rows(db,'question').values()),
        'dueCards':sum(reviews.get(f'card-{i}',{}).get('due',0)<=time.time() for i in range(len(FLASHCARDS))),
        'parts':[{'part':n,'name':name,'count':sum(len(g['questions']) for g in inventory if g['part']==n),
                  'attempts':sum(a['part']==n for a in rows),'accuracy':round(sum(a['correct'] for a in rows if a['part']==n)/sum(a['part']==n for a in rows)*100) if any(a['part']==n for a in rows) else None} for n,name in PARTS.items()],
        'sessions':[{'id':s['id'],'mode':s['mode'],'created':s['created'],'status':s['status'],'count':sum(len(g['questions']) for g in s['groups']),
                     'answered':len(s['answers']),'result':session_result(s) if s['status']=='completed' else None} for s in sessions],
        'lessonsDone':[r[0] for r in db.execute('SELECT id FROM lesson_progress')],
        'bankCount':sum(len(g['questions']) for g in inventory),'cardCount':len(FLASHCARDS),
        'originalCount':sum(len(g['questions']) for g in inventory if not g.get('variant') and g.get('origin')!='generated'),
        'variantCount':sum(len(g['questions']) for g in inventory if g.get('variant')),
        'examSets':[{'id':i,'name':f'Série {i:02}', 'kind':'Banque initiale' if i==1 else 'Variantes contrôlées',
                     'completed':i in completed_sets,
                     'seen':exam_seen[i]} for i in range(1,9)],
        'aiConfigured':bool(os.environ.get('OPENAI_API_KEY'))}

def start_session(db, body):
    mode = body.get('mode','daily')
    if mode not in ('daily','practice','diagnostic','exam','reading-exam','review','challenge'):
        raise APIError('Mode inconnu.')
    part = body.get('part')
    skill = body.get('skill')
    if part is not None and (type(part) is not int or part not in PARTS):
        raise APIError('Partie invalide.')
    if skill and skill not in SKILLS:
        raise APIError('Compétence inconnue.')
    rows = attempts(db)
    if mode == 'challenge' and not challenge_ready(rows):
        raise APIError('Le défi avancé se débloque après 40 questions B2/C1 distinctes avec au moins 85 % de réussite.')
    # An active timed exam must be resumed or explicitly finished; creating one cannot silently erase it.
    if mode in ('exam','reading-exam'):
        for r in db.execute("SELECT id FROM sessions WHERE status='active' AND mode IN ('exam','reading-exam')"):
            current = sync_session(db,get_session(db,r['id']))
            if current['status'] == 'active':
                raise APIError('Un examen est déjà en cours. Reprenez-le depuis le tableau de bord.',409)
    p = profile(db)
    budget = p['weekMinutes'][datetime.now(TZ).weekday()]
    minutes = max(10,min(60,budget * {'gentle':.8,'balanced':1,'intensive':1.2}[p['intensity']]))
    if 'minutes' in body:
        if type(body['minutes']) is not int or not 10<=body['minutes']<=60:
            raise APIError('Une séance doit durer entre 10 et 60 minutes.')
        minutes=body['minutes']
    due = [id for id,r in review_rows(db,'question').items() if r['due']<=time.time()]
    exam_set=body.get('examSet',1)
    if type(exam_set) is not int or exam_set not in range(1,9):
        raise APIError('Série d’examen invalide.')
    groups = select_groups(bank(db),rows,mode,part,skill,minutes=minutes,seed=str(uuid.uuid4()),due_ids=due,preferred=p['preference'],exam_set=exam_set,accent=p['accent'])
    if not groups:
        raise APIError('Aucune question disponible pour ce choix. Les révisions reviendront à leur échéance.')
    now = time.time()
    s = {'id':str(uuid.uuid4()),'mode':mode,'created':now,'status':'active','groups':groups,
         'answers':{},'index':0,'flags':[],'audio_started':{},'accentPreference':p['accent'],'exam_set':exam_set if mode in ('exam','reading-exam') else None}
    if mode == 'exam':
        s['listening_end'],s['deadline'] = now+2700, now+7200
        manifest_path = ROOT/'public/audio/manifest.json'
        manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
        listening = [g for g in groups if g['part']<5]
        if any(g['id'] not in manifest for g in listening) or not (ROOT/'public/images/workplace-atlas.png').exists():
            raise APIError('Les médias de l’examen doivent être installés avant de commencer.',409)
        durations = [manifest[g['id']]+(6 if g['part']<=2 else 18) for g in listening]
        total = sum(durations)
        if total > 2700:
            raise APIError('Les audios dépassent les 45 minutes autorisées. Régénérez les médias.',409)
        padding = (2700-total)/len(durations)
        cursor = now
        s['schedule'] = []
        for g,duration in zip(listening,durations):
            end = cursor+duration+padding
            s['schedule'].append({'group_id':g['id'],'start':cursor,'end':end,'audio_seconds':manifest[g['id']]})
            cursor = end
        s['schedule'][-1]['end'] = now+2700
    elif mode == 'reading-exam':
        s['deadline'] = now+4500
    elif mode == 'diagnostic':
        s['deadline'] = now+1800
    db.execute('INSERT INTO sessions VALUES(?,?,?,?,?)',(s['id'],mode,now,'active',json.dumps(s,ensure_ascii=False)))
    return public_session(s)

def update_profile(db, body):
    p = profile(db)
    if not isinstance(body.get('name'),str) or not 1<=len(body['name'].strip())<=40:
        raise APIError('Le prénom doit contenir de 1 à 40 caractères.')
    for key,low,high in [('dailyMinutes',30,180),('target',10,990),('listening',5,495),('reading',5,495)]:
        if type(body.get(key)) is not int or not low<=body[key]<=high:
            raise APIError(f'Valeur invalide : {key}.')
        if key != 'dailyMinutes' and body[key]%5:
            raise APIError('Les scores doivent être des multiples de 5.')
    if body.get('intensity') not in ('gentle','balanced','intensive') or body.get('preference') not in ('balanced','reading','listening') or body.get('accent') not in ('mixed','US','UK','AU'):
        raise APIError('Préférence invalide.')
    exam_date = body.get('examDate','')
    if exam_date:
        try:
            date.fromisoformat(exam_date)
        except (ValueError,TypeError):
            raise APIError('Date d’examen invalide.') from None
    week = body.get('weekMinutes')
    if not isinstance(week,list) or len(week)!=7 or any(type(x) is not int or x<0 or x>180 for x in week):
        raise APIError('Indiquez sept durées de 0 à 180 minutes.')
    for key in DEFAULT_PROFILE:
        if key in body and key!='finalTarget':
            p[key]=body[key]
    p['name']=p['name'].strip()
    db.execute('UPDATE settings SET value=? WHERE key=?',(json.dumps(p,ensure_ascii=False),'profile'))
    return p

def submit_answer(db,s,body):
    if s['status'] != 'active':
        raise APIError('Cette séance est terminée.',409)
    id,choice = body.get('questionId'),body.get('choice')
    match = next(((g,q) for g in s['groups'] for q in g['questions'] if q['id']==id),None)
    if not match:
        raise APIError('Question absente de cette séance.')
    group,item = match
    if type(choice) is not int or choice not in range(len(item['choices'])):
        raise APIError('Choix invalide.')
    immediate = s['mode'] not in ('exam','reading-exam','diagnostic')
    if immediate and id in s['answers']:
        return public_session(s)  # Idempotent double-click and network retry.
    if s['mode']=='exam':
        if time.time() < s['listening_end']:
            if group['id'] != s['groups'][s['index']]['id']:
                raise APIError('Seul le passage oral en cours est accessible.',409)
        elif group['part']<5:
            raise APIError('La section Listening est terminée.',409)
    seconds = body.get('seconds',0)
    if type(seconds) not in (int,float) or not 0<=seconds<=1800:
        raise APIError('Durée invalide.')
    confidence = body.get('confidence','sure')
    if confidence not in ('sure','unsure'):
        raise APIError('Confiance invalide.')
    answer = {'choice':choice,'seconds':round(seconds+s['answers'].get(id,{}).get('seconds',0),1),'confidence':confidence}
    s['answers'][id]=answer
    if immediate:
        record(db,s,group,item,answer)
    save_session(db,s)
    return public_session(s)

def api(db, method, path, body):
    if method=='GET' and path=='/api/dashboard':
        return dashboard(db)
    if method=='GET' and path=='/api/lessons':
        return LESSONS
    if method=='GET' and path=='/api/cards':
        review = review_rows(db,'card')
        return [{'id':f'card-{i}','front':f,'back':b,'example':ex,'skill':sk,
                 'due':review.get(f'card-{i}',{}).get('due',0), 'interval':review.get(f'card-{i}',{}).get('interval',0)} for i,(f,b,ex,sk) in enumerate(FLASHCARDS)]
    if method=='GET' and path=='/api/errors':
        lookup = {q['id']:(g,q) for g in bank(db) for q in g['questions']}
        return [{**r,'question':lookup[id][1],'title':lookup[id][0]['title'],'part':lookup[id][0]['part']} for id,r in review_rows(db,'question').items() if id in lookup]
    if method=='GET' and path=='/api/drafts':
        return [json.loads(r[0]) for r in db.execute('SELECT data FROM drafts ORDER BY rowid DESC')]
    if method=='GET' and path=='/api/export':
        return {'version':1,'exportedAt':datetime.now(TZ).isoformat(),'profile':profile(db),
                'attempts':attempts(db),'reviews':review_rows(db),
                'sessions':[get_session(db,r[0]) for r in db.execute('SELECT id FROM sessions')],
                'lessonsDone':[r[0] for r in db.execute('SELECT id FROM lesson_progress')],
                'drafts':[json.loads(r[0]) for r in db.execute('SELECT data FROM drafts')]}
    if method=='POST' and path=='/api/profile':
        return update_profile(db,body)
    if method=='POST' and path=='/api/sessions':
        return start_session(db,body)
    if path.startswith('/api/sessions/'):
        parts = path.split('/')
        s = sync_session(db,get_session(db,parts[3]))
        if method=='GET' and len(parts)==4:
            return public_session(s)
        action = parts[4] if len(parts)>4 else ''
        if method=='POST' and action=='answer':
            if s['status']=='completed':
                return public_session(s)
            return submit_answer(db,s,body)
        if method=='POST' and action=='finish':
            finish(db,s)
            return public_session(s)
        if method=='POST' and action=='navigate':
            if s['status']!='active':
                return public_session(s)
            index = body.get('index')
            if type(index) is not int or index not in range(len(s['groups'])):
                raise APIError('Position invalide.')
            if s['mode']=='exam' and (time.time()<s['listening_end'] or s['groups'][index]['part']<5):
                raise APIError('La navigation Listening est pilotée par le chronomètre.',409)
            s['index']=index
            save_session(db,s)
            return public_session(s)
        if method=='POST' and action=='flag':
            id=body.get('questionId')
            if not any(q['id']==id for g in s['groups'] for q in g['questions']):
                raise APIError('Question inconnue.')
            s['flags'] = [x for x in s['flags'] if x!=id] if id in s['flags'] else s['flags']+[id]
            save_session(db,s)
            return public_session(s)
        if method=='POST' and action=='audio':
            group_id=body.get('groupId')
            g=next((g for g in s['groups'] if g['id']==group_id),None)
            if not g or g['part']>4:
                raise APIError('Audio indisponible.')
            if s['status']!='active':
                return {'offset':0,'url':f'/audio/{group_id}.wav'}
            offset=0
            if s['mode']=='exam':
                if s['groups'][s['index']]['id']!=group_id or time.time()>=s['listening_end']:
                    raise APIError('Cet audio ne fait pas partie du passage en cours.',409)
                slot=s['schedule'][s['index']]
                offset=max(0,time.time()-slot['start'])
                if offset >= slot['audio_seconds']:
                    raise APIError('L’écoute de ce passage est terminée.',409)
            s['audio_started'][group_id]=time.time()
            save_session(db,s)
            return {'offset':offset,'url':f'/audio/{group_id}.wav'}
    if method=='POST' and path=='/api/cards/rate':
        id,rating=body.get('id'),body.get('rating')
        if id not in {f'card-{i}' for i in range(len(FLASHCARDS))} or rating not in ('again','good','easy'):
            raise APIError('Carte ou évaluation invalide.')
        previous=review_rows(db,'card').get(id,{})
        if previous.get('due',0)>time.time():
            return previous
        result=schedule_review(previous,rating)
        db.execute('INSERT OR REPLACE INTO reviews VALUES(?,?,?)',(id,'card',json.dumps(result)))
        return result
    if method=='POST' and path=='/api/lessons/complete':
        id=body.get('id')
        if id not in SKILLS:
            raise APIError('Cours inconnu.')
        db.execute('INSERT OR REPLACE INTO lesson_progress VALUES(?,?)',(id,time.time()))
        return {'saved':True}
    if method=='POST' and path=='/api/drafts/import':
        item=body.get('question')
        if body.get('rightsConfirmed') is not True:
            raise APIError('Confirmez que le contenu est original ou réutilisable avec autorisation.')
        existing={q['stem'].casefold() for g in bank(db) for q in g['questions']}
        errors=validate_question(item,existing)
        if errors:
            raise APIError(' / '.join(errors))
        return save_draft(db,item,'import',{'type':'structural','passed':True,'note':'Import déclaré autorisé. Le contrôle automatique ne garantit pas la justesse pédagogique.'})
    if method=='POST' and path.startswith('/api/drafts/'):
        id=path.split('/')[3]
        row=db.execute('SELECT data FROM drafts WHERE id=?',(id,)).fetchone()
        if not row:
            raise APIError('Brouillon introuvable.',404)
        draft=json.loads(row[0])
        if body.get('action')=='publish' and body.get('reviewed') is True:
            if draft['status']=='published':
                return draft
            existing={q['stem'].casefold() for g in bank(db) for q in g['questions']}
            errors=validate_question(draft['questions'][0],existing)
            if errors:
                raise APIError(' / '.join(errors))
            draft['status']='published'
            draft['reviewedAt']=time.time()
        elif body.get('action')=='reject':
            draft['status']='rejected'
        else:
            raise APIError('Relecture requise avant publication.')
        db.execute('UPDATE drafts SET data=? WHERE id=?',(json.dumps(draft,ensure_ascii=False),id))
        return draft
    raise APIError('Route introuvable.',404)

def save_draft(db,item,provider,review):
    id='generated-'+uuid.uuid4().hex[:12]
    item={**item,'id':id+'-q1'}
    draft={'id':id,'part':5,'title':SKILLS[item['skill']],'questions':[item],'documents':[],
           'status':'draft','origin':'generated','source':provider,'review':review,'created':time.time()}
    db.execute('INSERT INTO drafts VALUES(?,?)',(id,json.dumps(draft,ensure_ascii=False)))
    return draft

class Handler(BaseHTTPRequestHandler):
    server_version='TOEIC990/1.0'
    def log_message(self, fmt, *args):
        if not args or '200' not in str(args):
            super().log_message(fmt,*args)

    def send_json(self, value, status=200):
        data=json.dumps(value,ensure_ascii=False,allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(data)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.end_headers()
        self.wfile.write(data)

    def dispatch(self,method):
        try:
            host=self.headers.get('Host','')
            if host not in (f'localhost:{self.server.server_port}',f'127.0.0.1:{self.server.server_port}',f'[::1]:{self.server.server_port}'):
                raise APIError('Hôte non autorisé.',403)
            path=unquote(urlparse(self.path).path)
            if not path.startswith('/api/'):
                if method!='GET':
                    raise APIError('Méthode non autorisée.',405)
                return self.static(path)
            body={}
            if method=='POST':
                origin=self.headers.get('Origin')
                if self.headers.get('X-TOEIC-Client')!='1' or (origin and origin not in ('http://'+host,'https://'+host)):
                    raise APIError('Origine non autorisée.',403)
                if self.headers.get('Content-Type','').split(';')[0]!='application/json':
                    raise APIError('Le contenu doit être JSON.',415)
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=1_000_000:
                    raise APIError('Requête vide ou trop volumineuse.',413)
                try:
                    body=json.loads(self.rfile.read(length))
                except (UnicodeDecodeError,json.JSONDecodeError):
                    raise APIError('JSON invalide.') from None
                if not isinstance(body,dict):
                    raise APIError('Un objet JSON est requis.')
            if method=='POST' and path=='/api/generate':
                skill=body.get('skill','word-forms')
                level=body.get('level','B2')
                if skill not in SKILLS or level not in ('B1','B2','C1','C2'):
                    raise APIError('Compétence ou niveau invalide.')
                with LOCK,connect() as db:
                    existing={q['stem'].casefold() for g in bank(db) for q in g['questions']}
                    existing.update(json.loads(r[0])['questions'][0]['stem'].casefold() for r in db.execute('SELECT data FROM drafts'))
                item,review=generate(body.get('provider','local'),level,skill,existing)
                with LOCK,connect() as db:
                    result=save_draft(db,item,body.get('provider','local'),review)
                return self.send_json(result)
            with LOCK,connect() as db:
                result=api(db,method,path,body)
            self.send_json(result)
        except APIError as e:
            self.send_json({'error':e.message},e.status)
        except ValueError as e:
            self.send_json({'error':str(e)},400)
        except (BrokenPipeError,ConnectionResetError):
            pass
        except Exception:
            traceback.print_exc()
            self.send_json({'error':'Erreur interne. Vos réponses déjà enregistrées sont conservées.'},500)

    def static(self,path):
        if path in ('/','/index.html'):
            file=ROOT/'app/index.html'
        elif path.startswith('/app/'):
            file=(ROOT/path.lstrip('/')).resolve()
            if not file.is_relative_to(ROOT/'app'):
                raise APIError('Accès refusé.',403)
        elif path.startswith('/docs/'):
            file=(ROOT/path.lstrip('/')).resolve()
            if not file.is_relative_to(ROOT/'docs') or file.suffix!='.md':
                raise APIError('Accès refusé.',403)
        else:
            file=(ROOT/'public'/path.lstrip('/')).resolve()
            if not file.is_relative_to(ROOT/'public'):
                raise APIError('Accès refusé.',403)
        if not file.is_file():
            raise APIError('Fichier introuvable.',404)
        size=file.stat().st_size
        start,end=0,size-1
        range_header=self.headers.get('Range','')
        partial=False
        if range_header.startswith('bytes=') and ',' not in range_header:
            try:
                left,right=range_header[6:].split('-',1)
                if left:
                    start=int(left)
                    end=min(int(right),size-1) if right else size-1
                else:
                    start=max(0,size-int(right))
                if start<0 or start>end or start>=size:
                    raise ValueError
                partial=True
            except ValueError:
                self.send_response(416)
                self.send_header('Content-Range',f'bytes */{size}')
                self.end_headers()
                return
        self.send_response(206 if partial else 200)
        mime=mimetypes.guess_type(str(file))[0] or 'application/octet-stream'
        if file.suffix=='.js':
            mime='text/javascript'
        self.send_header('Content-Type',mime+('; charset=utf-8' if mime.startswith('text/') else ''))
        self.send_header('Content-Length',str(end-start+1))
        self.send_header('Accept-Ranges','bytes')
        if partial:
            self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','same-origin')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; media-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'self'")
        self.end_headers()
        with file.open('rb') as f:
            f.seek(start)
            remaining=end-start+1
            while remaining:
                chunk=f.read(min(65536,remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining-=len(chunk)

    def do_GET(self): self.dispatch('GET')
    def do_POST(self): self.dispatch('POST')

def main():
    init_db()
    port=int(os.environ.get('PORT','8787'))
    server=ThreadingHTTPServer(('127.0.0.1',port),Handler)
    print(f'TOEIC 990+ AI ready at http://localhost:{port} — database: {DB}',flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()

if __name__=='__main__': main()
