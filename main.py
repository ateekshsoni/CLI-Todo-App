#!/usr/bin/env python3
"""
Professional Todo CLI Application

A fully functional command-line todo application with CRUD operations,
data persistence, and beautiful terminal output.

Author: Atiksh Soni
Date: June 2025
"""

import json
import os
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm


# =============================================================================
# CONFIGURATION AND CONSTANTS
# =============================================================================

# Application configuration
APP_NAME = "todo-cli"
DATA_FILE = Path.home() / f".{APP_NAME}" / "todos.json"

# Ensure data directory exists
DATA_FILE.parent.mkdir(exist_ok=True)

# Rich console for beautiful output
console = Console()


# =============================================================================
# DATA MODELS AND ENUMS
# =============================================================================


class Priority(str, Enum):
    """Enumeration for task priorities with string values for easy serialization."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Status(str, Enum):
    """Enumeration for task status with string values for easy serialization."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Task:
    """
    Task model representing a single todo item.

    This class encapsulates all task-related data and provides methods
    for serialization and deserialization.
    """

    def __init__(
        self,
        title: str,
        description: str = "",
        priority: Priority = Priority.MEDIUM,
        status: Status = Status.PENDING,
        created_at: Optional[str] = None,
        completed_at: Optional[str] = None,
        task_id: Optional[int] = None,
    ):
        """
        Initialize a new task.

        Args:
            title: Task title (required)
            description: Detailed task description
            priority: Task priority level
            status: Current task status
            created_at: ISO timestamp when task was created
            completed_at: ISO timestamp when task was completed
            task_id: Unique identifier for the task
        """
        self.task_id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.created_at = created_at or datetime.now().isoformat()
        self.completed_at = completed_at

    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create task instance from dictionary (JSON deserialization)."""
        return cls(
            task_id=data.get("task_id"),
            title=data["title"],
            description=data.get("description", ""),
            priority=Priority(data.get("priority", Priority.MEDIUM.value)),
            status=Status(data.get("status", Status.PENDING.value)),
            created_at=data.get("created_at"),
            completed_at=data.get("completed_at"),
        )

    def mark_completed(self):
        """Mark task as completed and set completion timestamp."""
        self.status = Status.COMPLETED
        self.completed_at = datetime.now().isoformat()

    def mark_in_progress(self):
        """Mark task as in progress."""
        self.status = Status.IN_PROGRESS
        self.completed_at = None  # Clear completion time if previously set


# =============================================================================
# DATA PERSISTENCE LAYER
# =============================================================================


class TodoStorage:
    """
    Handles data persistence for todo tasks using JSON storage.

    This class provides a clean interface for loading and saving tasks,
    abstracting away the file system operations.
    """

    @staticmethod
    def load_tasks() -> List[Task]:
        """
        Load all tasks from the JSON file.

        Returns:
            List of Task objects, empty list if file doesn't exist or is invalid
        """
        try:
            if not DATA_FILE.exists():
                return []

            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return [Task.from_dict(task_data) for task_data in data]

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            console.print(f"[red]Error loading tasks: {e}[/red]")
            console.print("[yellow]Starting with empty task list.[/yellow]")
            return []
        except Exception as e:
            console.print(f"[red]Unexpected error loading tasks: {e}[/red]")
            return []

    @staticmethod
    def save_tasks(tasks: List[Task]) -> bool:
        """
        Save all tasks to the JSON file.

        Args:
            tasks: List of Task objects to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert tasks to dictionaries for JSON serialization
            task_data = [task.to_dict() for task in tasks]

            # Write to file with proper formatting
            with open(DATA_FILE, "w", encoding="utf-8") as file:
                json.dump(task_data, file, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            console.print(f"[red]Error saving tasks: {e}[/red]")
            return False


# =============================================================================
# BUSINESS LOGIC LAYER
# =============================================================================


class TodoManager:
    """
    Core business logic for managing todo tasks.

    This class handles all CRUD operations and task management logic,
    providing a clean interface between the CLI and data storage.
    """

    def __init__(self):
        """Initialize the todo manager and load existing tasks."""
        self.tasks: List[Task] = TodoStorage.load_tasks()
        self._assign_task_ids()

    def _assign_task_ids(self):
        """Assign unique sequential IDs to tasks that don't have them."""
        max_id = 0

        # Find the highest existing ID
        for task in self.tasks:
            if task.task_id is not None:
                max_id = max(max_id, task.task_id)

        # Assign IDs to tasks that don't have them
        for task in self.tasks:
            if task.task_id is None:
                max_id += 1
                task.task_id = max_id

    def _get_next_id(self) -> int:
        """Get the next available task ID."""
        if not self.tasks:
            return 1
        return max(task.task_id for task in self.tasks if task.task_id) + 1

    def add_task(
        self, title: str, description: str = "", priority: Priority = Priority.MEDIUM
    ) -> Task:
        """
        Add a new task to the list.

        Args:
            title: Task title (required)
            description: Task description
            priority: Task priority level

        Returns:
            The newly created Task object
        """
        task = Task(
            task_id=self._get_next_id(),
            title=title,
            description=description,
            priority=priority,
        )

        self.tasks.append(task)
        self._save_tasks()
        return task

    def get_tasks(self, status_filter: Optional[Status] = None) -> List[Task]:
        """
        Get all tasks, optionally filtered by status.

        Args:
            status_filter: Optional status to filter by

        Returns:
            List of tasks matching the filter criteria
        """
        if status_filter is None:
            return self.tasks.copy()

        return [task for task in self.tasks if task.status == status_filter]

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Get a specific task by its ID.

        Args:
            task_id: The ID of the task to retrieve

        Returns:
            Task object if found, None otherwise
        """
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[Priority] = None,
        status: Optional[Status] = None,
    ) -> bool:
        """
        Update an existing task.

        Args:
            task_id: ID of the task to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional)
            status: New status (optional)

        Returns:
            True if task was found and updated, False otherwise
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return False

        # Update only the provided fields
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if priority is not None:
            task.priority = priority
        if status is not None:
            task.status = status
            # Handle completion timestamp
            if status == Status.COMPLETED:
                task.mark_completed()
            elif status == Status.IN_PROGRESS:
                task.mark_in_progress()

        self._save_tasks()
        return True

    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by its ID.

        Args:
            task_id: ID of the task to delete

        Returns:
            True if task was found and deleted, False otherwise
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            return False

        self.tasks.remove(task)
        self._save_tasks()
        return True

    def mark_completed(self, task_id: int) -> bool:
        """
        Mark a task as completed.

        Args:
            task_id: ID of the task to mark as completed

        Returns:
            True if successful, False if task not found
        """
        return self.update_task(task_id, status=Status.COMPLETED)

    def _save_tasks(self):
        """Save current tasks to storage."""
        TodoStorage.save_tasks(self.tasks)


