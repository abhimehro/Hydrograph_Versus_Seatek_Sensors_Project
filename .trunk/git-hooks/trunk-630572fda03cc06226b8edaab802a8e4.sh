#!/bin/bash --norc
set -euo pipefail

if [[ ! -d .trunk ]]; then
  exit 0
fi

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." >/dev/null 2>&1 && pwd)"

hook=${0##*/}

# If this git-hook provides extra information on stdin, then save that to a file and tell trunk where to find it.
if [[ ${hook} != "pre-rebase" ]]; then
  mkdir -p "${repo_dir}/temp"
  file=$(mktemp "${repo_dir}/temp/trunk-${hook}-XXXXXX")
  trap 'rm -f ${file}' EXIT
  cat >>"${file}" || true
  export TRUNK_GIT_STDIN_FILE=${file}
fi

# Figure out if we have a tty and make that stdin, otherwise make it null.
if [[ -n ${TRUNK_TTY_PATH-} ]]; then
  export TRUNK_STDIN_IS_TTY=1
  exec <"${TRUNK_TTY_PATH}"
elif [[ -t 2 ]]; then
  export TRUNK_STDIN_IS_TTY=1
  exec </dev/tty
else
  exec </dev/null
fi

trunk=${repo_dir}/tools/trunk

TRUNK_LAUNCHER_QUIET=true "${trunk}" git-hooks callback "${0##*/}" -- "$@"
