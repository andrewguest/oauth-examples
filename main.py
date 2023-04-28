import os

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


load_dotenv()
app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_access_token(request_token: str) -> str:
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")

    url = "https://github.com/login/oauth/access_token"
    query_params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": request_token,
    }
    headers = {"Accept": "application/json"}

    response = requests.post(url, headers=headers, params=query_params)
    data = response.json()

    access_token = data["access_token"]

    return access_token


def get_user_data(access_token: str) -> dict:
    url = "https://api.github.com/user"
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(url, headers=headers)
    user_data = response.json()

    return user_data


# STEP 1 - Send a GET request to Github's OAuth authorization endpoint.
# The user signs into Github with their Github credentials and is then prompted
#   to give your application access their information or to act on their behalf.
# This returns a one-time authorization code to your CALLBACK URL.
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "client_id": os.getenv("CLIENT_ID")}
    )


# STEP 2 - Receive the one-time AUTHORIZATION code from Github as a query parameter.
# STEP 3 - Use the AUTHORIZATION code to make a POST request to Github's OAuth
#   access_token URL and and receive an ACCESS token in response.
# This access token can be used as an API key to interact with Github's API as if
#   you were the user.
# STEP 4 - Use the ACCESS token to make an API request to Github's `/user` route
#   to get information related to the user.
@app.get("/callbacks/github")
async def github_callback(request: Request, code: str):
    access_token = get_access_token(code)
    user_data = get_user_data(access_token)

    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "userData": user_data}
    )
