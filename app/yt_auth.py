from google_auth_oauthlib.flow import InstalledAppFlow

def Authorize(config):
    
    flow = InstalledAppFlow.from_client_config({
        "installed": {
            "client_id": config["yt_client_id"],
            "client_secret": config["yt_client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        }
    }, scopes=config["scopes"])

    flow.run_local_server(
        host='localhost',
        port=5500,
        authorization_prompt_message="")

    return flow
