import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path
from server import app

class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.old_db=app.DB
        app.DB=Path(cls.tmp.name)/'http.sqlite3';app.init_db()
        cls.server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
        cls.worker=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.worker.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.worker.join()
        app.DB=cls.old_db;cls.tmp.cleanup()
    def request(self,path,body=None,headers=None,raw=None):
        conn=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=10)
        data=json.dumps(body).encode() if body is not None else raw
        base={'X-TOEIC-Client':'1','Content-Type':'application/json'} if data is not None else {}
        conn.request('POST' if data is not None else 'GET',path,data,{**base,**(headers or {})})
        res=conn.getresponse();result=res.status,dict(res.getheaders()),res.read();conn.close();return result
    def test_static_and_range_audio(self):
        status,headers,body=self.request('/')
        self.assertEqual(status,200);self.assertIn(b'TOEIC',body)
        self.assertIn("frame-ancestors 'none'",headers['Content-Security-Policy'])
        status,headers,body=self.request('/audio/p2-001.wav',headers={'Range':'bytes=0-99'})
        self.assertEqual(status,206);self.assertEqual(len(body),100);self.assertTrue(body.startswith(b'RIFF'))
    def test_local_boundary_and_traversal(self):
        self.assertEqual(self.request('/api/dashboard',headers={'Host':'evil.example'})[0],403)
        self.assertEqual(self.request('/api/sessions',{'mode':'practice'},headers={'Origin':'https://evil.example'})[0],403)
        self.assertEqual(self.request('/api/sessions',{'mode':'practice'},headers={'X-TOEIC-Client':'0'})[0],403)
        self.assertEqual(self.request('/app/%2e%2e/server/app.py')[0],403)
        self.assertNotEqual(self.request('/data/toeic.sqlite3')[0],200)
    def test_invalid_and_valid_api_requests(self):
        self.assertEqual(self.request('/api/sessions',raw=b'{broken')[0],400)
        self.assertEqual(self.request('/api/sessions',raw=b'[]')[0],400)
        self.assertEqual(self.request('/api/sessions',{'mode':'practice','part':99})[0],400)
        status,_,body=self.request('/api/sessions',{'mode':'practice','part':5,'minutes':10})
        self.assertEqual(status,200);self.assertTrue(json.loads(body)['groups'])
    def test_local_generation_workflow(self):
        status,_,body=self.request('/api/generate',{'provider':'local','skill':'word-forms','level':'B2'})
        self.assertEqual(status,200);draft=json.loads(body);self.assertEqual(draft['status'],'draft')
        self.assertEqual(self.request('/api/drafts/'+draft['id'],{'action':'publish'})[0],400)
        self.assertEqual(self.request('/api/drafts/'+draft['id'],{'action':'publish','reviewed':True})[0],200)
