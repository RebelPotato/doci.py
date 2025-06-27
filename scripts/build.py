import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def run():
    """
    Run 'uv run literally.py' command and catch exceptions

    This function is used to execute the `literally.py` script using the `uv` command.
    It can be run in watch mode to automatically rerun the script when changes are detected.
    """
    try:
        subprocess.run(["uv", "run", "literally.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running literally.py: {e}")


def run_literally(watch=False):
    """
    Run 'uv run literally.py' command.

    Args:
        watch (bool): If True, watch literally.py for changes and rerun on save.
    """
    if not watch:
        # Just run the command once
        run()
        return

    # Watch mode
    print("Watching literally.py for changes (Ctrl+C to stop)...")

    class LiterallyHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path.endswith("literally.py"):
                print("\nFile changed, running 'uv run literally.py'...")
                run()
                print("\nWatching for changes...")

    # Initial run
    run()

    # Set up the file watcher
    event_handler = LiterallyHandler()
    observer = Observer()
    observer.schedule(
        event_handler,
        path=os.path.dirname(os.path.abspath("literally.py")),
        recursive=False,
    )
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    watch_mode = "-w" in sys.argv
    run_literally(watch=watch_mode)
