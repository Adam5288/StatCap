# -*- coding: utf-8 -*-
"""Pull ONE version's notes out of CHANGELOG.md into RELEASE_NOTES.md.

The packager ships whatever RELEASE_NOTES.md contains. StatCap releases its
flavors on their own schedules - 1.1.17, 1.1.18 and 1.1.19 were TBC only, 1.1.11
and 1.1.13 were retail only - so the notes for a release are the section for that
version AND that flavor, never both.

An empty changelog is also the one thing Wago refuses outright (HTTP 422), and it
does so AFTER CurseForge has already accepted the file, which leaves a version
live on one store and missing on the other. So a missing section is a hard error
here, before anything is uploaded.

    python Tools/release_notes.py 1.1.21 tbc
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANGELOG = os.path.join(HERE, "CHANGELOG.md")
OUT = os.path.join(HERE, "RELEASE_NOTES.md")

FLAVOR_LABEL = {"tbc": "TBC", "bcc": "TBC", "retail": "Retail", "mainline": "Retail",
                "forever": "Forever", "mists": "Mists", "era": "Classic Era"}


# The addon was called StatCoach until 1.2.0, and the history keeps the headings
# it shipped under. A section may also be written once for every flavor, with no
# flavor in its heading (StatCap 1.2.0, the rename, went to all five clients).
NAME = r"Stat(?:Cap|Coach)"


def section(version, label):
    """The text under '# StatCap <version> (<label>)' - or, when that flavor has no
    section of its own, under '# StatCap <version>' - up to the next heading.
    Returns (body, shared): shared is True when the flavor-less section was used."""
    text = io.open(CHANGELOG, encoding="utf-8").read()
    m = None
    for tail in (r" \(%s\)" % re.escape(label), ""):
        heading = re.compile(r"^# %s %s%s\s*$" % (NAME, re.escape(version), tail), re.M)
        m = heading.search(text)
        if m:
            break
    if not m:
        return None, False
    rest = text[m.end():]
    nxt = re.search(r"^# %s " % NAME, rest, re.M)
    body = rest[: nxt.start()] if nxt else rest
    # The separator between entries belongs to the file, not to the entry.
    return body.strip().rstrip("-").strip(), tail == ""


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: release_notes.py <version> <tbc|retail|forever|mists|era>")
    version = sys.argv[1].lstrip("vV")
    flavor = sys.argv[2].lower()
    label = FLAVOR_LABEL.get(flavor)
    if not label:
        sys.exit("unknown flavor %r - expected tbc, retail, forever, mists or era" % sys.argv[2])

    body, shared = section(version, label)
    if not body:
        sys.exit(
            "CHANGELOG.md has no '# StatCap %s (%s)' or '# StatCap %s' section.\n"
            "Write the notes for this release before publishing - Wago rejects an\n"
            "empty changelog, and it does so after CurseForge has taken the file."
            % (version, label, version)
        )

    # Every release ends with the support line. It lives here, not in
    # CHANGELOG.md, so it cannot be forgotten, cannot be worded two ways, and
    # does not repeat down the file when someone reads the whole history.
    footer = ("StatCap is free and stays free. If you would like to support "
              "the work: https://ko-fi.com/adam5288")
    # A section shared by every flavor gets a heading without the flavor, so the
    # GitHub release - whose text the LAST publish run of a version writes - reads
    # the same whichever flavor ran last.
    heading = "# StatCap %s" % version if shared else "# StatCap %s (%s)" % (version, label)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(
        "%s\n\n%s\n\n---\n\n%s\n" % (heading, body, footer)
    )
    print("RELEASE_NOTES.md written for %s (%s), %d characters."
          % (version, label, len(body)))


if __name__ == "__main__":
    main()
