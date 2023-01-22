# ======================================================================
#  PowerShell script with steps to deploy using the Azure CLI.
#
#  Some commented-out commands in this script are intended to be executed
#  separately using F8 in an IDE (or by pasting into a shell).
#
#  Running this script will initialize variables for use in
#  az-setup-storage.ps1 and az-setup-webapp.ps1
#
# ----------------------------------------------------------------------


$baseName = "fileupaz"
$uniqtag = "22"


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

Write-Host "INFO:               rgName = '$rgName'"
Write-Host "INFO:             location = '$location'"
Write-Host "INFO:       appServiceName = '$appServiceName'"
Write-Host "INFO:           webAppName = '$webAppName'"
Write-Host "INFO:      storageAcctName = '$storageAcctName'"
Write-Host "INFO: storageContainerName = '$storageContainerName'"


# -- Define a function to check if a resource group exists.
#    https://docs.microsoft.com/en-us/cli/azure/group?view=azure-cli-latest#az_group_list

function RGExists([string]$rgName)
{
    $t = az group list | ConvertFrom-Json | Select-Object Name
    if ($null -eq $t) {
        return $false
    }
    else {
        return $t.Name.Contains($rgName)
    }
}


# ======================================================================
