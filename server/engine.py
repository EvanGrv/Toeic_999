"""Explainable learning decisions; these are teaching heuristics, not calibrated scores."""
from collections import defaultdict
from datetime import datetime, timedelta, timezone
import random

from server.content import SKILLS

LEVELS = {'B1': 1, 'B2': 2, 'C1': 3, 'C2': 4}

def evidence(attempts):
    latest = {}
    for a in sorted(attempts, key=lambda a: a['created']):
        latest[a['question_id']] = a
    return list(latest.values())

def mastery(attempts):
    unique = evidence(attempts)
    result = {}
    for skill in SKILLS:
        rows = [a for a in unique if a['skill'] == skill]
        # Beta(2,2) smoothing prevents one lucky answer from implying mastery.
        n, correct = len(rows), sum(a['correct'] for a in rows)
        result[skill] = {'id': skill, 'name': SKILLS[skill], 'n': n,
                         'correct': correct, 'mastery': round((correct+2)/(n+4)*100),
                         'accuracy': round(correct/n*100) if n else None,
                         'confidence': 'Consolidée' if n >= 15 else 'À confirmer' if n >= 5 else 'Peu de données',
                         'average_seconds': round(sum(a['seconds'] for a in rows)/n) if n else 0}
    return result

def allocation(attempts):
    rows = evidence(attempts)
    reading = [a for a in rows if a['part'] >= 5]
    listening = [a for a in rows if a['part'] < 5]
    if len(reading) < 30 or len(listening) < 20:
        return {'reading': 65, 'listening': 35, 'adaptive': False,
                'reason': f'Priorité au Reading à partir de votre score officiel. Calibration : {min(len(reading),30)}/30 réponses Reading et {min(len(listening),20)}/20 Listening distinctes.'}
    r_error = (len(reading)-sum(a['correct'] for a in reading)+2)/(len(reading)+4)
    l_error = (len(listening)-sum(a['correct'] for a in listening)+2)/(len(listening)+4)
    r_share = round(max(.35, min(.8, .5 + .5*(r_error-l_error))) * 100)
    return {'reading': r_share, 'listening': 100-r_share, 'adaptive': True,
            'reason': 'Répartition recalculée à partir des erreurs sur les questions distinctes. Chaque section conserve au moins 20 % de pratique.'}

def challenge_ready(attempts):
    rows = evidence(attempts)
    advanced = [a for a in rows if a['level'] in ('B2','C1')]
    return len(advanced) >= 40 and sum(a['correct'] for a in advanced)/len(advanced) >= .85

