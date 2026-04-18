import requests
import os
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SPLUNK_HOST = os.getenv('SPLUNK_HOST')
SPLUNK_PORT = os.getenv('SPLUNK_PORT', '8089')
SPLUNK_TOKEN = os.getenv('SPLUNK_TOKEN')

def deploy_rule(rule_name, spl_query):
    # DƏYİŞİKLİK BURADADIR: "admin" sözünü çıxardıq, universal etdik
    url = f"https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/saved/searches"
    
    data = {
        'name': rule_name,
        'search': spl_query,
        'alert_type': 'number of events',
        'alert.comparator': 'greater than',
        'alert.threshold_value': '0',
        'cron_schedule': '*/5 * * * *',
        'is_scheduled': 1,
        'disabled': 0,
        'dispatch.earliest_time': '-24h',
        'dispatch.latest_time': 'now'
    }
    
    headers = {'Authorization': f'Bearer {SPLUNK_TOKEN}'}
    
    try:
        response = requests.post(url, data=data, headers=headers, verify=False, timeout=20)
        
        if response.status_code in [201, 200]:
            print(f"✅ SUCCESS: {rule_name} deploy olundu.")
        elif response.status_code == 409:
            print(f"⚠️ DİQQƏT: {rule_name} artıq mövcuddur.")
        else:
            print(f"❌ ERROR: {rule_name} alınmadı: {response.status_code} - {response.text}")
            sys.exit(1) # GitHub-a xətanı bildir
    except Exception as e:
        print(f"🚨 KRİTİK XƏTA: {e}")
        sys.exit(1)

rules_path = 'detections'
for file in os.listdir(rules_path):
    if file.endswith('.spl'):
        with open(os.path.join(rules_path, file), 'r') as f:
            query = f.read()
            name = file.replace('.spl', '')
            deploy_rule(name, query)