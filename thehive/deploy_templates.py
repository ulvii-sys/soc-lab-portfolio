import requests
import json

API_KEY = "booyTtFEIIyq5DPt1VIWEMYbgHLYk2jb"
BASE_URL = "http://localhost:9000"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

with open("/opt/thehive/templates.json", "r") as f:
    templates = json.load(f)

for tpl in templates:
    resp = requests.post(
        f"{BASE_URL}/api/v1/caseTemplate",
        headers=HEADERS,
        json=tpl
    )
    if resp.status_code == 201:
        print(f"OK: {tpl['name']}")
    else:
        print(f"XETA: {tpl['name']} — {resp.status_code}: {resp.text}")
