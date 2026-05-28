# ==========================================
# AKS Deployment Automation Script
# ==========================================

# 1. Navigate to the kubernetes directory
$KubeDir = Join-Path $PSScriptRoot "..\kubernetes"
Set-Location $KubeDir

Write-Host "Deploying application manifests using Kustomize..." -ForegroundColor Cyan
# Using Kustomize (-k) applies ALL the files (configmap, secrets, services, deployments, ingress) 
# and automatically replaces the image names with your ACR names as we set up earlier!
kubectl apply -k .

Write-Host ""
Write-Host "Installing Nginx Ingress Controller on AKS..." -ForegroundColor Cyan
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.2/deploy/static/provider/cloud/deploy.yaml

Write-Host ""
Write-Host "Waiting for Azure Load Balancer to assign a Public IP..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C when you see an IP address in the 'EXTERNAL-IP' column." -ForegroundColor Yellow
Write-Host "----------------------------------------------------------------------"
kubectl get service ingress-nginx-controller --namespace=ingress-nginx --watch
