import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

COMMAND = "uv run doci.py -m README.md -H index.html doci.py"


def run():
    """
    Run and catch exceptions from the doci.py script.
    """
    try:
        subprocess.run(
            COMMAND.split(" "),
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running doci.py: {e}")


def watch(watch=False):
    """
    Watch files for changes and run the command.
    """
    if not watch:
        # Just run the command once
        run()
        return

    # Watch mode
    print("Watching doci.py for changes (Ctrl+C to stop)...")

    class LiterallyHandler(FileSystemEventHandler):
        def on_modified(self, event):
            for file in ["doci.py", "doci.css", "template.html"]:
                if event.src_path.endswith(file):
                    print(f"{file} changed, running '{COMMAND}'...")
                    run()
                    print("Watching for changes...")
                    break

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
    watch(watch=watch_mode)
