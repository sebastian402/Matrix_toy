#!/bin/bash
LOG_FILE="$HOME/git_pull.log"

{
  echo "=============================="
  echo "$(date) - Checking GitHub version"

  cd /home/seba/wifi-toy || exit 1

  LOCAL=$(git rev-parse HEAD)
  REMOTE=$(git ls-remote origin -h refs/heads/main | awk '{print $1}')

  echo "$(date) - Local:  $LOCAL"
  echo "$(date) - Remote: $REMOTE"

  if [ "$LOCAL" != "$REMOTE" ]; then
      echo "$(date) - Updating from GitHub..."
      git pull --rebase --autostash
  else
      echo "$(date) - Already up to date"
  fi

  echo "$(date) - Launching matrix_console.py"

} >> "$LOG_FILE" 2>&1

# Start the app
DISPLAY=:0 SDL_VIDEODRIVER=x11 python3 /home/seba/wifi-toy/matrix_console.py
