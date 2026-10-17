#!/usr/bin/env python3
"""Install, verify, and remove bundled OpenCode v2 agent profiles.

OpenCode v2 must already be installed. This script manages project agent files
and its reversible project configuration change only; it never installs or
uninstalls the OpenCode CLI.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
SOURCE_AGENTS = PACKAGE_ROOT / ".opencode" / "agents"
MANIFEST = PACKAGE_ROOT / "AGENT-MANIFEST.csv"


def fail(message):
    raise RuntimeError(message)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def state_paths(project):
    state_home = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local" / "state")))
    key = hashlib.sha256(str(project).encode("utf-8")).hexdigest()[:20]
    root = state_home / "opencode-agent-pack" / key
    return root, root / "install-state.json"


def validate_package():
    if not SOURCE_AGENTS.is_dir() or not MANIFEST.is_file():
        fail("Package files are missing. Run this script from the complete extracted ZIP.")
    expected = {}
    for path in sorted(SOURCE_AGENTS.rglob("*.md")):
        rel = path.relative_to(SOURCE_AGENTS).as_posix()
        text = path.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not m:
            fail(f"Invalid agent frontmatter: {rel}")
        mode = re.search(r"(?m)^mode:\s*(primary|subagent|all)\s*$", m.group(1))
        desc = re.search(r"(?m)^description:\s*(.+)$", m.group(1))
        if not mode or not desc:
            fail(f"Missing V2 mode or description: {rel}")
        expected[rel] = {"source": path, "sha256": sha256(path), "mode": mode.group(1)}
    with MANIFEST.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    manifest_ids = {row["agent_id"] for row in rows}
    file_ids = {Path(rel).with_suffix("").as_posix() for rel in expected}
    if manifest_ids != file_ids or len(rows) != len(file_ids):
        fail(f"Package manifest mismatch: files={len(file_ids)}, manifest={len(manifest_ids)}")
    by_id = {row["agent_id"]: row for row in rows}
    for rel, rec in expected.items():
        agent_id = Path(rel).with_suffix("").as_posix()
        row = by_id[agent_id]
        if int(row["bytes_out"]) != rec["source"].stat().st_size:
            fail(f"Manifest output size is stale for agent: {agent_id}")
        if row.get("sha256_output") != rec["sha256"]:
            fail(f"Manifest output checksum mismatch for agent: {agent_id}")
    if len(expected) != 621:
        fail(f"Unexpected pack size ({len(expected)} agents); expected 621.")
    return expected


def project_path(value):
    p = Path(value).expanduser().resolve()
    if not p.is_dir():
        fail(f"Project directory does not exist: {p}")
    if p == Path(p.anchor) or p == Path.home().resolve():
        fail("Refusing to install into the filesystem root or the home directory; choose a project directory.")
    return p


def config_candidates(project):
    direct = [p for p in (project / "opencode.json", project / "opencode.jsonc") if p.exists()]
    hidden = [p for p in (project / ".opencode" / "opencode.json", project / ".opencode" / "opencode.jsonc") if p.exists()]
    # V2 merges direct project configs first and .opencode configs afterward,
    # so a single .opencode config has higher precedence than direct configs.
    return hidden if hidden else direct


def prepare_depth_change(project, enabled):
    if not enabled:
        return {"action": "skipped", "path": None, "original": None, "new_bytes": None}
    found = config_candidates(project)
    if len(found) > 1:
        fail("Found both opencode.json and opencode.jsonc at the same precedence level. Refusing to guess; merge experimental.subagent_depth: 2 into one effective config or use --no-depth-2.")
    if not found:
        path = project / "opencode.json"
        data = {"experimental": {"subagent_depth": 2}}
        return {"action": "created", "path": path, "original": None, "new_bytes": (json.dumps(data, indent=2) + "\n").encode()}
    path = found[0]
    original = path.read_bytes()
    try:
        data = json.loads(original.decode("utf-8"))
    except Exception as e:
        fail(f"Cannot safely edit {path}: it is not strict JSON (JSONC comments/trailing commas are left untouched). Merge experimental.subagent_depth: 2 manually or install with --no-depth-2. Details: {e}")
    if not isinstance(data, dict):
        fail(f"Cannot safely edit {path}: expected a JSON object at the root.")
    experimental = data.get("experimental", {})
    if not isinstance(experimental, dict):
        fail(f"Cannot safely edit {path}: existing 'experimental' value is not an object.")
    if experimental.get("subagent_depth") == 2:
        return {"action": "unchanged", "path": path, "original": original, "new_bytes": original}
    experimental["subagent_depth"] = 2
    data["experimental"] = experimental
    new_bytes = (json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return {"action": "modified", "path": path, "original": original, "new_bytes": new_bytes}


def version_of(binary, cwd=None, env=None):
    try:
        p = subprocess.run([str(binary), "--version"], cwd=cwd, env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, timeout=30)
    except Exception as e:
        fail(f"Could not run {binary} --version: {e}")
    if p.returncode != 0:
        fail(f"Could not read OpenCode version from {binary}: {p.stdout.strip()}")
    match = re.search(r"(?<!\d)(\d+)\.(\d+)\.(\d+)(?:[-+][A-Za-z0-9.-]+)?", p.stdout)
    if not match:
        fail(f"Unrecognized OpenCode version output: {p.stdout.strip()}")
    return p.stdout.strip(), int(match.group(1))


def resolve_cli():
    home = Path.home()
    local = home / ".opencode" / "bin" / "opencode"
    shim = home / ".opencode" / "bin" / "opencode2"
    if local.exists():
        output, major = version_of(local, cwd=home)
        if major != 2:
            fail(f"A non-V2 binary already exists at {local} ({output}); refusing to overwrite it.")
        return {"path": str(local), "version": output, "installed_by_script": False,
                "binary_sha256": sha256(local), "shim_path": str(shim) if shim.exists() else None,
                "shim_sha256": sha256(shim) if shim.exists() else None, "created_dirs": []}
    if shim.exists():
        fail(f"Found {shim} without a matching local V2 CLI; refusing to overwrite it.")
    external = shutil.which("opencode")
    if external:
        output, major = version_of(external, cwd=home)
        if major != 2:
            fail(f"A non-V2/package-managed OpenCode is on PATH ({external}: {output}). Per the official V2 migration guide, remove or resolve that installation manually before installing V2; this script will not uninstall package-managed software.")
        return {"path": str(Path(external).resolve()), "version": output, "installed_by_script": False,
                "binary_sha256": sha256(Path(external).resolve()), "shim_path": None,
                "shim_sha256": None, "created_dirs": []}
    fail("OpenCode v2 was not found. Install OpenCode v2 yourself first from https://opencode.ai/v2/docs/, then rerun this command. This agent installer will not install OpenCode.")


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try: os.unlink(tmp)
        except OSError: pass
        raise


def install(args):
    project = project_path(args.project)
    expected = validate_package()
    state_root, state_file = state_paths(project)
    if state_file.exists():
        fail(f"This project already has installer state at {state_file}. Run verify or uninstall first.")
    target_root = project / ".opencode" / "agents"
    conflicts = []
    already_same = []
    for rel, rec in expected.items():
        target = target_root / rel
        if target.exists():
            if sha256(target) == rec["sha256"]:
                already_same.append(rel)
            else:
                conflicts.append(str(target))
    if conflicts:
        fail("Refusing to overwrite existing agent files. Resolve these conflicts and retry:\n  " + "\n  ".join(conflicts[:30]))
    depth_plan = prepare_depth_change(project, not args.no_depth_2)
    # This pack never installs or removes the OpenCode CLI. Users must install V2 themselves.
    cli = resolve_cli()
    state_root.mkdir(parents=True, exist_ok=True)
    files_added = []
    dirs_created = []
    config_backup = None
    try:
        for rel in sorted(expected):
            src = expected[rel]["source"]
            dst = target_root / rel
            if dst.exists():
                continue
            missing = []
            parent = dst.parent
            while parent != project and not parent.exists():
                missing.append(parent)
                parent = parent.parent
            dst.parent.mkdir(parents=True, exist_ok=True)
            dirs_created.extend(str(p) for p in missing)
            shutil.copy2(src, dst)
            files_added.append({"path": str(dst), "sha256": expected[rel]["sha256"]})
        if depth_plan["action"] in ("created", "modified"):
            if depth_plan["action"] == "modified":
                config_backup = state_root / "project-config.original"
                atomic_write(config_backup, depth_plan["original"])
            atomic_write(depth_plan["path"], depth_plan["new_bytes"])
        state = {
            "version": 1,
            "project": str(project),
            "package_root": str(PACKAGE_ROOT),
            "expected_agent_count": len(expected),
            "agents_added": files_added,
            "agents_already_identical": already_same,
            "agent_dirs_created": dirs_created,
            "depth2": {"action": depth_plan["action"],
                       "path": str(depth_plan["path"]) if depth_plan["path"] else None,
                       "original_sha256": sha256_bytes(depth_plan["original"]) if depth_plan["original"] is not None else None,
                       "installed_sha256": sha256_bytes(depth_plan["new_bytes"]) if depth_plan["new_bytes"] is not None else None,
                       "backup": str(config_backup) if config_backup else None},
            "cli": cli,
        }
        atomic_write(state_file, (json.dumps(state, indent=2, ensure_ascii=False) + "\n").encode())
    except Exception:
        for rec in reversed(files_added):
            try: Path(rec["path"]).unlink(missing_ok=True)
            except OSError: pass
        if depth_plan["action"] == "modified" and depth_plan["path"].exists() and config_backup and config_backup.exists():
            atomic_write(depth_plan["path"], config_backup.read_bytes())
        elif depth_plan["action"] == "created" and depth_plan["path"].exists():
            depth_plan["path"].unlink()
        remove_empty_dirs(dirs_created)
        shutil.rmtree(state_root, ignore_errors=True)
        raise
    print(f"Installed {len(expected)} agent profiles into {target_root}")
    print(f"Detected existing OpenCode CLI: {cli['version']} at {cli['path']} (left untouched).")
    if depth_plan["action"] in ("created", "modified"):
        print(f"Enabled experimental.subagent_depth: 2 in {depth_plan['path']}")
    elif depth_plan["action"] == "unchanged":
        print(f"experimental.subagent_depth already equals 2; left unchanged in {depth_plan['path']}")
    else:
        print("experimental.subagent_depth was not changed (--no-depth-2).")
    print(f"State/backup record: {state_file}")
    print("Next: run this script with 'verify' from the same project and HOME.")


def remove_empty_dirs(paths):
    for raw in sorted(set(paths), key=lambda x: x.count(os.sep), reverse=True):
        p = Path(raw)
        try: p.rmdir()
        except OSError: pass


def locate_cli(project):
    local = Path.home() / ".opencode" / "bin" / "opencode"
    if local.is_file():
        return local
    found = shutil.which("opencode")
    return Path(found).resolve() if found else None


def runtime_list(binary, project, expected_ids):
    env = os.environ.copy()
    local_bin = str(Path(binary).parent)
    env["PATH"] = local_bin + os.pathsep + env.get("PATH", "")
    last_ids = set()
    for attempt in range(3):
        p = subprocess.run([str(binary), "debug", "agents"], cwd=project, env=env,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, timeout=120)
        if p.returncode:
            fail("OpenCode v2 could not enumerate agents at runtime. Output:\n" + p.stdout[-5000:])
        try:
            data = json.loads(p.stdout)
        except Exception as e:
            fail(f"OpenCode v2 debug agents did not return valid JSON: {e}")
        if not isinstance(data, list):
            fail("OpenCode v2 debug agents returned an unexpected non-list result.")
        last_ids = {row.get("id") for row in data if isinstance(row, dict) and isinstance(row.get("id"), str)}
        if expected_ids.issubset(last_ids):
            return last_ids
        if attempt < 2:
            time.sleep(1)
    return last_ids


def verify(args):
    project = project_path(args.project)
    expected = validate_package()
    errors = []
    target_root = project / ".opencode" / "agents"
    for rel, rec in expected.items():
        target = target_root / rel
        if not target.is_file():
            errors.append(f"missing: {rel}")
        elif sha256(target) != rec["sha256"]:
            errors.append(f"content differs from bundle: {rel}")
    config_files = config_candidates(project)
    depth2 = None
    if len(config_files) > 1:
        errors.append("multiple project config files make effective subagent_depth ambiguous")
    elif config_files:
        try:
            depth2 = json.loads(config_files[0].read_text("utf-8")).get("experimental", {}).get("subagent_depth") == 2
        except Exception as e:
            errors.append(f"could not parse project config: {e}")
    else:
        depth2 = False
    state_root, state_file = state_paths(project)
    state = None
    if state_file.exists():
        try: state = json.loads(state_file.read_text("utf-8"))
        except Exception as e: errors.append(f"invalid install state: {e}")
    if state and state.get("depth2", {}).get("action") != "skipped" and depth2 is not True:
        errors.append("experimental.subagent_depth: 2 is not active in project config")
    binary = locate_cli(project)
    cli_version = None
    runtime_count = None
    if not binary:
        errors.append("OpenCode CLI not found")
    else:
        try:
            cli_version, major = version_of(binary, cwd=project)
            if major != 2: errors.append(f"not OpenCode v2: {cli_version}")
            active = [rel for rel, rec in expected.items()
                      if rec["mode"] in ("primary", "all", "subagent")
                      and not re.search(r"(?m)^disabled:\s*true\s*$", (rec["source"].read_text("utf-8").split("---",2)[1] if "---" in rec["source"].read_text("utf-8") else ""))]
            # Disabled profiles intentionally remain installed but should not be discoverable.
            expected_ids = {Path(rel).with_suffix("").as_posix() for rel in active}
            listed_ids = runtime_list(binary, project, expected_ids)
            all_packaged_ids = {Path(rel).with_suffix("").as_posix() for rel in expected}
            missing_ids = sorted(expected_ids - listed_ids)
            if missing_ids:
                errors.append(f"runtime did not register {len(missing_ids)} enabled agents (first 12: {', '.join(missing_ids[:12])}). Ensure OpenCode recognizes this directory as the project root.")
            visible_disabled = sorted((all_packaged_ids - expected_ids) & listed_ids)
            if visible_disabled:
                errors.append("runtime unexpectedly exposed disabled profiles: " + ", ".join(visible_disabled))
            runtime_count = len(active)
        except Exception as e:
            errors.append(str(e))
    if errors:
        print("VERIFY FAILED")
        for e in errors: print(" - " + e)
        return 1
    print(f"VERIFY PASSED: {len(expected)} packaged agent files match byte-for-byte.")
    print(f"CLI reports {cli_version}; runtime listed all {runtime_count} enabled custom agent IDs.")
    print("Project experimental.subagent_depth: 2 is active." if depth2 else "Project experimental.subagent_depth: 2 is not active (the install was explicitly depth-2-disabled).")
    if state_file.exists(): print(f"Owned install state: {state_file}")
    return 0


def uninstall(args):
    project = project_path(args.project)
    state_root, state_file = state_paths(project)
    if not state_file.is_file():
        fail(f"No install record for this project at {state_file}; refusing to remove files by guesswork.")
    state = json.loads(state_file.read_text("utf-8"))
    if state.get("project") != str(project):
        fail("Install state project path does not match; refusing removal.")
    issues = []
    for rec in reversed(state.get("agents_added", [])):
        p = Path(rec["path"])
        if not p.exists(): continue
        if not p.is_file() or sha256(p) != rec["sha256"]:
            issues.append(f"preserved changed agent file: {p}")
        else:
            p.unlink()
    config = state.get("depth2", {})
    if config.get("action") in ("created", "modified"):
        p = Path(config["path"])
        if p.exists():
            try: current_hash=sha256(p)
            except OSError: current_hash=None
            if current_hash != config.get("installed_sha256"):
                issues.append(f"preserved project config changed since install: {p}")
            elif config["action"] == "created":
                p.unlink()
            else:
                backup=Path(config["backup"])
                if not backup.is_file() or sha256(backup) != config.get("original_sha256"):
                    issues.append(f"could not safely restore project config backup: {backup}")
                else:
                    atomic_write(p,backup.read_bytes())
    remove_empty_dirs(state.get("agent_dirs_created", []))
    # OpenCode is external user software and is never removed by this pack.
    if issues:
        state["uninstall_issues"] = issues
        atomic_write(state_file,(json.dumps(state,indent=2,ensure_ascii=False)+"\n").encode())
        print("UNINSTALL PARTIAL; user-modified files were preserved:")
        for issue in issues: print(" - "+issue)
        print(f"State retained for manual review: {state_file}")
        return 2
    backup = config.get("backup")
    if backup:
        Path(backup).unlink(missing_ok=True)
    state_file.unlink()
    try: state_root.rmdir()
    except OSError: pass
    try: state_root.parent.rmdir()
    except OSError: pass
    print(f"Removed this install's unchanged agent files and managed depth-2 setting from {project}.")
    print("The OpenCode CLI was left untouched.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Install, verify, and safely remove bundled OpenCode V2 agent profiles. OpenCode itself is never installed or removed.")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("install", "verify", "uninstall"):
        sp = sub.add_parser(name)
        sp.add_argument("--project", default=".", help="Existing project directory (default: current directory)")
        if name == "install":
            sp.add_argument("--no-depth-2", action="store_true", help="Do not set experimental.subagent_depth; nested team delegation will not work")
    args = parser.parse_args()
    try:
        if args.command == "install": install(args); return 0
        if args.command == "verify": return verify(args)
        if args.command == "uninstall": return uninstall(args)
    except Exception as e:
        print("ERROR: " + str(e), file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
