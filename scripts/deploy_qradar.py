import requests
import os
import sys
import urllib3
import json

# SSL xəbərdarlıqlarını söndürürük
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# QRadar tənzimləmələri (GitHub Secrets-dən gəlir)
QRADAR_HOST = os.getenv('QRADAR_HOST')
QRADAR_TOKEN = os.getenv('QRADAR_TOKEN')

HEADERS = {
    'SEC': QRADAR_TOKEN,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
BASE_URL = f"https://{QRADAR_HOST}/api/ariel/saved_searches"

def get_qradar_searches():
    """QRadar-dakı mövcud saved search-lərin siyahısını alır."""
    try:
        response = requests.get(BASE_URL, headers=HEADERS, verify=False)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"🚨 Error fetching QRadar list: {e}")
        return []

def deploy_qradar_search(name, aql_query, existing_searches):
    """Qaydanı yaradır və ya yeniləyir."""
    # Mövcud axtarışlar arasında ad uyğunluğunu yoxlayırıq
    search_id = next((s['id'] for s in existing_searches if s['name'] == name), None)
    
    payload = {
        "name": name,
        "aql_query": aql_query,
        "is_shared": True,
        "is_dashboard": True
    }

    try:
        if search_id:
            # YENİLƏMƏ (POST to ID)
            url = f"{BASE_URL}/{search_id}"
            response = requests.post(url, data=json.dumps(payload), headers=HEADERS, verify=False)
            if response.status_code in [200, 201]:
                print(f"✅ UPDATED: {name} (QRadar)")
        else:
            # YENİ YARATMA (POST)
            response = requests.post(BASE_URL, data=json.dumps(payload), headers=HEADERS, verify=False)
            if response.status_code == 201:
                print(f"✨ CREATED: {name} (QRadar)")
            else:
                print(f"❌ FAILED: {name} - {response.text}")
    except Exception as e:
        print(f"🚨 Deployment error: {name} - {e}")

if __name__ == "__main__":
    rules_path = 'detections_qradar'
    if not os.path.exists(rules_path):
        print(f"Error: '{rules_path}' folder not found!")
        sys.exit(1)

    # 1. QRadar-dakı cari vəziyyəti oxu
    existing_searches = get_qradar_searches()
    
    # 2. GitHub-dakı faylları oxu
    github_files = [f for f in os.listdir(rules_path) if f.endswith('.aql')]

    print(f"🚀 Starting QRadar Sync for {len(github_files)} rules...")
    for file_name in github_files:
        rule_name = file_name.replace('.aql', '')
        with open(os.path.join(rules_path, file_name), 'r') as f:
            query = f.read()
            deploy_qradar_search(rule_name, query, existing_searches)

    print("🔄 QRadar synchronization complete.")
