# ======================================================================
#  az-setup-4-deploy.ps1
# ----------------------------------------------------------------------


# -- Source the initialization script.
. ./az-setup-init.ps1


# -- Deploy the webapp ZIP file.
#    https://learn.microsoft.com/en-us/cli/azure/webapp?view=azure-cli-latest#az-webapp-deploy

$zipFile = "../deploy/fileup_deploy.zip"

az webapp deploy --name $webAppName -g $webappRG --src-path $zipFile


# ======================================================================
