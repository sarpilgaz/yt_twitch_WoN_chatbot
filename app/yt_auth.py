from google_auth_oauthlib.flow import InstalledAppFlow

def Authorize(config):
    """function to run the oauth flow for the youtube chatbot.
    scopes required are defined in the config, but should not be touched.
    port to be used for the auth process is also taken from the 

    return value is the flow object as defined in the oauth lib.
    """
    
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
        port=config['port'],
        authorization_prompt_message="")

    return flow
