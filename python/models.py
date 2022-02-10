import yaml
from time import time


class Square:
    def __init__(self):
        self.piece = None
        self.zone = False
        self.chest = False
        self.spells = []


class Piece:
    def __init__(self, color: bool, health: float, damage: float, distance: int, orthogonal: bool = False,
                 diagonal: bool = False, moves=None):
        # piece parameters
        self.color = color
        self.health = health
        self.damage = damage
        self.distance = distance
        self.orthogonal = orthogonal
        self.diagonal = diagonal
        self.moves = moves

        # board placement parameters
        self.coords = None
        self.game = None

    @staticmethod
    def generate(json: dict, color: bool):
        """
        Generate a Piece object from json
        :param json: dictionary containing information about the piece
        :param color: color of the piece
        :return: Piece object
        """
        return Piece(
            color,
            json.get('health'),
            json.get('damage'),
            json.get('distance'),
            orthogonal=json.get('orthogonal'),
            diagonal=json.get('diagonal'),
            moves=json.get('moves')
        )

    def place(self, game, coords: list) -> None:
        """
        Place a piece on the board
        :param game: Game object to place on its board
        :param coords: list of coordinates to place - [x, y]
        :return: None
        """
        self.game = game
        self.coords = coords
        game.board[coords[0]][coords[1]].piece = self

    def get(self) -> dict:
        """
        Get JSON-like representation of the game
        :return: dict containing all the information
        """
        return {
            "color": "white" if self.color else "black",
            "health": self.health,
            "damage": self.damage,
            "distance": self.distance,
            "moves": self.game.get_moves(self)
        }

    def __mod__(self, other):
        """
        Attack other piece
        :param other: other Piece to attack
        :return: True if other piece was killed, otherwise False
        """
        other.health -= self.damage
        return True if other.health <= 0 else False


class Game:
    def __init__(self, net, width=8, height=8):
        self.net = net
        self.height = height
        self.width = width
        self.board = [[Square() for h in range(height)] for w in range(width)]
        self.next_chest = 3
        self.next_zone = 8
        self.current_move = True
        self.last_move = 0
        self.time = {"white": 600,
                     "black": 600}

    def square(self, coords: tuple) -> Square:
        """
        Get a square from coords
        :param coords: tuple of coordinates of a square (x, y)
        :return: Square on the board at (x, y)
        """
        return self.board[coords[0]][coords[1]]

    def get(self) -> dict:
        """
        Get JSON-like representation of the game
        :return: dict containing all the information
        """
        board = []
        for x, line in enumerate(self.board):
            for y, square in enumerate(line):
                piece = square.piece.get() if square.piece else None
                if piece or square.zone:
                    board.append({"x": x,
                                  "y": y,
                                  "piece": piece,
                                  "zone": square.zone
                                  })
        return {
            "board": board,
            "next_zone": self.next_zone,
            "next_chest": self.next_chest,
            "current_move": "white" if self.current_move else "black",
            "time": self.get_time()
        }

    def get_time(self):
        if self.current_move:
            result = self.time
            pass

    def summon(self, object_id: str, coords: list, color: bool) -> None:
        """
        Summon an object (piece) from its ID on the board
        :param object_id: piece ID
        :param coords: list of coordinates [x, y] to place
        :param color: color of the piece
        :return: None
        """
        piece = Piece.generate(self.net.piece_types[object_id], color)
        piece.place(self, coords)

    def kill(self, coords: list) -> None:
        """
        Kill a piece on the board
        :param coords: coordinates of the piece
        :return: None
        """
        self.board[coords[0]][coords[1]].piece = None

    def move(self, from_coords: tuple, to_coords: tuple) -> bool:
        """
        Make a move from 'from_coords' to 'to_coords'
        :param from_coords: position to move from (x, y)
        :param to_coords: position to move to (x, y)
        :return: True if the move is correct and has been submitted, otherwise False
        """
        piece = self.square(from_coords).piece
        to_piece = self.square(to_coords).piece

        if piece and self.current_move == piece.color and to_coords in self.get_moves(piece):
            if to_piece and to_piece.color != piece.color:
                if piece % to_piece:
                    # TODO: add logging and attack effects
                    self.board[from_coords[0]][from_coords[1]].piece = None
                    piece.place(self, to_coords)
            else:
                self.board[from_coords[0]][from_coords[1]].piece = None
                piece.place(self, to_coords)
            return True
        else:
            return False

    def switch(self) -> None:
        """
        Switch the turn
        """
        self.current_move = not self.current_move
        self.last_move = time()

    def check_move(self, coords: list) -> bool:
        """
        Check if move is out of bounds
        :param coords: list of coordinates [x,y] to check
        :return: True if the move is possible
        """
        if coords[1] < 0 or coords[1] > (self.height - 1) or coords[0] < 0 or coords[0] > (self.width - 1):
            return False
        else:
            return True

    def get_moves(self, piece) -> list:
        """
        :param piece: Piece to get moves of
        :return: list of available moves
        """
        legal_moves = []
        orthogonal = ((-1, 0), (0, -1), (0, 1), (1, 0))
        diagonal = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        directions = ()
        if piece.diagonal:
            directions += diagonal
        if piece.orthogonal:
            directions += orthogonal

        for x, y in directions:
            collision = False
            for step in range(1, piece.distance + 1):
                if collision:
                    break
                destination_x, destination_y = piece.coords[0] + step * x, piece.coords[1] + step * y
                if destination_x < self.width and destination_y < self.height:
                    if not self.board[destination_x][destination_y].piece:
                        legal_moves.append([destination_x, destination_y])
                    elif self.board[destination_x][destination_y].piece.color == piece.color:
                        collision = True
                    else:
                        legal_moves.append([destination_x, destination_y])
                        collision = True

        if piece.moves:
            for x, y in piece.moves:
                if self.board[x][y].piece:
                    if not self.board[x][y].piece.color == piece.color:
                        legal_moves.append([x, y])
                else:
                    legal_moves.append([x, y])

        legal_moves = [move for move in legal_moves if self.check_move(move)]
        return legal_moves


class Network:
    """
    Object containing all other objects for backups and frontend connection
    """
    def __init__(self):
        self.waiting_room = []
        self.games = {}
        self.piece_types = {}
        self.item_types = {}

    def join(self, code: int) -> str:
        """
        Create a new game if doesn't exist, otherwise start the existing one
        :param code: Code of the particular game
        :return: 'started' if the game has been started, 'occupied' if it's unavailable, 'created' if it's just been created
        """
        if code in self.waiting_room:
            self.waiting_room.remove(code)
            self.games[code] = Game(self)
            return 'started'
        elif not code in self.games:
            self.waiting_room.append(code)
            return 'created'
        else:
            return 'occupied'

    def status(self, code: int) -> int:
        if code in self.waiting_room:
            return 1
        elif not code in self.games:
            return 0
        else:
            return 2

    def piece(self, piece_id: str, color: bool) -> Piece or None:
        """
        Get a Piece object from its ID
        :param piece_id: str containing piece ID
        :param color: color of the piece
        :return: Piece object or None if not found
        """
        if piece_id in self.piece_types:
            piece = Piece.generate(self.piece_types[piece_id], color)
            return piece
        else:
            return None

    def load_addon(self, name: str) -> bool:
        """
        Load an addon from files
        :param name: name of addon
        :return: True if the addon is loaded, False if broken or not found
        """
        try:
            pieces = yaml.load(open(f'{name}/pieces.yml'), yaml.CLoader)
            self.piece_types.update(pieces)
            return True
        except IOError or FileNotFoundError or yaml.YAMLError:
            return False