def select_groups(bank, attempts, mode='daily', part=None, skill=None, minutes=30, seed=None, due_ids=(), preferred='balanced', exam_set=1, accent='mixed'):
    rng = random.Random(seed)
    seen = {a['question_id'] for a in attempts}
    scores = mastery(attempts)
    candidates = [g for g in bank if g['status'] == 'published']
    if part:
        candidates = [g for g in candidates if g['part'] == part]
    if skill:
        candidates = [g for g in candidates if any(q['skill'] == skill for q in g['questions'])]
    if mode == 'review':
        candidates = [g for g in candidates if any(q['id'] in due_ids for q in g['questions'])]
    if mode == 'challenge':
        candidates = [g for g in candidates if any(q['level'] in ('C1','C2') for q in g['questions'])]
    else:
        candidates = [g for g in candidates if all(q['level'] != 'C2' for q in g['questions'])]
    if mode in ('exam', 'reading-exam'):
        candidates = [g for g in candidates if g.get('exam_set') == exam_set or g['part'] == 1]
        # Select whole passages; never split a conversation or combine its questions with another stimulus.
        result = []
        counts = {1:6, 2:25, 3:13, 4:10, 5:30, 6:4}
        for p, count in counts.items():
            if mode == 'reading-exam' and p < 5:
                continue
            pool = [g for g in candidates if g['part'] == p and g.get('origin') != 'generated']
            rng.shuffle(pool)
            if len(pool) < count:
                raise ValueError(f'Banque insuffisante pour la partie {p}.')
            result.extend(pool[:count])
        singles = [g for g in candidates if g.get('passage_type') == 'single']
        multiples = [g for g in candidates if g.get('passage_type') in ('double','triple')]
        # The original seed has precisely 10 single passages / 29 questions and 5 multiple sets / 25.
        singles = [g for g in singles if g.get('origin') != 'generated']
        multiples = [g for g in multiples if g.get('origin') != 'generated']
        rng.shuffle(singles)
        rng.shuffle(multiples)
        if sum(len(g['questions']) for g in singles) != 29 or sum(len(g['questions']) for g in multiples) != 25:
            raise ValueError('Structure de la partie 7 invalide.')
        return result + singles + multiples
    if accent != 'mixed':
        candidates = [g for g in candidates if g['part']>=5 or g.get('accent') == accent]
    target = 20 if mode == 'diagnostic' else max(5, min(70, round(minutes*.65)))
    if mode == 'challenge':
        target = 10
    def priority(g):
        novelty = sum(q['id'] not in seen for q in g['questions']) / len(g['questions'])
        weakness = 1-sum(scores[q['skill']]['mastery'] for q in g['questions']) / (100*len(g['questions']))
        level_gap = 0
        for item in g['questions']:
            score = scores[item['skill']]
            target_level = (1 if g['part'] >= 5 else 2) if score['n'] < 5 else (1 if score['accuracy'] < 65 else 2 if score['accuracy'] < 85 else 3)
            level_gap += abs(LEVELS[item['level']] - target_level)
        level_gap /= len(g['questions'])
        preferred_bonus = .15 if (preferred == 'reading' and g['part'] >= 5) or (preferred == 'listening' and g['part'] < 5) else 0
        return novelty * 2 + weakness - level_gap*.45 + preferred_bonus + rng.random()*.4
    candidates.sort(key=priority, reverse=True)
    ratio = allocation(attempts)['reading']/100
    chosen, r_count, l_count = [], 0, 0
    while candidates and r_count + l_count < target:
        need_reading = r_count < round(target*ratio)
        index = next((i for i,g in enumerate(candidates) if (g['part'] >= 5) == need_reading), 0)
        group = candidates.pop(index)
        chosen.append(group)
        if group['part'] >= 5:
            r_count += len(group['questions'])
        else:
            l_count += len(group['questions'])
    return chosen

def schedule_review(previous, rating, now=None):
    now = now or datetime.now(timezone.utc)
    repetitions = previous.get('repetitions', 0)
    ease = previous.get('ease', 2.5)
    if rating == 'again':
        interval, repetitions, ease = 0, 0, max(1.3, ease-.2)
        due = now + timedelta(minutes=10)
    else:
        interval = (1 if repetitions == 0 else 3 if repetitions == 1 else max(4, round(previous.get('interval', 1)*ease)))
        if rating == 'easy':
            interval = max(3, round(interval*1.5))
            ease = min(3, ease+.15)
        repetitions += 1
        due = now + timedelta(days=interval)
    return {'repetitions': repetitions, 'ease': ease, 'interval': interval, 'due': due.timestamp()}

def validate_question(q, existing=()):
    errors = []
    if not isinstance(q, dict):
        return ['Question must be an object.']
    if not isinstance(q.get('stem'), str) or not 15 <= len(q['stem']) <= 1200:
        errors.append('Énoncé manquant ou longueur invalide.')
    choices = q.get('choices', [])
    if not isinstance(choices, list) or len(choices) != 4 or any(not isinstance(x,str) or not x.strip() or len(x)>500 for x in choices):
        errors.append('Quatre choix textuels non vides sont requis.')
    elif len({x.strip().casefold() for x in choices}) != 4:
        errors.append('Les choix doivent être distincts.')
    if type(q.get('answer')) is not int or q['answer'] not in range(4):
        errors.append('La bonne réponse doit être un indice de 0 à 3.')
    if q.get('skill') not in SKILLS:
        errors.append('Compétence inconnue.')
    if q.get('level') not in LEVELS:
        errors.append('Niveau invalide.')
    if not isinstance(q.get('explanation'),str) or not 35 <= len(q['explanation']) <= 4000:
        errors.append('Une explication détaillée est requise.')
    if isinstance(q.get('stem'),str) and q['stem'].strip().casefold() in existing:
        errors.append('Énoncé déjà présent dans la banque.')
    if isinstance(q.get('stem'),str) and q['stem'].count('____') != 1:
        errors.append('La génération de partie 5 doit contenir un seul blanc ____.')
    return errors
