import tempfile
import unittest
from pathlib import Path
from account_memory import connect, append, read
from exploration_state import next_plan

class ExplorationStateTest(unittest.TestCase):
    def test_real_local_observation_changes_next_action(self):
        with tempfile.TemporaryDirectory() as temp:
            # Synthetic authorized publishing ledger; the observation is computed, not asserted by the model.
            ledger=Path(temp)/'synthetic-topics.txt'
            ledger.write_text('park\npark\ncafe\n')
            topics=ledger.read_text().splitlines()
            repeated=len(topics)-len(set(topics))
            db=connect(Path(temp)/'state')
            before=next_plan(read(db,'xiaotao'),['Which topics repeat?'])
            event=dict(account_key='xiaotao',event_id='synthetic-local-experiment',kind='exploration_result',text='local synthetic ledger analysis',source_ref='synthetic-topics.txt',evidence_status='confirmed',question=before['question'],action='Read and count synthetic ledger topics',expected='Each topic is distinct',observed={'repeated_topics':repeated},next_question='What scene angle differs from the repeated park topic?')
            append(db,'xiaotao',event)
            after=next_plan(read(db,'xiaotao'),['Which topics repeat?'])
            self.assertNotEqual(before['question'],after['question'])
            self.assertEqual(after['previous_observation']['repeated_topics'],1)
            self.assertEqual(after['source_event'],event['event_id'])
            self.assertEqual(next_plan(read(db,'outdoor'),[])['status'],'needs-interest')
            db.close()

if __name__=='__main__':unittest.main()
