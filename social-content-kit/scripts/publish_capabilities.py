#!/usr/bin/env python3
"""Publish the maintained capability registry with readback and mutation reconciliation."""
import argparse
import json
from pathlib import Path
import sys
from install_multica import Installer, skill_package, save_json

ROOT=Path(__file__).resolve().parents[2]
PROJECT=ROOT.parent
RETIRED_SLUGS = {'xhs-lifestyle-publisher', 'xhs-natural-expression',
                 'conversation-personality', 'xhs-outdoor-fitness', 'lady-s-man'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute', action='store_true')
    p.add_argument('--config',type=Path,default=PROJECT/'channel/.local/multica.json')
    p.add_argument('--state',type=Path,default=Path.home()/'.local/state/leo-capability-rebuild/publish-state.json')
    a=p.parse_args()
    catalog=json.loads((ROOT/'social-content-kit/references/capability-registry.json').read_text())['skills']
    if any(row['slug'] in RETIRED_SLUGS for row in catalog):
        raise ValueError('Retired compatibility skills must not be republished; maintain the account capability registry.')
    if not a.execute:
        print(json.dumps([{'name':r['slug'],'title':r['title']} for r in catalog],ensure_ascii=False,indent=2));return
    sys.path.insert(0,str(PROJECT/'channel'))
    from channel_service.multica import Multica
    remote=Multica(a.config)
    rows=remote.request('GET','/api/skills')
    if not a.state.exists():
        state={'schema':1,'skills':{},'agents':{},'pending':{}}
        for r in catalog:
            matches=[x for x in rows if x['name'] in {r['slug'],r.get('legacy_slug',r['slug'])}]
            if len(matches)>1:raise ValueError('Duplicate old and new skill: '+r['slug'])
            if matches:state['skills'][r['slug']]={'id':matches[0]['id']}
        save_json(a.state,state)
    # A managed old name may transition to its registered new name only once.
    installer=Installer(remote,a.state)
    for r in catalog:
        registered=installer.state['skills'].get(r['slug'])
        if registered and r.get('legacy_slug'):
            old=remote.request('GET','/api/skills/'+registered['id'])
            if old['name']==r['legacy_slug']:
                payload=skill_package(r['slug'])
                installer.mutation('rename:'+r['slug'],'PUT','/api/skills/'+old['id'],payload,
                    lambda old=old:remote.request('GET','/api/skills/'+old['id']),
                    lambda got,payload=payload:got['name']==payload['name'] and got['content']==payload['content'])
        item=installer.install_skill(skill_package(r['slug']))
        r['id']=item['id']
    save_json(a.state.parent/'published-capabilities.json',catalog)
    print('Published and verified',len(catalog),'skills and their supporting resources.')

if __name__=='__main__':main()
