#!/bin/bash
flakeOK=$(flake8 .)

if [ -z "$flakeOK" ]; then
  echo "Flake8 OK..."
  git add .
  cz commit
else
  echo "$flakeOK"
fi
