---
name: gifgrep
description: 通用·素材处理·搜索表情。Search GIF providers with CLI/TUI, download results, and extract stills/sheets.
metadata: {"clawdbot":{"emoji":"🧲","requires":{"bins":["gifgrep"]},"install":[{"id":"brew","kind":"brew","formula":"steipete/tap/gifgrep","bins":["gifgrep"],"label":"Install gifgrep (brew)"},{"id":"go","kind":"go","module":"github.com/steipete/gifgrep/cmd/gifgrep@latest","bins":["gifgrep"],"label":"Install gifgrep (go)"}]}}
---

# gifgrep

Project: https://gifgrep.com

Search, preview and inspect GIF files. For the installed CLI version and provider availability, use [runtime integration](references/runtime.md); it overrides older upstream examples. The current pinned CLI is 0.4.4.

## In an XHS conversation

The workbench already supplies account-owned images in `context.media_catalog` with real image attachments. Inspect their `image_number` and return a suitable `asset_id` in `reply_messages`, following xhs-natural-expression. A catalog reaction can be used proactively even if the peer sent only text. No CLI search or provider key is needed for these existing assets. Do not send a path, public URL, Markdown image or external platform request.

Read the runtime reference and invoke the CLI only when this task actually needs search or file inspection. Provider configuration must be real: GIPHY needs `GIPHY_API_KEY`; KLIPY, including the `tenor` alias, needs `KLIPY_API_KEY`. The old Tenor demo-key fallback does not work in 0.4.4. Do not claim search succeeded or fabricate a result when neither provider is configured. Use available catalog assets or text instead.

## Commands

- `gifgrep search --json "cat laughing"` — provider search when configured.
- `gifgrep still cat.gif --at 1.5s -o still.png` — inspect a local frame, no key needed.
- `gifgrep sheet cat.gif --frames 9 --cols 3 -o sheet.png` — inspect sampled frames, no key needed.
- Use `gifgrep <command> --help` for flags supported by the actual binary.

For any GIF chosen to convey a reaction, inspect its actual picture, text and motion sampling. A title or tag alone does not establish what the image means in this conversation. Online discovery is separate from importing an owned, validated workbench asset; the conversation agent cannot turn an arbitrary link into a sendable asset.
