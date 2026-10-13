import copy
import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from server import app
from server.content import GROUPS
from server.generation import generate
from scripts.backup import copy_database

class ApplicationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.old_db=app.DB;app.DB=Path(self.tmp.name)/'test.sqlite3'
        app.init_db();self.db=app.connect()
    def tearDown(self):
        self.db.close();app.DB=self.old_db;self.tmp.cleanup()
    def request(self,path,body=None):
        return app.api(self.db,'GET' if body is None else 'POST',path,body or {})
    def start(self,mode='practice',**kw):
        return self.request('/api/sessions',dict(mode=mode,part=5 if mode=='practice' else None,minutes=10,**kw))
    def test_initial_profile_inventory(self):
        d=self.request('/api/dashboard')
        self.assertEqual(d['profile']['dailyMinutes'],120)
        self.assertEqual(d['profile']['listening']+d['profile']['reading'],715)
        self.assertEqual(d['stats']['answered'],0)
        self.assertEqual((d['bankCount'],d['originalCount'],d['variantCount'],d['cardCount']),(2344,236,2108,305))
    def test_practice_correction_idempotency_resume_and_errors(self):
        s=self.start();qid=s['groups'][0]['questions'][0]['id']
        self.assertNotIn('answer',s['groups'][0]['questions'][0])
        backing=app.get_session(self.db,s['id']);key=backing['groups'][0]['questions'][0]['answer']
        body=dict(questionId=qid,choice=(key+1)%4,seconds=24,confidence='unsure')
        for _ in range(2): self.request('/api/sessions/'+s['id']+'/answer',body)
        restored=self.request('/api/sessions/'+s['id'])
        self.assertEqual(restored['answers'][qid]['seconds'],24)
        self.assertIn('answer',restored['groups'][0]['questions'][0])
        self.assertEqual(len(app.attempts(self.db)),1)
        self.assertEqual(len(self.request('/api/errors')),1)
        self.request('/api/sessions/'+s['id']+'/finish',{})
        self.assertEqual(len(app.attempts(self.db)),1)
    def test_listening_transcripts_and_choices_masked(self):
        s=self.request('/api/sessions',dict(mode='practice',part=2,minutes=10))
        g=s['groups'][0];item=g['questions'][0]
        self.assertNotIn('transcript',g)
        self.assertEqual(item['choices'],['Réponse A','Réponse B','Réponse C'])
        result=self.request('/api/sessions/'+s['id']+'/answer',dict(questionId=item['id'],choice=0))
        self.assertIn('transcript',result['groups'][0])
        self.assertNotEqual(result['groups'][0]['questions'][0]['choices'],item['choices'])
    def test_exam_revisions_correction_and_score(self):
        s=self.start('reading-exam',examSet=3);q=s['groups'][0]['questions'][0]
        key=app.get_session(self.db,s['id'])['groups'][0]['questions'][0]['answer']
        for choice,secs in [(0,18),(key,5)]:
            result=self.request('/api/sessions/'+s['id']+'/answer',dict(questionId=q['id'],choice=choice,seconds=secs))
        self.assertEqual(result['answers'][q['id']]['seconds'],23)
        self.assertNotIn('answer',result['groups'][0]['questions'][0])
        self.assertEqual(app.attempts(self.db),[])
        result=self.request('/api/sessions/'+s['id']+'/finish',{})
        self.assertEqual(result['result']['correct'],1)
        self.assertEqual(result['result']['total'],100)
        self.assertEqual(len(app.attempts(self.db)),100)
    def test_expiration_does_not_accept_late_answers(self):
        s=self.start('reading-exam');q=s['groups'][0]['questions'][0]
        saved=app.get_session(self.db,s['id']);saved['deadline']=time.time()-1;app.save_session(self.db,saved)
        result=self.request('/api/sessions/'+s['id']+'/answer',dict(questionId=q['id'],choice=0))
        self.assertEqual(result['status'],'completed');self.assertEqual(result['answers'],{})
        self.db.commit()
        self.assertEqual(app.get_session(self.db,s['id'])['status'],'completed')
    def test_dashboard_syncs_expired_before_statistics(self):
        s=self.start('diagnostic');saved=app.get_session(self.db,s['id']);saved['deadline']=0.1;app.save_session(self.db,saved)
        d=self.request('/api/dashboard')
        self.assertEqual(d['stats']['answered'],sum(len(g['questions']) for g in s['groups']))
    def test_full_exam_audio_clock_and_section_boundaries(self):
        s=self.start('exam',examSet=8)
        self.assertEqual(len(s['schedule']),54)
        self.assertAlmostEqual(s['schedule'][-1]['end'],s['listening_end'])
        self.assertEqual(s['deadline']-s['created'],7200)
        with self.assertRaises(app.APIError): self.start('exam')
        with self.assertRaises(app.APIError): self.request('/api/sessions/'+s['id']+'/navigate',{'index':1})
        with self.assertRaises(app.APIError): self.request('/api/sessions/'+s['id']+'/audio',{'groupId':s['groups'][1]['id']})
        with patch('server.app.time.time',return_value=s['created']+3):
            audio=self.request('/api/sessions/'+s['id']+'/audio',{'groupId':s['groups'][0]['id']})
            self.assertAlmostEqual(audio['offset'],3)
        with patch('server.app.time.time',return_value=s['listening_end']+1):
            reading=self.request('/api/sessions/'+s['id'])
            self.assertEqual(reading['groups'][reading['index']]['part'],5)
            with self.assertRaises(app.APIError): self.request('/api/sessions/'+s['id']+'/answer',dict(questionId=s['groups'][0]['questions'][0]['id'],choice=0))
    def test_profile_validation(self):
        p=copy.deepcopy(app.DEFAULT_PROFILE);p['dailyMinutes']=180;p['weekMinutes'][0]=0
        self.assertEqual(self.request('/api/profile',p)['dailyMinutes'],180)
        for invalid in ({'dailyMinutes':181},{'reading':500},{'weekMinutes':[15]}, {'target':901}):
            with self.assertRaises(app.APIError): self.request('/api/profile',{**p,**invalid})
    def test_draft_requires_rights_and_editorial_review(self):
        item,_=generate('local','B2','word-forms',set())
        with self.assertRaises(app.APIError): self.request('/api/drafts/import',dict(question=item))
        draft=self.request('/api/drafts/import',dict(question=item,rightsConfirmed=True))
        self.assertEqual(len(app.bank(self.db)),len(GROUPS))
        with self.assertRaises(app.APIError): self.request('/api/drafts/'+draft['id'],dict(action='publish'))
        self.request('/api/drafts/'+draft['id'],dict(action='publish',reviewed=True))
        self.assertEqual(len(app.bank(self.db)),len(GROUPS)+1)
        with self.assertRaises(app.APIError): self.request('/api/drafts/import',dict(question=item,rightsConfirmed=True))
    def test_cards_lessons_and_export_persist(self):
        self.request('/api/cards/rate',dict(id='card-0',rating='good'))
        self.request('/api/lessons/complete',dict(id='word-forms'))
        exported=self.request('/api/export')
        self.assertIn('card-0',exported['reviews']);self.assertIn('word-forms',exported['lessonsDone'])
        self.db.commit();self.db.close();self.db=app.connect()
        self.assertGreater(self.request('/api/cards')[0]['due'],time.time())
    def test_sqlite_backup_roundtrip(self):
        self.db.commit();destination=Path(self.tmp.name)/'backup.sqlite3'
        copy_database(app.DB,destination)
        self.request('/api/profile',{**app.DEFAULT_PROFILE,'name':'Temporary'})
        self.db.commit();self.db.close()
        copy_database(destination,app.DB);self.db=app.connect()
        self.assertEqual(app.profile(self.db)['name'],'Evan')
