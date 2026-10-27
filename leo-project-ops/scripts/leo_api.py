#!/usr/bin/env python3
"""Local project API client. Credentials stay in process memory; writes never retry."""
import argparse
import ast
import concurrent.futures
import html
import http.cookiejar
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path('/home/ubuntu/leo-project')
PROJECTS = {
    'douyin': {'base': 'http://127.0.0.1:8766', 'health': '/.well-known/bifrost/ready', 'origin': 'https://d.58nft.net:9445', 'source': 'douyin/web/app.py', 'mode': 'demo'},
    'ticket': {'base': 'http://127.0.0.1:8767', 'health': '/.well-known/bifrost/ready', 'source': 'ticket/web/__main__.py'},
    'bifrost': {'base': 'http://127.0.0.1:8790', 'health': '/login', 'source': 'bifrost/portal.py', 'mode': 'portal HTML + links.json; no business REST API'},
    'model-bridge': {'base': 'http://127.0.0.1:8788', 'health': '/health', 'mode': 'Open WebUI API; remote GPU'},
    'multica': {'base': 'http://127.0.0.1:8080', 'health': '/readyz', 'mode': 'task-scoped API / multica CLI'},
    'xianyu': {'directory': 'xianyu', 'mode': 'Python SDK/scripts; no verified HTTP server'},
}
# Independent cv-cat workspaces use local password login and platform-scoped data.
for _slug, _directory, _port, _tls in [
    ('bilibili','bilibili',8773,9451), ('weibo','weibo',8774,9452),
    ('jd','jd',8775,9453), ('kuaishou','kuaishou',8776,9454),
    ('zhihu','zhihu',8777,9455),
]:
    PROJECTS[_slug]={'base':f'http://127.0.0.1:{_port}','health':'/login',
        'origin':f'https://d.58nft.net:{_tls}','source':f'{_directory}/web/app.py',
        'directory':_directory,'workspace':True,'mode':'real adapters; platform account required'}

PROJECTS['channel']={'base':'http://127.0.0.1:8780','health':'/login','origin':'https://d.58nft.net:9456',
    'source':'channel/channel_service/app.py','directory':'channel','workspace':True,
    'password_file':'channel/.local/admin-password','mode':'durable queue; Multica agents; outputs for review'}

PROJECTS['xianyu-workbench']={'base':'http://127.0.0.1:8770','health':'/login','origin':'https://d.58nft.net:9448',
    'source':'xianyu/web/app.py','directory':'xianyu','workspace':True,
    'mode':'authenticated workbench; account selection required for account-scoped operations'}

SECRET = re.compile(r'(?i)(password|passwd|cookie|authorization|private.?key|secret|access.?token|refresh.?token|api.?key|csrf|ticket|^token$)')

def redact(value):
    if isinstance(value, dict):
        return {k: '[REDACTED]' if SECRET.search(k) else redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        return re.sub(r'\b(?:mul_|mat_|sk-)[A-Za-z0-9_-]{12,}', '[REDACTED]', value)
    return value

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None

# Loopback services use their actual local listener, without sending credentials to a proxy.
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

def raw(base, path, method='GET', payload=None, headers=None, timeout=30, opener=None):
    parsed = urllib.parse.urlsplit(path)
    if not path.startswith('/') or path.startswith('//') or parsed.scheme or parsed.netloc or parsed.fragment:
        raise ValueError('Use a relative API path beginning with one slash')
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(base + path, data, headers or {}, method=method)
    try:
        with (opener or OPENER).open(req, timeout=timeout) as response:
            return response.status, response.headers.get('Content-Type', ''), response.read(4 * 1024 * 1024)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers.get('Content-Type', ''), exc.read(65536)

def api(project, path, method='GET', payload=None, account_id=None):
    spec = PROJECTS[project]
    if project in ('bifrost', 'xianyu'):
        raise ValueError('This project uses its documented HTML/file or Python interfaces; see references/projects.md')
    if not (path.startswith('/api/') or (project == 'multica' and path == '/readyz') or
            (project == 'model-bridge' and path == '/health')):
        raise ValueError('Use a documented /api/ path')
    headers = {'Content-Type': 'application/json'}
    if account_id is not None:
        account = str(account_id)
        if not account or len(account)>160 or any(ord(c)<32 for c in account):
            raise ValueError('Invalid execution account')
        headers['X-Account-ID']=account
        headers['X-Execution-Account']=account
    workspace_opener=None
    if spec.get('workspace'):
        workspace_cookies=http.cookiejar.CookieJar()
        workspace_opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect(),urllib.request.HTTPCookieProcessor(workspace_cookies))
        headers.update({'Origin':spec['origin'],'X-App-Request':'1'})
        password_path=ROOT/spec.get('password_file',spec['directory']+'/.local/web/admin-password')
        machine_path=password_path.with_name('workspace-machine-key')
        if machine_path.is_file():
            headers['X-Ops-Machine-Key']=machine_path.read_text().strip()
        else:
            if not password_path.is_file(): raise ValueError('Workspace password file is not available')
            status,_,_=raw(spec['base'],'/api/login','POST',{'password':password_path.read_text().strip()},headers,opener=workspace_opener)
            if status!=200: raise ValueError('Workspace configured password login failed')
            headers['Cookie']='; '.join(cookie.name+'='+cookie.value for cookie in workspace_cookies)
    elif project == 'douyin':
        headers.update({'Origin': spec['origin'], 'X-App-Request': '1'})
    elif project == 'ticket' and method != 'GET':
        status, _, body = raw(spec['base'], '/')
        match = re.search(r'<meta\s+name=["\']workbench-token["\']\s+content=["\']([^"\']+)', body.decode())
        if status != 200 or not match:
            raise ValueError('Cannot obtain ticket page CSRF token')
        headers['X-Workbench-Token'] = html.unescape(match.group(1))
    elif project == 'multica':
        token = os.environ.get('MULTICA_TOKEN')
        ws = os.environ.get('MULTICA_WORKSPACE_ID')
        if not token:
            if any(os.environ.get(k) for k in ('MULTICA_TASK_ID', 'MULTICA_AGENT_ID', 'MULTICA_DAEMON_PORT')):
                raise ValueError('Task credential missing; refusing owner profile fallback')
            cfg = json.loads(Path('/home/ubuntu/.multica/config.json').read_text())
            token, ws = cfg['token'], cfg.get('workspace_id')
        headers['Authorization'] = 'Bearer ' + token
        if ws:
            headers['X-Workspace-ID'] = ws
    elif project == 'model-bridge' and path != '/health':
        env = {}
        for line in (ROOT / 'model-bridge/deploy/cloud.env').read_text().splitlines():
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env[key] = value.strip().strip('"').strip("'")
        status, _, body = raw(spec['base'], '/api/v1/auths/signin', 'POST',
                              {'email': env['WEBUI_ADMIN_EMAIL'], 'password': env['WEBUI_ADMIN_PASSWORD']},
                              {'Content-Type': 'application/json'})
        if status != 200:
            raise ValueError('Open WebUI configured administrator login failed')
        headers['Authorization'] = 'Bearer ' + json.loads(body)['token']
    status, kind, body = raw(spec['base'], path, method, payload, headers,opener=workspace_opener)
    try:
        value = json.loads(body)
    except (ValueError, UnicodeError):
        value = {'content_type': kind, 'bytes': len(body)}
    return {'project': project, 'status': status, 'data': redact(value)}

