# File Upload App using Flask and Azure

> This is a work-in-progress demo. If it works out, a LICENSE will be added when it is done. Otherwise this repository will probably go away.

<sub>Created: 2023-01-19</sub>

Started with a copy of the files in the [flask-file-up](https://github.com/wmelvin/flask-file-up) project as of commit [4f4ee83](https://github.com/wmelvin/flask-file-up/tree/4f4ee83b58f248874396ef977acde63cb8af695e).

Rather than clone that project, and bring along all of its history, a ZIP download was used to get the files. Code related to the database model (SQLAlchemy-derived classes), and for managing user identities within the app, was removed. This project will use only Azure Active Directory (via MSAL) for user identity management and Azure Storage for receiving uploaded files.

A new Git repository was created after pruning the code and successfully running the main functions of the app locally (the Flask app ran in the local development server, but was connected to live Azure resources).


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
