# ======================================================================
#  PowerShell script with steps to deploy using the Azure CLI.
#
#  Some commented-out commands in this script are intended to be executed
#  separately using F8 in an IDE (or by pasting into a shell).
#
#  Running this script will:
#  - Create a Resource Group.
#  - Create an App Service Plan (Linux).
#  - Create a Web App.
#  - Configure the Web App for ZIP file deployment.
#
# ----------------------------------------------------------------------

# az login

# az account set -s $SUBSCRIPTION

# ======================================================================

# -- Source the initialization script.
. ./az-setup-init.ps1


# -- Get the connection string.
#    https://learn.microsoft.com/en-us/cli/azure/storage/account?view=azure-cli-latest#az-storage-account-show-connection-string-examples

$storageConnStr = $(
  az storage account show-connection-string `
    -g $rgName `
    -n $storageAcctName `
    --query connectionString `
    --output tsv
)


if ($storageRoleAssignee) {
  #  If the setting for FILEUP_STORAGE_ACCOUNT_URL is empty, it will not be
  #  in $appSettingsStr. Add that setting when using $storageRoleAssignee.
  if (!$fileupSettings["FILEUP_STORAGE_ACCOUNT_URL"]) {
    Write-Host "`nAdd setting FILEUP_STORAGE_ACCOUNT_URL`n"
    $storageAcctUrl = "https://${storageAcctName}.blob.core.windows.net"
    $fileupSettings["FILEUP_STORAGE_ACCOUNT_URL"] = $storageAcctUrl
  }
}
else {
  #  When not using the DefaultAzureCredential to access blob storage,
  #  set the connection string.
  if (!$fileupSettings["FILEUP_STORAGE_CONNECTION"]) {
    Write-Host "`nAdd setting FILEUP_STORAGE_CONNECTION`n"
    $fileupSettings["FILEUP_STORAGE_CONNECTION"] = $storageConnStr
  }
}

# -- Add setting for table storage connection.

if (!$fileupSettings["FILEUP_TABLES_CONNECTION"]) {
  Write-Host "`nAdd setting FILEUP_TABLES_CONNECTION`n"
  $fileupSettings["FILEUP_TABLES_CONNECTION"] = $storageConnStr
}
  

#  Build a settings string, to use in 'az webapp config appsettings', using the
#  key=value pairs in the $fileupSettings dictionary loaded from $keysFile.

$appSettingsStr = ""
foreach ($key in $fileupSettings.Keys) {
  $value = $fileupSettings[$key]
  if (0 -lt $value.Length) {
    $appSettingsStr += (' "' + $key + '=' + $value + '"')
  }
}

#  Run this to see that the string has spaces in the right places.
# $appSettingsStr.Split(" ")



# ======================================================================
# Create and configure Azure resources.

if (RGExists($rgName)) {
    Write-Host "`nResource group exists: $rgName`n"
}
else {
    Write-Host "`nSTEP - Create resource group: $rgName`n"
    az group create -n $rgName -l $location
}


# -- Create the App Service Plan (Linux).
#    https://docs.microsoft.com/en-us/cli/azure/appservice/plan?view=azure-cli-latest#az-appservice-plan-create

Write-Host "`nSTEP - Create App Service Plan: $appServiceName`n"

az appservice plan create `
  --name $appServiceName `
  --resource-group $rgName `
  --is-linux `
  --sku s1


# -- Create the Web App.
#    https://docs.microsoft.com/en-us/cli/azure/webapp?view=azure-cli-latest#az-webapp-create
#
#    az webapp list-runtimes

Write-Host "`nSTEP - Create Web App: $webAppName`n"

az webapp create `
  -g $rgName `
  -p $appServiceName `
  --name $webAppName `
  --runtime "PYTHON:3.10"


# -- Configure for ZIP file deployment.
#    https://learn.microsoft.com/en-us/azure/app-service/quickstart-python?tabs=flask%2Cwindows%2Cazure-cli%2Czip-deploy%2Cdeploy-instructions-azcli%2Cterminal-bash%2Cdeploy-instructions-zip-azcli#3---deploy-your-application-code-to-azure

Write-Host "`nSTEP - Configure settings for: $webAppName`n"

az webapp config appsettings set `
    -g $rgName `
    --name $webAppName `
    --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true


# -- Configure settings for the web app. These are available to the app as environment variables.
#    https://learn.microsoft.com/en-us/cli/azure/webapp/config/appsettings?view=azure-cli-latest

Write-Host "`nSTEP - Configure web app settings for: $webAppName`n"


#  In order to treat the settings in $appSettingsStr as separate arguments that
#  follow '--settings', create the az command as an expression and invoke it.

$expr = "az webapp config appsettings set -g $rgName --name $webAppName --settings $appSettingsStr"
Invoke-Expression $expr


# -- Set custom startup command for running the Flask app.
#    https://learn.microsoft.com/en-us/azure/app-service/configure-language-python#customize-startup-command

Write-Host "`nSTEP - Configure startup command for: $webAppName`n"

$startCmd = "gunicorn --bind=0.0.0.0 --timeout 600 --chdir fileup_app fileup:app"
az webapp config set -g $rgName --name $webAppName --startup-file $startCmd


# ----------------------------------------------------------------------
# Additional commands and information.


# -- Zip deploy (update $zipFile value before running).
#    https://learn.microsoft.com/en-us/cli/azure/webapp?view=azure-cli-latest#az-webapp-deploy
#
# $zipFile = "../deploy/fileup_20230112_01.zip"
# az webapp deploy --name $webAppName -g $rgName --src-path $zipFile


# -- List resources.
#
# az resource list -g $rgName -o table


# ======================================================================