#!/usr/bin/env bash
# Ather Agents bootstrapper for OpenCode v2. This script installs agent files only.
set -Eeuo pipefail

REPO="Alqudimi/ather-agents"
BRANCH="main"
REPO_ARCHIVE="https://github.com/${REPO}/archive/refs/heads/${BRANCH}.tar.gz"

usage() {
  cat <<'EOF'
Usage:
  curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- install [--project PATH] [--no-depth-2]
  curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- verify [--project PATH]
  curl -fsSL https://raw.githubusercontent.com/Alqudimi/ather-agents/main/install.sh | bash -s -- uninstall [--project PATH]

OpenCode v2 must already be installed. This script never installs OpenCode.
EOF
}

fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

command_name="${1:-}"
if [[ -z "$command_name" || "$command_name" == "-h" || "$command_name" == "--help" ]]; then
  usage
  [[ -n "$command_name" ]] && exit 0 || exit 2
fi
case "$command_name" in
  install|verify|uninstall) shift ;;
  *) usage >&2; fail "Unknown command: $command_name" ;;
esac

for cmd in curl tar python3; do
  command -v "$cmd" >/dev/null 2>&1 || fail "Required command '$cmd' is missing. Install it and retry."
done

if [[ "$command_name" != "uninstall" ]]; then
  # The Python installer also checks the version; this avoids fetching the package before then.
  cli=""
  if [[ -x "$HOME/.opencode/bin/opencode" ]]; then
    cli="$HOME/.opencode/bin/opencode"
  elif command -v opencode >/dev/null 2>&1; then
    cli="$(command -v opencode)"
  fi
  if [[ -z "$cli" ]]; then
    fail "OpenCode v2 was not found. Install OpenCode v2 yourself first (https://opencode.ai/v2/docs/), then rerun this command. This script will not install it."
  fi
  version_output="$("$cli" --version 2>&1)" || fail "Could not read OpenCode version from $cli: $version_output"
  if ! grep -Eq '(^|[^0-9])2\.[0-9]+\.[0-9]+' <<<"$version_output"; then
    fail "OpenCode v2 is required, but '$cli --version' returned: $version_output. Install OpenCode v2 yourself first (https://opencode.ai/v2/docs/). This script will not install or replace it."
  fi
fi

workdir="$(mktemp -d "${TMPDIR:-/tmp}/ather-agents.XXXXXXXX")"
cleanup() { rm -rf -- "$workdir"; }
trap cleanup EXIT INT TERM
archive="$workdir/repo.tar.gz"
curl --fail --silent --show-error --location --retry 2 --connect-timeout 15 --max-time 180 "$REPO_ARCHIVE" --output "$archive" || fail "Could not download the Ather Agents repository archive."
tar -xzf "$archive" -C "$workdir" || fail "Downloaded repository archive is invalid."

installer=""
while IFS= read -r -d '' candidate; do
  if [[ -f "${candidate%/scripts/install-opencode-v2.py}/AGENT-MANIFEST.csv" && -d "${candidate%/scripts/install-opencode-v2.py}/.opencode/agents" ]]; then
    installer="$candidate"
    break
  fi
done < <(find "$workdir" -type f -path '*/scripts/install-opencode-v2.py' -print0)
[[ -n "$installer" ]] || fail "Could not find the agent package in the downloaded repository."

args=("$command_name")
if [[ "$command_name" == "install" ]]; then
  args+=("--project" "$(pwd)")
fi
# Forward caller options; Python's parser supports the same project selection.
args+=("$@")
if [[ "$command_name" == "install" ]]; then
  python3 "$installer" "${args[@]}"
else
  python3 "$installer" "${args[@]}"
fi
