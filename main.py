import requests
from dotenv import load_dotenv
import os

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
postdata = {"mmsi": [int(os.environ["MMSI"])]}


hent_ais_post = requests.post(
    posturl,
    headers=postheader,
    json=postdata
)

print(hent_ais_post.status_code)
print(hent_ais_post.text)



#https://developer.barentswatch.no/docs/appreg/

