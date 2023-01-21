# ======================================================================
#  PowerShell script with steps to deploy using the Azure CLI.
#
#  Some commented-out commands in this script are intended to be executed
#  separately using F8 in an IDE (or by pasting into a shell).
#
#  Running this script will:
#  - Create a Resource Group.
#  TODO: Fill in the missing items here...
#  - Create an App Service Plan (Linux).
#  - Create a Web App.
#  - Configure the Web App for ZIP file deployment.
#
# ----------------------------------------------------------------------

# az login

# az account set -s $SUBSCRIPTION

# ----------------------------------------------------------------------
# Script initialization:

$baseName = "fileupaz"
$uniqtag = "21"


# -- Get key variables from file in local encrypted folder.

$profilePath = [Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
$keysFile = [System.IO.Path]::Combine($profilePath, "KeepLocal", "${baseName}-settings.ps1")


# -- Source the file to set the $fileupSettings variable (dictionary).
. $keysFile

# -- Check that the required variables were set.
function CheckVarSet ([string] $varName) {
    
  if (![bool](Get-Variable -Name $varName -ErrorAction:Ignore)) {
    Write-Host "ERROR: '$varName' not set in '$keysFile'."
    Exit 1
  }
}

CheckVarSet "fileupSettings"
CheckVarSet "storageRoleAssignee"


# -- Check that required settings (dictionary keys) exist.
function CheckKeyExists ([string] $varName) {

  if (! $fileupSettings.ContainsKey($varName)) {
    Write-Host "ERROR: '$varName' not set in '$keysFile'."
    Exit 1
  }
}

CheckKeyExists "FILEUP_SECRET_KEY"
CheckKeyExists "FILEUP_MAX_UPLOAD_MB"
CheckKeyExists "FILEUP_ENABLE_FEATURES"
CheckKeyExists "FILEUP_UPLOAD_ACCEPT"
CheckKeyExists "FILEUP_MSAL_REDIRECT_PATH"
CheckKeyExists "FILEUP_MSAL_AUTHORITY"
CheckKeyExists "FILEUP_MSAL_CLIENT_ID"
CheckKeyExists "FILEUP_MSAL_CLIENT_SECRET"
CheckKeyExists "FILEUP_MSAL_SCOPE"
CheckKeyExists "FILEUP_STORAGE_ACCOUNT_URL"
CheckKeyExists "FILEUP_STORAGE_CONNECTION"
CheckKeyExists "FILEUP_STORAGE_CONTAINER"
CheckKeyExists "FILEUP_TABLES_CONNECTION"


# -- Assign additional variables used in this script.

$rgName = "${baseName}_rg"
$location = "eastus"
$appServiceName = "${baseName}${uniqtag}appserv"
$webAppName = "${baseName}${uniqtag}webapp"
$storageAcctName = "${baseName}${uniqtag}storage"

$storageContainerName = $fileupSettings["FILEUP_STORAGE_CONTAINER"]
if (!$storageContainerName) {
  $storageContainerName = "fileup"
}
Write-Host "INFO: storageContainerName = '$storageContainerName'"


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

Write-Host "`nSTEP - Create resource group: $rgName`n"

az group create -n $rgName -l $location


Write-Host "`nSTEP - Create Storage Account: $storageAcctName`n"

# -- Create the Storage Account.
#    https://docs.microsoft.com/en-us/cli/azure/storage/account?view=azure-cli-latest#az-storage-account-create

az storage account create -n $storageAcctName -l $location -g $rgName --sku Standard_LRS


# -- Get the storage account key.
#    Example found in Microsoft Docs: "Mount a file share to a Python function app - Azure CLI"
#    https://docs.microsoft.com/en-us/azure/azure-functions/scripts/functions-cli-mount-files-storage-linux

$storageKey = $(az storage account keys list -g $rgName -n $storageAcctName --query '[0].value' -o tsv)


# -- Get the connection string.
#    https://learn.microsoft.com/en-us/cli/azure/storage/account?view=azure-cli-latest#az-storage-account-show-connection-string-examples

$storageConnStr = $(az storage account show-connection-string -g $rgName -n $storageAcctName --query connectionString --output tsv)



# -- Assign role to access blob storage. Used for DefaultAzureCredential to
#    access BlobServiceClient when not using a connection string.
#
#    Authenticate to Azure and authorize access to blob data:
#    https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-dotnet?tabs=visual-studio%2Cmanaged-identity%2Croles-azure-cli%2Csign-in-azure-cli%2Cidentity-visual-studio#authenticate-to-azure-and-authorize-access-to-blob-data

if ($storageRoleAssignee) {
  Write-Host "`nSTEP - Assign blob data access role for : $storageAcctName`n"
  $storageResourceId = $(az storage account show -g $rgName -n $storageAcctName --query id)
  az role assignment create --assignee $storageRoleAssignee --role "Storage Blob Data Contributor" --scope $storageResourceId

  #  If the setting for FILEUP_STORAGE_ACCOUNT_URL is empty, it will not be
  #  in $appSettingsStr. Add that setting when using $storageRoleAssignee.

  if (!$appSettingsStr.Contains("FILEUP_STORAGE_ACCOUNT_URL")) {
    Write-Host "`nAdd setting FILEUP_STORAGE_ACCOUNT_URL`n"
    $storageAcctUrl = "https://${storageAcctName}.blob.core.windows.net"
    $s = '"FILEUP_STORAGE_ACCOUNT_URL=' + $storageAcctUrl + '"'
    $appSettingsStr += " $s"
  }  
}
else {
  #  When not using the DefaultAzureCredential to access blob storage,
  #  set the connection string.
  if (!$appSettingsStr.Contains("FILEUP_STORAGE_CONNECTION")) {
    Write-Host "`nAdd setting FILEUP_STORAGE_CONNECTION`n"
    $s = '"FILEUP_STORAGE_CONNECTION=' + $storageConnStr + '"'
    $appSettingsStr += " $s"
  }
}


# -- Add setting for table storage connection.

if (!$appSettingsStr.Contains("FILEUP_TABLES_CONNECTION")) {
  Write-Host "`nAdd setting FILEUP_TABLES_CONNECTION`n"
  $s = '"FILEUP_TABLES_CONNECTION=' + $storageConnStr + '"'
  $appSettingsStr += " $s"
}


# -- Create storage container.
#    https://docs.microsoft.com/en-us/cli/azure/storage/container?view=azure-cli-latest#az-storage-container-create

Write-Host "`nSTEP - Create Storage Container: $storageContainerName`n"

az storage container create `
  --account-key $storageKey `
  --account-name $storageAcctName `
  --name $storageContainerName


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
