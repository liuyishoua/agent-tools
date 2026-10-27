#!/usr/bin/env python3
"""Read one Multica issue and its selected reply skills in a single tool call."""
import argparse
import json
import subprocess
import os
from pathlib import Path
import re
import tomllib
from compose import compose


def diagnostics(previous_task):
    """Return only named non-secret configuration and numeric lifecycle fields."""
    home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    data = {}
    try:
        config = tomllib.loads((home / 'config.toml').read_text())
        data['config'] = {k: config[k] for k in
            ('model', 'model_reasoning_effort', 'service_tier', 'model_provider') if k in config}
    except (OSError, ValueError):
        data['config_unavailable'] = True
    phases = []
    if previous_task and re.fullmatch(r'[0-9a-f-]{36}', previous_task):
        for log in (Path.home() / '.multica').rglob('daemon.log'):
            with log.open(errors='replace') as handle:
                for line in handle:
                    if previous_task not in line or 'task phase recorded' not in line:
                        continue
                    phase = re.search(r'task_phase=([a-z_]+)', line)
                    elapsed = re.search(r'phase_elapsed_ms=(\d+)', line)
                    total = re.search(r'total_elapsed_ms=(\d+)', line)
                    if phase and elapsed and total:
                        phases.append({'phase': phase[1], 'elapsed_ms': int(elapsed[1]),
                                       'total_ms': int(total[1])})
    data['previous_task_phases'] = phases
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--issue', required=True)
    parser.add_argument('--persona', required=True)
    parser.add_argument('--diagnostics', action='store_true')
    parser.add_argument('--previous-task')
    args = parser.parse_args()
    result = subprocess.run(['multica', 'issue', 'get', args.issue, '--output', 'json'],
                            capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise SystemExit('Issue read failed; no reply context produced')
    issue = json.loads(result.stdout)
    context = compose(args.persona, 'reply', 'xhs', brief='按当前任务契约回应')
    # Preserve the entire task description and account profile; remove only
    # unrelated board metadata and pretty-print/escaping overhead.
    payload = {'issue': {k: issue.get(k) for k in
        ('id', 'title', 'description', 'assignee_id', 'assignee_type', 'status', 'attachments')},
        'reply_context': context}
    if args.diagnostics:
        # Put compact diagnostics first so transcript truncation cannot hide it.
        payload = {'diagnostics': diagnostics(args.previous_task), **payload}
    print(json.dumps(payload, ensure_ascii=False, separators=(',', ':')))


if __name__ == '__main__':
    main()
