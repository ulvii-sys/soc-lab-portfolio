import requests
import os

# Splunk məlumatlarını GitHub Secrets-dən götürürük
SPLUNK_HOST = os.getenv('SPLUNK_HOST')
SPLUNK_PORT = os.getenv('SPLUNK_PORT', '8089')
SPLUNK_TOKEN = os.getenv('SPLUNK_TOKEN')

def deploy_rule(rule_name, spl_query):
    url = f"https://{SPLUNK_HOST}:{SPLUNK_PORT}/servicesNS/admin/search/saved/searches"
    
    data = {
        'name': rule_name,
        'search': spl_query,
        'alert_type': 'number of events',
        'alert.comparator': 'greater than',
        'alert.threshold_value': '0',
        'cron_schedule': '*/5 * * * *', # Hər 5 dəqiqədən bir işləsin
        'is_scheduled': 1,
        'disabled': 0
    }
    
    headers = {'Authorization': f'Bearer {SPLUNK_TOKEN}'}
    response = requests.post(url, data=data, headers=headers, verify=False)
    
    if response.status_code == 201:
        print(f"SUCCESS: {rule_name} deploy olundu.")
    else:
        print(f"ERROR: {rule_name} alınmadı: {response.text}")

# Detections qovluğundakı faylları oxu
rules_path = 'detections'
for file in os.listdir(rules_path):
    if file.endswith('.spl'):
        with open(os.path.join(rules_path, file), 'r') as f:
            query = f.read()
            name = file.replace('.spl', '')
            deploy_rule(name, query)