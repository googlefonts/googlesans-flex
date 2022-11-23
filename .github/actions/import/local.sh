#!/usr/bin/env bash

# TODO: consider yell/die/try
# https://stackoverflow.com/questions/37919034/capturing-bash-execution-errors

if [[ -z "$1" ]] ; then
    echo "ERROR: must pass branch to use as staging as 1st arg"
    exit 1
fi

if [[ ! $(docker image inspect import) ]] ; then
    echo "Docker image not found, building"
    docker build -t import .github/actions/import
fi

REPO_DIR=$(pwd)
STAGING_BRANCH=$1

MAIN_COMMIT=$(git log -n 1 --oneline main | cut -d' ' -f 1)
STAGING_COMMIT=$(git log -n 1 --oneline "$STAGING_BRANCH" | cut -d' ' -f 1)

MAIN_DIR=$(mktemp -d)
STAGING_DIR=$(mktemp -d)

echo "main -> $MAIN_DIR"
echo "$STAGING_BRANCH -> $STAGING_DIR"

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

# shellcheck disable=SC2164
cd "$MAIN_DIR"
# Ensure the import scripts actually changed something & docker succeeded
# https://stackoverflow.com/a/5143914
if [[ docker_exit_status -eq 0 && ! $(git diff-index --quiet HEAD --) ]] ; then
    IMPORT_BRANCH_NAME="import-$STAGING_BRANCH"
    # Use exit codes from this command to work out what's happening
    git ls-remote --exit-code --heads git@github.com:googlefonts/googlesans-flex.git "$IMPORT_BRANCH_NAME" &> /dev/null
    case $? in
        2)
            echo "Creating new import branch locally ($IMPORT_BRANCH_NAME)"
            git checkout -b "$IMPORT_BRANCH_NAME"
            git add sources
            git commit --quiet -m "Import from $STAGING_BRANCH
            
            This commit was creating automatically using the local import script"
            echo "Pushing import branch to GitHub repository"
            git push -u origin "$IMPORT_BRANCH_NAME"
            echo
            echo "SUCCESS: pushed to branch $IMPORT_BRANCH_NAME, ready for you to open a PR!"
            ;;
        0) echo "WARNING: import branch already exists. Currently don't handle this" ;;
        128) echo "ERROR: authentication failed, please check the README for the import action for how to set up SSH authentication" ;;
        *) echo "ERROR: unknown error checking Git remote branches"
    esac
    echo
fi

echo "Cleaning up..."
# shellcheck disable=SC2164
cd "$REPO_DIR"
# --force may be necessary here if the scripts made some changes but we had to
# abort
git worktree remove --force "$MAIN_DIR"
git worktree remove "$STAGING_DIR"

exit $docker_exit_status
