#!/usr/bin/env bash

if [[ -z "$1" ]] ; then
    echo "ERROR: must pass branch to use as staging as 1st arg"
    exit 1
fi

if [[ ! $(docker image inspect import) ]] ; then
    echo "Docker image not found, building"
    docker build -t import .github/actions/import
fi

MAIN_COMMIT=$(git log -n 1 --oneline main | cut -d' ' -f 1)
STAGING_COMMIT=$(git log -n 1 --oneline "$1" | cut -d' ' -f 1)

MAIN_DIR=$(mktemp -d)
STAGING_DIR=$(mktemp -d)

echo "main -> $MAIN_DIR"
echo "$1 -> $STAGING_DIR"

echo

echo "Using commit $MAIN_COMMIT for main"
git worktree add "$MAIN_DIR" "$MAIN_COMMIT" || exit 1
echo
echo "Using commit $STAGING_COMMIT for staging"
git worktree add "$STAGING_DIR" "$STAGING_COMMIT" || exit 1

echo

echo "Running import scripts through Docker..."
docker run --rm \
    --name "import-$MAIN_COMMIT-$STAGING_COMMIT" \
    -v "$MAIN_DIR:/github/workspace/main" \
    -v "$STAGING_DIR:/github/workspace/staging:ro" \
    import
docker_exit_status=$?
echo

read -p "Pausing before cleanup, press enter to continue "

echo "Cleaning up..."
git worktree remove "$MAIN_DIR"
git worktree remove "$STAGING_DIR"

exit $docker_exit_status
