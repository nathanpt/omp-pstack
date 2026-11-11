#!/usr/bin/env bash
# Expose this repo's skills at a harness's discovery depth.
# Skills must be discoverable at <skills-dir>/<name>/SKILL.md (one level).
set -euo pipefail

uninstall=0
if [ "${1:-}" = "--uninstall" ]; then uninstall=1; shift; fi
target="${1:-$HOME/.omp/agent/skills}"

[ -d "$target" ] || { echo "no such skills directory: $target" >&2; exit 1; }
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
status=0

for src in "$repo"/skills/*/; do
  name="$(basename "$src")"
  dest="$target/$name"
  if [ "$uninstall" = 1 ]; then
    if [ -L "$dest" ]; then rm "$dest"; echo "unlinked $dest"; else echo "skip $name (not a symlink)"; fi
    continue
  fi
  if [ -e "$dest" ] && [ ! -L "$dest" ]; then
    echo "REFUSED $name: $dest exists and is not a symlink; move it first" >&2
    status=1
    continue
  fi
  ln -sfn "${src%/}" "$dest"
  echo "linked $dest -> ${src%/}"
done

# Prune links into this repo whose skill no longer exists. Only links pointing at
# $repo/skills are touched, so a neighbouring skill library is never disturbed.
if [ "$uninstall" = 0 ]; then
  for link in "$target"/*; do
    [ -L "$link" ] || continue
    dest="$(readlink "$link")"
    case "$dest" in
      "$repo"/skills/*) ;;
      *) continue ;;
    esac
    [ -d "$dest" ] && continue
    rm "$link"
    echo "pruned stale link $link (target gone: $dest)"
  done
fi

exit "$status"
