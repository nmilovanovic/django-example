#!/bin/bash

# Default configuration
SERVER_HOST=${1:-"nm-thinkpad-t430.tailacb688.ts.net"}
SERVER_USER=nm
DEPLOY_PATH="~/django-example-deploy"

echo "🚀 Starting deployment to $SERVER_HOST..."

echo "📦 Creating deployment archive..."
# Archive the current directory, excluding common dev/temp folders and the local docker override
tar -czf deploy.tar.gz \
    --exclude='.git' \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='staticfiles' \
    --exclude='docker-compose.override.yml' \
    .

echo "👤 Connecting via SSH to create deployment directory..."
ssh "${SERVER_USER}@${SERVER_HOST}" "mkdir -p ${DEPLOY_PATH}"

echo "📤 Transferring archive to server..."
scp deploy.tar.gz "${SERVER_USER}@${SERVER_HOST}:${DEPLOY_PATH}/"

echo "🏗️  Extracting and starting containers remotely on the server..."
ssh "${SERVER_USER}@${SERVER_HOST}" << EOF
    cd ${DEPLOY_PATH}
    tar -xzf deploy.tar.gz
    rm deploy.tar.gz
    # Run using the production base file and the TLS override
    docker compose -f docker-compose.yml -f docker-compose.tls.yml up -d --build
EOF

SSH_EXIT_CODE=$?

echo "🧹 Cleaning up local archive..."
rm deploy.tar.gz

if [ $SSH_EXIT_CODE -eq 0 ]; then
    echo -e "\e[32m✅ Deployment successful!\e[0m"
    echo -e "\e[32m🌍 Your app should now be running at https://$SERVER_HOST\e[0m"
else
    echo -e "\e[31m❌ Deployment failed. Please check the error messages above.\e[0m"
fi
