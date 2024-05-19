#!/bin/bash

REPO_DIR="/home/pet/site-pet/backend"
SERVICE_NAME="site-pet-backend.service"

cd $REPO_DIR || exit 1

git fetch origin

LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ $LOCAL != $REMOTE ]; then
    sudo /bin/systemctl stop $SERVICE_NAME
    
    if git pull --rebase origin stable; then
        sudo /bin/systemctl start $SERVICE_NAME
    else
        echo "Error: failed to pull changes; aborting update"
        git rebase --abort
        sudo /bin/systemctl start $SERVICE_NAME
    fi
fi
