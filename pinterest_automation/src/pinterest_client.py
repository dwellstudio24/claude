import requests
import webbrowser
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, urlparse, parse_qs
from dataclasses import dataclass
from typing import Optional

PINTEREST_API = "https://api.pinterest.com/v5"
OAUTH_URL = "https://www.pinterest.com/oauth/"
TOKEN_URL = f"{PINTEREST_API}/oauth/token"
REDIRECT_URI = "http://localhost:8085/callback"
SCOPES = "boards:read,pins:write,pins:read"


@dataclass
class PinResult:
    pin_id: str
    pin_url: str
    title: str
    scheduled_for: Optional[str] = None


class PinterestClient:
    def __init__(self, access_token: str):
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        )

    def verify_token(self) -> dict:
        r = self.session.get(f"{PINTEREST_API}/user_account")
        r.raise_for_status()
        return r.json()

    def get_boards(self) -> list:
        boards = []
        params = {"page_size": 25}
        url = f"{PINTEREST_API}/boards"
        while url:
            r = self.session.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            boards.extend(data.get("items", []))
            bookmark = data.get("bookmark")
            params = {"bookmark": bookmark, "page_size": 25} if bookmark else None
            url = f"{PINTEREST_API}/boards" if bookmark else None
        return boards

    def create_pin(
        self,
        board_id: str,
        title: str,
        description: str,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        link: Optional[str] = None,
        publish_date: Optional[str] = None,
    ) -> PinResult:
        if image_base64:
            media_source = {
                "source_type": "image_base64",
                "content_type": "image/jpeg",
                "data": image_base64,
            }
        elif image_url:
            media_source = {"source_type": "image_url", "url": image_url}
        else:
            raise ValueError("Provide image_url or image_base64")

        payload = {
            "board_id": board_id,
            "title": title,
            "description": description,
            "media_source": media_source,
        }
        if link:
            payload["link"] = link
        if publish_date:
            payload["publish_date"] = publish_date

        r = self.session.post(f"{PINTEREST_API}/pins", json=payload)
        if not r.ok:
            raise Exception(f"Pinterest API {r.status_code}: {r.text}")

        data = r.json()
        return PinResult(
            pin_id=data["id"],
            pin_url=f"https://www.pinterest.com/pin/{data['id']}/",
            title=title,
            scheduled_for=publish_date,
        )


# ── OAuth helper ────────────────────────────────────────────────────────────

def get_oauth_token(client_id: str, client_secret: str) -> str:
    """
    Run local OAuth flow. Opens browser, catches callback on localhost:8085.
    Returns access_token string.
    """
    auth_params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
    }
    auth_url = f"{OAUTH_URL}?{urlencode(auth_params)}"

    # One-shot HTTP server to catch the callback
    received_code = [None]

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            qs = parse_qs(urlparse(self.path).query)
            received_code[0] = qs.get("code", [None])[0]
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"<h2>Authenticated! You can close this tab.</h2>")

        def log_message(self, *args):
            pass  # Silence HTTP log

    server = HTTPServer(("localhost", 8085), Handler)
    thread = threading.Thread(target=server.handle_request)
    thread.start()

    webbrowser.open(auth_url)
    thread.join(timeout=120)
    server.server_close()

    code = received_code[0]
    if not code:
        raise TimeoutError("OAuth callback not received within 120 seconds.")

    r = requests.post(
        TOKEN_URL,
        auth=(client_id, client_secret),
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    r.raise_for_status()
    return r.json()["access_token"]
