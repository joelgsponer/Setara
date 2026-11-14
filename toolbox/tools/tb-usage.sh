#!/bin/bash
# praxis-version: 0.4.1 (= plugin.json; tb-refresh.sh moves toolbox copies forward only)
# praxis tb-usage — mine the toolbox's senses; with --stats fold them into .stats.
# Usage: tb-usage.sh [toolbox-dir] [--stats [--verified] | --wishes | --candidates | --domains]
#   mine (default): hits per artifact, open wishes, consolidation + retire candidates,
#                   raw-CMD count. Read-only.
#   --stats:   accumulate uses/last-used/since per artifact, restamp status, migrate
#              legacy `[wish]` lines from .usage.log into .wishes, truncate the log.
#              --verified also stamps last-verified=today (train runs this right after
#              a green `make lint test`). TRAIN-ONLY: sessions read .stats, never write.
#              One field is carried through the rewrite untouched: `unreviewed=` (see below).
#   --wishes:     open wishes, one per line (.wishes, then legacy [wish] lines).
#   --candidates: retire candidates, one per line:
#                 <name> dead|stale|shim uses=<n> last-used=<d> since=<d>
#                 dead = never used and older than stale_days; stale = status=stale;
#                 shim = bin/<name> carries a `# shim:` header (replaced by a CLI).
#                 Names on `keep=` in .praxis (comma list; skills as skill:<name>) are skipped.
#                 Deleting is /praxis:retire's job, with consent — never automatic.
#   --domains:    <domain> <n> <name...> for name-prefix groups (before the first '-')
#                 of >= consolidate_min non-shim scripts — CLI consolidation feedstock.
# .stats line: <name> uses=<n> last-used=<d> last-verified=<d> since=<d> status=hot|ok|stale [unreviewed=<sha12>|-]
#   unreviewed= is the stamp `tb-run-done.sh --changes` puts on a tool a train created or
#   edited (the sha is HEAD before that train: `git diff <sha> -- <path>`); only
#   `tb-review.sh mark` (the user's word) removes it. --stats keeps it and never sets it.
# Exit: 0 ok, 2 no toolbox, 3 a state file is a symlink (refused). bash 3.2 / POSIX only.
set -u
TB=""; MODE=mine; VERIFIED=0
for a in "$@"; do
  case "$a" in
    --stats) MODE=stats ;;
    --verified) VERIFIED=1 ;;
    --wishes) MODE=wishes ;;
    --candidates) MODE=candidates ;;
    --domains) MODE=domains ;;
    *) TB="$a" ;;
  esac
done
if [ -z "$TB" ]; then
  if [ -f "toolbox/index.md" ]; then TB="toolbox"
  elif [ -f ".claude/toolbox/index.md" ]; then TB=".claude/toolbox"
  else echo "tb-usage: no toolbox found"; exit 2; fi
fi
LOG="$TB/.usage.log"; ST="$TB/.stats"; WISHES="$TB/.wishes"
# Never write through a link: a clone can commit any of these as a symlink to a file
# outside the repo, and touch/append/truncate would all land on its target.
for f in "$LOG" "$ST" "$ST.tmp" "$WISHES"; do
  [ -L "$f" ] && { echo "tb-usage: refusing — $f is a symlink" >&2; exit 3; }
done
[ -f "$LOG" ] || touch "$LOG"

stale_days=30; hot_hits=3; consolidate_min=3; keep=
if [ -f "$TB/.praxis" ]; then
  while IFS='=' read -r k v || [ -n "$k" ]; do
    case "$k" in
      stale_days) stale_days="$v" ;;
      hot_hits) hot_hits="$v" ;;
      consolidate_min) consolidate_min="$v" ;;
      keep) keep=$(printf '%s' "$v" | tr -d ' \t\r') ;;
    esac
  done < "$TB/.praxis"
fi