# =============================================================================
# CLI PRESENTATION LAYER
# =============================================================================


class TodoCLI:
    """
    Command-line interface for the todo application.

    This class handles all user interaction, input validation,
    and output formatting using Rich for beautiful terminal output.
    """

    def __init__(self):
        """Initialize the CLI with a TodoManager instance."""
        self.manager = TodoManager()

    def display_tasks(self, tasks: List[Task], title: str = "Tasks"):
        """
        Display tasks in a beautiful table format.

        Args:
            tasks: List of tasks to display
            title: Table title
        """
        if not tasks:
            console.print(f"[yellow]No {title.lower()} found.[/yellow]")
            return

        # Create a rich table
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=4)
        table.add_column("Title", style="green", min_width=20)
        table.add_column("Priority", width=8)
        table.add_column("Status", width=12)
        table.add_column("Created", width=16)

        # Color mapping for priorities and statuses
        priority_colors = {
            Priority.LOW: "blue",
            Priority.MEDIUM: "yellow",
            Priority.HIGH: "red",
        }

        status_colors = {
            Status.PENDING: "yellow",
            Status.IN_PROGRESS: "blue",
            Status.COMPLETED: "green",
        }

        # Add rows to the table
        for task in tasks:
            priority_color = priority_colors.get(task.priority, "white")
            status_color = status_colors.get(task.status, "white")

            # Format the created date
            try:
                created_date = datetime.fromisoformat(task.created_at).strftime(
                    "%Y-%m-%d %H:%M"
                )
            except (ValueError, TypeError):
                created_date = "Unknown"

            table.add_row(
                str(task.task_id),
                task.title,
                f"[{priority_color}]{task.priority.value.title()}[/{priority_color}]",
                f"[{status_color}]{task.status.value.replace('_', ' ').title()}[/{status_color}]",
                created_date,
            )

        console.print(table)

    def display_task_details(self, task: Task):
        """
        Display detailed information about a single task.

        Args:
            task: Task to display details for
        """
        # Create a panel with task details
        details = f"""
[bold]Title:[/bold] {task.title}
[bold]Description:[/bold] {task.description or 'No description provided'}
[bold]Priority:[/bold] {task.priority.value.title()}
[bold]Status:[/bold] {task.status.value.replace('_', ' ').title()}
[bold]Created:[/bold] {datetime.fromisoformat(task.created_at).strftime("%Y-%m-%d %H:%M:%S")}"""

        if task.completed_at:
            details += f"\n[bold]Completed:[/bold] {datetime.fromisoformat(task.completed_at).strftime('%Y-%m-%d %H:%M:%S')}"

        panel = Panel(details, title=f"Task #{task.task_id}", border_style="blue")
        console.print(panel)


