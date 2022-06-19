import requests
from requests.auth import HTTPBasicAuth


def get_auth(username: str, password: str, cms: str):
    """_summary_

    Args:
        username (str): username with access to external API
        password (str): password of the account

    Returns:
        dict: dictionary with the authorization token. Includes one key, 'Authorization'
    """
    auth_url = f"https://cms-v3.{cms}/api/v2/ext/auth"
    post = requests.post(auth_url, auth=HTTPBasicAuth(username, password))
    
    try:
            auth_data = post.json()
    except:
        raise Exception("Your email or password were entered incorrectly")
    
    return auth_data


def add_dialog(uuid: str, body: dict, auth_data: dict, cms: str):
    """_summary_

    Args:
        uuid (str): uuid of the agent
        body (dict): dictionary with the body of the request. Must contain msisdn.
        auth_data (dict): dict with the authorization token. Obtain from auth_data()

    Returns:
        str: code of the response
    """
    headers = {"Authorization":"Bearer " + auth_data["token"]}
    call_url = f"https://cms-v3.{cms}/api/v2/ext/dialog/dialogs-group-initial?agent_uuid={uuid}"
    uuid_ent = requests.post(call_url,json=body,headers=headers)
    print(str(body))
    print(uuid_ent)
    print(uuid_ent.text)
    print(uuid_ent.status_code == 500)
    
    if(uuid_ent.status_code == 500 or uuid_ent.status_code == "500"):
        new_body = [{str(key): str(value) for key, value in item.items()} for item in body]
        new_uuid_ent = requests.post(call_url,json=new_body,headers=headers)
        print("-"*20)
        print("Call failed, sending request with new body")
        print(str(new_body))
        print(new_uuid_ent.text)
        print("-"*20)
        return new_uuid_ent.status_code
    
    return uuid_ent.status_code


def refresh_token(username: str, password: str, auth_data: dict, cms: str):
    refresh_url = f"https://cms-v3.{cms}/api/v2/ext/auth/refresh"
    refresh_body = {"refresh_token":auth_data["refresh_token"]}
    refresh_post = requests.post(refresh_url,auth=HTTPBasicAuth(username,password),json=refresh_body)
    try:
        refresh_data = refresh_post.json()
    except:
        raise Exception("Your email or password were entered incorrectly")
    return refresh_data
