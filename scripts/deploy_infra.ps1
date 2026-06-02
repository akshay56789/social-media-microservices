# Get first resource group
$resourceGroup = az group list --query "[0].name" -o tsv

Write-Host "Using Resource Group: $resourceGroup"

$securePassword = Read-Host "Enter SQL Admin Password" -AsSecureString

$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
$sqlPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

az deployment group create `
  --resource-group $resourceGroup `
  --template-file \main.bicep `
  --parameters sqlAdminPassword="$sqlPassword"