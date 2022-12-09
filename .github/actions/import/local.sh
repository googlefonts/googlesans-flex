#!/usr/bin/env bash

# TODO: consider yell/die/try
# https://stackoverflow.com/questions/37919034/capturing-bash-execution-errors

if [[ -z "$1" ]] ; then
    echo "ERROR: must pass branch to use as staging as 1st arg"
    exit 1
fi

REPO_DIR=$(pwd)
SOURCE_BRANCH=$1
TARGET_BRANCH_NAME="import-$SOURCE_BRANCH"
git ls-remote --exit-code --heads git@github.com:googlefonts/googlesans-flex.git "$TARGET_BRANCH_NAME" &> /dev/null
BRANCH_EXISTS_STATUS=$?
case $BRANCH_EXISTS_STATUS in
    2)
        # Branch doesn't already exist, new import
        echo "Creating new import branch"
        BASE_BRANCH=main
        ;;
    0)
        # Branch already exists, update
        echo "Updating existing import branch $TARGET_BRANCH_NAME"
        BASE_BRANCH=$TARGET_BRANCH_NAME
        ;;
    128)
        echo "ERROR: authentication failed, please check the README for the import action for how to set up SSH authentication"
        exit 1
        ;;
    *)
        echo "ERROR: unknown error checking Git remote branches"
        exit 1
        ;;
esac

git fetch --quiet origin "$BASE_BRANCH" "$SOURCE_BRANCH"
BASE_COMMIT=$(git log -n 1 --oneline "origin/$BASE_BRANCH" | cut -d' ' -f 1)
SOURCE_COMMIT=$(git log -n 1 --oneline "origin/$SOURCE_BRANCH" | cut -d' ' -f 1)

BASE_DIR=$(mktemp -d)
SOURCE_DIR=$(mktemp -d)

echo "$BASE_BRANCH -> $BASE_DIR"
echo "$SOURCE_BRANCH -> $SOURCE_DIR"

echo

echo "Using commit $BASE_COMMIT for base"
git worktree add "$BASE_DIR" "$BASE_COMMIT" || exit 1
echo
echo "Using commit $SOURCE_COMMIT for staging"
git worktree add "$SOURCE_DIR" "$SOURCE_COMMIT" || exit 1

echo

echo "Running import scripts through Docker..."
docker build -t import "$REPO_DIR/.github/actions/import"
docker run --rm \
    --name "import-$BASE_COMMIT-$SOURCE_COMMIT" \
    -v "$BASE_DIR:/github/workspace/main" \
    -v "$SOURCE_DIR:/github/workspace/staging:ro" \
    import
DOCKER_EXIT_STATUS=$?
echo

# shellcheck disable=SC2164
cd "$BASE_DIR"
# Ensure the import scripts actually changed something & docker succeeded
# https://stackoverflow.com/a/5143914
if [[ $DOCKER_EXIT_STATUS -eq 0 && ! $(git diff-index --quiet HEAD --) ]] ; then
    if [[ $BRANCH_EXISTS_STATUS -eq 2 ]] ; then
        echo "Creating new import branch locally ($TARGET_BRANCH_NAME)"
        git checkout -b "$TARGET_BRANCH_NAME"
        git add sources
        git commit --quiet -m "Import from $SOURCE_BRANCH
        
This commit was creating automatically using the local import script"
        echo "Pushing import branch to GitHub repository"
        git push -u origin "$TARGET_BRANCH_NAME"
        echo
        echo "SUCCESS: pushed to branch $TARGET_BRANCH_NAME, ready for you to open a PR!"
    else
        echo "Updating existing import branch ($TARGET_BRANCH_NAME)"
        git checkout --quiet "$TARGET_BRANCH_NAME"
        git add sources
        git commit --quiet -m "Update from $SOURCE_BRANCH
            
This commit was creating automatically using the local import script"
        git push
        echo
        echo "SUCCESS: pushed to branch $TARGET_BRANCH_NAME"
    fi
    echo
fi

echo "Cleaning up..."
# shellcheck disable=SC2164
cd "$REPO_DIR"
# --force may be necessary here if the scripts made some changes but we had to
# abort
git worktree remove --force "$BASE_DIR"
git worktree remove "$SOURCE_DIR"

exit $DOCKER_EXIT_STATUS
