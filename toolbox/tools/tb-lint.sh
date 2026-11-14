#!/bin/bash
# praxis-version: 0.4.1 (= plugin.json; tb-refresh.sh moves toolbox copies forward only)
# praxis tb-lint — zero-token toolbox health check (the lint floor).
# Usage: tb-lint.sh [--static] [toolbox-dir]  (default: resolve from CWD)
#   --static  never EXECUTE toolbox content (skips the `bin/* --help` run) — the
#             SessionStart path (hook → tb-due.sh) uses it: no repo script runs, no
#             slow launcher eats the hook timeout.
# HEALTH only: cadence and wish backlog are dueness (tb-due.sh owns it) and print as
# INFO, never as findings — an overdue train must not turn `make test` red.
# Exit: 0 clean, 1 findings, 2 no toolbox. Self-contained (copied into <tb>/tools/).
# bash 3.2 + POSIX only.
set -u
TB=""; STATIC=0
for a in "$@"; do
  case "$a" in --static) STATIC=1 ;; *) TB="$a" ;; esac
done
if [ -z "$TB" ]; then
  if [ -f "toolbox/index.md" ]; then TB="toolbox"
  elif [ -f ".claude/toolbox/index.md" ]; then TB=".claude/toolbox"
  else echo "tb-lint: no toolbox found"; exit 2; fi
fi
[ -f "$TB/index.md" ] || { echo "tb-lint: $TB/index.md missing"; exit 2; }
issues=0
warn() { echo "WARN: $*"; issues=$((issues+1)); }

ATB=$(CDPATH='' cd -- "$TB" && pwd)
case "$ATB" in
  */.claude/toolbox) PROOT="${ATB%/.claude/toolbox}" ;;
  *) PROOT=$(dirname "$ATB") ;;
esac
# Skill mirrors (same marker rules and checksum as tb-sync-skills.sh): mine = a praxis
# mirror of that name (an old-style empty marker, or one a merge left conflicted,
# counts); edited = its content no longer matches the checksum sync recorded.
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
mine() {
  [ ! -L "$1" ] && [ -f "$1/.praxis-managed" ] || return 1
  m=$(tr -d '\r' < "$1/.praxis-managed"); case "$m" in *"<<<<<<< "*) return 0 ;; esac
  n=$(printf '%s\n' "$m" | sed -n 1p); [ -z "$n" ] || [ "$n" = "${1##*/}" ]
}
edited() {
  m=$(tr -d '\r' < "$1/.praxis-managed"); case "$m" in *"<<<<<<< "*) return 1 ;; esac
  c=$(printf '%s\n' "$m" | sed -n 2p); [ -n "$c" ] && [ "$c" != "$(msum "$1")" ]
}

# --- 1. catalog cap ----------------------------------------------------------
n=$(wc -l < "$TB/index.md" | tr -d ' ')
[ "$n" -gt 50 ] && warn "index.md is $n lines (cap 50) — trim hooks, the catalog is the map not the manual"

# --- 2. bin floor: executable, --help exits 0 (skipped --static), catalogued ---
shims=0
for f in "$TB"/bin/*; do
  [ -f "$f" ] || continue
  name=$(basename "$f")
  [ "$name" = ".gitkeep" ] && continue
  [ -x "$f" ] || warn "bin/$name not executable"
  [ "$STATIC" = "1" ] || "$f" --help >/dev/null 2>&1 </dev/null || warn "bin/$name --help failed"
  grep -q "\[$name\]" "$TB/index.md" || warn "bin/$name not in catalog"
  grep -q '^# shim:' "$f" 2>/dev/null && shims=$((shims+1))
done
[ "$shims" -gt 0 ] && echo "INFO: $shims shim(s) in bin/ awaiting /praxis:retire"

# --- 3. catalog honesty: every [name] exists ----------------------------------
for name in $(grep -o '^- \[[^]]*\]' "$TB/index.md" 2>/dev/null | sed 's/^- \[//; s/\]$//'); do
  [ -f "$TB/bin/$name" ] || [ -d "$TB/skills/$name" ] || \
    warn "catalog lists [$name] but no bin/$name or skills/$name exists"
done

# --- 4. src/ tools: README, launcher, Makefile targets -------------------------
for d in "$TB"/src/*/; do
  [ -d "$d" ] || continue
  t=$(basename "$d")
  [ -f "$d/README.md" ] || warn "src/$t has no README.md (deps/build/test must be documented)"
  [ -f "$TB/bin/$t" ] || warn "src/$t has no bin/$t launcher"
  grep -q "^build-$t:" "$TB/Makefile" 2>/dev/null || warn "Makefile lacks build-$t target"
  grep -q "^test-$t:" "$TB/Makefile" 2>/dev/null || warn "Makefile lacks test-$t target"
