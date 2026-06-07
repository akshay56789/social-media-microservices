
# ============================
# Variables
# ============================

$ACR_NAME = "acr4c4a33d309"
$AKS_CLUSTER = "SocialLiteCluster"
$AKS_RG = "SocialLiteRG"
$TAG = "latest"

# Optional image tag
$TAG = "latest"

# ============================
# Build Auth Service
# ============================

Write-Host "Building auth-service..."

az acr build `
--registry $ACR_NAME `
--image auth-service:$TAG `
../auth-service

# ============================
# Build Post Service
# ============================

Write-Host "Building post-service..."

az acr build `
--registry $ACR_NAME `
--image post-service:$TAG `
../post-service

# ============================
# Build Comment Service
# ============================

Write-Host "Building comment-service..."

az acr build `
--registry $ACR_NAME `
--image comment-service:$TAG `
../comment-service

# ============================
# Build Media Service
# ============================

Write-Host "Building media-service..."

az acr build `
--registry $ACR_NAME `
--image media-service:$TAG `
../media-service

# ============================
# Build Frontend
# ============================

Write-Host "Building frontend..."

az acr build `
--registry $ACR_NAME `
--image frontend:$TAG `
../frontend

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

# ============================
# Connect to AKS
# ============================

Write-Host ""
Write-Host "Connecting to AKS..."

az aks get-credentials `
  --resource-group $AKS_RG `
  --name $AKS_CLUSTER `
  --overwrite-existing

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to connect to AKS"
    exit 1
}

Write-Host "Connected to AKS successfully."

# ============================
# Update Kustomization & Deploy
# ============================

Write-Host ""
Write-Host "Updating kustomization.yaml with ACR name ($ACR_NAME)..."
Push-Location ../kubernetes

# Update the images dynamically in Kustomize
kustomize edit set image auth-service=$ACR_NAME.azurecr.io/auth-service:$TAG
kustomize edit set image post-service=$ACR_NAME.azurecr.io/post-service:$TAG
kustomize edit set image comment-service=$ACR_NAME.azurecr.io/comment-service:$TAG
kustomize edit set image media-service=$ACR_NAME.azurecr.io/media-service:$TAG
kustomize edit set image frontend=$ACR_NAME.azurecr.io/frontend:$TAG

Write-Host "Applying Kubernetes manifests via Kustomize..."
kubectl apply -k .

Pop-Location
Write-Host "Deployment initiated!"
```
