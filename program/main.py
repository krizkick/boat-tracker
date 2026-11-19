import requests
from dotenv import load_dotenv
from boat import Boat
import os
from lag_kart import lag_kart

load_dotenv()



tokenurl = "https://id.barentswatch.no/connect/token"
tokenheader = {"Content-Type": "application/x-www-form-urlencoded"}
tokendata = {"client_id":os.environ["CLIENT_ID"],
           "scope": "ais",
            "client_secret":os.environ["CLIENT_SECRET"],
            "grant_type":"client_credentials"}
hent_token_post = requests.post(tokenurl, headers=tokenheader, data=tokendata)

token = hent_token_post.json()["access_token"]

posturl = "https://live.ais.barentswatch.no/v1/latest/combined"
postheader =   {"Authorization" : f"Bearer {token}",
                "Accept" : "application/json",
                "Content-Type" : "application/json"}
postdata = {"mmsi": [257276800]} #[int(os.environ["MMSI"])]}

hent_ais_post = requests.post(
    posturl,
    headers=postheader,
    json=postdata
)
boat_json = hent_ais_post.json()[0]


print(hent_ais_post.status_code)
print(hent_ais_post.text)

kamilla = Boat()

if boat_json != []:
    kamilla.oppdater_info(boat_json["msgtime"],
                        lat=boat_json["latitude"],
                        long=boat_json["longitude"],
                        speed=boat_json["speedOverGround"],
                        retning=boat_json["courseOverGround"])

    lag_kart(kamilla, SIZE_KM=25, WIDTH=400, HEIGHT=300)

    with open("version.txt", "w") as versjon:
        with open("kart.bin", "rb") as kart:
            data = kart.read()
            hashnr = hash(data)
        versjon.write(hashnr)