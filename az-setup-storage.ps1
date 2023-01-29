# ======================================================================
#  PowerShell script with steps to deploy using the Azure CLI.
#
#  Some commented-out commands in this script are intended to be executed
#  separately using F8 in an IDE (or by pasting into a shell).
#
#  Running this script will:
#  - Create a Resource Group.
#  TODO: Fill in the missing items here...
#
# ----------------------------------------------------------------------

# az login

# az account set -s $SUBSCRIPTION

# ======================================================================

# -- Source the initialization script.
. ./az-setup-init.ps1


# ======================================================================
# Create and configure Azure resources.

if (RGExists($rgName)) {
    Say "`nResource group exists: $rgName`n"
}
else {
    Say "`nSTEP - Create resource group: $rgName`n"
    az group create -n $rgName -l $location
}


Say "`nSTEP - Create Storage Account: $storageAcctName`n"

# -- Create the Storage Account.
#    https://docs.microsoft.com/en-us/cli/azure/storage/account?view=azure-cli-latest#az-storage-account-create

az storage account create -n $storageAcctName -l $location -g $rgName --sku Standard_LRS


# -- Get the storage account key.
#    Example found in Microsoft Docs: "Mount a file share to a Python function app - Azure CLI"
#    https://docs.microsoft.com/en-us/azure/azure-functions/scripts/functions-cli-mount-files-storage-linux

$storageKey = $(az storage account keys list -g $rgName -n $storageAcctName --query '[0].value' -o tsv)


# -- Assign role to access blob storage. Used for DefaultAzureCredential to
#    access BlobServiceClient when not using a connection string.
#
#    Authenticate to Azure and authorize access to blob data:
#    https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-dotnet?tabs=visual-studio%2Cmanaged-identity%2Croles-azure-cli%2Csign-in-azure-cli%2Cidentity-visual-studio#authenticate-to-azure-and-authorize-access-to-blob-data

if ($storageRoleAssignee) {
  Say "`nSTEP - Assign blob data access role for : $storageAcctName`n"
  $storageResourceId = $(az storage account show -g $rgName -n $storageAcctName --query id)

  az role assignment create `
    --assignee $storageRoleAssignee `
    --role "Storage Blob Data Contributor" `
    --scope $storageResourceId

}



# -- Create storage container for blob data.
#    https://docs.microsoft.com/en-us/cli/azure/storage/container?view=azure-cli-latest#az-storage-container-create

Say "`nSTEP - Create Storage Container: $storageContainerName`n"

az storage container create `
  --account-key $storageKey `
  --account-name $storageAcctName `
  --name $storageContainerName


# -- Create Uploads table.
#    https://learn.microsoft.com/en-us/cli/azure/storage/table?view=azure-cli-latest#az-storage-table-create

Say "`nSTEP - Create Storage Table: $storageTableName`n"

az storage table create `
  --account-key $storageKey `
  --account-name $storageAcctName `
  --name $storageTableName



# ----------------------------------------------------------------------
# Additional commands and information.


# -- List resources.
#
# az resource list -g $rgName -o table


# ======================================================================
