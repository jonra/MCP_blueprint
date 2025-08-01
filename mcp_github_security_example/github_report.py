# github_report.py
import requests
import time
from datetime import datetime
from collections import Counter, defaultdict

GENERIC_SECRET_TYPES = [
    "password",
    "http_basic_authentication_header",
    "http_bearer_authentication_header",
    "mongodb_connection_string",
    "mysql_connection_string",
    "openssh_private_key",
    "pgp_private_key",
    "postgres_connection_string",
    "rsa_private_key"
]

_cache = {"timestamp": 0, "data": None}

def fetch_all_pages(url, headers, params=None):
    alerts = []
    page = 1
    while True:
        actual_params = params.copy() if params else {}
        actual_params['page'] = page
        response = requests.get(url, headers=headers, params=actual_params)
        if response.status_code == 403:
            print(f"⚠️ Skipping inaccessible URL: {url}")
            break
        response.raise_for_status()
        data = response.json()
        if not data:
            break
        alerts.extend(data)
        page += 1
    return alerts

def get_rate_limit(headers):
    url = "https://api.github.com/rate_limit"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    rate = data["rate"]
    return {
        "Limit": rate["limit"],
        "Remaining": rate["remaining"],
        "Resets At": datetime.fromtimestamp(rate["reset"]).strftime("%Y-%m-%d %H:%M:%S")
    }

def summarize_alerts_by_repo(alerts, type_label):
    repo_summary = defaultdict(lambda: defaultdict(lambda: {"total": 0, "by_severity": Counter()}))
    for alert in alerts:
        repo = alert.get("repository", {}).get("name", "unknown")
        severity = alert.get("rule", {}).get("severity", "unknown") if type_label == "code_scanning" else \
            alert.get("security_advisory", {}).get("severity", "unknown") if type_label == "dependabot" else "info"
        repo_summary[repo][type_label]["total"] += 1
        repo_summary[repo][type_label]["by_severity"][severity] += 1
    return repo_summary

def code_scanning_summary(headers, org):
    if not org or org == "-":
        return 0, Counter(), Counter(), {}
    url = f"https://api.github.com/orgs/{org}/code-scanning/alerts"
    alerts = fetch_all_pages(url, headers, {"state": "open", "per_page": 100})
    severity_counter = Counter()
    tool_counter = Counter()
    for alert in alerts:
        severity_counter[alert.get("rule", {}).get("severity", "unknown")] += 1
        tool_counter[alert.get("tool", {}).get("name", "unknown")] += 1
    repo_data = summarize_alerts_by_repo(alerts, "code_scanning")
    return len(alerts), severity_counter, tool_counter, repo_data

def secret_scanning_summary(headers, org):
    if not org or org == "-":
        return 0, 0, {}
    url = f"https://api.github.com/orgs/{org}/secret-scanning/alerts"
    all_alerts = fetch_all_pages(url, headers, {"state": "open", "per_page": 100})
    generic_params = {
        "state": "open",
        "per_page": 100,
        "secret_type": ",".join(GENERIC_SECRET_TYPES)
    }
    generic_alerts = fetch_all_pages(url, headers, generic_params)
    default_alerts = [a for a in all_alerts if a["secret_type"] not in GENERIC_SECRET_TYPES]
    repo_data = summarize_alerts_by_repo(all_alerts, "secret_scanning")
    return len(default_alerts), len(generic_alerts), repo_data

def dependabot_summary(headers, org):
    if not org or org == "-":
        return 0, Counter(), {}
    url = f"https://api.github.com/orgs/{org}/dependabot/alerts"
    alerts = fetch_all_pages(url, headers, {"state": "open", "per_page": 100})
    severity_counter = Counter()
    for alert in alerts:
        severity_counter[alert.get("security_advisory", {}).get("severity", "unknown")] += 1
    repo_data = summarize_alerts_by_repo(alerts, "dependabot")
    return len(alerts), severity_counter, repo_data

def load_summary(token: str, org: str = None, use_cache=True) -> dict:
    global _cache
    if use_cache and _cache["data"] and time.time() - _cache["timestamp"] < 600:
        return _cache["data"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    rate = get_rate_limit(headers)
    code_total, code_sev, code_tool, code_repos = code_scanning_summary(headers, org)
    secret_default, secret_generic, secret_repos = secret_scanning_summary(headers, org)
    dep_total, dep_sev, dep_repos = dependabot_summary(headers, org)

    per_repo = defaultdict(dict)
    for dataset in [code_repos, secret_repos, dep_repos]:
        for repo, types in dataset.items():
            for typ, data in types.items():
                if typ not in per_repo[repo]:
                    per_repo[repo][typ] = {"total": 0, "by_severity": {}}
                per_repo[repo][typ]["total"] += data["total"]
                for sev, count in data["by_severity"].items():
                    per_repo[repo][typ]["by_severity"].setdefault(sev, 0)
                    per_repo[repo][typ]["by_severity"][sev] += count

    for repo, data in per_repo.items():
        total_high = sum(
            typ_data["by_severity"].get("high", 0)
            for typ_data in data.values()
        )
        data["problematic"] = total_high >= 5

    result = {
        "rate_limit": rate,
        "totals": {
            "code_scanning": {
                "total": code_total,
                "by_severity": dict(code_sev),
                "tools": dict(code_tool)
            },
            "secret_scanning": {
                "default": secret_default,
                "generic": secret_generic
            },
            "dependabot": {
                "total": dep_total,
                "by_severity": dict(dep_sev)
            }
        },
        "per_repository": dict(per_repo)
    }

    _cache["data"] = result
    _cache["timestamp"] = time.time()
    return result