done

# --- 5. skills floor -----------------------------------------------------------
for d in "$TB"/skills/*/; do
  [ -d "$d" ] || continue
  s=$(basename "$d")
  if [ ! -f "$d/SKILL.md" ]; then warn "skills/$s has no SKILL.md"; continue; fi
  if [ "$(head -1 "$d/SKILL.md")" != "---" ]; then
    warn "skills/$s SKILL.md has no frontmatter"
  else
    awk '/^---$/{fm++; next} fm==1' "$d/SKILL.md" | grep -q '^name:' \
      || warn "skills/$s frontmatter lacks name:"
    awk '/^---$/{fm++; next} fm==1' "$d/SKILL.md" | grep -q '^description:' \
      || warn "skills/$s frontmatter lacks description:"
  fi
  # process substitution, not a pipe: warn must count in THIS shell (paths with spaces ok)
  while IFS= read -r sc; do
    [ -x "$sc" ] || warn "skill script $sc not executable"
  done < <(find "$d" -name '*.sh' -type f 2>/dev/null)
  for ref in $(grep -ho 'toolbox/bin/[A-Za-z0-9_.-]*[A-Za-z0-9_-]' "$d/SKILL.md" 2>/dev/null | sed 's|.*/||' | sort -u); do
    [ -f "$TB/bin/$ref" ] || warn "skills/$s references missing tool bin/$ref"
  done
  MIRROR="$PROOT/.claude/skills/$s"
  if [ ! -d "$MIRROR" ]; then
    warn "skills/$s not synced to .claude/skills (run: make -C $TB sync)"
  elif ! mine "$MIRROR"; then
    warn "skills/$s collides with .claude/skills/$s, which is not a praxis mirror (no marker, a symlink, or a copy of another mirror) — rename one"
  elif [ "$(msum "$ATB/skills/$s")" != "$(msum "$MIRROR")" ]; then
    if edited "$MIRROR"; then
      warn "skills/$s mirror .claude/skills/$s was edited by hand — move the edit into skills/$s (sync never overwrites it; once the two match, make -C $TB sync takes the mirror back)"
    else
      warn "skills/$s mirror stale (run: make -C $TB sync)"
    fi
  fi
done

# --- 6. wish backlog + train cadence: INFO only (dueness is tb-due.sh's) ---------
train_days=7; wish_max=5
if [ -f "$TB/.praxis" ]; then
  while IFS='=' read -r k v; do
    case "$k" in train_days) train_days="$v" ;; wish_max) wish_max="$v" ;; esac
  done < "$TB/.praxis"
fi
wishes=$(grep -c '[^[:space:]]' "$TB/.wishes" 2>/dev/null); wishes=${wishes:-0}
legacy=$(grep -c '^\[wish\]' "$TB/.usage.log" 2>/dev/null); legacy=${legacy:-0}
wishes=$((wishes + legacy))
[ "$wishes" -ge "$wish_max" ] && echo "INFO: wish backlog: $wishes entries (max $wish_max) — training due"
[ "$legacy" -gt 0 ] && echo "INFO: $legacy legacy [wish] line(s) in .usage.log — the next train migrates them to .wishes"

