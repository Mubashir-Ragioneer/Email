# function_app.py  (Functions v2 model)
import azure.functions as func
from app.main import app as fastapi_app   # your existing FastAPI instance

# Mount FastAPI as an Azure Function (HTTP trigger, anonymous)
app = func.AsgiFunctionApp(app=fastapi_app, http_auth_level=func.AuthLevel.ANONYMOUS)
