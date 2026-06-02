@description('Azure Region')
param location string = 'East US'

@secure()
@description('SQL Server Admin Password')
param sqlAdminPassword string

@description('SQL Admin Username')
param sqlAdminUsername string = 'sqladmin'

@description('SQL Server Name')
param sqlServerName string = 'akshayserver56789'

@description('SQL Database Name')
param sqlDatabaseName string = 'akshaydb56789'

@description('Storage Account Name')
param storageAccountName string = 'akshaystorage56789'

@description('Blob Container Name')
param containerName string = 'social-media-images'

//
// SQL Server
//
resource sqlServer 'Microsoft.Sql/servers@2023-08-01-preview' = {
  name: sqlServerName
  location: location

  properties: {
    administratorLogin: sqlAdminUsername
    administratorLoginPassword: sqlAdminPassword
    publicNetworkAccess: 'Enabled'
    version: '12.0'
  }
}

//
// SQL Database (Basic Tier)
//
resource sqlDatabase 'Microsoft.Sql/servers/databases@2023-08-01-preview' = {
  parent: sqlServer
  name: sqlDatabaseName
  location: location

  sku: {
    name: 'Basic'
    tier: 'Basic'
    capacity: 5
  }

  properties: {
    maxSizeBytes: 104857600
  }
}

//
// Allow Azure Services
//
resource allowAzureServices 'Microsoft.Sql/servers/firewallRules@2023-08-01-preview' = {
  parent: sqlServer
  name: 'AllowAzureServices'

  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

//
// Storage Account
//
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageAccountName
  location: location

  sku: {
    name: 'Standard_LRS'
  }

  kind: 'StorageV2'

  properties: {
    allowBlobPublicAccess: false
    minimumTlsVersion: 'TLS1_2'
    supportsHttpsTrafficOnly: true
  }
}

//
// Blob Container
//
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = {
  parent: storageAccount
  name: 'default'
}

resource blobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = {
  parent: blobService
  name: containerName

  properties: {
    publicAccess: 'None'
  }
}

//
// Outputs
//
output sqlServerName string = sqlServer.name
output sqlDatabaseName string = sqlDatabase.name
output storageAccountName string = storageAccount.name
output containerName string = blobContainer.name

output sqlServerFQDN string = '${sqlServer.name}.database.windows.net'

output blobEndpoint string = storageAccount.properties.primaryEndpoints.blob