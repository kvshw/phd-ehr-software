#!/bin/bash
# CSC Rahti Deployment Script
# Usage: ./rahti/deploy.sh

set -e

echo "========================================="
echo "EHR Platform - CSC Rahti Deployment"
echo "========================================="

# Check if logged in
if ! oc whoami &> /dev/null; then
    echo "❌ Not logged in to Rahti!"
    echo ""
    echo "Please login first:"
    echo "1. Go to https://rahti.csc.fi"
    echo "2. Click your username → 'Copy login command'"
    echo "3. Run the command in terminal"
    exit 1
fi

echo "✅ Logged in as: $(oc whoami)"
echo ""

# Check/create project
PROJECT="ehr-platform"
if oc get project $PROJECT &> /dev/null; then
    echo "✅ Project '$PROJECT' exists"
    oc project $PROJECT
else
    echo "Creating project '$PROJECT'..."
    echo ""
    echo "⚠️  Rahti requires your CSC computing project ID in the description."
    echo "   Get it from: https://my.csc.fi → Your Project → Project ID"
    echo ""
    read -p "Enter your CSC Project ID (e.g., project_2001234): " CSC_PROJECT_ID
    
    oc new-project $PROJECT \
      --display-name="EHR Research Platform" \
      --description="EHR Research Platform - CSC Project: ${CSC_PROJECT_ID}"
fi

# Check/create secrets
if oc get secret ehr-secrets &> /dev/null; then
    echo "✅ Secrets already exist"
else
    echo ""
    echo "Creating secrets..."
    echo "You'll need:"
    echo "  1. Database URL (Supabase connection string)"
    echo "  2. JWT Secret (generate with: openssl rand -hex 32)"
    echo ""
    read -p "Enter Database URL: " DB_URL
    read -p "Enter JWT Secret: " JWT_SECRET
    
    oc create secret generic ehr-secrets \
      --from-literal=database-url="$DB_URL" \
      --from-literal=jwt-secret="$JWT_SECRET"
    echo "✅ Secrets created"
fi

echo ""
echo "Deploying Backend..."
echo "--------------------"

# Update Git URL in backend.yaml
read -p "Enter your GitHub repo URL (e.g., https://github.com/user/repo): " REPO_URL
sed -i.bak "s|https://github.com/YOUR_USERNAME/YOUR_REPO.git|$REPO_URL|g" rahti/backend.yaml
sed -i.bak "s|https://github.com/YOUR_USERNAME/YOUR_REPO.git|$REPO_URL|g" rahti/frontend.yaml

# Apply backend
oc apply -f rahti/backend.yaml

echo ""
echo "Starting backend build..."
oc start-build ehr-backend --follow || true

echo ""
echo "Deploying Frontend..."
echo "---------------------"

# Apply frontend
oc apply -f rahti/frontend.yaml

echo ""
echo "Starting frontend build..."
oc start-build ehr-frontend --follow || true

echo ""
echo "Waiting for deployments to be ready..."
sleep 10

# Get URLs
BACKEND_URL=$(oc get route ehr-backend -o jsonpath='{.spec.host}' 2>/dev/null || echo "Not ready yet")
FRONTEND_URL=$(oc get route ehr-frontend -o jsonpath='{.spec.host}' 2>/dev/null || echo "Not ready yet")

# Update CORS if frontend URL is available
if [ "$FRONTEND_URL" != "Not ready yet" ]; then
    echo ""
    echo "Updating CORS settings..."
    oc set env deployment/ehr-backend \
      CORS_ORIGINS="[\"https://${FRONTEND_URL}\"]" 2>/dev/null || true
fi

# Update frontend API URL if backend URL is available
if [ "$BACKEND_URL" != "Not ready yet" ]; then
    echo "Updating frontend API URL..."
    oc set env deployment/ehr-frontend \
      NEXT_PUBLIC_API_URL="https://${BACKEND_URL}" 2>/dev/null || true
fi

echo ""
echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="
echo ""
echo "Your URLs:"
oc get routes
echo ""
echo "Pod Status:"
oc get pods
echo ""
echo "📋 Next Steps:"
echo "1. Wait for pods to be 'Running' (may take 5-10 minutes for first build)"
echo "2. Check logs if pods aren't starting:"
echo "   oc logs -f deployment/ehr-backend"
echo "   oc logs -f deployment/ehr-frontend"
echo "3. Test your frontend URL in browser"
echo ""
echo "🔄 To rebuild after code changes:"
echo "   oc start-build ehr-backend"
echo "   oc start-build ehr-frontend"