# =============================================================================
# TYPER CLI APPLICATION
# =============================================================================

# Initialize Typer app
app = typer.Typer(
    name="todo",
    help="Professional Todo CLI - Manage your tasks efficiently",
    add_completion=False,
)

# Global TodoCLI instance
cli = TodoCLI()


@app.command("add")
def add_task(
    title: str = typer.Argument(..., help="Task title"),
    description: str = typer.Option("", "--desc", "-d", help="Task description"),
    priority: Priority = typer.Option(
        Priority.MEDIUM, "--priority", "-p", help="Task priority"
    ),
):
    """Add a new task to your todo list."""
    try:
        task = cli.manager.add_task(title, description, priority)
        console.print(f"[green]✓ Task #{task.task_id} added successfully![/green]")
        cli.display_task_details(task)
    except Exception as e:
        console.print(f"[red]Error adding task: {e}[/red]")


@app.command("list")
def list_tasks(
    status: Optional[Status] = typer.Option(
        None, "--status", "-s", help="Filter by status"
    ),
    all_tasks: bool = typer.Option(False, "--all", "-a", help="Show all tasks"),
):
    """List all tasks or filter by status."""
    try:
        if all_tasks:
            tasks = cli.manager.get_tasks()
            title = "All Tasks"
        elif status:
            tasks = cli.manager.get_tasks(status)
            title = f"{status.value.replace('_', ' ').title()} Tasks"
        else:
            # Default: show pending and in-progress tasks
            pending = cli.manager.get_tasks(Status.PENDING)
            in_progress = cli.manager.get_tasks(Status.IN_PROGRESS)
            tasks = pending + in_progress
            title = "Active Tasks"

        cli.display_tasks(tasks, title)
    except Exception as e:
        console.print(f"[red]Error listing tasks: {e}[/red]")


@app.command("show")
def show_task(task_id: int = typer.Argument(..., help="Task ID to show")):
    """Show detailed information about a specific task."""
    try:
        task = cli.manager.get_task_by_id(task_id)
        if task:
            cli.display_task_details(task)
        else:
            console.print(f"[red]Task #{task_id} not found.[/red]")
    except Exception as e:
        console.print(f"[red]Error showing task: {e}[/red]")


@app.command("update")
def update_task(
    task_id: int = typer.Argument(..., help="Task ID to update"),
    title: Optional[str] = typer.Option(None, "--title", "-t", help="New title"),
    description: Optional[str] = typer.Option(
        None, "--desc", "-d", help="New description"
    ),
    priority: Optional[Priority] = typer.Option(
        None, "--priority", "-p", help="New priority"
    ),
    status: Optional[Status] = typer.Option(None, "--status", "-s", help="New status"),
):
    """Update an existing task."""
    try:
        if cli.manager.update_task(task_id, title, description, priority, status):
            console.print(f"[green]✓ Task #{task_id} updated successfully![/green]")
            task = cli.manager.get_task_by_id(task_id)
            if task:
                cli.display_task_details(task)
        else:
            console.print(f"[red]Task #{task_id} not found.[/red]")
    except Exception as e:
        console.print(f"[red]Error updating task: {e}[/red]")


