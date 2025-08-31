#!/bin/bash

echo "🚀 Vercel Setup for Invoice Verifier"
echo "===================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first:"
    echo "   Visit: https://nodejs.org/"
    echo "   Or use: brew install node (on macOS)"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js and npm are installed"
echo ""

# Install Vercel CLI globally
echo "📦 Installing Vercel CLI..."
npm install -g vercel

if [ $? -eq 0 ]; then
    echo "✅ Vercel CLI installed successfully"
else
    echo "❌ Failed to install Vercel CLI"
    exit 1
fi

echo ""
echo "🔧 Vercel CLI Setup Complete!"
echo ""
echo "📝 Next steps:"
echo "1. Login to Vercel:"
echo "   vercel login"
echo ""
echo "2. Deploy your project:"
echo "   vercel"
echo ""
echo "3. Or deploy to production:"
echo "   vercel --prod"
echo ""
echo "4. View your deployments:"
echo "   vercel ls"
echo ""
echo "🌐 Alternative: Deploy via Vercel Dashboard"
echo "   Visit: https://vercel.com/new"
echo "   Import: sudeepbhurat/invoice-verifier"
echo ""
echo "📖 For detailed instructions, see: VERCEL_DEPLOYMENT_GUIDE.md"
echo ""
echo "🎯 Your Invoice Verifier will be live on the internet in minutes!"
