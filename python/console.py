from models import *


def execute(game: Game, query):
    args = query.split()
    if args[0] == 'summon':
        color = True if args[4].lower() == 'white' else False
        game.summon(args[1], [int(args[2]), int(args[3])], color)
    elif args[0] == 'kill':
        game.kill([int(args[1]), int(args[2])])
