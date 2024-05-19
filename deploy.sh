#!/bin/bash

REPO_DIR="/home/pet/site-pet/backend"
SERVICE_NAME="site-pet-backend.service"

cd $REPO_DIR

git fetch

LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ $LOCAL != $REMOTE ]; then
    systemctl stop $SERVICE_NAME
    
    if git pull --rebase origin main; then
        systemctl start $SERVICE_NAME
    else
        echo "Error: failed to pull changes; aborting update"
        git rebase --abort
        systemctl start $SERVICE_NAME
    fi
fi
