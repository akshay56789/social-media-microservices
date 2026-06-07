
# ============================
# Variables
# ============================

$ACR_NAME = "akshayregistry"
$AKS_CLUSTER = "akshaycluster"
$AKS_RG = az group list --query "[0].name" -o tsv
Write-Host "Resource Group: $AKS_RG"
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


# login to acr
$acrCreds = az acr credential show `
    --name $ACR_NAME `
    | ConvertFrom-Json

$acrUser = $acrCreds.username
$acrPass = $acrCreds.passwords[0].value

kubectl create secret docker-registry acr-secret `
  --docker-server=akshayregistry.azurecr.io `
  --docker-username=$acrUser `
  --docker-password=$acrPass



# Write-Host "Applying Kubernetes manifests via Kustomize..."
# kubectl apply -k .

Pop-Location
Write-Host "Deployment initiated!"