def health(item):
    name, spec = item
    if 'base' not in spec:
        return {'project': name, 'state': 'sdk', 'session_file_present': (ROOT / 'xianyu/.local/session.json').is_file()}
    try:
        status, _, _ = raw(spec['base'], spec['health'], timeout=8)
        return {'project': name, 'status': status, 'reachable': status == 200, 'mode': spec.get('mode', 'local API')}
    except (OSError, urllib.error.URLError):
        return {'project': name, 'reachable': False}

def routes(project):
    spec = PROJECTS[project]
    source = spec.get('source')
    if not source:
        return {'project': project, **spec}
    tree = ast.parse((ROOT / source).read_text())
    found = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for deco in node.decorator_list:
                if not isinstance(deco, ast.Call) or not isinstance(deco.func, ast.Attribute) or not deco.args:
                    continue
                if deco.func.attr not in ('route', 'get', 'post', 'patch', 'delete', 'put'):
                    continue
                if isinstance(deco.args[0], ast.Constant):
                    methods = ['GET'] if deco.func.attr == 'route' else [deco.func.attr.upper()]
                    for kw in deco.keywords:
                        if kw.arg == 'methods':
                            methods = ast.literal_eval(kw.value)
                    found.append({'path': deco.args[0].value, 'methods': methods, 'handler': node.name})
    return {'project': project, 'source': str(ROOT / source), 'routes': found,
            'note': 'For ticket dynamic routes and body schemas, read the source and references/projects.md'}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    sub.add_parser('status')
    r = sub.add_parser('routes'); r.add_argument('project', choices=PROJECTS)
    c = sub.add_parser('call'); c.add_argument('project', choices=PROJECTS); c.add_argument('path')
    c.add_argument('--method', choices=['GET', 'POST', 'PATCH', 'PUT', 'DELETE'], default='GET')
    c.add_argument('--body-file', help='JSON file, or - for stdin')
    c.add_argument('--execute', action='store_true', help='Execute a requested non-GET operation')
    args = p.parse_args()
    try:
        if args.command == 'list': result = PROJECTS
        elif args.command == 'status':
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
                result = list(pool.map(health, PROJECTS.items()))
        elif args.command == 'routes': result = routes(args.project)
        else:
            if args.method != 'GET' and not args.execute:
                raise ValueError('Non-GET requires --execute after checking the user request')
            payload = json.loads(sys.stdin.read() if args.body_file == '-' else Path(args.body_file).read_text()) if args.body_file else None
            result = api(args.project, args.path, args.method, payload)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if isinstance(result, dict) and result.get('status', 200) >= 400 else 0
    except Exception as exc:
        # Some exceptions include URLs or credentials; only report the type for unexpected errors.
        print(json.dumps({'error': str(exc) if isinstance(exc, ValueError) else type(exc).__name__,
                          'note': 'No automatic write retry; inspect current state before retrying.'}, ensure_ascii=False))
        return 1

if __name__ == '__main__':
    sys.exit(main())
