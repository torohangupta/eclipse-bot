import json
import os

token = os.environ.get("token")
game_number = os.environ.get("game_number")
gamestate_path = os.environ.get("gamestate_path")


def update_game_number():
    with open("config.json", "w") as f:
        data["game_number"] += 1
        json.dump(data, f)
