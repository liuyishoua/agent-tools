#!/usr/bin/env python3
"""Persist account-scoped sourced events; no credentials or platform effects."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3

KINDS = {'creative_setting', 'published_content', 'interaction_fact', 'preference_candidate', 'exploration_result'}


def connect(state_dir):
    root = Path(state_dir).expanduser()
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = root / 'memory.sqlite3'
    db = sqlite3.connect(path)
    path.chmod(0o600)
    db.execute('CREATE TABLE IF NOT EXISTS events(account_key TEXT NOT NULL,event_id TEXT NOT NULL,payload TEXT NOT NULL,digest TEXT NOT NULL,PRIMARY KEY(account_key,event_id))')
    return db


def append(db, account_key, event):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', account_key):
        raise ValueError('Invalid account key')
    if event.get('account_key') != account_key:
        raise ValueError('Event does not belong to the selected account')
    if event.get('kind') not in KINDS or not all(isinstance(event.get(k), str) and event[k].strip() for k in ('event_id', 'text', 'source_ref', 'evidence_status')):
        raise ValueError('Memory needs an allowed kind and sourced evidence')
    if event['evidence_status'] not in {'confirmed', 'candidate', 'fictional'}:
        raise ValueError('Unknown evidence status')
    if event['kind'] == 'published_content' and (event['evidence_status'] != 'confirmed' or not event.get('receipt')):
        raise ValueError('Published content needs an actual confirmed receipt')
    if event['kind'] == 'creative_setting' and event['evidence_status'] != 'fictional':
        raise ValueError('Creative setting must be explicitly fictional')
    if event['kind'] == 'interaction_fact' and event['evidence_status'] != 'confirmed':
        raise ValueError('Interaction facts need confirmed source evidence')
    if event['kind'] == 'exploration_result' and (event['evidence_status'] != 'confirmed' or not all(event.get(k) for k in ('question', 'action', 'expected', 'observed'))):
        raise ValueError('Exploration needs an actual sourced action and observation')
    payload = json.dumps(event, ensure_ascii=False, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    with db:
        old = db.execute('SELECT digest FROM events WHERE account_key=? AND event_id=?', (account_key, event['event_id'])).fetchone()
        if old:
            if old[0] != digest:
                raise ValueError('Same event ID has different content')
            return False
        db.execute('INSERT INTO events VALUES(?,?,?,?)', (account_key, event['event_id'], payload, digest))
    return True


def read(db, account_key):
    return [json.loads(x[0]) for x in db.execute('SELECT payload FROM events WHERE account_key=? ORDER BY rowid', (account_key,))]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['read', 'append'])
    p.add_argument('--account', required=True)
    p.add_argument('--state-dir', default=str(Path.home()/'.local/state/leo-account-memory'))
    p.add_argument('--event-file', type=Path)
    a = p.parse_args()
    db = connect(a.state_dir)
    try:
        if a.action == 'append':
            if not a.event_file: p.error('append requires --event-file')
            value = {'saved': append(db, a.account, json.loads(a.event_file.read_text()))}
        else: value = {'account_key': a.account, 'events': read(db, a.account)}
        print(json.dumps(value, ensure_ascii=False, indent=2))
    finally: db.close()


if __name__ == '__main__': main()
