import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def run():
    """
    Run 'uv run doci.py' command and catch exceptions

    This function is used to execute the `doci.py` script using the `uv` command.
    It can be run in watch mode to automatically rerun the script when changes are detected.
    """
    try:
        subprocess.run(["uv", "run", "doci.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running doci.py: {e}")


def run_doci(watch=False):
    """
    Run 'uv run doci.py' command.

    Args:
        watch (bool): If True, watch doci.py for changes and rerun on save.
    """
    if not watch:
        # Just run the command once
        run()
        return

    # Watch mode
    print("Watching doci.py for changes (Ctrl+C to stop)...")

    class LiterallyHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path.endswith("doci.py"):
                print("\nFile changed, running 'uv run doci.py'...")
                run()
                print("\nWatching for changes...")

    # Initial run
    run()

    # Set up the file watcher
    event_handler = LiterallyHandler()
    observer = Observer()
    observer.schedule(
        event_handler,
        path=os.path.dirname(os.path.abspath("doci.py")),
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
    run_doci(watch=watch_mode)
