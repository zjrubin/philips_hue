#!/usr/bin/env python3
from phue import Bridge, Group
from typing import Tuple
import os
import argparse


SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
CREDENTIALS_PATH = os.path.join(SCRIPT_DIR, "credentials.json")

PHILIPS_HUE_BRIDGE_IP = "10.0.0.79"
ROOM_NAME = "Office"


def main():
    args, parser = parse_arguments()

    bridge = Bridge(ip=PHILIPS_HUE_BRIDGE_IP, config_file_path=CREDENTIALS_PATH)

    api = bridge.get_api()

    task_executed = False
    if args.list_rooms:
        task_executed = True
        list_rooms(api)

    if args.list_scenes:
        task_executed = True
        list_scenes(api)

    if args.scene:
        task_executed = True
        activate_scene(bridge, api, room=args.room, scene=args.scene)

    if not task_executed:
        parser.print_help()


def parse_arguments() -> Tuple[argparse.Namespace, argparse.ArgumentParser]:
    parser = argparse.ArgumentParser()
    parser.add_argument("--room", "-r", type=str, help="the room to affect")
    parser.add_argument("--scene", "-s", type=str, help="the scene to activate")
    parser.add_argument(
        "--list-rooms",
        "-m",
        dest="list_rooms",
        action="store_true",
        help="list all available rooms",
    )
    parser.add_argument(
        "--list-scenes",
        "-l",
        dest="list_scenes",
        action="store_true",
        help="list all available scenes",
    )

    args = parser.parse_args()

    if args.scene and not args.room:
        parser.error("--room required")

    if args.room and not args.scene:
        parser.error("--scene required")

    return args, parser


def list_rooms(api: dict) -> None:
    sorted_rooms: list = sorted((group["name"] for group in api["groups"].values()))

    print("Rooms:")
    for room in sorted_rooms:
        print(f"\t{room}")
    print()


def list_scenes(api: dict) -> None:
    scenes = set()
    for scene_dict in api["scenes"].values():
        scenes.add(scene_dict["name"])

    sorted_scenes: list = sorted(scenes)

    print("Scenes:")
    for scene in sorted_scenes:
        print(f"\t{scene}")
    print("\tOff")
    print()


def activate_scene(bridge: Bridge, api: dict, room: str, scene: str) -> None:
    group_id = get_group_id(api=api, room_name=room)

    if scene == "Off":
        # This isn't actually a scene, so it is needs to be handled differently
        group = Group(bridge, group_id)
        group.on = False
        return

    scene_id = get_scene_id(api=api, group_id=group_id, scene_name=scene)

    bridge.activate_scene(group_id=group_id, scene_id=scene_id, transition_time=1)


def get_group_id(api: dict, room_name: str) -> str:
    for group_id, group_dict in api["groups"].items():
        if room_name == group_dict["name"]:
            return group_id
    raise ValueError(f"Could not find group id for room [{room_name}].")


def get_scene_id(api: dict, group_id: str, scene_name: str) -> str:
    group_scenes = [
        (scene_id, scend_dict["name"])
        for scene_id, scend_dict in api["scenes"].items()
        if scend_dict["group"] == group_id
    ]
    for scene_id, _scene_name in group_scenes:
        if scene_name == _scene_name:
            return scene_id

    # Could not find the scene
    sorted_scenes: list = sorted((scene_name for _, scene_name in group_scenes))
    raise ValueError(
        f"Could not find scene [{scene_name}] for group [{group_id}]."
        f" Available scenes are [{', '.join(sorted_scenes)}]."
        " Do you need to add this scene to this room?"
    )


def output_api() -> None:
    with open("hue_api.json", "w") as outfile:
        import json

        json.dump(bridge.get_api(), outfile, indent=4)


if __name__ == "__main__":
    main()
