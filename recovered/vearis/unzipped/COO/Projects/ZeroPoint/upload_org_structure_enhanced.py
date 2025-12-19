
import os
import requests
from dotenv import load_dotenv
from markdown import markdown

# Load .env vars
load_dotenv()

EMAIL = os.getenv("ATLASSIAN_EMAIL")
API_KEY = os.getenv("CONFLUENCE_ADMIN_API_KEY")
BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
SPACE_KEY = "ADAPT"
PARENT_PAGE_URL = os.getenv("CONFLUENCE_ADAPT_MASTER_MAIN_PAGE")
MARKDOWN_FILE = "ADAPT_OrgStructure.md"

# Configurable fields
PAGE_TITLE = "ADAPT Executive Organizational Structure"
LABELS = ["adapt", "org-structure", "nova", "ops"]
WATCHERS = ["chase@levelup2x.com"]

def get_page_id_from_url(url):
    if "/wiki/" not in url:
        raise ValueError("Invalid Confluence URL.")
    return url.split("/")[-1].replace("x/", "")

PARENT_PAGE_ID = get_page_id_from_url(PARENT_PAGE_URL)

def get_auth():
    return (EMAIL, API_KEY)

def markdown_to_confluence_html(md_content):
    html = markdown(md_content, extensions=["fenced_code", "tables", "toc"])
    html = html.replace("<h1>", "<h1><ac:structured-macro ac:name='info'><ac:parameter ac:name='title'>ADAPT Org Structure</ac:parameter><ac:rich-text-body>")
    html = html.replace("</h1>", "</ac:rich-text-body></ac:structured-macro></h1>")
    html = html.replace("<table>", "<ac:structured-macro ac:name='table-plus'><ac:rich-text-body><table>")
    html = html.replace("</table>", "</table></ac:rich-text-body></ac:structured-macro>")
    return html

def get_existing_page(title):
    url = f"{BASE_URL}/rest/api/content"
    params = {
        "title": title,
        "spaceKey": SPACE_KEY,
        "expand": "version"
    }
    response = requests.get(url, auth=get_auth(), params=params)
    if response.status_code == 200 and response.json()["size"] > 0:
        return response.json()["results"][0]
    return None

def add_labels(page_id, labels):
    url = f"{BASE_URL}/rest/api/content/{page_id}/label"
    label_data = [{"prefix": "global", "name": label} for label in labels]
    r = requests.post(url, auth=get_auth(), json=label_data)
    print(f"🏷️  Labels added: {r.status_code}")

def add_watchers(page_id, watchers):
    for user in watchers:
        user_key = user.split("@")[0]
        url = f"{BASE_URL}/rest/api/user/watch/content"
        params = {
            "contentId": page_id,
            "username": user_key
        }
        r = requests.post(url, auth=get_auth(), params=params)
        print(f"👁️  Watcher added for {user}: {r.status_code}")

def create_or_update_page(title, content):
    existing_page = get_existing_page(title)
    headers = {"Content-Type": "application/json"}
    html_content = markdown_to_confluence_html(content)

    if existing_page:
        page_id = existing_page["id"]
        current_version = existing_page["version"]["number"]
        url = f"{BASE_URL}/rest/api/content/{page_id}"
        payload = {
            "id": page_id,
            "type": "page",
            "title": title,
            "space": {"key": SPACE_KEY},
            "body": {
                "storage": {
                    "value": html_content,
                    "representation": "storage"
                }
            },
            "version": {"number": current_version + 1}
        }
        r = requests.put(url, json=payload, auth=get_auth(), headers=headers)
        print(f"✅ Page updated: {r.status_code}")
        add_labels(page_id, LABELS)
        add_watchers(page_id, WATCHERS)
    else:
        url = f"{BASE_URL}/rest/api/content/"
        payload = {
            "type": "page",
            "title": title,
            "ancestors": [{"id": PARENT_PAGE_ID}],
            "space": {"key": SPACE_KEY},
            "body": {
                "storage": {
                    "value": html_content,
                    "representation": "storage"
                }
            }
        }
        r = requests.post(url, json=payload, auth=get_auth(), headers=headers)
        print(f"✅ Page created: {r.status_code}")
        if r.ok:
            new_page_id = r.json()["id"]
            add_labels(new_page_id, LABELS)
            add_watchers(new_page_id, WATCHERS)

if __name__ == "__main__":
    with open(MARKDOWN_FILE, "r") as f:
        md = f.read()
    create_or_update_page(PAGE_TITLE, md)
