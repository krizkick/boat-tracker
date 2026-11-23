import requests
from dotenv import load_dotenv
from boat import Boat
import os
from map import create_map
import time

load_dotenv()


def fetch_api_token():
    token_url = "https://id.barentswatch.no/connect/token"
    token_header = {"Content-Type": "application/x-www-form-urlencoded"}
    token_data = {"client_id":os.environ["CLIENT_ID"],
            "scope": "ais",
                "client_secret":os.environ["CLIENT_SECRET"],
                "grant_type":"client_credentials"}
    fetch_token_post = requests.post(token_url, headers=token_header, data=token_data)
    return fetch_token_post.json()["access_token"]

def fetch_api_json(token):
    post_url = "https://live.ais.barentswatch.no/v1/latest/combined"
    post_header =   {"Authorization" : f"Bearer {token}",
                    "Accept" : "application/json",
                    "Content-Type" : "application/json"}
    post_data = {"mmsi": [int(os.environ["MMSI"])]}

    fetch_ais_post = requests.post(
        post_url,
        headers=post_header,
        json=post_data)
    if fetch_ais_post.json() == []:
        return None
    else:
        return fetch_ais_post.json()[0]

def upload(name, data):
    r = requests.put(f"{os.environ["AZURE_CONNECTION_STRING"]}/{name}{os.environ["AZURE_SAS_TOKEN"]}",\
                    data=data, headers={"x-ms-blob-type": "BlockBlob"},\
                    timeout=30)

def main():
    boat = Boat()
    is_running = True

    while is_running:
        token = fetch_api_token()
        json = fetch_api_json(token)
        if json is not None:
            boat.update_info(json["msgtime"],
                        lat=json["latitude"],
                        long=json["longitude"],
                        speed=json["speedOverGround"],
                        direction=json["courseOverGround"])

            create_map(boat, SIZE_KM=25, WIDTH=400, HEIGHT=300)
            with open("version.txt", "w") as version:
                with open("kart.bin", "rb") as map_file:
                    data = map_file.read()
                    upload("kart.bin", data)
                    hash_data = str(hash(data))
                    upload("versjon.txt", hash_data)
                    version.write(hash_data)
            print("ferdig")
            time.sleep(300)
        else:
            time.sleep(3600)

main()