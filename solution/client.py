import requests
import json

BASE_URL = "http://localhost:8080/guess"

def create_game(player):
    url = BASE_URL
    data = {"player": player}
    response = requests.post(url, json=data)
    print(response.json())

def get_games(player=None, game_id=None):
    url = BASE_URL
    if player:
        url += f"?player={player}"
    elif game_id:
        url += f"/{game_id}"
    response = requests.get(url)
    print(response.json())

def make_attempt(game_id, attempt):
    url = f"{BASE_URL}/{game_id}"
    data = {"attempt": attempt}
    response = requests.put(url, json=data)
    print(response.json())

def delete_game(game_id):
    url = f"{BASE_URL}/{game_id}"
    response = requests.delete(url)
    print(response.json())


for i in range (1,25):

    if __name__ == "__main__":
        create_game("Julian")
        get_games()
        make_attempt(i, 25)
        make_attempt(i, 75)
        make_attempt(i, 50)
        delete_game(i)
        get_games()