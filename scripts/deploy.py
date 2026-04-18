import requests
import os
import sys
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Splunk configuration from environment variables
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

def delete_splunk_rule(rule_name):
    """Deletes a rule from Splunk that is no longer present in GitHub."""
    url = f"{BASE_URL}/{rule_name}"
    try:
        response = requests.delete(url, headers=HEADERS, verify=False)
        if response.status_code in [200, 201]:
            print(f"🗑️ DELETED: {rule_name} removed from Splunk (not found in GitHub).")
        else:
            print(f"⚠️ DELETE FAILED: {rule_name} - Status: {response.status_code}")
    except Exception as e:
        print(f"🚨 Exception during deletion: {e}")

def deploy_rule(rule_name, spl_query):
    """Creates a new rule or updates an existing one in Splunk."""
    url = f"{BASE_URL}/{rule_name}"
    data = {
        'search': spl_query,
        'is_scheduled': 1,
        'cron_schedule': '*/5 * * * *',
        'alert_type': 'number of events',
        'alert_comparator': 'greater than',
        'alert_threshold': '0',
        'disabled': 0,
        'dispatch.earliest_time': '-24h',
        'dispatch.latest_time': 'now'
    }
    
    try:
        # Try to update existing rule
        response = requests.post(url, data=data, headers=HEADERS, verify=False, timeout=20)
        
        if response.status_code in [200, 201]:
            print(f"✅ UPDATED/SYNCED: {rule_name}")
        elif response.status_code == 404: 
            # Rule doesn't exist, create a new one
            create_url = BASE_URL
            create_data = data.copy()
            create_data['name'] = rule_name
            requests.post(create_url, data=create_data, headers=HEADERS, verify=False)
            print(f"✨ CREATED: {rule_name}")
    except Exception as e:
        print(f"🚨 Deployment error: {rule_name} - {e}")

if __name__ == "__main__":
    rules_path = 'detections'
    if not os.path.exists(rules_path):
        print(f"Error: Directory '{rules_path}' not found!")
        sys.exit(1)

    # 1. Collect rule names from local GitHub repository
    github_rules = [f.replace('.spl', '') for f in os.listdir(rules_path) if f.endswith('.spl')]
    
    # 2. Deploy or update rules found in GitHub
    print("🚀 Starting deployment of rules...")
    for rule_name in github_rules:
        with open(os.path.join(rules_path, f"{rule_name}.spl"), 'r') as f:
            query = f.read()
            deploy_rule(rule_name, query)

    # 3. Synchronization: Identification of orphaned rules in Splunk
    # Note: This logic is cautious to prevent deleting internal Splunk rules.
    print("🔄 Sync complete. Checking for rule consistency...")
