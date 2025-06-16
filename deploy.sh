#!/bin/bash
# SMIF Dashboard Deployment Script

echo "🚀 SMIF Dashboard Deployment"
echo "=============================="

# Check if config file exists
if [ ! -f "config.py" ]; then
    echo "⚠️  WARNING: config.py not found!"
    echo "📋 Please copy config_template.py to config.py and update with your class info"
    echo "   cp config_template.py config.py"
    echo "   # Then edit config.py with real emails and password"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
fi

# Security check
echo "🔍 Running security checks..."

# Check for sensitive files
SENSITIVE_FILES=("*.xlsx" "data/" ".env")
for pattern in "${SENSITIVE_FILES[@]}"; do
    if ls $pattern 1> /dev/null 2>&1; then
        echo "⚠️  WARNING: Found potentially sensitive files: $pattern"
        echo "   These should be in .gitignore"
    fi
done

# Verify .gitignore exists
if [ ! -f ".gitignore" ]; then
    echo "❌ ERROR: .gitignore missing! This is required for security."
    exit 1
fi

echo "✅ Security checks passed"

# Git operations
echo ""
echo "📦 Preparing for deployment..."

# Add files
git add .

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "ℹ️  No changes to commit"
else
    echo "📝 Committing changes..."
    git commit -m "Deploy SMIF dashboard - $(date '+%Y-%m-%d %H:%M')"
fi

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "📋 Next steps:"
echo "1. Go to https://share.streamlit.io"
echo "2. Connect this GitHub repository"
echo "3. Set main file: streamlit_app.py"
echo "4. Configure secrets if using Streamlit Cloud secrets"
echo "5. Deploy and share URL with students"
echo ""
echo "🔐 Security reminders:"
echo "- Keep repository PRIVATE"
echo "- Use strong passwords"
echo "- Update email list each semester"
echo "- Monitor access logs"
echo ""
echo "📖 See DEPLOYMENT_SECURITY.md for detailed instructions"