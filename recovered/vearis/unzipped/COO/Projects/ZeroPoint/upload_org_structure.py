
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

# Extract Parent Page ID
def get_page_id_from_url(url):
    if "/wiki/" not in url:
        raise ValueError("Invalid Confluence URL.")
    return url.split("/")[-1].replace("x/", "")

PARENT_PAGE_ID = get_page_id_from_url(PARENT_PAGE_URL)

def get_auth():
    return (EMAIL, API_KEY)

def markdown_to_confluence_html(md_content):
    # Convert to basic HTML
    html = markdown(md_content, extensions=["fenced_code", "tables", "toc"])
    # Add Confluence macros manually
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

if __name__ == "__main__":
    with open(MARKDOWN_FILE, "r") as f:
        md = f.read()
    create_or_update_page("ADAPT Executive Organizational Structure", md)
