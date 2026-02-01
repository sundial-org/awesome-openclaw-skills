#!/usr/bin/env python3
"""
ClickUp API Client for OpenClaw
Handles multi-workspace operations, tasks, spaces, folders, lists, docs, and time tracking.
"""

import os
import sys
import json
import time
import requests
from typing import Optional, Dict, List, Any
from urllib.parse import urlencode

class ClickUpClient:
    BASE_URL = "https://api.clickup.com/api/v2"
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv("CLICKUP_API_TOKEN")
        if not self.api_token:
            raise ValueError("ClickUp API token required. Set CLICKUP_API_TOKEN env var.")
        
        self.headers = {
            "Authorization": self.api_token,
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make authenticated request to ClickUp API."""
        url = f"{self.BASE_URL}{endpoint}"
        
        if "headers" not in kwargs:
            kwargs["headers"] = self.headers
        
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}
    
    # ===== TEAM/WORKSPACE OPERATIONS =====
    
    def get_teams(self) -> List[Dict]:
        """Get all workspaces (teams) user has access to."""
        result = self._request("GET", "/team")
        return result.get("teams", [])
    
    def get_team(self, team_id: str) -> Dict:
        """Get specific workspace details."""
        return self._request("GET", f"/team/{team_id}")
    
    # ===== SPACE OPERATIONS =====
    
    def get_spaces(self, team_id: str, archived: bool = False) -> List[Dict]:
        """Get all spaces in a workspace."""
        params = {"archived": str(archived).lower()}
        result = self._request("GET", f"/team/{team_id}/space", params=params)
        return result.get("spaces", [])
    
    def get_space(self, space_id: str) -> Dict:
        """Get specific space details."""
        return self._request("GET", f"/space/{space_id}")
    
    def create_space(self, team_id: str, name: str, **kwargs) -> Dict:
        """Create a new space in a workspace."""
        data = {"name": name, **kwargs}
        return self._request("POST", f"/team/{team_id}/space", json=data)
    
    def update_space(self, space_id: str, **kwargs) -> Dict:
        """Update space configuration (name, statuses, etc.)."""
        return self._request("PUT", f"/space/{space_id}", json=kwargs)
    
    def delete_space(self, space_id: str) -> Dict:
        """Delete a space."""
        return self._request("DELETE", f"/space/{space_id}")
    
    # ===== FOLDER OPERATIONS =====
    
    def get_folders(self, space_id: str, archived: bool = False) -> List[Dict]:
        """Get all folders in a space."""
        params = {"archived": str(archived).lower()}
        result = self._request("GET", f"/space/{space_id}/folder", params=params)
        return result.get("folders", [])
    
    def get_folder(self, folder_id: str) -> Dict:
        """Get specific folder details."""
        return self._request("GET", f"/folder/{folder_id}")
    
    def create_folder(self, space_id: str, name: str) -> Dict:
        """Create a new folder in a space."""
        return self._request("POST", f"/space/{space_id}/folder", json={"name": name})
    
    def update_folder(self, folder_id: str, name: str) -> Dict:
        """Rename a folder."""
        return self._request("PUT", f"/folder/{folder_id}", json={"name": name})
    
    def delete_folder(self, folder_id: str) -> Dict:
        """Delete a folder."""
        return self._request("DELETE", f"/folder/{folder_id}")
    
    # ===== LIST OPERATIONS =====
    
    def get_lists(self, folder_id: str, archived: bool = False) -> List[Dict]:
        """Get all lists in a folder."""
        params = {"archived": str(archived).lower()}
        result = self._request("GET", f"/folder/{folder_id}/list", params=params)
        return result.get("lists", [])
    
    def get_space_lists(self, space_id: str, archived: bool = False) -> List[Dict]:
        """Get all lists directly in a space (no folder)."""
        params = {"archived": str(archived).lower()}
        result = self._request("GET", f"/space/{space_id}/list", params=params)
        return result.get("lists", [])
    
    def get_list(self, list_id: str) -> Dict:
        """Get specific list details."""
        return self._request("GET", f"/list/{list_id}")
    
    def create_list(self, folder_id: str, name: str, **kwargs) -> Dict:
        """Create a new list in a folder."""
        data = {"name": name, **kwargs}
        return self._request("POST", f"/folder/{folder_id}/list", json=data)
    
    def create_space_list(self, space_id: str, name: str, **kwargs) -> Dict:
        """Create a new list directly in a space."""
        data = {"name": name, **kwargs}
        return self._request("POST", f"/space/{space_id}/list", json=data)
    
    def update_list(self, list_id: str, **kwargs) -> Dict:
        """Update list configuration (name, statuses, etc.)."""
        return self._request("PUT", f"/list/{list_id}", json=kwargs)
    
    def delete_list(self, list_id: str) -> Dict:
        """Delete a list."""
        return self._request("DELETE", f"/list/{list_id}")
    
    # ===== TASK OPERATIONS =====
    
    def get_tasks(self, list_id: str, **filters) -> List[Dict]:
        """Get tasks from a list with optional filters."""
        result = self._request("GET", f"/list/{list_id}/task", params=filters)
        return result.get("tasks", [])
    
    def get_task(self, task_id: str, custom_task_ids: bool = False, 
                 team_id: Optional[str] = None) -> Dict:
        """Get specific task details."""
        params = {}
        if custom_task_ids and team_id:
            params = {"custom_task_ids": "true", "team_id": team_id}
        return self._request("GET", f"/task/{task_id}", params=params)
    
    def create_task(self, list_id: str, name: str, **kwargs) -> Dict:
        """Create a new task in a list."""
        data = {"name": name, **kwargs}
        return self._request("POST", f"/list/{list_id}/task", json=data)
    
    def update_task(self, task_id: str, custom_task_ids: bool = False,
                    team_id: Optional[str] = None, **kwargs) -> Dict:
        """Update task details."""
        params = {}
        if custom_task_ids and team_id:
            params = {"custom_task_ids": "true", "team_id": team_id}
        return self._request("PUT", f"/task/{task_id}", params=params, json=kwargs)
    
    def delete_task(self, task_id: str, custom_task_ids: bool = False,
                    team_id: Optional[str] = None) -> Dict:
        """Delete a task."""
        params = {}
        if custom_task_ids and team_id:
            params = {"custom_task_ids": "true", "team_id": team_id}
        return self._request("DELETE", f"/task/{task_id}", params=params)
    
    # ===== TIME TRACKING OPERATIONS =====
    
    def get_time_entries(self, team_id: str, **filters) -> List[Dict]:
        """Get time entries for a workspace."""
        result = self._request("GET", f"/team/{team_id}/time_entries", params=filters)
        return result.get("data", [])
    
    def get_time_entry(self, team_id: str, time_entry_id: str) -> Dict:
        """Get specific time entry."""
        return self._request("GET", f"/team/{team_id}/time_entries/{time_entry_id}")
    
    def create_time_entry(self, team_id: str, task_id: str, duration: int, 
                         description: Optional[str] = None, start: Optional[int] = None,
                         billable: bool = False, **kwargs) -> Dict:
        """Create a time entry for a task."""
        # If no start time provided, calculate it from duration (end is now)
        if start is None:
            end_time = int(time.time() * 1000)
            start = end_time - duration
        
        data = {
            "tid": task_id,
            "start": start,
            "duration": duration,
            "billable": billable,
            **kwargs
        }
        if description:
            data["description"] = description
        
        return self._request("POST", f"/team/{team_id}/time_entries", json=data)
    
    def update_time_entry(self, team_id: str, time_entry_id: str, **kwargs) -> Dict:
        """Update a time entry."""
        return self._request("PUT", f"/team/{team_id}/time_entries/{time_entry_id}", json=kwargs)
    
    def delete_time_entry(self, team_id: str, time_entry_id: str) -> Dict:
        """Delete a time entry."""
        return self._request("DELETE", f"/team/{team_id}/time_entries/{time_entry_id}")
    
    def start_timer(self, team_id: str, task_id: str) -> Dict:
        """Start a timer for a task."""
        return self._request("POST", f"/team/{team_id}/time_entries/start", json={"tid": task_id})
    
    def stop_timer(self, team_id: str) -> Dict:
        """Stop the running timer."""
        return self._request("POST", f"/team/{team_id}/time_entries/stop")
    
    # ===== DOCUMENT OPERATIONS (API v3) =====
    
    def _request_v3(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make authenticated request to ClickUp API v3."""
        url = f"https://api.clickup.com/api/v3{endpoint}"
        
        if "headers" not in kwargs:
            kwargs["headers"] = self.headers
        
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}
    
    def get_docs(self, workspace_id: str, **filters) -> List[Dict]:
        """Get documents in a workspace."""
        result = self._request_v3("GET", f"/workspaces/{workspace_id}/docs", params=filters)
        return result.get("docs", [])
    
    def get_doc(self, doc_id: str) -> Dict:
        """Get document details."""
        return self._request_v3("GET", f"/docs/{doc_id}")
    
    def create_doc(self, workspace_id: str, name: str, **kwargs) -> Dict:
        """Create a new document."""
        data = {"name": name, **kwargs}
        return self._request_v3("POST", f"/workspaces/{workspace_id}/docs", json=data)
    
    def update_doc(self, doc_id: str, **kwargs) -> Dict:
        """Update a document."""
        return self._request_v3("PUT", f"/docs/{doc_id}", json=kwargs)
    
    def delete_doc(self, doc_id: str) -> Dict:
        """Delete a document."""
        return self._request_v3("DELETE", f"/docs/{doc_id}")
    
    def get_doc_pages(self, doc_id: str) -> List[Dict]:
        """Get pages in a document."""
        result = self._request_v3("GET", f"/docs/{doc_id}/pages")
        return result.get("pages", [])
    
    def create_doc_page(self, doc_id: str, name: str, content: Optional[str] = None) -> Dict:
        """Create a new page in a document."""
        data = {"name": name}
        if content:
            data["content"] = content
        return self._request_v3("POST", f"/docs/{doc_id}/pages", json=data)
    
    def update_doc_page(self, doc_id: str, page_id: str, **kwargs) -> Dict:
        """Update a document page."""
        return self._request_v3("PUT", f"/docs/{doc_id}/pages/{page_id}", json=kwargs)
    
    def delete_doc_page(self, doc_id: str, page_id: str) -> Dict:
        """Delete a document page."""
        return self._request_v3("DELETE", f"/docs/{doc_id}/pages/{page_id}")
    
    # ===== DOC-TASK LINKING =====
    
    def link_doc_to_task(self, task_id: str, doc_id: str, custom_task_ids: bool = False,
                         team_id: Optional[str] = None) -> Dict:
        """Link a document to a task via attachment/relationship.
        
        In ClickUp, docs can be attached to tasks as attachments.
        """
        # Docs can be linked via task attachments or relationships
        # Using the task attachment endpoint
        params = {}
        if custom_task_ids and team_id:
            params = {"custom_task_ids": "true", "team_id": team_id}
        
        # Create attachment pointing to the doc
        data = {
            "attachment": {
                "url": f"https://app.clickup.com/{team_id}/docs/{doc_id}",
                "title": "Linked Document",
                "type": "url"
            }
        }
        return self._request("POST", f"/task/{task_id}/attachment", params=params, json=data)
    
    def add_doc_mention_to_task(self, task_id: str, doc_id: str, custom_task_ids: bool = False,
                                team_id: Optional[str] = None) -> Dict:
        """Add a doc mention to task description.
        
        Updates task description to include a link to the doc.
        """
        # Get current task
        task = self.get_task(task_id, custom_task_ids, team_id)
        if "error" in task:
            return task
        
        # Build doc mention markdown
        doc_url = f"https://app.clickup.com/{team_id}/docs/{doc_id}" if team_id else f"https://app.clickup.com/docs/{doc_id}"
        mention = f"\n\n[Linked Document]({doc_url})"
        
        # Append to description
        current_desc = task.get("description", "") or ""
        new_desc = current_desc + mention
        
        return self.update_task(task_id, custom_task_ids, team_id, description=new_desc)
    
    # ===== TASK DEPENDENCIES & LINKS =====
    
    def add_task_dependency(self, task_id: str, depends_on: Optional[str] = None, 
                           waiting_on: Optional[str] = None,
                           custom_task_ids: bool = False,
                           team_id: Optional[str] = None) -> Dict:
        """Add a dependency relationship between tasks.
        
        Args:
            task_id: The task to add dependency to
            depends_on: Task ID that this task depends on (blocking/waiting on)
            waiting_on: Task ID that is waiting on this task (blocked by)
        """
        params = {}
        if custom_task_ids and team_id:
            params = {"custom_task_ids": "true", "team_id": team_id}
        
        data = {}
        if depends_on:
            data["depends_on"] = depends_on
        if waiting_on:
            data["waiting_on"] = waiting_on
        
        if not data:
            return {"error": "Must provide either depends_on or waiting_on"}
        
        return self._request("POST", f"/task/{task_id}/dependency", params=params, json=data)
    
    def delete_task_dependency(self, task_id: str, depends_on: Optional[str] = None,
                              waiting_on: Optional[str] = None,
                              custom_task_ids: bool = False,
                              team_id: Optional[str] = None) -> Dict:
        """Remove a dependency relationship between tasks."""
        params = {}
        if custom_task_ids and team_id:
            params = {"custom_task_ids": "true", "team_id": team_id}
        
        if depends_on:
            params["depends_on"] = depends_on
        if waiting_on:
            params["waiting_on"] = waiting_on
        
        return self._request("DELETE", f"/task/{task_id}/dependency", params=params)
    
    def get_task_dependencies(self, task_id: str, custom_task_ids: bool = False,
                              team_id: Optional[str] = None) -> Dict:
        """Get all dependencies for a task."""
        params = {}
        if custom_task_ids and team_id:
            params = {"custom_task_ids": "true", "team_id": team_id}
        
        return self._request("GET", f"/task/{task_id}/dependency", params=params)
    
    def link_tasks(self, task_id: str, links_to: str, 
                   custom_task_ids: bool = False,
                   team_id: Optional[str] = None) -> Dict:
        """Link two tasks together (arbitrary relationship, not dependency).
        
        Args:
            task_id: Source task
            links_to: Target task ID to link to
        """
        params = {}
        if custom_task_ids and team_id:
            params = {"custom_task_ids": "true", "team_id": team_id}
        
        return self._request("POST", f"/task/{task_id}/link/{links_to}", params=params)
    
    def unlink_tasks(self, task_id: str, links_to: str,
                     custom_task_ids: bool = False,
                     team_id: Optional[str] = None) -> Dict:
        """Remove a link between two tasks."""
        params = {}
        if custom_task_ids and team_id:
            params = {"custom_task_ids": "true", "team_id": team_id}
        
        return self._request("DELETE", f"/task/{task_id}/link/{links_to}", params=params)
    
    # ===== REPORTING & ANALYTICS =====
    
    def get_all_tasks(self, team_id: str, include_closed: bool = False, 
                     space_ids: Optional[List[str]] = None,
                     assignees: Optional[List[str]] = None,
                     **filters) -> List[Dict]:
        """Get ALL tasks from workspace with automatic pagination.
        
        CRITICAL: Always includes subtasks (subtasks=true) to avoid missing 70%+ of work.
        ClickUp API returns max 100 tasks per page — this handles pagination automatically.
        
        Args:
            team_id: Workspace ID
            include_closed: Include closed/completed tasks
            space_ids: Optional list of space IDs to filter
            assignees: Optional list of user IDs to filter by assignee
            **filters: Additional filter parameters
        
        Returns:
            List of all tasks (parents and subtasks)
        """
        all_tasks = []
        page = 0
        
        while True:
            params = {
                "subtasks": "true",  # CRITICAL: Always include subtasks
                "include_closed": str(include_closed).lower(),
                "page": page,
                **filters
            }
            
            if space_ids:
                for i, sid in enumerate(space_ids):
                    params[f"space_ids[{i}]"] = sid
            
            if assignees:
                for i, uid in enumerate(assignees):
                    params[f"assignees[{i}]"] = uid
            
            result = self._request("GET", f"/team/{team_id}/task", params=params)
            
            if "error" in result:
                return [{"error": result["error"], "page": page}]
            
            tasks = result.get("tasks", [])
            all_tasks.extend(tasks)
            
            # Check if last page
            if result.get("last_page", True):
                break
            
            page += 1
            
            # Safety limit: max 10 pages (1000 tasks)
            if page >= 10:
                all_tasks.append({"warning": "Pagination limit reached (1000 tasks). More tasks may exist."})
                break
        
        return all_tasks
    
    def get_task_counts(self, team_id: str, **filters) -> Dict:
        """Get task count breakdown: total, parents, subtasks.
        
        Returns:
            Dict with total, parents, subtasks, and unassigned counts
        """
        tasks = self.get_all_tasks(team_id, **filters)
        
        if tasks and "error" in tasks[0]:
            return {"error": tasks[0]["error"]}
        
        parents = [t for t in tasks if t.get("parent") is None]
        subtasks = [t for t in tasks if t.get("parent") is not None]
        unassigned = [t for t in tasks if not t.get("assignees")]
        
        return {
            "total": len(tasks),
            "parents": len(parents),
            "subtasks": len(subtasks),
            "unassigned": len(unassigned)
        }
    
    def get_assignee_breakdown(self, team_id: str, **filters) -> Dict:
        """Get workload breakdown by assignee.
        
        Returns:
            Dict mapping username -> task count, sorted by count descending
        """
        tasks = self.get_all_tasks(team_id, **filters)
        
        if tasks and "error" in tasks[0]:
            return {"error": tasks[0]["error"]}
        
        from collections import Counter
        
        assignee_counts = Counter()
        for task in tasks:
            assignees = task.get("assignees", [])
            if assignees:
                for assignee in assignees:
                    username = assignee.get("username", "Unknown")
                    assignee_counts[username] += 1
            else:
                assignee_counts["Unassigned"] += 1
        
        # Sort by count descending
        return dict(assignee_counts.most_common())
    
    def get_status_breakdown(self, team_id: str, **filters) -> Dict:
        """Get task count breakdown by status.
        
        Returns:
            Dict mapping status -> count, sorted by count descending
        """
        tasks = self.get_all_tasks(team_id, **filters)
        
        if tasks and "error" in tasks[0]:
            return {"error": tasks[0]["error"]}
        
        from collections import Counter
        
        status_counts = Counter()
        for task in tasks:
            status = task.get("status", {})
            status_name = status.get("status", "Unknown")
            status_counts[status_name] += 1
        
        return dict(status_counts.most_common())
    
    def get_priority_breakdown(self, team_id: str, **filters) -> Dict:
        """Get task count breakdown by priority.
        
        Returns:
            Dict mapping priority -> count
        """
        tasks = self.get_all_tasks(team_id, **filters)
        
        if tasks and "error" in tasks[0]:
            return {"error": tasks[0]["error"]}
        
        from collections import Counter
        
        priority_counts = Counter()
        for task in tasks:
            priority = task.get("priority")
            if priority:
                priority_name = priority.get("priority", "none")
            else:
                priority_name = "none"
            priority_counts[priority_name] += 1
        
        return dict(priority_counts.most_common())
    
    def get_daily_standup_report(self, team_id: str, assignee_id: Optional[str] = None) -> Dict:
        """Generate daily standup report.
        
        Shows tasks grouped by status for specific assignee or all team members.
        
        Args:
            team_id: Workspace ID
            assignee_id: Optional user ID to filter (if None, shows all)
        
        Returns:
            Dict with tasks grouped by status category
        """
        filters = {}
        if assignee_id:
            filters["assignees"] = [assignee_id]
        
        tasks = self.get_all_tasks(team_id, **filters)
        
        if tasks and "error" in tasks[0]:
            return {"error": tasks[0]["error"]}
        
        # Group by status type
        report = {
            "to_do": [],
            "in_progress": [],
            "complete": [],
            "other": []
        }
        
        for task in tasks:
            status = task.get("status", {})
            status_type = status.get("type", "other")
            task_summary = {
                "id": task.get("id"),
                "name": task.get("name"),
                "status": status.get("status"),
                "assignees": [a.get("username") for a in task.get("assignees", [])],
                "url": task.get("url")
            }
            
            if status_type == "open":
                report["to_do"].append(task_summary)
            elif status_type == "custom":
                report["in_progress"].append(task_summary)
            elif status_type == "closed":
                report["complete"].append(task_summary)
            else:
                report["other"].append(task_summary)
        
        return report


