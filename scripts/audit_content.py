#!/usr/bin/env python3
"""Check structural consistency and speech presence; not a linguistic certification."""
import json
import sys
import wave
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server.content import GROUPS, FLASHCARDS, LESSONS, SKILLS
from server.engine import select_groups
ROOT=Path(__file__).resolve().parents[1]

def audit():
    errors=[]
    ids=set()
    stems=Counter()
    counts=Counter()
    audio=json.loads((ROOT/'public/audio/manifest.json').read_text())
    for g in GROUPS:
        if g['id'] in ids: errors.append('Duplicate group '+g['id'])
        ids.add(g['id'])
        for q in g['questions']:
            if q['id'] in ids: errors.append('Duplicate question '+q['id'])
            ids.add(q['id']); counts[g['part']]+=1
            stems[q['stem']]+=1
            if len(q['choices'])!=(3 if g['part']==2 else 4): errors.append('Choice count '+q['id'])
            if len(set(q['choices']))!=len(q['choices']): errors.append('Duplicate choices '+q['id'])
            if type(q['answer']) is not int or not 0<=q['answer']<len(q['choices']): errors.append('Key '+q['id'])
            if q['skill'] not in SKILLS or len(q['explanation'])<35: errors.append('Metadata '+q['id'])
            if q['level'] not in ('B1','B2','C1','C2'): errors.append('Level '+q['id'])
        if g['part']<5:
            path=ROOT/'public/audio'/f"{g['id']}.wav"
            if not path.exists() or g['id'] not in audio:
                errors.append('Missing audio '+g['id']);continue
            with wave.open(str(path)) as w:
                duration=w.getnframes()/w.getframerate()
                speech=any(w.readframes(w.getnframes()))
                if not speech or duration<2: errors.append('Silent audio '+g['id'])
                if abs(duration-audio[g['id']])>.02: errors.append('Duration '+g['id'])
    exam_minutes=[]
    for n in range(1,9):
        groups=select_groups(GROUPS,[],'exam',seed='audit',exam_set=n)
        actual=Counter({p:sum(len(g['questions']) for g in groups if g['part']==p) for p in range(1,8)})
        if actual!={1:6,2:25,3:39,4:30,5:30,6:16,7:54}: errors.append(f'Exam counts {n}: {actual}')
        secs=sum(audio[g['id']]+(6 if g['part']<=2 else 18) for g in groups if g['part']<5)
        exam_minutes.append(round(secs/60,1))
        if secs>2700: errors.append(f'Audio exceeds 45 minutes for exam {n}')
    result={'questions':sum(counts.values()),'parts':dict(sorted(counts.items())),
        'initial':sum(len(g['questions']) for g in GROUPS if not g.get('variant')),
        'variants':sum(len(g['questions']) for g in GROUPS if g.get('variant')),
        'cards':len(FLASHCARDS),'lessons':len(LESSONS),'audio_files':len(audio),
        'audio_minutes':round(sum(audio.values())/60,1),'exam_audio_with_minimum_pauses_minutes':exam_minutes,
        'errors':errors}
    return result

if __name__=='__main__':
    result=audit();print(json.dumps(result,ensure_ascii=False,indent=2));sys.exit(bool(result['errors']))
