#!/usr/bin/env python3
#
# Executes a command when a file is added
#
# Written by Jakob Ruhe (http://www.github.com/jakeru) November 2022

import argparse
import logging
import os
import subprocess
import threading
import time
import yaml
from pathlib import Path

import watchdog.events
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Handler(FileSystemEventHandler):
    def __init__(self, wakeup, files):
        self._wakeup = wakeup
        self._files = files

    def on_any_event(self, event):
        logging.debug(f"On {event.event_type}: {event.src_path}")
        interesting_events = (
            watchdog.events.EVENT_TYPE_CREATED,
            watchdog.events.EVENT_TYPE_DELETED,
        )
        if event.event_type in interesting_events and event.src_path in self._files:
            self._wakeup.set()


def parse_args():
    parser = argparse.ArgumentParser(description="Run a command when a file is created")
    parser.add_argument("config", help="Configuration file")
    parser.add_argument(
        "--delay",
        default=1,
        type=float,
        help="Delay (in seconds) before executing the command",
    )
    parser.add_argument(
        "--runatstart", action="store_true", help="Execute command once at start"
    )
    parser.add_argument("--verbose", help="Verbose mode", action="store_true")
    return parser.parse_args()


def collect_paths(files):
    return set([Path(f).parent for f in files])


def find_existing_files(files):
    existing = set()
    for f in files:
        if os.path.exists(f):
            existing.add(f)
    return existing


def run(cmd):
    return subprocess.Popen(cmd, shell=True)


def run_hook_for_files(files, hooks):
    new_processes = []
    for f in files:
        cmd = hooks[f]["cmd"]
        logging.info(f"Running hook for file {f}: {cmd}")
        new_processes.append(run(cmd))
    return new_processes


def parse_config(filename):
    with open(filename, "r") as f:
        config = yaml.safe_load(f)
    hooks = {}
    for f in config["files"]:
        hooks[f["file"]] = {"cmd": f["cmd"]}
    return hooks


def main():
    args = parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    log_format = "%(asctime)-15s %(levelname)-7s %(name)s %(message)s"
    logging.basicConfig(format=log_format, level=log_level)

    hooks = parse_config(args.config)
    files = hooks.keys()
    processes = []
    paths = collect_paths(files)
    logging.debug(f"Watching: {paths}")

    wakeup = threading.Event()
    event_handler = Handler(wakeup, files)
    observer = Observer()
    for path in paths:
        observer.schedule(event_handler, path)
    observer.start()
    try:
        existing = find_existing_files(files)
        if args.runatstart:
            processes += run_hook_for_files(existing, hooks)
        while True:
            wakeup.wait()
            time.sleep(args.delay)
            existed = existing
            existing = find_existing_files(files)
            processes += run_hook_for_files(existing - existed, hooks)
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    main()
