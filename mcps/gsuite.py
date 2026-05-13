import os.path
from typing import List, Optional, Any
from mcp.server.fastmcp import FastMCP
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.message import EmailMessage

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/calendar.readonly",
]

mcp = FastMCP("Google Services")

def get_credentials(account: str = "primary"):
    """Gets valid user credentials from storage or runs the flow."""
    creds = None
    token_file = f"token_{account}.json"
    
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                raise FileNotFoundError(
                    "credentials.json not found. Please follow the instructions to get your Google API credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, "w") as token:
            token.write(creds.to_json())
    return creds

@mcp.tool()
async def list_google_accounts() -> List[str]:
    """List all configured Google accounts by looking for token_{account}.json files."""
    import glob
    token_files = glob.glob("token_*.json")
    accounts = [f.replace("token_", "").replace(".json", "") for f in token_files]
    return accounts if accounts else ["No accounts configured. Use any tool with an account name to authenticate."]

@mcp.tool()
async def list_emails(account: str = "primary", max_results: int = 10) -> List[dict]:
    """List recent emails from the user's inbox."""
    creds = get_credentials(account)
    try:
        service = build("gmail", "v1", credentials=creds)
        results = service.users().messages().list(userId="me", maxResults=max_results).execute()
        messages = results.get("messages", [])

        email_list = []
        for msg in messages:
            m = service.users().messages().get(userId="me", id=msg["id"]).execute()
            payload = m.get("payload", {})
            headers = payload.get("headers", [])
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
            sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
            email_list.append({
                "id": msg["id"],
                "threadId": msg["threadId"],
                "subject": subject,
                "from": sender,
                "snippet": m.get("snippet")
            })
        return email_list
    except HttpError as error:
        return [{"error": str(error)}]

@mcp.tool()
async def read_email(account: str = "primary", message_id: str = "") -> dict:
    """Read the full content of a specific email by ID."""
    creds = get_credentials(account)
    try:
        service = build("gmail", "v1", credentials=creds)
        message = service.users().messages().get(userId="me", id=message_id).execute()
        
        payload = message.get("payload", {})
        headers = payload.get("headers", [])
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
        
        # Simple extraction of body (might need more robust parsing for multipart)
        body = ""
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] == "text/plain":
                    if "data" in part["body"]:
                        body = base64.urlsafe_b64decode(part["body"]["data"]).decode()
        elif "body" in payload and payload["body"].get("data"):
            body = base64.urlsafe_b64decode(payload["body"]["data"]).decode()
            
        return {
            "id": message_id,
            "subject": subject,
            "from": sender,
            "body": body,
            "snippet": message.get("snippet")
        }
    except HttpError as error:
        return {"error": str(error)}

@mcp.tool()
async def create_draft(to: str, subject: str, body: str, account: str = "primary") -> dict:
    """Create a new email draft."""
    creds = get_credentials(account)
    try:
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()
        message.set_content(body)
        message["To"] = to
        message["From"] = "me"
        message["Subject"] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"message": {"raw": encoded_message}}
        draft = service.users().drafts().create(userId="me", body=create_message).execute()
        return {"id": draft["id"], "message": "Draft created successfully"}
    except HttpError as error:
        return {"error": str(error)}

@mcp.tool()
async def list_calendar_events(account: str = "primary", max_results: int = 10) -> List[dict]:
    """List upcoming events from the primary calendar."""
    creds = get_credentials(account)
    try:
        service = build("calendar", "v3", credentials=creds)
        from datetime import datetime
        now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        events_result = service.events().list(
            calendarId="primary", timeMin=now,
            maxResults=max_results, singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])

        return [{
            "id": e.get("id"),
            "summary": e.get("summary"),
            "start": e.get("start", {}).get("dateTime", e.get("start", {}).get("date")),
            "end": e.get("end", {}).get("dateTime", e.get("end", {}).get("date")),
            "description": e.get("description")
        } for e in events]
    except HttpError as error:
        return [{"error": str(error)}]

@mcp.tool()
async def add_calendar_event(summary: str, start_time: str, end_time: str, account: str = "primary", description: Optional[str] = None) -> dict:
    """Add a new event to the primary calendar. start_time and end_time should be in ISO format (e.g., 2024-05-12T10:00:00Z)."""
    creds = get_credentials(account)
    try:
        service = build("calendar", "v3", credentials=creds)
        event = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time},
            "end": {"dateTime": end_time},
        }
        event = service.events().insert(calendarId="primary", body=event).execute()
        return {"id": event.get("id"), "htmlLink": event.get("htmlLink"), "status": "Event created"}
    except HttpError as error:
        return {"error": str(error)}

if __name__ == "__main__":
    mcp.run()
