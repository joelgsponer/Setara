#!/bin/bash
# praxis-version: 0.4.1 (= plugin.json; tb-refresh.sh moves toolbox copies forward only)
# praxis tb-sync-skills — mirror <toolbox>/skills/ into <project>/.claude/skills/.
# Marker-guarded: only ever creates/updates/deletes dirs carrying .praxis-managed;
# user-authored skills in .claude/skills/ are untouchable (spec decision 6).
# The marker records the mirror's name (line 1) and a checksum of what sync wrote
# (line 2). So a copy or rename of a mirror (cp -R carries the hidden marker) is the
# user's, and a mirror edited by hand is never overwritten or deleted: WARN instead.
# A mirror identical to its source is sync's again (after an edit moved into skills/),
# and a marker a merge left conflicted is re-synced. Symlinks are never followed: not a
# mirror dir, not the toolbox dir, not .claude or .claude/skills. An old-style empty
# marker (praxis <= 0.3.0) is trusted to be overwritten from its source skill, but
# without a source it may be the user's copy, so it is kept with a WARN, never deleted.
# Usage: tb-sync-skills.sh [toolbox-dir]   Exit: 0 ok (conflicts warn), 2 no toolbox.
set -u
TB="${1:-}"
if [ -z "$TB" ]; then
  if [ -f "toolbox/index.md" ]; then TB="toolbox"
  elif [ -f ".claude/toolbox/index.md" ]; then TB=".claude/toolbox"
  else echo "tb-sync: no toolbox found"; exit 2; fi
fi
# never resolve a symlinked toolbox (or its .claude parent): a cloned repo can point one
# outside itself, and everything below would be written there
case "${TB%/}" in .claude/toolbox|*/.claude/toolbox) [ -L "${TB%/}" ] || [ -L "${TB%/toolbox}" ] ;; *) [ -L "${TB%/}" ] ;; esac \
  && { echo "tb-sync: $TB (or its .claude) is a symlink — refusing: praxis state must be a real dir in the repo"; exit 2; }
TB=$(CDPATH='' cd -P -- "$TB" 2>/dev/null && pwd) || { echo "tb-sync: not a directory: ${1:-}"; exit 2; }
[ -f "$TB/index.md" ] || { echo "tb-sync: $TB is not a toolbox (no index.md)"; exit 2; }
case "$TB" in
  */.claude/toolbox) PROOT="${TB%/.claude/toolbox}" ;;
  *) PROOT=$(dirname "$TB") ;;
esac
DEST="$PROOT/.claude/skills"
if [ -L "$PROOT/.claude" ] || [ -L "$DEST" ]; then
  echo "tb-sync: $DEST (or .claude) is a symlink — refusing to write through it"; exit 2
