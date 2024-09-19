#!/bin/sh

# Build a Windows .exe binary

if [[ "$BLASTAX_MERGE" == "true" ]]; then
  echo "BLASTAX_MERGE is set to true. Executing alternate script."
  SCRIPT_DIR=$(dirname "$0")
  "$SCRIPT_DIR/make-executable-merge.sh"
  exit 0
fi

DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Reading config..."
source "$DIR/config.sh" "$@" || exit 1
echo "Building $APP_NAME..."

echo "Calling pyinstaller..."
pyinstaller --noconfirm "$DIR/specs/windows.spec" || exit 1

echo "Success!"
