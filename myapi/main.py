import signal
import pickle
import sys
import os

TODO_FILE = "todo.pickle"

# Global todo list
todo = []


def load_todo():
    """Load todo list from pickle file if it exists."""
    global todo
    if os.path.exists(TODO_FILE):
        try:
            with open(TODO_FILE, "rb") as f:
                todo = pickle.load(f)
            print(f"Loaded {len(todo)} todo items from {TODO_FILE}")
        except Exception as e:
            print(f"Error loading todo: {e}")
            todo = []
    else:
        print("No existing todo file found, starting fresh.")
        todo = []


def save_todo():
    """Save todo list to pickle file."""
    try:
        with open(TODO_FILE, "wb") as f:
            pickle.dump(todo, f)
        print(f"Saved {len(todo)} todo items to {TODO_FILE}")
    except Exception as e:
        print(f"Error saving todo: {e}")


def graceful_exit(signum, frame):
    """Handle shutdown signals gracefully."""
    signal_name = signal.Signals(signum).name
    print(f"\nReceived {signal_name}, shutting down gracefully...")
    save_todo()
    print("Goodbye!")
    sys.exit(0)


def main():
    # Register signal handlers
    signal.signal(signal.SIGINT, graceful_exit)   # Ctrl+C
    signal.signal(signal.SIGTERM, graceful_exit)  # kill command

    # Load existing todo on startup
    load_todo()

    print("\nTodo Manager - Commands: add <item>, list, remove <index>, quit")
    print("Press Ctrl+C or send SIGTERM to save and exit gracefully.\n")

    while True:
        try:
            user_input = input("> ").strip()

            if not user_input:
                continue

            if user_input.startswith("add "):
                item = user_input[4:].strip()
                if item:
                    todo.append(item)
                    print(f"Added: {item}")
                else:
                    print("Please provide an item to add.")

            elif user_input == "list":
                if todo:
                    print("Todo list:")
                    for i, item in enumerate(todo):
                        print(f"  {i}: {item}")
                else:
                    print("Todo list is empty.")

            elif user_input.startswith("remove "):
                try:
                    index = int(user_input[7:].strip())
                    if 0 <= index < len(todo):
                        removed = todo.pop(index)
                        print(f"Removed: {removed}")
                    else:
                        print(f"Invalid index. Use 0-{len(todo)-1}")
                except ValueError:
                    print("Please provide a valid index number.")

            elif user_input == "quit":
                print("Quitting...")
                save_todo()
                print("Goodbye!")
                break

            else:
                print("Unknown command. Use: add <item>, list, remove <index>, quit")

        except EOFError:
            # Handle EOF (e.g., piped input ends)
            graceful_exit(signal.SIGTERM, None)


if __name__ == "__main__":
    main()
