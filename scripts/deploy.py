import requests
import os
import sys
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Splunk configuration from environment variables (GitHub Secrets)
SPLUNK_HOST = os.getenv('SPLUNK_HOST')
SPLUNK_PORT = os.getenv('SPLUNK_PORT', '8089')
SPLUNK_TOKEN = os.getenv('SPLUNK_TOKEN')

HEADERS = {'Authorization': f'Bearer {SPLUNK_TOKEN}'}
BASE_URL = f"https://{SPLUNK_HOST}:{SPLUNK_PORT}/services/saved/searches"

def get_splunk_rules():
    """Fetches a list of all existing Saved Searches from Splunk."""
    try:
        response = requests.get(f"{BASE_URL}?output_mode=json&count=-1", headers=HEADERS, verify=False)
        if response.status_code == 200:
            entries = response.json().get('entry', [])
            return [entry['name'] for entry in entries]
        return []
    except Exception as e:
        print(f"🚨 Error fetching Splunk rule list: {e}")
        return []

def deploy_rule(rule_name, spl_query):
    """Creates a new rule or updates an existing one with automatic Email Actions."""
    url = f"{BASE_URL}/{rule_name}"
    
    # Alert Configuration with Email Automation
    data = {
        'search': spl_query,
        'is_scheduled': 1,
        'cron_schedule': '*/5 * * * *',
        'alert_type': 'number of events',
        'alert_comparator': 'greater than',
        'alert_threshold': '0',
        'disabled': 0,
        'dispatch.earliest_time': '-24h',
        'dispatch.latest_time': 'now',
        
        # Email Notification Settings
        'actions': 'email',
        'action.email.to': 'itisabook100@gmail.com',
        'action.email.subject': f"SOC Alert: {rule_name} detected",
        'action.email.message.view': 'table',
        'action.email.sendresults': 1,
        'action.email.priority': '2'  # High priority
    }
    
    try:
        # Try to update the rule if it already exists
        response = requests.post(url, data=data, headers=HEADERS, verify=False, timeout=20)
        
        if response.status_code in [200, 201]:
            print(f"✅ SYNCED & UPDATED: {rule_name}")
        elif response.status_code == 404: 
            # Rule does not exist, create it from scratch
            create_data = data.copy()
            create_data['name'] = rule_name
            create_response = requests.post(BASE_URL, data=create_data, headers=HEADERS, verify=False)
            if create_response.status_code in [200, 201]:
                print(f"✨ CREATED NEW RULE: {rule_name}")
            else:
                print(f"❌ FAILED TO CREATE: {rule_name} - {create_response.text}")
    except Exception as e:
        print(f"🚨 Deployment error for {rule_name}: {e}")

if __name__ == "__main__":
    # Validate required directory
    rules_path = 'detections'
    if not os.path.exists(rules_path):
        print(f"Fatal Error: '{rules_path}' directory not found!")
        sys.exit(1)

    # 1. Gather all rule names from the GitHub repository
    github_rules = [f.replace('.spl', '') for f in os.listdir(rules_path) if f.endswith('.spl')]
    
    print("🚀 Starting Automated Detection Deployment...")
    print(f"Found {len(github_rules)} rules in GitHub. Syncing with Splunk...")

    # 2. Deploy or update each rule
    for rule_name in github_rules:
        file_path = os.path.join(rules_path, f"{rule_name}.spl")
        with open(file_path, 'r') as f:
            query = f.read()
            deploy_rule(rule_name, query)

    print("🔄 All rules have been successfully synchronized with Email Actions enabled.")
