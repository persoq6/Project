import json
import requests
from tqdm import tqdm
from pprint import pprint

Token_VKAPI = ""
OAuth = ""


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

    def get_max_size_of_photo(self):
        photos = self.get_photos()
        links = []
        for i in range(len(photos)):
            links.append(max(photos[i]["sizes"], key=lambda x: x["height"] * x["width"]))
        return links

    def save_in_json(self):
        info = []
        for i in tqdm(range(len(self.get_photos())), desc="Saving photo info", unit="photo"):
            photo_info = {"file_name": f"{self.get_photos()[i]['likes']['count']}.jpg",
                          "size": self.get_max_size_of_photo()[i]["type"]}
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

    def build_folder(self):
        URL_folder = f"{self.yd_URL}/v1/disk/resources"
        params = {"path": "reserved"}
        headers = self.headers()
        response = requests.put(URL_folder, params=params, headers=headers)
        return response

    def upload_to_yandex(self, url, filename):
        file_url = f"{self.yd_URL}/v1/disk/resources/upload"
        params = {"url": url,
                  "path": f"reserved/{filename}"}
        response = requests.post(file_url, params=params, headers=self.headers())
        return response


vk = VKPHOTO(350760736, Token_VKAPI)

yad = SAVEONYANDEX(OAuth)
photos = vk.get_photos()
vk.save_in_json()
a = SAVEONYANDEX(OAuth)
a.build_folder()

likes_count = {}
for i in tqdm(range(len(photos)), desc="uploading_photos", unit='photos'):
    name = f"{photos[i]["likes"]["count"]}"
    if name in likes_count:
        likes_count[name] += 1
        name += f"_{photos[i]["date"]}"
        a.upload_to_yandex(vk.get_max_size_of_photo()[i]["url"], name)
    else:
        likes_count[name] = 1
        a.upload_to_yandex(vk.get_max_size_of_photo()[i]["url"], name)
