#!/bin/bash
# got from https://gist.github.com/rdeavila/9618969
# keeps your master in sync
git remote add upstream https://github.com/mukulhase/WebWhatsapp-Wrapper
git fetch upstream
git checkout master
git rebase upstream/master
git merge upstream/master
git push -f origin master
