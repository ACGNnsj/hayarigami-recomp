#!/bin/bash
# Push to GitHub bypassing the global gh-proxy url rewrite and the broken
# credential-manager path: the token comes from the gh CLI, so nothing is
# stored in .git/config. Usage: bash tools/push.sh [extra git push args]
set -e
cd "$(dirname "$0")/.." || exit 1
T=$(gh auth token)
exec git -c credential.helper= push "https://x-access-token:$T@github.com/ACGNnsj/hayarigami-recomp.git" HEAD:refs/heads/main "$@"