@app.command("complete")
def complete_task(
    task_id: int = typer.Argument(..., help="Task ID to mark as completed")
):
    """Mark a task as completed."""
    try:
        if cli.manager.mark_completed(task_id):
            console.print(f"[green]✓ Task #{task_id} marked as completed![/green]")
        else:
            console.print(f"[red]Task #{task_id} not found.[/red]")
    except Exception as e:
        console.print(f"[red]Error completing task: {e}[/red]")


@app.command("delete")
def delete_task(
    task_id: int = typer.Argument(..., help="Task ID to delete"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
):
    """Delete a task from your todo list."""
    try:
        task = cli.manager.get_task_by_id(task_id)
        if not task:
            console.print(f"[red]Task #{task_id} not found.[/red]")
            return

        # Show task details and confirm deletion
        cli.display_task_details(task)

        if not force:
            if not Confirm.ask(f"Are you sure you want to delete task #{task_id}?"):
                console.print("[yellow]Deletion cancelled.[/yellow]")
                return

        if cli.manager.delete_task(task_id):
            console.print(f"[green]✓ Task #{task_id} deleted successfully![/green]")
        else:
            console.print(f"[red]Failed to delete task #{task_id}.[/red]")

    except Exception as e:
        console.print(f"[red]Error deleting task: {e}[/red]")


@app.command("stats")
def show_statistics():
    """Show task statistics and summary."""
    try:
        all_tasks = cli.manager.get_tasks()

        if not all_tasks:
            console.print("[yellow]No tasks found.[/yellow]")
            return

        # Calculate statistics
        total = len(all_tasks)
        pending = len([t for t in all_tasks if t.status == Status.PENDING])
        in_progress = len([t for t in all_tasks if t.status == Status.IN_PROGRESS])
        completed = len([t for t in all_tasks if t.status == Status.COMPLETED])

        # Priority breakdown
        high_priority = len([t for t in all_tasks if t.priority == Priority.HIGH])
        medium_priority = len([t for t in all_tasks if t.priority == Priority.MEDIUM])
        low_priority = len([t for t in all_tasks if t.priority == Priority.LOW])

        # Create statistics display
        stats_text = f"""
[bold]Total Tasks:[/bold] {total}

[bold]Status Breakdown:[/bold]
  • [yellow]Pending:[/yellow] {pending}
  • [blue]In Progress:[/blue] {in_progress}
  • [green]Completed:[/green] {completed}

[bold]Priority Breakdown:[/bold]
  • [red]High:[/red] {high_priority}
  • [yellow]Medium:[/yellow] {medium_priority}
  • [blue]Low:[/blue] {low_priority}

[bold]Completion Rate:[/bold] {(completed / total * 100):.1f}%
        """

        panel = Panel(stats_text, title="📊 Task Statistics", border_style="green")
        console.print(panel)

    except Exception as e:
        console.print(f"[red]Error showing statistics: {e}[/red]")


@app.command("clear")
def clear_completed(
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation")
):
    """Remove all completed tasks."""
    try:
        completed_tasks = cli.manager.get_tasks(Status.COMPLETED)

        if not completed_tasks:
            console.print("[yellow]No completed tasks to clear.[/yellow]")
            return

        console.print(
            f"[yellow]Found {len(completed_tasks)} completed task(s):[/yellow]"
        )
        cli.display_tasks(completed_tasks, "Completed Tasks to Remove")

        if not force:
            if not Confirm.ask(
                f"Are you sure you want to delete {len(completed_tasks)} completed task(s)?"
            ):
                console.print("[yellow]Clear operation cancelled.[/yellow]")
                return

        # Delete all completed tasks
        deleted_count = 0
        for task in completed_tasks:
            if cli.manager.delete_task(task.task_id):
                deleted_count += 1

        console.print(f"[green]✓ {deleted_count} completed task(s) cleared![/green]")

    except Exception as e:
        console.print(f"[red]Error clearing completed tasks: {e}[/red]")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


def main():
    """Main entry point for the application."""
    try:
        # Display welcome message on first run
        if len(sys.argv) == 1:
            console.print(
                Panel(
                    "[bold blue]Welcome to Professional Todo CLI![/bold blue]\n\n"
                    "Use [cyan]--help[/cyan] to see available commands.\n"
                    'Example: [green]python main.py add "Buy groceries" --desc "Milk, bread, eggs"[/green]',
                    title="🚀 Todo CLI",
                    border_style="blue",
                )
            )

        app()

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
