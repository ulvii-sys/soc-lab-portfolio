import requests
import os
import sys
import urllib3
import json

# SSL xəbərdarlıqlarını söndürürük
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_HOST = os.getenv('QRADAR_HOST')
QRADAR_TOKEN = os.getenv('QRADAR_TOKEN')

HEADERS = {
    'SEC': QRADAR_TOKEN,
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Version': '12.0' # Versiyanı qeyd etmək bəzən metod xətalarını düzəldir
}
# URL-in sonuna slash əlavə etdik
BASE_URL = f"https://{QRADAR_HOST}/api/ariel/saved_searches"

def get_qradar_searches():
    try:
        # Bütün siyahını gətiririk
        response = requests.get(BASE_URL, headers=HEADERS, verify=False)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"🚨 Error fetching QRadar list: {e}")
        return []

def deploy_qradar_search(name, aql_query, existing_searches):
    # Adına görə ID-ni tapırıq
    search_id = next((s['id'] for s in existing_searches if s.get('name') == name), None)
    
    payload = {
        "name": name,
        "aql_query": aql_query,
        "is_shared": True,
        "is_dashboard": True
    }

    try:
        if search_id:
            # UPDATE: Mövcud rulu yeniləyirik (ID ilə URL-ə POST atılır)
            update_url = f"{BASE_URL}/{search_id}"
            response = requests.post(update_url, data=json.dumps(payload), headers=HEADERS, verify=False)
            if response.status_code in [200, 201]:
                print(f"✅ UPDATED: {name} (QRadar)")
            else:
                print(f"❌ UPDATE FAILED: {name} - {response.text}")
        else:
            # CREATE: Tamamilə yeni rul yaradırıq (Əsas URL-ə POST)
            # Bəzi QRadar versiyalarında POST /saved_searches üçün fərqli icazələr tələb olunur
            response = requests.post(BASE_URL, data=json.dumps(payload), headers=HEADERS, verify=False)
            if response.status_code == 201:
                print(f"✨ CREATED NEW: {name} (QRadar)")
            else:
                # Əgər hələ də xəta verərsə, detalı görək
                print(f"❌ CREATE FAILED: {name} - {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"🚨 Deployment exception: {name} - {e}")

if __name__ == "__main__":
    rules_path = 'detections_qradar'
    if not os.path.exists(rules_path):
        print(f"Error: '{rules_path}' folder not found!")
        sys.exit(1)

    existing_searches = get_qradar_searches()
    github_files = [f for f in os.listdir(rules_path) if f.endswith('.aql')]

    print(f"🚀 Starting QRadar Sync for {len(github_files)} rules...")
    for file_name in github_files:
        rule_name = file_name.replace('.aql', '')
        with open(os.path.join(rules_path, file_name), 'r') as f:
            query = f.read().strip()
            deploy_qradar_search(rule_name, query, existing_searches)

    print("🔄 QRadar synchronization complete.")
