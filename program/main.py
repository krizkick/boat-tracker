import requests
from dotenv import load_dotenv
from boat import Boat
import os
from lag_kart import lag_kart
import time

load_dotenv()


def hent_api_token():
    tokenurl = "https://id.barentswatch.no/connect/token"
    tokenheader = {"Content-Type": "application/x-www-form-urlencoded"}
    tokendata = {"client_id":os.environ["CLIENT_ID"],
            "scope": "ais",
                "client_secret":os.environ["CLIENT_SECRET"],
                "grant_type":"client_credentials"}
    hent_token_post = requests.post(tokenurl, headers=tokenheader, data=tokendata)
    return hent_token_post.json()["access_token"]

def hent_api_json(token):
    posturl = "https://live.ais.barentswatch.no/v1/latest/combined"
    postheader =   {"Authorization" : f"Bearer {token}",
                    "Accept" : "application/json",
                    "Content-Type" : "application/json"}
    postdata = {"mmsi": [int(os.environ["MMSI"])]}

    hent_ais_post = requests.post(
        posturl,
        headers=postheader,
        json=postdata)
    if hent_ais_post.json() == []:
        return None
    else:
        return hent_ais_post.json()[0]

def last_opp(navn, data):
    r = requests.put(f"{os.environ["AZURE_CONNECTION_STRING"]}/{navn}{os.environ["AZURE_SAS_TOKEN"]}",\
                    data=data, headers={"x-ms-blob-type": "BlockBlob"},\
                    timeout=30)

def hovedprogram():
    kamilla = Boat()
    is_running = True

    while is_running:
        token = hent_api_token()
        json = hent_api_json(token)
        if json is not None:
            kamilla.oppdater_info(json["msgtime"],
                        lat=json["latitude"],
                        long=json["longitude"],
                        speed=json["speedOverGround"],
                        retning=json["courseOverGround"])

            lag_kart(kamilla, SIZE_KM=25, WIDTH=400, HEIGHT=300)
            with open("version.txt", "w") as versjon:
                with open("kart.bin", "rb") as kart:
                    data = kart.read()
                    last_opp("kart.bin", data)
                    hashdata = str(hash(data))
                    last_opp("versjon.txt", hashdata)
                    versjon.write(hashdata)
            print("ferdig")
            time.sleep(60)

            
        else:
            time.sleep(3600)

hovedprogram()