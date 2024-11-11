import requests

class Client:
    def __init__(self, phone_id: str, product_id: str, api_token: str):
        self._phone_id = phone_id
        self._product_id = product_id
        self._api_token = api_token
        self._headers  = { "Content-Type": "application/json", "x-maytapi-key": self._api_token }
        self._url_message = f"https://api.maytapi.com/api/{self._product_id}/{self._phone_id}/sendMessage"
        self._base_url = f"https://api.maytapi.com/api/{self._product_id}/{self._phone_id}/"

    def send_message(self, phone: str, text: str, reply_to: str = None):
        payload = {
            "to_number": str(phone),
            "type": "text",
            "message": text,
            "skip_filter": True
        }
        if reply_to is not None: payload.update({'reply_to': reply_to})
        return requests.post(self._url_message, json=payload, headers=self._headers).json()

    def send_message_buttons(self, phone: str, text: str, buttons: list):
        payload = {
            "to_number": str(phone),
            "type": "buttons",
            "message": text,
            "buttons": buttons,
            "skip_filter": True
        }
        return requests.post(self._url_message, json=payload, headers=self._headers).json()

    def send_file(self, phone: str, file_address: str, file_name=None):
        payload = {
            "to_number": str(phone),
            "type": "media",
            "message": file_address,
            "filename": file_name,
            "skip_filter": True
        }
        return requests.post(self._url_message, json=payload, headers=self._headers).json()

    def send_audio(self, phone: str, file_address: str, file_name=None):
        payload = {
            "to_number": str(phone),
            "type": "media",
            "message": file_address,
            "filename": file_name,
            "skip_filter": True
        }
        return requests.post(self._url_message, json=payload, headers=self._headers).json()

    def send_vcard(self, phone: str, name: str, vcard_phone: str):
        payload = {
            "to_number": phone,
            "type": "vcard",
            "message": {
                "displayName": name,
                "vcard": f"BEGIN:VCARD\nVERSION:3.0\nFN;CHARSET=UTF-8:{name}\nN;CHARSET=UTF-8:;{name};\nTEL;TYPE=CELL:{vcard_phone}\nREV:2020-01-23T11:09:14.782Z\nEND:VCARD"
            }
        }
        return requests.post(self._url_message, json=payload, headers=self._headers).json()

    def create_group(self, name: str, numbers: list):
        payload = {
            "name": name,
            "numbers": numbers
        }
        return requests.post(self._base_url + 'createGroup', json=payload, headers=self._headers).json()

    def add_to_group(self, group_id: str, phone: str):
        payload = {
            "conversation_id": group_id + "@g.us",
            "number": phone + '@c.us'
        }
        return requests.post(self._base_url + 'group/add', json=payload, headers=self._headers).json()

    def promote(self, group_id: str, phone: str):
        payload = {
            "conversation_id": group_id + "@g.us",
            "number": phone + '@c.us'
        }
        return requests.post(self._base_url + 'group/promote', json=payload, headers=self._headers).json()
        
    def get_group(self, group_id: str):
        return requests.get(self._base_url + f'getGroups/{group_id}@g.us', headers=self._headers).json()

    def get_groups(self):
        return requests.get(self._base_url + f'getGroups', headers=self._headers).json()

    def config(self, group_id: str, method: str):
        send = 'all' if method == 'open' else 'admins' 
        payload = {
            "conversation_id": group_id + "@g.us",
            "config": {
                "edit": "admins",
                "send": send,
                "disappear": False
            }
        }
        return requests.post(self._base_url + 'group/config', json=payload, headers=self._headers).json()

    def set_profil_group(self, group_id: str, url: str):
        payload = {
            "conversation_id": group_id + "@g.us",
            "image": url 
        }
        return requests.post(self._base_url + 'setProfileImage', json=payload, headers=self._headers).json()