def main():
    """CLI interface for ClickUp operations."""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command specified"}))
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    try:
        client = ClickUpClient()
        
        # Parse arguments as key=value pairs
        kwargs = {}
        for arg in args:
            if "=" in arg:
                key, value = arg.split("=", 1)
                # Try to parse as JSON, fallback to string
                try:
                    kwargs[key] = json.loads(value)
                except json.JSONDecodeError:
                    kwargs[key] = value
        
        # Execute command
        if command == "get_teams":
            result = client.get_teams()
        elif command == "get_spaces":
            result = client.get_spaces(kwargs["team_id"])
        elif command == "create_space":
            result = client.create_space(kwargs.pop("team_id"), kwargs.pop("name"), **kwargs)
        elif command == "get_folders":
            result = client.get_folders(kwargs["space_id"])
        elif command == "create_folder":
            result = client.create_folder(kwargs["space_id"], kwargs["name"])
        elif command == "get_lists":
            result = client.get_lists(kwargs["folder_id"])
        elif command == "get_space_lists":
            result = client.get_space_lists(kwargs["space_id"])
        elif command == "create_list":
            result = client.create_list(kwargs.pop("folder_id"), kwargs.pop("name"), **kwargs)
        elif command == "create_space_list":
            result = client.create_space_list(kwargs.pop("space_id"), kwargs.pop("name"), **kwargs)
        elif command == "get_task":
            result = client.get_task(kwargs.pop("task_id"), **kwargs)
        elif command == "get_tasks":
            result = client.get_tasks(kwargs.pop("list_id"), **kwargs)
        elif command == "create_task":
            result = client.create_task(kwargs.pop("list_id"), kwargs.pop("name"), **kwargs)
        elif command == "update_task":
            result = client.update_task(kwargs.pop("task_id"), **kwargs)
        elif command == "get_time_entries":
            result = client.get_time_entries(kwargs.pop("team_id"), **kwargs)
        elif command == "create_time_entry":
            result = client.create_time_entry(**kwargs)
        elif command == "start_timer":
            result = client.start_timer(kwargs["team_id"], kwargs["task_id"])
        elif command == "stop_timer":
            result = client.stop_timer(kwargs["team_id"])
        elif command == "get_docs":
            result = client.get_docs(kwargs["workspace_id"])
        elif command == "create_doc":
            result = client.create_doc(kwargs.pop("workspace_id"), kwargs.pop("name"), **kwargs)
        elif command == "get_doc":
            result = client.get_doc(kwargs["doc_id"])
        elif command == "get_doc_pages":
            result = client.get_doc_pages(kwargs["doc_id"])
        elif command == "create_doc_page":
            result = client.create_doc_page(kwargs.pop("doc_id"), kwargs.pop("name"), kwargs.get("content"))
        elif command == "update_doc_page":
            doc_id = kwargs.pop("doc_id")
            page_id = kwargs.pop("page_id")
            result = client.update_doc_page(doc_id, page_id, **kwargs)
        elif command == "delete_doc_page":
            result = client.delete_doc_page(kwargs["doc_id"], kwargs["page_id"])
        elif command == "link_doc_to_task":
            result = client.link_doc_to_task(kwargs.pop("task_id"), kwargs.pop("doc_id"), **kwargs)
        elif command == "mention_doc_in_task":
            result = client.add_doc_mention_to_task(kwargs.pop("task_id"), kwargs.pop("doc_id"), **kwargs)
        elif command == "add_dependency":
            result = client.add_task_dependency(kwargs.pop("task_id"), **kwargs)
        elif command == "remove_dependency":
            result = client.delete_task_dependency(kwargs.pop("task_id"), **kwargs)
        elif command == "get_dependencies":
            result = client.get_task_dependencies(kwargs.pop("task_id"), **kwargs)
        elif command == "link_tasks":
            result = client.link_tasks(kwargs.pop("task_id"), kwargs.pop("links_to"), **kwargs)
        elif command == "unlink_tasks":
            result = client.unlink_tasks(kwargs.pop("task_id"), kwargs.pop("links_to"), **kwargs)
        
        # Reporting commands
        elif command == "get_all_tasks":
            result = client.get_all_tasks(kwargs.pop("team_id"), **kwargs)
        elif command == "task_counts":
            result = client.get_task_counts(kwargs.pop("team_id"), **kwargs)
        elif command == "assignee_breakdown":
            result = client.get_assignee_breakdown(kwargs.pop("team_id"), **kwargs)
        elif command == "status_breakdown":
            result = client.get_status_breakdown(kwargs.pop("team_id"), **kwargs)
        elif command == "priority_breakdown":
            result = client.get_priority_breakdown(kwargs.pop("team_id"), **kwargs)
        elif command == "standup_report":
            result = client.get_daily_standup_report(kwargs.pop("team_id"), kwargs.get("assignee_id"))
        
        else:
            result = {"error": f"Unknown command: {command}"}
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
