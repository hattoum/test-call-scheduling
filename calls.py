import requests
from requests.auth import HTTPBasicAuth


def get_auth(username: str, password: str):
    """_summary_

    Args:
        username (str): username with access to external API
        password (str): password of the account

    Returns:
        dict: dictionary with the authorization token. Includes one key, 'Authorization'
    """
    auth_url = "https://cms-v3.voctiv.com/api/v2/ext/auth"
    post = requests.post(auth_url, auth=HTTPBasicAuth(username, password))
    
    try:
            auth_data = post.json()
    except:
        raise Exception("Your email or password were entered incorrectly")
    
    return auth_data


def add_dialog(uuid: str, body: dict, auth_data: dict):
    """_summary_

    Args:
        uuid (str): uuid of the agent
        body (dict): dictionary with the body of the request. Must contain msisdn.
        auth_data (dict): dict with the authorization token. Obtain from auth_data()

    Returns:
        str: code of the response
    """
    headers = {"Authorization":"Bearer " + auth_data["token"]}
    call_url = f"https://cms-v3.voctiv.com/api/v2/ext/dialog/dialogs-group-initial?agent_uuid={uuid}"
    uuid_ent = requests.post(call_url,json=body,headers=headers)
    return uuid_ent.status_code


def refresh_token(username: str, password: str, auth_data: dict):
    refresh_url = "https://cms-v3.voctiv.com/api/v2/ext/auth/refresh"
    refresh_body = {"refresh_token":auth_data["refresh_token"]}
    # print(f"Refresh body: {refresh_body}")
    refresh_post = requests.post(refresh_url,auth=HTTPBasicAuth(username,password),json=refresh_body)
    try:
        refresh_data = refresh_post.json()
    except:
        raise Exception("Your email or password were entered incorrectly")
    return refresh_data