today=$(date +%Y-%m-%d)
now=$(date +%s)
epoch() { date -d "$1" +%s 2>/dev/null || date -j -f %Y-%m-%d "$1" +%s 2>/dev/null || echo 0; }
age_days() { # "never" -> -1 (unknown)
  if [ -z "${1:-}" ] || [ "$1" = "never" ]; then echo -1
  else echo $(( (now - $(epoch "$1")) / 86400 )); fi
}
is_shim() { [ -f "$TB/bin/$1" ] && grep -q '^# shim:' "$TB/bin/$1" 2>/dev/null; }
inventory() {
  for f in "$TB"/bin/*; do
    [ -f "$f" ] || continue
    case "$(basename "$f")" in .gitkeep) continue ;; esac
    basename "$f"
  done
  for d in "$TB"/skills/*/; do [ -d "$d" ] && echo "skill:$(basename "$d")"; done
}
stat_field() { # <line> <key> <default>
  v=$(printf '%s' "$1" | sed -n "s/.*$2=\([^ ]*\).*/\1/p"); printf '%s' "${v:-$3}"
}
forge_date() { # <bare name> -> first ledger date, or ""
  grep -E "^[0-9]{4}-[0-9]{2}-[0-9]{2} (forged|forged-skill|adopted|consolidated|shimmed) $1( |\$)" \
    "$TB/.forge.log" 2>/dev/null | head -1 | cut -d' ' -f1
}
list_wishes() {
  grep '[^[:space:]]' "$WISHES" 2>/dev/null
  grep '^\[wish\]' "$LOG" 2>/dev/null
  return 0
}
list_domains() {
  for f in "$TB"/bin/*-*; do
    [ -f "$f" ] || continue
    n=$(basename "$f")
    is_shim "$n" && continue
    [ -d "$TB/src/$n" ] && continue
    echo "${n%%-*} $n"
  done | sort | awk -v min="$consolidate_min" '
    { names[$1] = names[$1] " " $2; c[$1]++ }
    END { for (d in c) if (c[d] >= min) printf "%s %d%s\n", d, c[d], names[d] }' | sort
}
is_kept() { case ",$keep," in *",$1,"*) return 0 ;; esac; return 1; }
list_kept() { # keep= names that exist in the inventory
  for name in $(inventory); do is_kept "$name" && echo "$name"; done
  return 0
}
warn_keep() { # keep= names that match nothing: a typo would silently retire-nominate
  [ -n "$keep" ] || return 0
  inv=" $(inventory | tr '\n' ' ')"
  old_ifs=$IFS; IFS=,; set -f
  for k in $keep; do
    [ -n "$k" ] || continue
    case "$inv" in *" $k "*) ;; *) echo "tb-usage: WARN keep= names '$k', not in this toolbox" >&2 ;; esac
  done
  IFS=$old_ifs; set +f
}
list_candidates() {
  for name in $(inventory); do
    is_kept "$name" && continue
    line=$(awk -v n="$name" '$1==n' "$ST" 2>/dev/null | head -1)
    uses=$(stat_field "$line" uses 0); lu=$(stat_field "$line" last-used never)
    since=$(stat_field "$line" since never); status=$(stat_field "$line" status ok)
    reason=""
    if is_shim "$name"; then reason=shim
    elif [ -n "$line" ] && [ "$uses" = "0" ] && [ "$(age_days "$since")" -ge "$stale_days" ]; then reason=dead
    elif [ "$status" = "stale" ]; then reason=stale
    fi
    [ -n "$reason" ] && echo "$name $reason uses=$uses last-used=$lu since=$since"
  done
  return 0
}
indent_or_none() { out=$(cat); if [ -n "$out" ]; then printf '%s\n' "$out" | sed 's/^/  /'; else echo "  (none)"; fi; }

case "$MODE" in
  wishes) list_wishes; exit 0 ;;
  candidates) warn_keep; list_candidates; exit 0 ;;
  domains) list_domains; exit 0 ;;
  mine)
    echo "== hits this rotation"
    awk '$2=="HIT"{c[$3]++} END{for (k in c) printf "  %d %s\n", c[k], k}' "$LOG" | sort -rn
    echo "== open wishes"
    list_wishes | indent_or_none
    echo "== consolidation candidates (>= $consolidate_min scripts in one domain)"
    list_domains | indent_or_none
    echo "== retire candidates (/praxis:retire decides — never automatic)"
    list_candidates | indent_or_none
    echo "== kept (keep=) — never nominated for retire"
    list_kept | indent_or_none
    warn_keep
    n=$(grep -c ' CMD ' "$LOG" 2>/dev/null); n=${n:-0}
    echo "== raw commands captured: $n (pattern feedstock — read the log)"
    exit 0 ;;
esac

# --- stats: fold this rotation into .stats, then rotate -------------------------
tmp="$ST.tmp"; : > "$tmp"
for name in $(inventory); do
  hits=$(awk -v n="$name" '$2=="HIT" && $3==n {c++} END{print c+0}' "$LOG")
  last_hit=$(awk -v n="$name" '$2=="HIT" && $3==n {d=substr($1,1,10)} END{print d ? d : "never"}' "$LOG")
  prev=$(awk -v n="$name" '$1==n' "$ST" 2>/dev/null | head -1)
  prev_uses=$(stat_field "$prev" uses 0)
  prev_last=$(stat_field "$prev" last-used never)
  prev_ver=$(stat_field "$prev" last-verified never)
  since=$(stat_field "$prev" since never)
  uses=$((prev_uses + hits))
  last_used="$last_hit"; [ "$last_used" = "never" ] && last_used="$prev_last"
  ver="$prev_ver"; [ "$VERIFIED" = "1" ] && ver="$today"
  if [ "$since" = "never" ]; then
    since=$(forge_date "${name#skill:}"); [ -n "$since" ] || since="$today"
  fi
  ua=$(age_days "$last_used"); [ "$ua" -lt 0 ] && ua=$(age_days "$since")
  va=$(age_days "$ver")
  status=ok
  if [ "$ua" -gt "$stale_days" ] || [ "$va" -gt "$stale_days" ]; then status=stale; fi
  [ "$hits" -ge "$hot_hits" ] && status=hot
  rev=$(stat_field "$prev" unreviewed "")
  case " $prev " in *" unreviewed="*) rev=${rev:-?} ;; esac   # an empty value is still a stamp
  echo "$name uses=$uses last-used=$last_used last-verified=$ver since=$since status=$status${rev:+ unreviewed=$rev}" >> "$tmp"
done
mv "$tmp" "$ST"

# Legacy wishes (v0.1 kept them in the git-ignored log, so they were per-machine)
# migrate into the committed .wishes; then the log is truncated — HIT/CMD lines have
# been folded in, and raw commands are one-rotation feedstock by design.
migrated=$(grep -c '^\[wish\] ' "$LOG" 2>/dev/null); migrated=${migrated:-0}
grep '^\[wish\] ' "$LOG" 2>/dev/null | sed 's/^\[wish\] //' | while IFS= read -r text; do
  [ -n "$text" ] || continue
  grep -qF -- "$text" "$WISHES" 2>/dev/null && continue
  echo "$today $text" >> "$WISHES"
done
: > "$LOG"
n=$(wc -l < "$ST" | tr -d ' ')
echo "tb-usage: stats updated ($n artifacts), log rotated ($migrated wishes migrated to .wishes)"
exit 0
