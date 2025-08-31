#!/bin/bash

echo "🚀 GitHub Repository Setup for Invoice Verifier"
echo "================================================"
echo ""
echo "This script will help you set up your GitHub repository."
echo ""

# Get GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

# Get repository name
read -p "Enter your repository name (or press Enter for 'invoice-verifier'): " REPO_NAME
REPO_NAME=${REPO_NAME:-invoice-verifier}

echo ""
echo "📋 Repository Details:"
echo "  Username: $GITHUB_USERNAME"
echo "  Repository: $REPO_NAME"
echo "  URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""

# Confirm
read -p "Is this correct? (y/n): " CONFIRM
if [[ $CONFIRM != "y" && $CONFIRM != "Y" ]]; then
    echo "❌ Setup cancelled."
    exit 1
fi

echo ""
echo "🔧 Setting up GitHub remote..."

# Add remote origin
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git

# Set upstream branch
git branch -M main

echo ""
echo "✅ GitHub remote configured!"
echo ""
echo "📝 Next steps:"
echo "1. Create a new repository on GitHub: https://github.com/new"
echo "   - Name: $REPO_NAME"
echo "   - Description: Invoice Verifier - GST Compliance System"
echo "   - Make it Public or Private as you prefer"
echo "   - Don't initialize with README (we already have one)"
echo ""
echo "2. Push your code:"
echo "   git push -u origin main"
echo ""
echo "3. Or run this command to push automatically:"
echo "   ./push_to_github.sh"
echo ""

# Create push script
cat > push_to_github.sh << 'EOF'
#!/bin/bash
echo "🚀 Pushing to GitHub..."
git push -u origin main
echo "✅ Code pushed successfully!"
echo "🌐 View your repository: https://github.com/'$GITHUB_USERNAME'/'$REPO_NAME'"
EOF

chmod +x push_to_github.sh
echo "📄 Created push_to_github.sh script for easy pushing!"
