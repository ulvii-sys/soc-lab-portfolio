# 🛡️ SOC Lab Portfolio

A production-grade Security Operations Center (SOC) lab environment built over multiple weeks, covering reactive and proactive detection engineering, threat hunting, SOAR automation, and case management.

---

## 🏗️ Architecture

```
Splunk SIEM ──────────────────────────────────────┐
QRadar SIEM ──────────────────────────────────────┤
Wallarm WAF ──────────────────────────────────────┼──► Shuffle SOAR ──► TheHive (Case Management)
Active Directory ─────────────────────────────────┤         │                    │
AbuseIPDB / VirusTotal ───────────────────────────┘         │                    ▼
                                                             │              Cortex (Enrichment)
                                                             ▼
                                                       Telegram Bot
                                                       FortiGate Firewall
```

---

## 🗂️ Repository Structure

| Folder | Description |
|---|---|
| `detections/` | 12 Splunk SPL detection rules (NB-SPL-001–012) + 6 Sigma rules |
| `detections_qradar/` | 12 QRadar AQL detection rules |
| `scripts/` | Python deployment scripts for Splunk and QRadar |
| `thehive/` | TheHive 5 Docker setup + 5 case templates + deploy script |
| `network/fortigate/` | FortiGate firewall security policy and log forwarding config |
| `SOC Detection Coverage — MITRE ATT&CK.json` | MITRE ATT&CK Navigator coverage matrix |
| `.github/workflows/` | CI/CD pipeline for automatic detection rule deployment |

---

## 🔧 Tools & Technologies

| Category | Tool |
|---|---|
| SIEM | Splunk, IBM QRadar |
| SOAR | Shuffle |
| Case Management | TheHive 5 |
| Enrichment | Cortex, AbuseIPDB, VirusTotal |
| WAF | Wallarm, CrowdSec |
| Firewall | FortiGate |
| Threat Intel | OpenCTI |
| Endpoint | Bitdefender XDR |
| Deception | CanaryToken, Honey User (svc_sql_admin) |
| Notification | Telegram Bot |
| CI/CD | GitHub Actions |

---

## 📋 MITRE ATT&CK Coverage

| Technique | ID | Detection |
|---|---|---|
| Brute Force | T1110 | Splunk NB-SPL-012, QRadar |
| PowerShell | T1059.001 | Sigma nb-sigma-001/002/003 |
| Clear Logs | T1070.002 | Sigma nb-sigma-005 |
| Web Shell | T1505.003 | Sigma nb-sigma-008 |
| Exfiltration | T1041 | Sigma nb-sigma-009/010 |
| Valid Accounts | T1078 | QRadar Honey User rule |
| SQL Injection | T1190 | Splunk NB-SPL-001 |
| XSS | T1189 | Splunk NB-SPL-007 |
| Path Traversal | T1083 | Splunk NB-SPL-006 |
| Privilege Escalation | T1068 | QRadar |

---

## 📁 TheHive Case Templates

5 production-ready case templates deployed via API (`/api/v1/caseTemplate`):

| Template | Severity | MITRE |
|---|---|---|
| Brute Force Attack | HIGH | T1110 |
| Phishing Email Incident | HIGH | T1566 |
| Malicious IP Activity | HIGH | T1071 |
| Suspicious Login / Account Compromise | HIGH | T1078 |
| False Positive Handling | LOW | — |

Each template follows the SOC workflow: **Triage → Investigation → Decision → Response → Closure**

---

## 🔄 SOAR Playbooks (Shuffle)

| Playbook | Trigger | Actions |
|---|---|---|
| PB-001: XSS Detection | Splunk NB-SPL-007 | AbuseIPDB check → TheHive alert |
| PB-002: Brute Force Response | Splunk NB-SPL-012 | AbuseIPDB → VirusTotal → FortiGate block → TheHive case |
| PB-003: AD Privilege Escalation | QRadar offense | WinRM disable user → Telegram → TheHive alert |

---

## 🚀 Quick Start

### Deploy Splunk Detection Rules
```bash
cd scripts/
python3 deploy.py
```

### Deploy QRadar Rules
```bash
cd scripts/
python3 deploy_qradar.py
```

### Deploy TheHive Templates
```bash
cd thehive/
python3 deploy_templates.py
```

### Start TheHive (Docker)
```bash
cd thehive/
docker-compose up -d
```

---

## 👥 Team

5-person SOC lab team — weekly task-based learning environment.

---

## 📌 Notes

- Shuffle playbooks are configured directly in the Shuffle UI
- All credentials are managed via environment variables in production
- TheHive is accessible at `http://SERVER_IP:9000`
