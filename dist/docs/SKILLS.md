# Skills

Repository-local index of available prompt vault skills.

## Prompt Vault

| Skill | Purpose | Path |
| --- | --- | --- |
| `prompt-db-ideal-state-guard` | Audit `db/prompts.json` against the canonical target. | `.agents/skills/prompt-db-guard/SKILL.md` |
| `prompt-vault-workflow` | Route source inputs into DB and artifact updates. | `.agents/skills/workflow/SKILL.md` |
| `safe-git-delivery` | Validate, preflight-audit, and safely commit repository changes. | `.agents/skills/safe-git-delivery/SKILL.md` |

## Voice

| Skill | Purpose | Path |
| --- | --- | --- |
| `voice-caption-writer` | Draft concise Japanese captions for TTS and VoiceDesign voices. | `.agents/skills/voice-caption-writer/SKILL.md` |
| `speech-mode-kafka-writer` | Draft `speech_mode_kafka` text for concise Kafka-style replies and narration. | `.agents/skills/speech-mode-kafka-writer/SKILL.md` |

## Subagents

| Subagent | Purpose | Path |
| --- | --- | --- |
| `audit-repair-subagent` | Triage and repair database/artifact validation failures. | `.agents/subagents/audit-repair-subagent.md` |
