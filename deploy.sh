#!/bin/bash

eval $(ssh-agent -s) && \
ssh-add ~/.ssh/dokku/dokku.private && \

git init && \
git add . && \
git commit -m "Init" && \
git remote add lputormis dokku@192.168.2.45:lputormis && \

git push -f lputormis master