# MARKER RULE (canonical copy in tb-due.sh): .last-train is TRACKED, so git resets
# its mtime on checkout. The CONTENT is the truth — an ISO UTC stamp written at train
# close-out; `seeded`/empty falls back to the mtime test. Here it only feeds an INFO.
marker_due() { # <file> <days> -> exit 0 when due
  c=$(head -1 "$1" 2>/dev/null | tr -d '[:space:]')
  case "$c" in
    [0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T*)
      cut=$(date -u -v-"$2"d +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d "-$2 days" +%Y-%m-%dT%H:%M:%SZ)
      [ "$c" \< "$cut" ] ;;
    *) [ -n "$(find "$1" -mtime +"$2" 2>/dev/null)" ] ;;
  esac
}
if [ -f "$TB/.last-train" ]; then
  marker_due "$TB/.last-train" "$train_days" && echo "INFO: last train more than ${train_days}d ago — training due"
else
  echo "INFO: never trained (no .last-train marker) — training due"
fi

# --- 7. staleness accounting (INFO, not a finding) ------------------------------
if [ -s "$TB/.stats" ]; then
  st=$(grep -c 'status=stale' "$TB/.stats" 2>/dev/null); st=${st:-0}
  [ "$st" -gt 0 ] && echo "INFO: $st artifact(s) stale — review before relying (see $TB/.stats)"

fi
# --- 8. path-derived roots (INFO, never a finding) -----------------------------------
# A script that finds its root from $0/__file__ plus ".." changes meaning when it moves.
# The lint cannot tell a broken ROOT from a fixed one, so this is INFO: a WARN would turn
# the SessionStart `--static` run red and dispatch a paid train (tb-due.sh). Read-only:
# regular files only (a link is never followed), nothing is executed, no git call.
rootpath_note() { # relpath firstline extra
  local more=""
  [ "$3" -gt 0 ] && more=" (+$3 more)"
  echo "INFO: root-from-path $1:$2 derives its root from its own location — a move changes what \"..\" reaches; ask git or \$PRAXIS_ROOT instead, and check it still resolves after the move$more"
}
rp_dirs=()
for d in "$TB/bin" "$TB/src"; do [ -d "$d" ] && [ ! -L "$d" ] && rp_dirs+=("$d"); done
rp_files=0
RP_OWN='\$0|\$\{0[^0-9A-Za-z_]|BASH_SOURCE|__file__'
RP_UP='(^|[^A-Za-z0-9_.])\.\.([^A-Za-z0-9_.]|$)|\.parent([^A-Za-z_s]|$)|\.parents\['
if [ "${#rp_dirs[@]}" -gt 0 ]; then
  # a fixed number of processes however many files: ONE grep -H over every file, then
  # builtins only. Directories are pruned before descending (-type d: a FILE named build
  # is still scanned); only regular files <=256 KB; a symlink is never opened.
  rp_find() { find "${rp_dirs[@]}" -type d \( -name node_modules -o -name .venv -o -name venv \
      -o -name site-packages -o -name __pycache__ -o -name .git -o -name dist -o -name build \) -prune \
      -o -type f -size -257k "$@" 2>/dev/null; }
  rp_skip=$(rp_find -exec grep -I -l -E '^# (shim|inplace):' {} + | sed 's/^/:/; s/$/:/' | tr '\n' ' ')
  prev=""; cnt=0; firstl=""
  while IFS= read -r l; do
    p=${l%%:*}; ln=${l#*:}
    if [ "$p" != "$prev" ]; then
      [ -n "$prev" ] && [ "$rp_files" -le 10 ] && rootpath_note "${prev#"$TB"/}" "$firstl" $((cnt-1))
      case " $rp_skip" in *" :$p: "*) prev=""; cnt=0; continue ;; esac
      prev=$p; cnt=0; firstl=$ln; rp_files=$((rp_files+1))
    fi
    [ -n "$prev" ] && cnt=$((cnt+1))
  done < <(rp_find -exec grep -I -H -n -E "$RP_OWN" {} + \
      | grep -v -E '^[^:]*:[0-9]+:[[:space:]]*#' \
      | sed -E 's#/\.\./(src|bin|tools|tests|skills)/#/#g' \
      | grep -E "^[^:]*:[0-9]+:.*($RP_UP)" \
      | sed -E 's/^([^:]*):([0-9]+):.*/\1:\2/' | sort -t: -k1,1 -k2,2n)
  [ -n "$prev" ] && [ "$rp_files" -le 10 ] && rootpath_note "${prev#"$TB"/}" "$firstl" $((cnt-1))
