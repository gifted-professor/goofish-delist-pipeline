# Agent Entry Point

Read `START_HERE.md` first.

It contains the current Codex entrypoint for this project: which docs to read,
which checks are safe to run first, and the boundary between lightweight
`--push`, prune/full sync, browser login state, local ledger, and Feishu output.

Do not start by scanning browser profiles, checkpoints, logs, or historical
data dumps. Do not perform publish, payment, refund, delete, send, export,
or account-switch actions unless the user explicitly asks in the current turn.
