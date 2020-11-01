#!/usr/bin/env python3
from phue import Bridge
import os
import argparse


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CREDENTIALS_PATH = os.path.join(SCRIPT_DIR, "credentials.json")


def main():

    args = parse_arguments()

    bridge = Bridge(ip="192.168.1.2", config_file_path=CREDENTIALS_PATH)

    api = bridge.get_api()

    if args.list_scenes:
        list_scenes(bridge, api)
    elif args.scene:
        activate_scene(bridge, api, scene=args.scene)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene", "-s", type=str, help="the scene to activate")
    parser.add_argument(
        "--list-scenes",
        "-l",
        dest="list_scenes",
        action="store_true",
        help="list all available scenes",
    )
    return parser.parse_args()


def list_scenes(bridge: Bridge, api: dict) -> None:
    scenes: set = set()
    for scene_dict in api["scenes"].values():
        scenes.add(scene_dict["name"])

    sorted_scenes: list = sorted(scenes)

    print("Scenes:")
    for scene in sorted_scenes:
        print(f"\t{scene}")
    print()


def activate_scene(bridge: Bridge, api: dict, scene: str) -> None:
    basement_id = get_group_id(api=api, room_name="Basement")

    scene_id = get_scene_id(api=api, scene_name=scene)

    bridge.activate_scene(group_id=basement_id, scene_id=scene_id, transition_time=1)


def get_group_id(api: dict, room_name: str) -> int:
    for group_id, group_dict in api["groups"].items():
        if room_name == group_dict["name"]:
            return int(group_id)


def get_scene_id(api: dict, scene_name: str) -> int:
    for scene_id, scene_dict in api["scenes"].items():
        if scene_name == scene_dict["name"]:
            return scene_id


def output_api() -> None:
    with open("hue_api.json", "w") as outfile:
        import json

        json.dump(bridge.get_api(), outfile, indent=4)


if __name__ == "__main__":
    main()
