### 2023-01-20

Added [azure-data-tables](https://pypi.org/project/azure-data-tables/) to project requirements.

[Azure Tables client library for Python](https://learn.microsoft.com/en-us/python/api/overview/azure/data-tables-readme?view=azure-python)

`azure.data.tables.TableServiceClient`: [create-table-if-not-exists](https://learn.microsoft.com/en-us/python/api/azure-data-tables/azure.data.tables.tableserviceclient?view=azure-python#azure-data-tables-tableserviceclient-create-table-if-not-exists)

---

### 2023-02-07

What is the correct way to handle providing **https** responses when Flask is behind a proxy and receiving **http** requests as happens in an Azure App Service container for Python web apps? It looks like the **X-Forwarded-For Proxy Fix** is the way.

[Tell Flask it is Behind a Proxy](https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/) - Flask Documentation

[X-Forwarded-For Proxy Fix](https://werkzeug.palletsprojects.com/en/0.16.x/middleware/proxy_fix/) - Werkzeug Documentation

[Standalone WSGI Containers - Proxy Setups](https://flask.palletsprojects.com/en/2.0.x/deploying/wsgi-standalone/#proxy-setups) - Flask Documentation

[Configure Linux Python apps](https://learn.microsoft.com/en-us/azure/app-service/configure-language-python#detect-https-session) - Azure App Service - Microsoft Learn

