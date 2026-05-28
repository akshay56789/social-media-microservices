```powershell
# ============================
# Variables
# ============================

$ACR_NAME = "youracrname"

# Optional image tag
$TAG = "latest"

# ============================
# Build Auth Service
# ============================

Write-Host "Building auth-service..."

az acr build `
--registry $ACR_NAME `
--image auth-service:$TAG `
./auth-service

# ============================
# Build Post Service
# ============================

Write-Host "Building post-service..."

az acr build `
--registry $ACR_NAME `
--image post-service:$TAG `
./post-service

# ============================
# Build Comment Service
# ============================

Write-Host "Building comment-service..."

az acr build `
--registry $ACR_NAME `
--image comment-service:$TAG `
./comment-service

# ============================
# Build Media Service
# ============================

Write-Host "Building media-service..."

az acr build `
--registry $ACR_NAME `
--image media-service:$TAG `
./media-service

# ============================
# Build Frontend
# ============================

Write-Host "Building frontend..."

az acr build `
--registry $ACR_NAME `
--image frontend:$TAG `
./frontend

# ============================
# Done
# ============================

Write-Host ""
Write-Host "All images built successfully!"
Write-Host ""

# ============================
# Verify Images
# ============================

az acr repository list `
--name $ACR_NAME `
--output table
```
