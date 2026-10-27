import tempfile
import unittest
from account_memory import connect, append, read

class AccountMemoryTest(unittest.TestCase):
    def test_isolation_and_idempotency(self):
        with tempfile.TemporaryDirectory() as p:
            db = connect(p)
            event = dict(account_key='xiaotao', event_id='sample-1',kind='creative_setting', text='fictional park',source_ref='editor sample',evidence_status='fictional')
            self.assertTrue(append(db,'xiaotao',event))
            self.assertFalse(append(db,'xiaotao',event))
            self.assertEqual(read(db,'outdoor'),[])
            with self.assertRaises(ValueError): append(db,'outdoor',event)
            with self.assertRaises(ValueError): append(db,'xiaotao',{**event,'text':'changed'})
            db.close()

    def test_draft_cannot_become_published_fact(self):
        with tempfile.TemporaryDirectory() as p:
            db = connect(p)
            event = dict(account_key='xiaotao',event_id='draft-1',kind='published_content',text='draft',source_ref='generated draft',evidence_status='confirmed')
            with self.assertRaises(ValueError): append(db,'xiaotao',event)
            self.assertEqual(read(db,'xiaotao'),[])
            db.close()

if __name__ == '__main__': unittest.main()
