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

# Source function definitions.
. .\az-funcs.ps1

$baseName = "fileupaz"
$uniqtag = "01"


# -- Get key variables from file in local encrypted folder.

$profilePath = [Environment]::GetFolderPath([Environment+SpecialFolder]::UserProfile)
$keysFile = [System.IO.Path]::Combine($profilePath, "KeepLocal", "${baseName}-settings.ps1")


# -- Source the file to set the $fileupSettings variable (dictionary).
. $keysFile

# -- Check that the required variables were set.
function CheckVarSet ([string] $varName) {

  if (![bool](Get-Variable -Name $varName -ErrorAction:Ignore)) {
    Yell "ERROR: '$varName' not set in '$keysFile'."
    Exit 1
  }
}

CheckVarSet "fileupSettings"
CheckVarSet "storageRoleAssignee"


# -- Check that required settings (dictionary keys) exist.
function CheckKeyExists ([string] $varName) {

  if (! $fileupSettings.ContainsKey($varName)) {
    Yell "ERROR: '$varName' not set in '$keysFile'."
    Exit 1
  }
}

CheckKeyExists "FILEUP_SECRET_KEY"
CheckKeyExists "FILEUP_PROXY_LEVEL"
CheckKeyExists "FILEUP_MAX_UPLOAD_MB"
CheckKeyExists "FILEUP_ENABLE_FEATURES"
CheckKeyExists "FILEUP_UPLOAD_ACCEPT"
CheckKeyExists "FILEUP_MSAL_REDIRECT_PATH"
CheckKeyExists "FILEUP_MSAL_AUTHORITY"
CheckKeyExists "FILEUP_MSAL_CLIENT_ID"
CheckKeyExists "FILEUP_MSAL_CLIENT_SECRET"
CheckKeyExists "FILEUP_MSAL_SCOPE"
CheckKeyExists "FILEUP_STORAGE_CONTAINER"
CheckKeyExists "FILEUP_STORAGE_TABLE_UPLOADS"
CheckKeyExists "FILEUP_STORAGE_TABLE_CACHE"
CheckKeyExists "FILEUP_STORAGE_ACCOUNT_NAME"
CheckKeyExists "FILEUP_STORAGE_ACCOUNT_KEY"
CheckKeyExists "FILEUP_STORAGE_ENDPOINT_SUFFIX"


# -- Assign additional variables used in this script.

# -- Put storage and webapp in different resource groups
#    (or give them the same name to use a single group).
# $storageRG = "${baseName}_storage_rg"
# $webappRG = "${baseName}_webapp_rg"
$storageRG = "${baseName}_rg"
$webappRG = "${baseName}_rg"

$location = "eastus"
$appServiceName = "${baseName}${uniqtag}appserv"
$webAppName = "${baseName}${uniqtag}webapp"
$storageAcctName = "${baseName}${uniqtag}storage"

$storageContainerName = $fileupSettings["FILEUP_STORAGE_CONTAINER"]
if (!$storageContainerName) {
  $storageContainerName = "fileup"
}

$uploadsTableName = "Uploads"
$cacheTableName = "Cache"

Say "INFO:            storageRG = '$storageRG'"
Say "INFO:             webappRG = '$webappRG'"
Say "INFO:             location = '$location'"
Say "INFO:       appServiceName = '$appServiceName'"
Say "INFO:           webAppName = '$webAppName'"
Say "INFO:      storageAcctName = '$storageAcctName'"
Say "INFO: storageContainerName = '$storageContainerName'"
Say "INFO:     uploadsTableName = '$uploadsTableName'"
Say "INFO:       cacheTableName = '$cacheTableName'"


# ======================================================================
