# File Upload App using Flask and Azure

> This is a work-in-progress demo. If it works out, a LICENSE will be added when it is done. Otherwise this repository will probably go away.

<sub>Created: 2023-01-19</sub>

Started with a copy of the files in the [flask-file-up](https://github.com/wmelvin/flask-file-up) project as of commit [4f4ee83](https://github.com/wmelvin/flask-file-up/tree/4f4ee83b58f248874396ef977acde63cb8af695e).

Rather than clone that project, and bring along all of its history, a ZIP download was used to get the files. Code related to the database model (SQLAlchemy-derived classes), and for managing user identities within the app, was removed. This project will use only Azure Active Directory (via MSAL) for user identity management and Azure Storage for receiving uploaded files.

A new Git repository was created after pruning the code and successfully running the main functions of the app locally (the Flask app ran in the local development server, but was connected to live Azure resources).


## Configuration

### Environment Variables

The following envirionment variables configure the application:

```sh
FILEUP_SECRET_KEY=""
FILEUP_ENABLE_FEATURES=""
FILEUP_UPLOAD_ACCEPT=""
FILEUP_MAX_UPLOAD_MB=""
FILEUP_MSAL_REDIRECT_PATH=""
FILEUP_MSAL_AUTHORITY=""
FILEUP_MSAL_CLIENT_ID=""
FILEUP_MSAL_CLIENT_SECRET=""
FILEUP_MSAL_SCOPE=""
FILEUP_STORAGE_ACCOUNT_NAME=""
FILEUP_STORAGE_CONTAINER=""
FILEUP_STORAGE_TABLE=""
FILEUP_STORAGE_ACCOUNT_KEY=""
FILEUP_STORAGE_ENDPOINT_SUFFIX=""
```

The puropse of each environment variable is described below.

#### Web Application Settings

**`FILEUP_SECRET_KEY`** Sets the Flask [SECRET_KEY](https://flask.palletsprojects.com/en/latest/config/?highlight=secret_key#SECRET_KEY).

**`FILEUP_PROXY_LEVEL`** Set this to the number of proxies the app is running behind to [Tell Flask it is Behind a Proxy](https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/). That enables the [X-Forwarded-For Proxy Fix](https://werkzeug.palletsprojects.com/en/0.16.x/middleware/proxy_fix/). If not running behind a proxy, set the level to '0' (zero) to disable the ProxyFix middleware.

**`FILEUP_ENABLE_FEATURES`** - Enable optional features in the application. Options are enabled using option names. Enable multiple options by separating the names with a space.
* `CheckStorage` enables a `/checkstorage` route that calls a function to ckeck access to Azure Blob and Table storage. 
* `LogDebug` sets the Flask logging level to `DEBUG` (most verbose).
* `LogInfo` sets the Flask logging level to `INFO` (default logging level is `WARNING`).
* `NoPrefix` disables adding a "upload-*date_time*-" prefix to the name of uploaded files.
* `NoRole` allows any authenticated user to upload files without an *App Role* assignment.

**`FILEUP_UPLOAD_ACCEPT`** - Comma-separated list of file types (extensions) to accept in uploaded file names. The default settings is `".csv,.xls,.xlsx"`. This is used limit the upload file selection on the client side (form input field) and for server-side file name validation.

**`FILEUP_MAX_UPLOAD_MB`** - Maximum allowed file size, in megabytes, for uploaded files. If not set, the default maximum size is 2 MB.


#### User Identity (Authentication/Authorization) Settings

**`FILEUP_APP_ROLE`** - *App Role* that must be assigned to authorize a user to upload files (unelss *NoRole* feature is enabled). Default value is `File.Upload`.

**`FILEUP_MSAL_REDIRECT_PATH`** - *Not yet implemented - currently hard-coded as* `"/signin-oidc"`

**`FILEUP_MSAL_AUTHORITY`** - Authority to which the web app delegates sign-in. In this case, the Azure Active Directory providing user identity. (TODO: More detail; links to docs)

**`FILEUP_MSAL_CLIENT_ID`** - Client ID assigned to the **App Registration** in Azure Active Directory. (TODO: More detail; links to docs)

**`FILEUP_MSAL_CLIENT_SECRET`** - Client Secret assigned to the App Registration (Azure Active Directory). (TODO: More detail; links to docs)

**`FILEUP_MSAL_SCOPE`** - *Currently left blank - not used*


#### Azure Storage Settings

**`FILEUP_STORAGE_ACCOUNT_NAME`** - Name of the Azure Storage Account. (TODO: More detail; links to docs)

**`FILEUP_STORAGE_CONTAINER`** - Name of the Blob container, in the Azure Storage Account, that receives uploaded files. Container name must be all lower case. If not set, the default is `fileup`. (TODO: More detail; links to docs)

**`FILEUP_STORAGE_TABLE`** - Name of the table, in the Azure Storage Account, that receives data about uploaded files. This is optional. If not set, files can still be uploaded to blob storage, but no data about the uploads is recorded.

**`FILEUP_STORAGE_ACCOUNT_KEY`** - Azure Storage Account **Key** to use in connection strings. Leave blank when using IAM roles, instead of connection strings, to access storage. (TODO: More detail; links to docs)

**`FILEUP_STORAGE_ENDPOINT_SUFFIX`** - Suffix used to construct URLs for storage targets. Used to build connection strings. (TODO: More detail; links to docs)


---

## Reference Links

### Flask

[Flask Documentation](https://flask.palletsprojects.com/en/latest/)

[Modular Applications with Blueprints](https://flask.palletsprojects.com/en/latest/blueprints/)

Use [flask.current_app](https://flask.palletsprojects.com/en/latest/api/#flask.current_app) to access `app.config` values in view modules using blueprints. Only available in the [Request Context](https://flask.palletsprojects.com/en/latest/reqcontext/#notes-on-proxies).


### Flask WTForms

[Flask-WTF](https://pypi.org/project/Flask-WTF/) - PyPI
[Flask-WTF](https://flask-wtf.readthedocs.io/en/1.0.x/) - Documentation
[WTForms](https://wtforms.readthedocs.io/en/3.0.x/) - Documentation
[Fields / Convenience Fields](https://wtforms.readthedocs.io/en/3.0.x/fields/#convenience-fields)
[Validators](https://wtforms.readthedocs.io/en/3.0.x/validators/)


### MSAL

[AzureAD/microsoft-authentication-library-for-python](https://github.com/AzureAD/microsoft-authentication-library-for-python) - GitHub
> Microsoft Authentication Library (MSAL) for Python makes it easy to authenticate to Azure Active Directory. These documented APIs are stable https://msal-python.readthedocs.io. If you have questions but do not have a github account, ask your questions on Stackoverflow with tag &quot;msal&quot; + &quot;python&quot;.

 Wiki: [AzureAD/microsoft-authentication-library-for-python](https://github.com/AzureAD/microsoft-authentication-library-for-python/wiki) - GitHub

[Microsoft identity platform overview](https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-overview) - Microsoft Entra -  Microsoft Learn


### Azure Storage

[Understanding the Table service data model](https://learn.microsoft.com/en-us/rest/api/storageservices/understanding-the-table-service-data-model) (REST API)


### Deploy to Azure

[Quickstart: Deploy a Python (Django or Flask) web app to Azure](https://learn.microsoft.com/en-us/azure/app-service/quickstart-python?tabs=flask%2Cmac-linux%2Cazure-cli%2Czip-deploy%2Cdeploy-instructions-azcli%2Cterminal-bash%2Cdeploy-instructions-zip-azcli#3---deploy-your-application-code-to-azure) -  Microsoft Learn

[az webapp deploy](https://learn.microsoft.com/en-us/cli/azure/webapp?view=azure-cli-latest#az-webapp-deploy) - Microsoft Learn


### Azure AD

[Add app roles and get them from a token](https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-add-app-roles-in-azure-ad-apps) - Microsoft Entra
