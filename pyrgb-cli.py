#!/usr/bin/env python3
"""
Headless CLI for managing RGB keyboard configurations.
Allows saving current keyboard colors to a file and loading colors from a file to apply to the keyboard.
Requires root privileges to change keyboard colors.
"""

from __future__ import annotations

import argparse
import os
import sys
from types import FrameType
from typing import NoReturn, cast

from pyrgb_keyboard import KeyboardManager
from pyrgb_core import Color, LEDDevice
from animations import RandomColorAnimation, WaveAnimation, PulseAnimation
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
        choices=["random", "wave", "pulse"],
        required=True,
        help="Type of animation to start",
    )
    _ = animate_parser.add_argument(
        "--sleep",
        type=float,
        help="Sleep time in seconds between animation steps (default 0.5 for random, 0.1 for wave, 0.1 for pulse)",
    )
    _ = animate_parser.add_argument(
        "--target",
        choices=["keyboard", "lightbar", "key"],
        help="Target for pulse animation (required for pulse type)",
    )
    _ = animate_parser.add_argument(
        "--key-name",
        help="Name of the key to pulse (e.g., Space) (used for target key) may not work with all hardware",
    )
    _ = animate_parser.add_argument(
        "--color",
        help="Color for pulse animation in hex format (e.g., #ff0000) (used for pulse type)",
    )

    args = parser.parse_args()
    command: str | None = cast(str | None, args.command)
    anim_type: str | None = cast(str | None, getattr(args, "type", None))
    filename: str | None = cast(str | None, getattr(args, "filename", None))
    sleep: float | None = cast(float | None, getattr(args, "sleep", None))
    target: str | None = cast(str | None, getattr(args, "target", None))
    color: str | None = cast(str | None, getattr(args, "color", None))

    if command is None:
        parser.print_help()
        sys.exit(1)

    # Check for root privileges for commands that write to device files
    if command in ["load", "animate"] and os.geteuid() != 0:
        print(
            "To change the keyboard colors, you need root privileges.\n"
            + "Please try again, this time using 'sudo'.\n"
            + "Note: 'save' command works without root as it only reads current colors.",
            file=sys.stderr,
        )
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
            _ = manager.load_config(filename)
            print(f"Configuration loaded from {filename} and applied to keyboard")
        except Exception as e:
            print(f"Error loading configuration: {e}", file=sys.stderr)
            sys.exit(1)
    elif command == "animate":
        if anim_type is None:
            parser.print_help()
            sys.exit(1)
        if sleep is None:
            sleep = 0.5 if anim_type == "random" else 0.1
        if anim_type == "pulse":
            max_b = 50
            devices: list[LEDDevice] = []
            if not target:
                print("Pulse animation requires --target", file=sys.stderr)
                sys.exit(1)
            if target == "keyboard":
                devices = [LEDDevice.for_key(-1)]
            elif target == "lightbar":
                lightbar = LEDDevice.lightbar()
                if not lightbar.supported:
                    print("Lightbar not supported", file=sys.stderr)
                    sys.exit(1)
                devices = [lightbar]
                max_b = 100
            elif target == "key":
                key_name = str(getattr(args, "key_name", None))
                if not key_name:
                    print("Key target requires --key-name", file=sys.stderr)
                    sys.exit(1)
                dev = manager.get_device_by_name(key_name)
                if dev is None:
                    print(f"Key {key_name} not found or not present", file=sys.stderr)
                    sys.exit(1)
                devices = [dev]
                max_b = 50
            else:
                print(f"Invalid target: {target}", file=sys.stderr)
                sys.exit(1)
            if color:
                try:
                    pulse_color = Color.from_hex(color)
                except ValueError as e:
                    print(f"Invalid color: {e}", file=sys.stderr)
                    sys.exit(1)
                for dev in devices:
                    try:
                        dev.set_color(pulse_color)
                    except Exception as e:
                        print(f"Error setting color: {e}", file=sys.stderr)
                        sys.exit(1)
            anim = PulseAnimation(devices, max_b, sleep_time=sleep)
        else:
            animations = {
                "random": RandomColorAnimation,
                "wave": WaveAnimation,
            }
            anim_class = animations.get(anim_type)
            if not anim_class:
                print(f"Unknown animation type: {anim_type}", file=sys.stderr)
                sys.exit(1)
            anim = anim_class(manager, sleep_time=sleep)
        anim.start()
        print(
            f"Started {anim_type} animation with sleep {sleep}s. Press Ctrl+C to stop."
        )

        def signal_handler(sig: int, frame: FrameType | None) -> None:
            anim.stop()
            print(f"Stopped {anim_type} {sig} {frame} animation.")
            sys.exit(0)

        _ = signal.signal(signal.SIGINT, signal_handler)
        while True:
            time.sleep(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
