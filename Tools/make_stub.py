# -*- coding: utf-8 -*-
"""Write (or check) the settings-only StatCoach folder that ships next to StatCap.

    python Tools/make_stub.py           rewrite StatCoach/*.toc from the StatCap TOCs
    python Tools/make_stub.py --check   fail if StatCoach/*.toc are out of step

StatCap was called StatCoach until 1.2.0. The game keeps an addon's saved settings
under its folder name, and addon apps delete the old StatCoach folder when they
update to StatCap - so without a StatCoach folder of its own, StatCap could never
read the old settings. That folder holds one TOC and no code: load-on-demand,
SavedVariables StatCoachDB. StatCap loads it once, copies the settings and switches
it off (StatCap.lua, ns.TakeOverOldName).

There is one stub TOC per StatCap TOC, with the old package's file name for that
client (StatCap_Mainline.toc -> StatCoach_Mainline.toc), so a player who unzips over
the old StatCoach folder replaces its TOC and the old code stops loading. Each one
carries the same Interface and Version lines as its StatCap TOC: an out-of-date
folder would not load, and nothing would be carried. The release workflow keeps one
of them per flavor in its reduce step, exactly as it keeps one StatCap TOC, and runs
--check first.

The files are committed, not generated at package time, because the packager leaves
out every file git does not track.
"""
import glob
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUB = "StatCoach"


def wanted():
    """{stub file name: text} for every StatCap TOC in the repo."""
    template = io.open(os.path.join(HERE, "Tools", "stub.toc"), encoding="utf-8").read()
    out = {}
    for path in sorted(glob.glob(os.path.join(HERE, "StatCap*.toc"))):
        text = io.open(path, encoding="utf-8-sig").read()
        interface = re.search(r"^## Interface:\s*(.+?)\s*$", text, re.M)
        version = re.search(r"^## Version:\s*(.+?)\s*$", text, re.M)
        if not (interface and version):
            sys.exit("make_stub: %s has no Interface or Version line" % os.path.basename(path))
        name = os.path.basename(path).replace("StatCap", STUB, 1)
        out[name] = template.format(interface=interface.group(1), version=version.group(1))
    if not out:
        sys.exit("make_stub: no StatCap TOC found in %s" % HERE)
    return out


def main():
    check = "--check" in sys.argv[1:]
    folder = os.path.join(HERE, STUB)
    want = wanted()
    have = {os.path.basename(p): io.open(p, encoding="utf-8").read()
            for p in glob.glob(os.path.join(folder, "*"))} if os.path.isdir(folder) else {}
    if check:
        problems = []
        for name, text in want.items():
            if name not in have:
                problems.append("%s/%s is missing" % (STUB, name))
            elif have[name].replace("\r\n", "\n") != text:
                problems.append("%s/%s differs from what its StatCap TOC asks for" % (STUB, name))
        for name in sorted(set(have) - set(want)):
            problems.append("%s/%s has no StatCap TOC behind it" % (STUB, name))
        if problems:
            sys.exit("make_stub --check:\n  " + "\n  ".join(problems)
                     + "\nRun: python Tools/make_stub.py, then commit the StatCoach folder.")
        print("StatCoach folder in step with the StatCap TOCs: %s" % ", ".join(sorted(want)))
        return
    os.makedirs(folder, exist_ok=True)
    for name in sorted(set(have) - set(want)):
        os.remove(os.path.join(folder, name))
    for name, text in sorted(want.items()):
        io.open(os.path.join(folder, name), "w", encoding="utf-8", newline="\n").write(text)
        print("wrote %s/%s" % (STUB, name))


if __name__ == "__main__":
    main()
