#!/usr/bin/env python3
"""Carry sourced exploration results into the next topic/action plan."""
import argparse
import json
from pathlib import Path
from account_memory import connect, read


def next_plan(events, interests):
    for event in reversed(events):
        if event.get('kind') == 'exploration_result' and event.get('next_question'):
            return {'question':event['next_question'], 'source_event':event['event_id'],
                    'previous_observation':event['observed'], 'status':'continue-research'}
    return {'question':interests[0] if interests else None,'source_event':None,'status':'new-question' if interests else 'needs-interest'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['next-plan'])
    p.add_argument('--account',required=True)
    p.add_argument('--state-dir',default=str(Path.home()/'.local/state/leo-account-memory'))
    p.add_argument('--interest',action='append',default=[])
    a=p.parse_args();db=connect(a.state_dir)
    try:print(json.dumps(next_plan(read(db,a.account),a.interest),ensure_ascii=False,indent=2))
    finally:db.close()

if __name__=='__main__':main()
