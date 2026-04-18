import requests
import os
import sys
import urllib3
import json

# SSL xəbərdarlıqlarını gizlədirik
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

QRADAR_HOST = os.getenv('QRADAR_HOST')
QRADAR_TOKEN = os.getenv('QRADAR_TOKEN')

HEADERS = {
    'SEC': QRADAR_TOKEN,
    'Accept': 'application/json',
    'Version': '12.0'
}

# Diqqət: Endpoint artıq 'saved_searches' deyil, birbaşa 'searches' endpointidir (AQL işlətmək üçün)
BASE_URL = f"https://{QRADAR_HOST}/api/ariel/searches"

def run_threat_hunt(name, aql_query):
    # AQL sorğusunu URL parametri kimi QRadar-a göndəririk
    payload = {
        "query_expression": aql_query
    }
    
    try:
        # POST sorğusu ilə QRadar-da anında axtarış başladırıq
        response = requests.post(BASE_URL, params=payload, headers=HEADERS, verify=False)
        
        if response.status_code == 201:
            search_id = response.json().get('search_id')
            print(f"✅ THREAT HUNT STARTED: {name} (Search ID: {search_id})")
        else:
            print(f"❌ HUNT FAILED: {name} - {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"🚨 Execution exception: {name} - {e}")

if __name__ == "__main__":
    rules_path = 'detections_qradar'
    if not os.path.exists(rules_path):
        print(f"Error: '{rules_path}' folder not found!")
        sys.exit(1)

    github_files = [f for f in os.listdir(rules_path) if f.endswith('.aql')]

    print(f"🚀 Starting Automated Threat Hunt in QRadar for {len(github_files)} rules...")
    
    for file_name in github_files:
        rule_name = file_name.replace('.aql', '')
        with open(os.path.join(rules_path, file_name), 'r') as f:
            # Fayldakı AQL kodunu oxuyub boşluqları təmizləyirik
            query = f.read().strip()
            run_threat_hunt(rule_name, query)

    print("🔄 QRadar Threat Hunting dispatch complete.")
