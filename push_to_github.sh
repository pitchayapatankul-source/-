#!/bin/bash
# TableChain GitHub Push Helper
# Usage: ./push_to_github.sh https://github.com/YOUR_USERNAME/YOUR_REPO.git

REPO_URL=$1

if [ -z "$REPO_URL" ]; then
    echo "============================================================"
    echo "   TableChain - Push to GitHub"
    echo "============================================================"
    echo ""
    echo "Please provide your GitHub repository URL."
    echo "Example:"
    echo "   ./push_to_github.sh https://github.com/your-username/tablechain.git"
    echo ""
    echo "Or follow the manual steps below:"
    echo "1. Create a new repository on https://github.com/new"
    echo "   (Name it: tablechain, public, do NOT check README/.gitignore)"
    echo "2. Run:"
    echo "   git remote add origin <YOUR_REPO_URL>"
    echo "   git push -u origin main"
    echo "============================================================"
    exit 1
fi

echo "Adding git remote origin: $REPO_URL ..."
git remote remove origin 2>/dev/null
git remote add origin "$REPO_URL"

echo "Pushing main branch to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo ""
    echo "To host the website live on GitHub Pages:"
    echo "1. Go to your repo on GitHub -> Settings -> Pages"
    echo "2. Under 'Build and deployment', choose:"
    echo "   - Source: Deploy from a branch"
    echo "   - Branch: main, Folder: / (root)"
    echo "3. Click Save. Your website will be live in 1-2 minutes!"
else
    echo ""
    echo "❌ Failed to push. Please check your GitHub repository URL and credentials."
fi
