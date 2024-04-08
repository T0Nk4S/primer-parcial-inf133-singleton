import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import random

BASE_URL = 'http://localhost:8080/guess'

class Game:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.games = {}
            cls._instance.counter = 0
        return cls._instance

    def create_game(self, player):
        self.counter += 1
        game_id = self.counter
        number = random.randint(1, 100)  
        game_info = {
            "id": game_id,
            "player": player,
            "number": 50,
            "attempts": [],
            "status": "En Progreso"
        }
        self.games[game_id] = game_info
        return game_info

    def get_all_games(self):
        return self.games.values()

    def get_game_by_id(self, game_id):
        return self.games.get(game_id)

    def get_game_by_player(self, player):
        for game_id, game_info in self.games.items():
            if game_info["player"] == player:
                return game_info
        return None

    def update_attempts(self, game_id, attempt):
        if game_id in self.games:
            self.games[game_id]["attempts"].append(attempt)
            if attempt == self.games[game_id]["number"]:
                self.games[game_id]["status"] = "Finalizado"
                return "¡Felicitaciones! Has adivinado el número"
            elif attempt < self.games[game_id]["number"]:
                return "El número a adivinar es mayor"
            else:
                return "El número a adivinar es menor"
        return "Partida no encontrada"

    def delete_game(self, game_id):
        if game_id in self.games:
            del self.games[game_id]
            return True
        return False

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/guess":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            player = data.get("player")
            game_info = Game().create_game(player)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(game_info).encode())
        else:
            self.send_error(404, "Endpoint no encontrado")

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/guess":
            query_params = parse_qs(parsed_path.query)
            player = query_params.get("player")
            game_id = query_params.get("id")
            if game_id:
                game_id = int(game_id[0])
                game_info = Game().get_game_by_id(game_id)
            elif player:
                player = player[0]
                game_info = Game().get_game_by_player(player)
            else:
                games_info = {str(game_id): info for game_id, info in Game()._instance.games.items()}
                game_info = json.dumps(games_info)
            if game_info:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(game_info).encode())
            else:
                self.send_error(404, "Partida no encontrada")
        else:
            self.send_error(404, "Endpoint no encontrado")

    def do_PUT(self):
        if self.path.startswith("/guess/"):
            game_id = int(self.path.split("/")[-1])
            content_length = int(self.headers['Content-Length'])
            put_data = self.rfile.read(content_length)
            data = json.loads(put_data)
            attempt = int(data.get("attempt"))
            response_message = Game().update_attempts(game_id, attempt)
            response = {"message": response_message}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404, "Endpoint no encontrado")

    def do_DELETE(self):
        if self.path.startswith("/guess/"):
            game_id = int(self.path.split("/")[-1])
            if Game().delete_game(game_id):
                response = {"message": "Partida eliminada"}
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_error(404, "Partida no encontrada")
        else:
            self.send_error(404, "Endpoint no encontrado")

def run():
    print('Iniciando servidor...')
    server_address = ('localhost', 8080)
    httpd = HTTPServer(server_address, HTTPRequestHandler)
    print('Servidor en funcionamiento')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
