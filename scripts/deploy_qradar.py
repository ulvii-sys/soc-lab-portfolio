import requests
import os
import sys
import urllib3
import json
import time # Gözləmə müddəti üçün əlavə etdik

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_HOST = os.getenv('QRADAR_HOST')
QRADAR_TOKEN = os.getenv('QRADAR_TOKEN')

HEADERS = {
    'SEC': QRADAR_TOKEN,
    'Accept': 'application/json',
    'Version': '12.0'
}

BASE_URL = f"https://{QRADAR_HOST}/api/ariel/searches"

def run_threat_hunt(name, aql_query):
    payload = {"query_expression": aql_query}
    try:
        response = requests.post(BASE_URL, params=payload, headers=HEADERS, verify=False)
        if response.status_code == 201:
            search_id = response.json().get('search_id')
            print(f"✅ HUNT STARTED: {name} (Search ID: {search_id})")
            return search_id
        else:
            print(f"❌ HUNT FAILED: {name} - {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"🚨 Execution exception: {name} - {e}")
        return None

def get_hunt_results(search_id, name):
    """Axtarışın statusunu yoxlayır və bitəndə nəticələri gətirir."""
    status_url = f"{BASE_URL}/{search_id}"
    results_url = f"{BASE_URL}/{search_id}/results"

    print(f"⏳ {name} üçün nəticələr gözlənilir...")
    while True:
        status_response = requests.get(status_url, headers=HEADERS, verify=False)
        if status_response.status_code != 200:
            print("🚨 Status yoxlanışında xəta oldu.")
            return

        status = status_response.json().get('status')

        if status == 'COMPLETED':
            # Axtarış bitdi, logları çəkirik
            results_response = requests.get(results_url, headers=HEADERS, verify=False)
            events = results_response.json().get('events', [])
            print(f"🎯 NƏTİCƏ: '{name}' üzrə {len(events)} şübhəli log tapıldı!")
            
            # Əgər log tapılıbsa, ekrana və ya fayla yaza bilərsiniz
            if len(events) > 0:
                print(json.dumps(events[0], indent=2)) # Yalnız ilk logu nümunə kimi çap edirik
            break
            
        elif status in ['ERROR', 'CANCELED']:
            print(f"❌ Axtarış dayandırıldı və ya xəta verdi. Status: {status}")
            break
            
        else:
            # WAIT, EXECUTE, SORTING statuslarında olarsa 5 saniyə gözləyib təkrar yoxlayır
            time.sleep(5)

if __name__ == "__main__":
    rules_path = 'detections_qradar'
    if not os.path.exists(rules_path):
        print(f"Error: '{rules_path}' folder not found!")
        sys.exit(1)

    github_files = [f for f in os.listdir(rules_path) if f.endswith('.aql')]
    print(f"🚀 Starting Automated Threat Hunt in QRadar for {len(github_files)} rules...\n")
    
    for file_name in github_files:
        rule_name = file_name.replace('.aql', '')
        with open(os.path.join(rules_path, file_name), 'r', encoding='utf-8') as f:
            query = f.read().strip()
            
            # 1. Axtarışı başlat
            search_id = run_threat_hunt(rule_name, query)
            
            # 2. Nəticələri gözlə və al
            if search_id:
                get_hunt_results(search_id, rule_name)
                print("-" * 50)

    print("🔄 QRadar Threat Hunting dispatch complete.")
