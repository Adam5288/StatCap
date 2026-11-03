# -*- coding: utf-8 -*-
"""Build StatCap's package for one flavor exactly as the release workflow does, and
install it into that flavor's client - or build all five and install nothing.

    python Tools/sync_clients.py forever             # build, install into _forever_
    python Tools/sync_clients.py retail _retail_     # name the client folder yourself
    python Tools/sync_clients.py --check             # build all five, install nothing

The package is made the way the BigWigs packager makes it, not written down a
second time:
  1. only files git tracks (the packager leaves out everything untracked, so an
     uncommitted new file is reported and left out here too);
  2. the workflow's own "Reduce the tree" step from .github/workflows/release.yml;
  3. .pkgmeta's ignore list, and its move-folders, which puts the settings-only
     StatCoach folder next to StatCap (StatCap was called StatCoach until 1.2.0).
Installing replaces exactly the folders the package holds - StatCap and StatCoach -
and nothing else. Replacing StatCoach is what an addon app does on update: the old
full StatCoach folder goes, the settings-only one comes.
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
STUB = "StatCoach"
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


def pkgmeta():
    return yaml.safe_load(io.open(os.path.join(HERE, ".pkgmeta"), encoding="utf-8")) or {}


def git_files(*args):
    out = subprocess.run(["git", "-C", HERE, "ls-files", "-z"] + list(args), capture_output=True, check=True).stdout
    return [p for p in out.decode("utf-8").split("\0") if p]


def toc_line(text, key):
    m = re.search(r"^## %s:\s*(.+?)\s*$" % key, text, re.M)
    return m.group(1) if m else None


def build(flavor, into, quiet=False):
    """Package one flavor under <into>; return {folder name: path} for the zip's top folders."""
    pkg = os.path.join(into, NAME)
    for rel in git_files():                                   # 1. tracked files only
        src = os.path.join(HERE, rel)
        if os.path.isfile(src):
            dst = os.path.join(pkg, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
    untracked = git_files("--others", "--exclude-standard")
    if untracked and not quiet:
        print("note: untracked, so the packager would leave these out: %s" % ", ".join(untracked))

    env = dict(os.environ, GITHUB_ENV=os.path.join(into, "github_env.txt"))
    script = reduce_step().replace("${{ inputs.flavor }}", flavor)   # 2. the workflow's own step
    r = subprocess.run([git_bash(), "-e", "-c", script], cwd=pkg, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("reduce step failed for %s:\n%s%s" % (flavor, r.stdout, r.stderr))

    meta = pkgmeta()                                          # 3. ignore + move-folders
    for name in os.listdir(pkg):
        if name.startswith(".") or name in set(meta.get("ignore") or []):
            path = os.path.join(pkg, name)
            shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
    folders = {NAME: pkg}
    for src, dest in (meta.get("move-folders") or {}).items():
        if not src.startswith(NAME + "/"):
            sys.exit("move-folders entry %r does not start with %s/" % (src, NAME))
        moved = os.path.join(pkg, *src.split("/")[1:])
        if not os.path.isdir(moved):
            sys.exit("%s package: move-folders source %s is missing" % (flavor, src))
        shutil.move(moved, os.path.join(into, dest))
        folders[dest] = os.path.join(into, dest)

    # the StatCap folder
    tocs = sorted(f for f in os.listdir(pkg) if f.endswith(".toc"))
    if len(tocs) != 1 or not tocs[0].startswith(NAME):
        sys.exit("%s package should carry one %s TOC, has %s" % (flavor, NAME, tocs))
    toc = io.open(os.path.join(pkg, tocs[0]), encoding="utf-8-sig").read()
    version, interface = toc_line(toc, "Version"), toc_line(toc, "Interface")
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
        sys.exit("%s package: the StatCap folder still has old-name files: %s" % (flavor, old))

    # the settings-only StatCoach folder
    stub = folders.get(STUB)
    if not stub:
        sys.exit("%s package has no %s folder - .pkgmeta move-folders?" % (flavor, STUB))
    stub_files = sorted(os.listdir(stub))
    expect = ("StatCoach.toc" if flavor == "forever" else tocs[0].replace(NAME, STUB, 1))
    if stub_files != [expect]:
        sys.exit("%s package: %s should hold only %s, holds %s" % (flavor, STUB, expect, stub_files))
    s = io.open(os.path.join(stub, expect), encoding="utf-8-sig").read()
    for key, want in (("Interface", interface), ("Version", version),
                      ("LoadOnDemand", "1"), ("SavedVariables", "StatCoachDB")):
        if toc_line(s, key) != want:
            sys.exit("%s package: %s/%s has %s %r, expected %r" % (flavor, STUB, expect, key, toc_line(s, key), want))
    if [l for l in s.splitlines() if l.strip() and not l.startswith("#")]:
        sys.exit("%s package: %s/%s must list no files" % (flavor, STUB, expect))

    print("%-8s %s  v%s  interface %s  |  %s  |  %s/%s" % (flavor, tocs[0], version, interface, " ".join(lua), STUB, expect))
    return folders


def install(folders, client):
    addons = os.path.join(WOW, client, "Interface", "AddOns")
    if not os.path.isdir(addons):
        sys.exit("no AddOns folder for %s - is that client installed?" % client)
    for name, src in folders.items():
        if name not in (NAME, STUB):            # never anything but our own folders
            sys.exit("refusing to install %s" % name)
        dest = os.path.join(addons, name)
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
        print("installed -> %s" % dest)


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        sys.exit(__doc__)
    with tempfile.TemporaryDirectory() as tmp:
        if args[0] == "--check":
            for i, flavor in enumerate(("forever", "retail", "tbc", "era", "mists")):
                build(flavor, os.path.join(tmp, flavor), quiet=i > 0)
            return
        flavor = args[0].lower()
        if flavor not in CLIENT:
            sys.exit("unknown flavor %r - expected %s" % (flavor, ", ".join(CLIENT)))
        client = args[1] if len(args) > 1 else CLIENT[flavor]
        install(build(flavor, os.path.join(tmp, flavor)), client)


if __name__ == "__main__":
    main()
