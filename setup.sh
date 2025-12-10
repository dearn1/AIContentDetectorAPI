#!/bin/bash

# Install Heroku CLI
if ! command -v heroku &> /dev/null; then
    echo "Installing Heroku CLI..."
    curl https://cli-assets.heroku.com/install.sh | sh
fi

# Login to Heroku
heroku login

# Create a new Heroku app
echo "Creating a new Heroku app..."
heroku create ${1:-ai-content-detector-api}

# Set environment variables
echo "Setting environment variables..."
heroku config:set PYTHONPATH=/app
heroku config:set DEBUG=False
heroku config:set API_KEYS='[]'  # Start with empty API keys

# Add PostgreSQL addon (free tier)
echo "Adding PostgreSQL addon..."
heroku addons:create heroku-postgresql:hobby-dev

# Deploy to Heroku
echo "Deploying to Heroku..."
git push heroku main

# Open the app in browser
heroku open

echo "\n🎉 Deployment complete!"
echo "To manage your API keys, use the Heroku CLI:"
echo "  heroku config:set API_KEYS='$(cat .env | grep API_KEYS=)'"
echo "\nTo view logs:"
echo "  heroku logs --tail"
