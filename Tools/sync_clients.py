# -*- coding: utf-8 -*-
"""Build StatCap's package for one flavor exactly as the release workflow does, and
install it into that flavor's client - or build all five and install nothing.

    python Tools/sync_clients.py forever             # build, install into _forever_
    python Tools/sync_clients.py retail _retail_     # name the client folder yourself
    python Tools/sync_clients.py --check             # build all five, install nothing

The file selection is not written down twice. This script runs the workflow's own
"Reduce the tree" step out of .github/workflows/release.yml, and leaves out what
.pkgmeta's ignore list leaves out, so a package installed by hand is the package
the stores get. Only the StatCap folder in AddOns is replaced; every other folder,
an old StatCoach copy included, is left alone.
"""
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = "StatCap"
WOW = r"C:\Program Files (x86)\World of Warcraft"
CLIENT = {"forever": "_forever_", "retail": "_retail_", "tbc": "_anniversary_",
          "era": "_classic_era_", "mists": "_classic_"}


def git_bash():
    """Git for Windows' bash, never WSL's: the step must see this folder's files."""
    git = shutil.which("git")
    root = os.path.dirname(git) if git else ""
    for _ in range(4):                       # ...\Git\cmd\git.exe or ...\Git\mingw64\bin\git.exe
        root = os.path.dirname(root)
        for cand in (os.path.join(root, "bin", "bash.exe"), os.path.join(root, "usr", "bin", "bash.exe")):
            if os.path.isfile(cand):
                return cand
    sys.exit("Git Bash not found - the workflow's reduce step is a bash script")


def reduce_step():
    wf = yaml.safe_load(io.open(os.path.join(HERE, ".github", "workflows", "release.yml"), encoding="utf-8"))
    for step in wf["jobs"]["release"]["steps"]:
        if str(step.get("name", "")).startswith("Reduce the tree"):
            return step["run"]
    sys.exit("release.yml has no 'Reduce the tree' step")


def ignored():
    meta = yaml.safe_load(io.open(os.path.join(HERE, ".pkgmeta"), encoding="utf-8"))
    return set(meta.get("ignore") or []) | {".git", ".pkgmeta", ".release", "RELEASE_NOTES.md"}


def build(flavor, into):
    """Package one flavor into <into>/StatCap and return that folder."""
    skip = ignored()
    pkg = os.path.join(into, NAME)
    shutil.copytree(HERE, pkg, ignore=lambda d, names: [n for n in names if os.path.samefile(d, HERE) and n in skip])
    env = dict(os.environ, GITHUB_ENV=os.path.join(into, "github_env.txt"))
    script = reduce_step().replace("${{ inputs.flavor }}", flavor)
    r = subprocess.run([git_bash(), "-e", "-c", script], cwd=pkg, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("reduce step failed for %s:\n%s%s" % (flavor, r.stdout, r.stderr))

    tocs = sorted(f for f in os.listdir(pkg) if f.endswith(".toc"))
    if len(tocs) != 1 or not tocs[0].startswith(NAME):
        sys.exit("%s package should carry one %s TOC, has %s" % (flavor, NAME, tocs))
    toc = io.open(os.path.join(pkg, tocs[0]), encoding="utf-8-sig").read()
    version = re.search(r"^## Version:\s*(\S+)", toc, re.M).group(1)
    interface = re.search(r"^## Interface:\s*(.+)$", toc, re.M).group(1).strip()
    listed = [l.strip() for l in toc.splitlines() if l.strip() and not l.startswith("#")]
    missing = [l for l in listed if not os.path.isfile(os.path.join(pkg, l.replace("\\", os.sep)))]
    if missing:
        sys.exit("%s package: the TOC lists files it does not carry: %s" % (flavor, missing))
    lua = sorted(f for f in os.listdir(pkg) if f.endswith(".lua"))
    unlisted = [f for f in lua if f not in listed]
    if unlisted:
        sys.exit("%s package carries Lua the TOC never loads: %s" % (flavor, unlisted))
    old = [f for f in os.listdir(pkg) if "StatCoach" in f]
    if old:
        sys.exit("%s package still has old-name files: %s" % (flavor, old))
    print("%-8s %s  v%s  interface %s  |  %s" % (flavor, tocs[0], version, interface, " ".join(lua)))
    return pkg


def install(pkg, client):
    addons = os.path.join(WOW, client, "Interface", "AddOns")
    if not os.path.isdir(addons):
        sys.exit("no AddOns folder for %s - is that client installed?" % client)
    dest = os.path.join(addons, NAME)
    if os.path.basename(dest) != NAME:          # never anything but our own folder
        sys.exit("refusing to replace %s" % dest)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    shutil.copytree(pkg, dest)
    print("installed -> %s" % dest)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        sys.exit(__doc__)
    with tempfile.TemporaryDirectory() as tmp:
        if args[0] == "--check":
            for flavor in ("forever", "retail", "tbc", "era", "mists"):
                build(flavor, os.path.join(tmp, flavor))
            return
        flavor = args[0].lower()
        if flavor not in CLIENT:
            sys.exit("unknown flavor %r - expected %s" % (flavor, ", ".join(CLIENT)))
        client = args[1] if len(args) > 1 else CLIENT[flavor]
        install(build(flavor, os.path.join(tmp, flavor)), client)


if __name__ == "__main__":
    main()
