import json
import requests
from tqdm import tqdm

Token_VKAPI = ""
OAuth = "y0__xDaifaeAhjblgMgjI3C9RL7UCitZbUYOlmsCOYjVLCYPDnQUA"


class VKPHOTO:
    URL = 'https://api.vk.com/method/photos.get'

    def __init__(self, user_id, token):
        self.user_id = user_id
        self.token = token

    def necessary_params(self):
        return {
            "album_id": "profile",
            "access_token": self.token,
            "v": "5.199",
            "extended": "1",
            "photo_sizes": "1",
        }

    def get_photos(self):
        params = self.necessary_params()
        params.update({"owner_id": self.user_id})
        response = requests.get(self.URL, params=params)
        return response.json()["response"]["items"]

    def download_photo(self):
        photos = self.get_photos()
        for i in tqdm(range(len(photos)), desc="Downloading photos", unit="photo"):
            resp = requests.get(photos[i]["sizes"][4]["url"])
            with open(f"{photos[i]['likes']['count']}.jpg", "wb") as f:
                f.write(resp.content)

    def save_in_json(self):
        info = []
        for i in tqdm(range(len(self.get_photos())), desc="Saving photo info", unit="photo"):
            photo_info = {"file_name": f"{self.get_photos()[i]['likes']['count']}.jpg",
                          "size": self.get_photos()[i]["sizes"][4]["type"]}
            info.append(photo_info)
        with open("info.json", "w") as g:
            json.dump(info, g, ensure_ascii=False, indent=2)


class SAVEONYANDEX:
    yd_URL = "https://cloud-api.yandex.net"

    def __init__(self, token):
        self.token = token

    def headers(self):
        return {
            "Authorization": self.token
        }

    def get_params(self):
        return {
            "path": "reserved"
        }

    def build_folder(self):
        URL_folder = f"{self.yd_URL}/v1/disk/resources"
        params = self.get_params()
        headers = self.headers()
        response = requests.put(URL_folder, params=params, headers=headers)
        return response

    def get_FILE_URL(self, filename):
        File_URL = f"{self.yd_URL}/v1/disk/resources/upload"
        params = {"path": f"reserved/{filename}"}
        headers = self.headers()
        response = requests.get(File_URL, params=params, headers=headers)
        return response.json()["href"]

    def upload_to_yandex(self, filename):
        file_url = self.get_FILE_URL(filename)
        with open(filename, 'rb') as f:
            requests.put(file_url, files={"file": f})


vk = VKPHOTO(350760736, Token_VKAPI)
vk.download_photo()
vk.save_in_json()

a = SAVEONYANDEX(OAuth)
a.build_folder()

for i in tqdm(range(len(vk.get_photos())), desc="Uploading photos to Yandex", unit="photo"):
    filename = f"{vk.get_photos()[i]['likes']['count']}.jpg"
    a.upload_to_yandex(filename)
