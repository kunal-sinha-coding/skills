# Shared Codex skills

Store each skill in its own child directory. Every skill directory must contain a
`SKILL.md` file with the skill instructions and metadata.

When `post-training/start.sh` runs, it updates this repository and registers
every directory containing `SKILL.md` under `${CODEX_HOME:-~/.codex}/skills`.
