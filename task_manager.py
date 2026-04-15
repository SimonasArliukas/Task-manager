import argparse
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored output
init(autoreset=True)

TASKS_FILE = os.environ.get("TASKS_FILE", "tasks.json")


def load_tasks() -> List[Dict]:
    """Load tasks from the JSON file."""
    if not os.path.exists(TASKS_FILE):
        return []
    try:
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_tasks(tasks: List[Dict]) -> None:
    """Save tasks to the JSON file."""
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def get_next_id(tasks: List[Dict]) -> int:
    """Get the next available task ID."""
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


def add_task(title: str, priority: str = "medium", tags: Optional[List[str]] = None) -> Dict:
    """Add a new task."""
    tasks = load_tasks()
    task = {
        "id": get_next_id(tasks),
        "title": title,
        "priority": priority,
        "tags": tags or [],
        "done": False,
        "created_at": datetime.now().isoformat(),
    }
    tasks.append(task)
    save_tasks(tasks)
    return task


def list_tasks(show_done: bool = False, priority_filter: Optional[str] = None,
               tag_filter: Optional[str] = None) -> List[Dict]:
    """List tasks with optional filters."""
    tasks = load_tasks()
    if not show_done:
        tasks = [t for t in tasks if not t["done"]]
    if priority_filter:
        tasks = [t for t in tasks if t["priority"] == priority_filter]
    if tag_filter:
        tasks = [t for t in tasks if tag_filter in t.get("tags", [])]
    return tasks


def complete_task(task_id: int) -> Optional[Dict]:
    """Mark a task as complete."""
    tasks = load_tasks()
    for task in tasks:
        if task["id"] == task_id:
            task["done"] = True
            task["completed_at"] = datetime.now().isoformat()
            save_tasks(tasks)
            return task
    return None


def delete_task(task_id: int) -> Optional[Dict]:
    """Delete a task by ID."""
    tasks = load_tasks()
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            removed = tasks.pop(i)
            save_tasks(tasks)
            return removed
    return None


def priority_color(priority: str) -> str:
    """Return a colored priority label."""
    colors = {
        "high":   Fore.RED,
        "medium": Fore.YELLOW,
        "low":    Fore.GREEN,
    }
    color = colors.get(priority, Fore.WHITE)
    return f"{color}[{priority.upper()}]{Style.RESET_ALL}"


def print_task(task: Dict) -> None:
    """Pretty-print a single task."""
    status = f"{Fore.GREEN}✔{Style.RESET_ALL}" if task["done"] else f"{Fore.CYAN}○{Style.RESET_ALL}"
    tags_str = ""
    if task.get("tags"):
        tags_str = "  " + " ".join(f"{Fore.MAGENTA}#{t}{Style.RESET_ALL}" for t in task["tags"])
    print(f"  {status} {Fore.WHITE}{task['id']:>3}.{Style.RESET_ALL} "
          f"{priority_color(task['priority'])} {task['title']}{tags_str}")


def cmd_add(args: argparse.Namespace) -> None:
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
    task = add_task(args.title, priority=args.priority, tags=tags)
    print(f"{Fore.GREEN}✔ Added task #{task['id']}:{Style.RESET_ALL} {task['title']}")


def cmd_list(args: argparse.Namespace) -> None:
    tasks = list_tasks(
        show_done=args.all,
        priority_filter=args.priority,
        tag_filter=args.tag,
    )
    if not tasks:
        print(f"{Fore.YELLOW}No tasks found.{Style.RESET_ALL}")
        return
    header = "ALL TASKS" if args.all else "PENDING TASKS"
    print(f"\n{Fore.CYAN}{Style.BRIGHT}  {header}{Style.RESET_ALL}")
    print(f"  {'─' * 50}")
    for task in tasks:
        print_task(task)
    print(f"  {'─' * 50}")
    print(f"  {Fore.WHITE}{len(tasks)} task(s) shown{Style.RESET_ALL}\n")


def cmd_done(args: argparse.Namespace) -> None:
    task = complete_task(args.id)
    if task:
        print(f"{Fore.GREEN}✔ Completed:{Style.RESET_ALL} {task['title']}")
    else:
        print(f"{Fore.RED}✘ Task #{args.id} not found.{Style.RESET_ALL}")
        sys.exit(1)


def cmd_delete(args: argparse.Namespace) -> None:
    task = delete_task(args.id)
    if task:
        print(f"{Fore.YELLOW}🗑  Deleted:{Style.RESET_ALL} {task['title']}")
    else:
        print(f"{Fore.RED}✘ Task #{args.id} not found.{Style.RESET_ALL}")
        sys.exit(1)


def cmd_stats(_args: argparse.Namespace) -> None:
    tasks = load_tasks()
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    pending = total - done
    priorities = {"high": 0, "medium": 0, "low": 0}
    for t in tasks:
        priorities[t.get("priority", "medium")] += 1

    print(f"\n{Fore.CYAN}{Style.BRIGHT}  TASK STATISTICS{Style.RESET_ALL}")
    print(f"  {'─' * 30}")
    print(f"  Total:   {total}")
    print(f"  {Fore.GREEN}Done:    {done}{Style.RESET_ALL}")
    print(f"  {Fore.YELLOW}Pending: {pending}{Style.RESET_ALL}")
    print(f"  {'─' * 30}")
    for p, count in priorities.items():
        print(f"  {priority_color(p)}: {count}")
    print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="task_manager",
        description="📋 Task Manager CLI — manage your tasks from the terminal",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = subparsers.add_parser("add", help="Add a new task")
    p_add.add_argument("title", help="Task title")
    p_add.add_argument("-p", "--priority", choices=["high", "medium", "low"],
                       default="medium", help="Task priority (default: medium)")
    p_add.add_argument("-t", "--tags", help="Comma-separated tags, e.g. work,urgent")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = subparsers.add_parser("list", help="List tasks")
    p_list.add_argument("-a", "--all", action="store_true", help="Show completed tasks too")
    p_list.add_argument("-p", "--priority", choices=["high", "medium", "low"],
                        help="Filter by priority")
    p_list.add_argument("-t", "--tag", help="Filter by tag")
    p_list.set_defaults(func=cmd_list)

    # done
    p_done = subparsers.add_parser("done", help="Mark a task as complete")
    p_done.add_argument("id", type=int, help="Task ID")
    p_done.set_defaults(func=cmd_done)

    # delete
    p_del = subparsers.add_parser("delete", help="Delete a task")
    p_del.add_argument("id", type=int, help="Task ID")
    p_del.set_defaults(func=cmd_delete)

    # stats
    p_stats = subparsers.add_parser("stats", help="Show task statistics")
    p_stats.set_defaults(func=cmd_stats)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()