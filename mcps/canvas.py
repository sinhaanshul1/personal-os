import os
from typing import List, Optional
from mcp.server.fastmcp import FastMCP
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Initialize FastMCP server
mcp = FastMCP("Canvas")

# Configuration from environment variables
CANVAS_BASE_URL = os.environ.get("CANVAS_BASE_URL", "").rstrip("/")
CANVAS_API_TOKEN = os.environ.get("CANVAS_API_TOKEN")

if not CANVAS_BASE_URL or not CANVAS_API_TOKEN:
    raise ValueError("CANVAS_BASE_URL and CANVAS_API_TOKEN must be set")

headers = {
    "Authorization": f"Bearer {CANVAS_API_TOKEN}"
}

async def fetch_all(url: str, params: Optional[dict] = None) -> List[dict]:
    """Helper to fetch all items with pagination."""
    results = []
    current_url = url
    async with httpx.AsyncClient() as client:
        while current_url:
            response = await client.get(current_url, headers=headers, params=params)
            response.raise_for_status()
            results.extend(response.json())
            
            # Check for pagination links
            if "next" in response.links:
                current_url = response.links["next"]["url"]
                params = None # Parameters are usually included in the next link
            else:
                current_url = None
    return results

@mcp.tool()
async def list_courses() -> List[dict]:
    """List all active courses for the user, returning only id and name."""
    url = f"{CANVAS_BASE_URL}/api/v1/courses"
    params = {"enrollment_state": "active", "include[]": "term"}
    courses = await fetch_all(url, params)
    return [{"id": c.get("id"), "name": c.get("name"), "course_code": c.get("course_code")} for c in courses if "name" in c]

@mcp.tool()
async def get_announcements(course_ids: List[int]) -> List[dict]:
    """Get recent announcements for specific courses."""
    url = f"{CANVAS_BASE_URL}/api/v1/announcements"
    params = {"context_codes[]": [f"course_{cid}" for cid in course_ids]}
    announcements = await fetch_all(url, params)
    return [{
        "id": a.get("id"),
        "title": a.get("title"),
        "message": a.get("message")[:200] + "..." if a.get("message") and len(a.get("message")) > 200 else a.get("message"),
        "posted_at": a.get("posted_at"),
        "course_id": a.get("context_code").split("_")[1] if a.get("context_code") else None
    } for a in announcements]

@mcp.tool()
async def get_assignments(course_id: int) -> List[dict]:
    """Get assignments for a specific course with due dates."""
    url = f"{CANVAS_BASE_URL}/api/v1/courses/{course_id}/assignments"
    assignments = await fetch_all(url)
    return [{
        "id": a.get("id"),
        "name": a.get("name"),
        "due_at": a.get("due_at"),
        "description": a.get("description")[:100] + "..." if a.get("description") and len(a.get("description")) > 100 else a.get("description"),
        "html_url": a.get("html_url")
    } for a in assignments]

@mcp.tool()
async def get_todo_items() -> List[dict]:
    """Get current to-do items (assignments to submit or grade)."""
    url = f"{CANVAS_BASE_URL}/api/v1/users/self/todo"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        todos = response.json()
        return [{
            "type": t.get("type"),
            "assignment_name": t.get("assignment", {}).get("name"),
            "course_id": t.get("course_id"),
            "due_at": t.get("assignment", {}).get("due_at"),
            "html_url": t.get("html_url")
        } for t in todos]

@mcp.tool()
async def get_upcoming_events() -> List[dict]:
    """Get upcoming events across all courses."""
    url = f"{CANVAS_BASE_URL}/api/v1/users/self/upcoming_events"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        events = response.json()
        return [{
            "id": e.get("id"),
            "title": e.get("title"),
            "start_at": e.get("start_at"),
            "end_at": e.get("end_at"),
            "description": e.get("description")[:100] + "..." if e.get("description") and len(e.get("description")) > 100 else e.get("description")
        } for e in events]

if __name__ == "__main__":
    mcp.run()
