import unittest
from datetime import datetime, timezone
from server.engine import allocation, mastery, evidence, challenge_ready, schedule_review, select_groups, validate_question
from server.content import GROUPS
from server.generation import generate

def attempt(i,part=5,correct=1,level='B2'):
    return dict(question_id=str(i),part=part,correct=correct,level=level,skill='word-forms',created=i,seconds=20)

class LearningTests(unittest.TestCase):
    def test_repeats_do_not_inflate_evidence(self):
        rows=[attempt(1,correct=0),dict(attempt(1),created=2)]
        self.assertEqual(len(evidence(rows)),1)
        self.assertEqual(mastery(rows)['word-forms']['accuracy'],100)
        self.assertEqual(mastery([])['word-forms']['accuracy'],None)
    def test_adaptive_ratio_requires_both_sections(self):
        self.assertEqual(allocation([attempt(i) for i in range(100)])['reading'],65)
        rows=[attempt(i,correct=0) for i in range(30)]+[attempt(i,part=2) for i in range(30,50)]
        self.assertTrue(allocation(rows)['adaptive'])
        self.assertEqual(allocation(rows)['reading'],80)
    def test_challenge_requires_distinct_advanced_success(self):
        self.assertFalse(challenge_ready([attempt(1)]*100))
        self.assertFalse(challenge_ready([attempt(i,level='B1') for i in range(50)]))
        self.assertTrue(challenge_ready([attempt(i) for i in range(40)]))
    def test_srs_failure_and_success(self):
        now=datetime(2026,1,1,tzinfo=timezone.utc)
        again=schedule_review({},'again',now)
        self.assertEqual(again['due']-now.timestamp(),600)
        good=schedule_review(again,'good',now)
        self.assertEqual(good['interval'],1)
        self.assertEqual(schedule_review(good,'good',now)['interval'],3)
    def test_exam_integrity_all_series(self):
        for n in range(1,9):
            groups=select_groups(GROUPS,[],'exam',seed=23,exam_set=n)
            self.assertEqual([sum(len(g['questions']) for g in groups if g['part']==p) for p in range(1,8)],[6,25,39,30,30,16,54])
            self.assertEqual(sum(len(g['questions']) for g in groups if g.get('passage_type')=='single'),29)
            self.assertEqual(sum(len(g['questions']) for g in groups if g.get('passage_type') in ('double','triple')),25)
            self.assertTrue(all(q['level']!='C2' for g in groups for q in g['questions']))
    def test_select_preserves_stimuli_and_filters(self):
        groups=select_groups(GROUPS,[],'practice',part=3,minutes=10,seed=3,accent='UK')
        self.assertTrue(groups)
        self.assertTrue(all(len(g['questions'])==3 and g['part']==3 and g['accent']=='UK' for g in groups))
        qid=groups[0]['questions'][0]['id']
        review=select_groups(GROUPS,[],'review',due_ids=[qid])
        self.assertEqual(review,[groups[0]])
    def test_question_drafts_validation_and_novelty(self):
        item,_=generate('local','B2','word-forms',set())
        self.assertEqual(validate_question(item),[])
        self.assertTrue(validate_question(item,{item['stem'].casefold()}))
        self.assertTrue(validate_question({**item,'answer':True}))
        self.assertTrue(validate_question({**item,'choices':['x']*4}))
        self.assertTrue(validate_question({**item,'stem':'No blank in this sentence.'}))
        fresh,_=generate('local','B2','word-forms',{item['stem'].casefold()})
        self.assertNotEqual(fresh['stem'],item['stem'])