fi
mkdir -p "$DEST"
# Content checksum of a mirror (the same function lives in tb-lint.sh — keep identical).
# Byte-wise in the C locale on every platform; CRs stripped (autocrlf checkouts); the
# marker, Finder litter (.DS_Store, ._*), Python bytecode a skill's script leaves behind,
# and — when the mirror travels through git — every file git ignores are not content.
# Where git cannot answer (no repo, "dubious ownership") ignored files do count, so a
# mirror holding one may read as edited there; bytecode is excluded either way. Git is
# asked from the project root only (see msum): a toolbox in a subdirectory of a larger
# repo uses that repo's .gitignore, found by walking up from the project root.
msum() { (CDPATH='' cd -- "$1" || exit; export LC_ALL=C
  l=$(find . -type f ! -name .praxis-managed ! -name .DS_Store ! -name '._*' ! -name '*.pyc' ! -path '*/__pycache__/*' | sort)
  # git never runs with its cwd inside the mirror or the skill: a repo planted there
  # (.git, or a bare layout with core.bare=false) would have its core.fsmonitor executed.
  # It is asked from $PROOT with paths relative to it, so discovery starts at the project
  # root and walks up (a toolbox inside a larger repo keeps that repo's .gitignore); a
  # planted repo sits below the root and is never reached. fsmonitor is off and a bare
  # repo needs an explicit opt-in.
  rel=""; case "$1" in "$PROOT"/*) rel=${1:$((${#PROOT}+1))}; rel=${rel%/} ;; esac
  if [ -n "$rel" ]; then
    gi() { git -C "$PROOT" -c core.fsmonitor= -c safe.bareRepository=explicit -c core.quotePath=false check-ignore "$@" 2>/dev/null; }
    gi -q "$rel/.praxis-managed"
    if [ "$?" = 1 ]; then
      i=$(printf '%s\n' "$l" | while IFS= read -r f; do [ -n "$f" ] && printf '%s\n' "$rel/${f#./}"; done | gi --stdin \
        | while IFS= read -r f; do printf './%s\n' "${f:$((${#rel}+1))}"; done)
      [ -z "$i" ] || l=$(printf '%s\n' "$l" | grep -vxF -- "$i")
    fi
  fi
  printf '%s\n' "$l" | while IFS= read -r f; do [ -n "$f" ] || continue; printf '%s ' "$f"; tr -d '\r' < "$f" | cksum; done) | cksum; }
# mstate <dir>: 0 sync's own mirror (untouched, identical to its source, or with a marker
# a merge left conflicted); 1 not a mirror (unmarked, a symlink, or a copy/rename of
# one); 2 old-style empty marker; 3 a mirror edited by hand
mstate() {
  [ -L "$1" ] && return 1
  [ -f "$1/.praxis-managed" ] || return 1
  m=$(tr -d '\r' < "$1/.praxis-managed")
  case "$m" in *"<<<<<<< "*) return 0 ;; esac
  n=$(printf '%s\n' "$m" | sed -n 1p); c=$(printf '%s\n' "$m" | sed -n 2p)
  [ -z "$n" ] && return 2
  [ "$n" = "${1##*/}" ] || return 1
  [ "$c" = "$(msum "$1")" ] && return 0
  [ -d "$TB/skills/${1##*/}" ] && [ "$(msum "$TB/skills/${1##*/}")" = "$(msum "$1")" ] && return 0
  return 3
}
synced=0; removed=0; skipped=0
for d in "$TB"/skills/*/; do
  [ -d "$d" ] || continue
  name=$(basename "$d")
  if [ ! -f "$d/SKILL.md" ]; then
    echo "tb-sync: WARN skills/$name has no SKILL.md — skipped"; skipped=$((skipped+1)); continue
  fi
  if [ -e "$DEST/$name" ] || [ -L "$DEST/$name" ]; then
    mstate "$DEST/$name"; rc=$?
    if [ "$rc" = 1 ]; then
      echo "tb-sync: WARN .claude/skills/$name is not praxis's (no marker, a symlink, or a copy of another mirror) — skipped; rename one of the two"
      skipped=$((skipped+1)); continue
    elif [ "$rc" = 3 ]; then
      echo "tb-sync: WARN .claude/skills/$name was edited by hand — not overwritten (move the edit into skills/$name and the next sync takes the mirror back, or delete the mirror)"
      skipped=$((skipped+1)); continue
    fi
  fi
  rm -rf -- "${DEST:?}/${name:?}"
  cp -R "$d" "$DEST/$name"
  rm -f "$DEST/$name/.praxis-managed"
  printf '%s\n%s\n' "$name" "$(msum "$DEST/$name")" > "$DEST/$name/.praxis-managed"
  synced=$((synced+1))
done
for d in "$DEST"/*/; do
  d=${d%/}
  [ -d "$d" ] || continue
  name=${d##*/}
  [ -d "$TB/skills/$name" ] && continue
  mstate "$d"; rc=$?
  case "$rc" in
    1) continue ;;
    2) echo "tb-sync: WARN .claude/skills/$name has an old-style praxis marker but no source skill — kept: delete it if its skill was retired, or remove its .praxis-managed to keep it as yours"
       skipped=$((skipped+1)); continue ;;
    3) echo "tb-sync: WARN .claude/skills/$name: source skill gone but the mirror was edited by hand — kept"
       skipped=$((skipped+1)); continue ;;
  esac
  rm -rf -- "$d"
  removed=$((removed+1))
done
echo "tb-sync: $synced synced, $removed removed, $skipped skipped"
exit 0