fi
[ "$rp_files" -gt 10 ] && echo "INFO: root-from-path: $((rp_files-10)) more file(s)"

# --- 9. unreviewed tool run by a hook (REVIEW line: NOT a finding) ----------------------
# A tool a training run changed and the user has not reviewed (.stats `unreviewed=`), which a
# project hook or statusLine runs unasked, deserves a human look. It is printed, never
# counted: no warn(), no `issues`, exit code unchanged, never a `WARN:` prefix — so
# tb-due.sh never says `lint red` and no paid train is bought for a finding only a human
# can clear. File reads only (safe under --static): regular files, no link followed, no
# git call, nothing executed. <name> and <s> come from committed data: validated first.
tbrel=${ATB#"$PROOT"/}
rv_n=0; rv_more=0
rv_word() { case "$1" in [[:alnum:]_.-]) return 0 ;; esac; return 1; } # one name character
rv_hits() { # string name -> 0 when the string names $tbrel/bin/<name> exactly
  local s=$1 needle="$tbrel/bin/$2" pre post pc nc
  while :; do
    case "$s" in *"$needle"*) ;; *) return 1 ;; esac
    pre=${s%%"$needle"*}; post=${s#*"$needle"}
    pc=${pre: -1}; nc=${post:0:1}
    rv_word "$pc" || rv_word "$nc" || return 0
    s=$post
  done
}
if [ -f "$TB/.stats" ] && [ -d "$PROOT/.claude" ] && [ ! -L "$PROOT/.claude" ]; then
  while IFS= read -r l || [ -n "$l" ]; do
    case "$l" in *" unreviewed="*) ;; *) continue ;; esac
    rv_name=${l%% *}
    case "$rv_name" in ""|skill:*|*[!0-9A-Za-z_.-]*) continue ;; esac
    rv_s=${l##* unreviewed=}; rv_s=${rv_s%% *}
    printf '%s' "$rv_s" | grep -qE '^(-|[0-9a-f]{4,40})$' || rv_s="?"
    rv_file=""
    for f in settings.json settings.local.json; do
      [ -f "$PROOT/.claude/$f" ] && [ ! -L "$PROOT/.claude/$f" ] || continue
      rv_cmds=$(grep -oE '"command"[[:space:]]*:[[:space:]]*"([^"\\]|\\.)*"' "$PROOT/.claude/$f" 2>/dev/null)
      while IFS= read -r c || [ -n "$c" ]; do
        rv_hits "$c" "$rv_name" && { rv_file=$f; break; }
      done <<RVEOF
$rv_cmds
RVEOF
      [ -n "$rv_file" ] && break
    done
    [ -n "$rv_file" ] || continue
    if [ "$rv_n" -ge 10 ]; then rv_more=$((rv_more+1)); continue; fi
    rv_n=$((rv_n+1))
    if [ "$rv_s" = "?" ]; then hint="review it"
    else hint="review it (git diff $rv_s -- $tbrel/bin/$rv_name)"; fi
    echo "REVIEW: bin/$rv_name was changed by a training run (unreviewed since $rv_s) and a hook in .claude/$rv_file runs it — $hint, then mark it reviewed in /praxis:status"
  done < "$TB/.stats"
fi
[ "$rv_more" -gt 0 ] && echo "REVIEW: $rv_more more"

# --- summary --------------------------------------------------------------------
tools=0
for f in "$TB"/bin/*; do [ -f "$f" ] && [ "$(basename "$f")" != ".gitkeep" ] && tools=$((tools+1)); done
sk=0
for d in "$TB"/skills/*/; do [ -d "$d" ] && sk=$((sk+1)); done
if [ "$issues" -eq 0 ]; then
  echo "tb-lint: clean — $tools tools, $sk skills, $wishes open wishes"
  exit 0
else
  echo "tb-lint: $issues finding(s) — $tools tools, $sk skills, $wishes open wishes"
  exit 1
fi
