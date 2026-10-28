#!/usr/bin/env python3
"""Prune old, regenerable task metadata caches; retain all task and user records."""
import argparse
import json
from pathlib import Path
import time

CACHE_NAMES = ('remote_plugin_catalog', 'codex_apps_tools')


def clean(root, age_hours=24, execute=False, now=None):
    root = Path(root).expanduser().resolve()
    cutoff = (time.time() if now is None else now) - age_hours * 3600
    result = {'eligible_files': 0, 'eligible_bytes': 0, 'removed_files': 0, 'removed_bytes': 0}
    if not root.is_dir():
        return result
    for home in root.glob('*/*/codex-home'):
        if not home.resolve().is_relative_to(root) or home.is_symlink() or not home.is_dir() or (home / 'cache').is_symlink():
            continue
        if not (home / 'config.toml').is_file():
            continue
        for name in CACHE_NAMES:
            folder = home / 'cache' / name
            if folder.is_symlink() or not folder.is_dir():
                continue
            for file in folder.iterdir():
                try:
                    if file.suffix != '.json' or file.is_symlink() or not file.is_file():
                        continue
                    stat = file.stat()
                    if stat.st_mtime >= cutoff:
                        continue
                    size = stat.st_blocks * 512
                    result['eligible_files'] += 1
                    result['eligible_bytes'] += size
                    if execute:
                        file.unlink()
                        result['removed_files'] += 1
                        result['removed_bytes'] += size
                except FileNotFoundError:
                    # An active cache refresh can replace a file during the sweep.
                    continue
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.home() / 'multica_workspaces')
    parser.add_argument('--age-hours', type=int, default=24)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    if args.age_hours < 24:
        parser.error('Retain at least the last 24 hours of cache files')
    print(json.dumps(clean(args.root, args.age_hours, args.execute)))


if __name__ == '__main__':
    main()
