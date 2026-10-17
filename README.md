# OpenCode v2 Team Agent Pack

[![CI and GitHub Pages](https://github.com/Alqudimi/ather-agents/actions/workflows/ci-cd.yml/badge.svg?branch=main)](https://github.com/Alqudimi/ather-agents/actions/workflows/ci-cd.yml) [![CodeQL](https://github.com/Alqudimi/ather-agents/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/Alqudimi/ather-agents/actions/workflows/codeql.yml)

> **بالعربية:** يتضمن المستودع 621 وكيلاً لـOpenCode v2، يتقدمهم `orchestrator` و14 قائداً للمجالات. يجب أن يكون OpenCode v2 مثبتاً مسبقاً؛ هذا المشروع لا يثبته ولا يزيله. لتثبيت الحزمة من مجلد المشروع:
>
> ```bash
> curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- install
> ```
>
> الأدلة العربية: [مركز التوثيق](docs/README.md) · [التثبيت](docs/INSTALLATION.md) · [الاستخدام](docs/USING-AGENTS.md) · [فهرس الوكلاء](docs/AGENT-CATALOG.md) · [الأسئلة الشائعة](docs/FAQ.md) · [استكشاف الأخطاء](docs/TROUBLESHOOTING.md) · [CI/CD](docs/CI-CD.md) · [إعداد GitHub](docs/GITHUB-SETUP.md) · [نشر المشروع](docs/PUBLISH.md) · [نشر Wiki](docs/WIKI.md) · [الدعم](SUPPORT.md) · [المساهمة](CONTRIBUTING.md) · [الأمان](SECURITY.md) · [حالة الترخيص](LICENSE-NOTICE.md).

**Website:** [alqudimi.github.io/ather-agents](https://alqudimi.github.io/ather-agents/) · **Wiki:** [GitHub Wiki](https://github.com/Alqudimi/ather-agents/wiki)

This repository contains 621 discoverable OpenCode v2 Markdown agents. The 14 team leads are grouped by domain; a global `orchestrator` coordinates them. See [`AGENT-MANIFEST.csv`](AGENT-MANIFEST.csv) for IDs and source/output checksums, and [`INSTALL-OPENCODE-V2.md`](INSTALL-OPENCODE-V2.md) for the sourced installation guide.

## Install, verify, and uninstall

OpenCode **v2 must already be installed**. The installer never installs or uninstalls OpenCode. From your project directory, run:

```bash
curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- install
curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- verify
curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- uninstall
```

Pass `--project /absolute/path/to/project` to target another project. If OpenCode v2 is missing, the command reports an error and asks the user to install it first. The bootstrap needs `bash`, `curl`, `tar`, and Python 3.9+. It places agents in `.opencode/agents/`, enables `experimental.subagent_depth: 2` by default, and keeps a reversible record. `uninstall` removes only unchanged files owned by this pack and restores settings it changed when safe; user-modified files and the OpenCode CLI are preserved. Use `--no-depth-2` to skip the config edit.

For local development, the Python implementation can also be run directly:

```bash
python3 scripts/install-opencode-v2.py install --project /absolute/path/to/project
python3 scripts/install-opencode-v2.py verify --project /absolute/path/to/project
python3 scripts/install-opencode-v2.py uninstall --project /absolute/path/to/project
```

## Use

- Choose `orchestrator` to coordinate across the 14 teams, or select a team lead directly for work limited to one domain.
- Give the chosen agent a concrete outcome and project constraints. The global orchestrator selects only relevant leads and integrates their results; it does not call all teams by default.
- Leads can call only the specialist agents listed in their permission rules. Team members are subagents.
- Nested paths under `.opencode/agents/` become part of each agent ID.
- This pack does not set `default_agent` or global permissions, so it does not silently change a project's defaults.

## V2 behavior and safety

OpenCode V2 delegates through the `subagent` tool. Child sessions start with fresh context, and each child uses its own configured permissions. The 14 team leads use `mode: all`, so they remain selectable as primaries and can also be called by `orchestrator`. The global orchestrator is `mode: primary` and is permission-limited to the 14 leads. V2 defaults to one delegation level; `experimental.subagent_depth: 2` enables the intended hierarchy `orchestrator → team lead → specialist`. It does not enable a third delegation level.

The installer safely edits strict JSON only. For JSONC or ambiguous same-precedence config files, it refuses to rewrite them; use `--no-depth-2` and merge the V2 key manually. The official migration guide says V2 ignores the old top-level `subagent_depth` key: use `experimental.subagent_depth` instead. The published JSON schema currently lags this V2 field; see the installation guide for the source and caveat.

The agent instructions retain usable source material while removing legacy V1 fields. `temperature`/`top_p` were moved under `request.body`, `max_steps` to `steps`, and legacy permission maps to ordered V2 permission rules. The evaluation-only `specialized-domains/simple-responder` fixture remains disabled; 7 incomplete source files remain quarantined and excluded from active discovery.

An agent profile does not install its named frameworks, connect services, grant credentials, guarantee factual accuracy, or provide persistent shared memory. Configure a model/provider before asking agents to perform model-backed work.
