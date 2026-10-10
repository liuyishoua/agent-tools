# Runtime integration

Upstream skill: https://skillhub.cn/skills/gifgrep (steipete, 1.0.1).
CLI: /home/ubuntu/.local/bin/gifgrep, pinned 0.4.4. Release SHA256:
974bb32c99f5b2931498809600a135e656f67e9cdfd5eff3fb018afbe8e886dc

The mirrored skill predates the provider migration. CLI 0.4.4 uses GIPHY_API_KEY or KLIPY_API_KEY, not Tenor's old demo key. Do not claim online CLI search works without a configured provider. Local `still` and `sheet` require no key. Public Tenor reaction collection is performed by the workbench's maintenance script, outside the model's conversation turn.

For XHS turns read xhs-natural-expression. The workbench provides actual image attachments and owned asset_id values. Return asset_id in reply_messages; do not return local paths, Markdown images, public URLs, or execute platform sends. Catalog images already imported into the account require no GIF search credentials. No need to invoke the CLI when the current catalog already contains the right reaction.
