# ======================================================================
#  az-setup-3-roles.ps1
# ----------------------------------------------------------------------

# -- Source the initialization script.
. ./az-setup-0-init.ps1


# -- Create a system-assigned managed identity for the web app.
#    https://learn.microsoft.com/en-us/azure/app-service/overview-managed-identity?tabs=cli%2Chttp#add-a-system-assigned-identity

Say "`nSTEP - Add system-assigned managed identity to: $webAppName`n"

az webapp identity assign  -g $webappRG -n $webAppName


# -- Get the service principal ID for the managed identity.
#    https://learn.microsoft.com/en-us/azure/role-based-access-control/scope-overview
#    https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/howto-assign-access-cli#use-azure-rbac-to-assign-a-managed-identity-access-to-another-resource

$webappIdentityId = (az resource list -g $webappRG -n $webAppName --query [*].identity.principalId --out tsv)


# -- Get the storage account resource ID.

$storageAcctResId = $(az storage account show -g $storageRG -n $storageAcctName --query id --out tsv)


# -- Get the blob and table resource IDs.

#  The portal does not seem to have an option for setting IAM roles at the blob
#  container scope. This ID did not work.
# $blobResId = "$storageAcctResId/blobServices/default/blobs/fileup"

#  This ID does work to assign the role at the blob service scope.
$blobResId = "$storageAcctResId/blobServices/default"

#  The role can be assigned at the individual table scope.
$tableResId = "$storageAcctResId/tableServices/default/tables/Uploads"


# -- Get the ID (name) of the roles to be assigned to the managed identity.
$blobRoleId = (az role definition list --name "Storage Blob Data Contributor" --query [*].name --out tsv)
$tableRoleId = (az role definition list --name "Storage Table Data Contributor" --query [*].name --out tsv)


# -- Add the role assignments to the managed identity.
az role assignment create --assignee $webappIdentityId --role $blobRoleId --scope $blobResId
az role assignment create --assignee $webappIdentityId --role $tableRoleId --scope $tableResId


# ======================================================================
