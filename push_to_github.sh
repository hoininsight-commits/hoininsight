#!/bin/bash

# Project HOIN Git Push Helper

# Set GH_TOKEN as an environment variable or it will prompt for it if missing from remote
GH_REPO="github.com/hoininsight-commits/hoininsight.git"
COMMIT_MSG="[DP] Implement Production-Ready Topic Gate & Hardened Decision Dashboard v1.0"

echo "Checking for Git installation..."
if ! command -v git &> /dev/null; then
    echo "Error: Git is not installed. Please install Xcode Command Line Tools or Git manually."
    exit 1
fi

echo "Initializing Git repository..."
if [ ! -d ".git" ]; then
    git init
    echo "Git initialized."
fi

echo "Configuring remote..."
# Check if the current remote has a token
CURRENT_URL=$(git remote get-url origin 2>/dev/null)
if [[ $CURRENT_URL == *"ghp_"* ]]; then
    echo "Using existing token from remote."
elif [ -n "$GH_TOKEN" ]; then
    echo "Using PROVIDED GH_TOKEN."
    git remote set-url origin "https://${GH_TOKEN}@${GH_REPO}"
else
    echo "Warning: No token found. Please set the GH_TOKEN environment variable."
    echo "Example: export GH_TOKEN=your_token_here"
    exit 1
fi

# Ensure remote is named origin and pointing to the right place if it wasn't set
if ! git remote | grep -q "origin"; then
    git remote add origin "https://${GH_TOKEN:-$SAVED_TOKEN}@${GH_REPO}"
fi

echo "Adding files..."
git add .

echo "Committing..."
git commit -m "$COMMIT_MSG"

echo "Pushing to main..."
git branch -M main
git push -u origin main

echo "Done! Project HOIN files have been pushed."
