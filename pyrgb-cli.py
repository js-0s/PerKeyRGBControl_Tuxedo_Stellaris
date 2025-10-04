#!/usr/bin/env python3
"""
Headless CLI for managing RGB keyboard configurations.
Allows saving current keyboard colors to a file and loading colors from a file to apply to the keyboard.
Requires root privileges to access keyboard LEDs.
"""

from __future__ import annotations

import argparse
import sys
from types import FrameType
from typing import NoReturn, cast

from pyrgb_keyboard import KeyboardManager
from animations import RandomColorAnimation, WaveAnimation
import signal
import time


def main() -> NoReturn:
    parser = argparse.ArgumentParser(
        description="CLI tool for saving and loading RGB keyboard configurations."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Save command
    save_parser = subparsers.add_parser(
        "save", help="Save current keyboard configuration to a file"
    )
    _ = save_parser.add_argument("filename", help="Path to the INI file to save to")

    # Load command
    load_parser = subparsers.add_parser(
        "load", help="Load keyboard configuration from a file and apply it"
    )
    _ = load_parser.add_argument("filename", help="Path to the INI file to load from")

    # Animate command
    animate_parser = subparsers.add_parser("animate", help="Start a keyboard animation")
    _ = animate_parser.add_argument(
        "--type",
        choices=["random", "wave"],
        required=True,
        help="Type of animation to start",
    )

    args = parser.parse_args()
    command: str | None = cast(str | None, args.command)
    anim_type: str | None = cast(str | None, getattr(args, "type", None))
    filename: str | None = cast(str | None, getattr(args, "filename", None))

    if command is None:
        parser.print_help()
        sys.exit(1)

    manager = KeyboardManager()

    if command == "save":
        if filename is None:
            parser.print_help()
            sys.exit(1)
        try:
            manager.save_config(filename)
            print(f"Configuration saved to {filename}")
        except Exception as e:
            print(f"Error saving configuration: {e}", file=sys.stderr)
            sys.exit(1)
    elif command == "load":
        if filename is None:
            parser.print_help()
            sys.exit(1)
        try:
            manager.load_config(filename)
            print(f"Configuration loaded from {filename} and applied to keyboard")
        except Exception as e:
            print(f"Error loading configuration: {e}", file=sys.stderr)
            sys.exit(1)
    elif command == "animate":
        if anim_type is None:
            parser.print_help()
            sys.exit(1)
        animations = {
            "random": RandomColorAnimation,
            "wave": WaveAnimation,
        }
        anim_class = animations.get(anim_type)
        if not anim_class:
            print(f"Unknown animation type: {anim_type}", file=sys.stderr)
            sys.exit(1)
        anim = anim_class(manager)
        anim.start()
        print(f"Started {anim_type} animation. Press Ctrl+C to stop.")

        def signal_handler(sig: int, frame: FrameType):
            anim.stop()
            print(f"Stopped {anim_type} {sig} {frame} animation.")
            sys.exit(0)

        _ = signal.signal(signal.SIGINT, signal_handler)
        while True:
            time.sleep(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
