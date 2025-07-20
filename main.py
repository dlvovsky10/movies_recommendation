from Game import Game
from Handlers import CLIIOHandler

def main():
    game = Game(CLIIOHandler())
    game.show_main_menu()


if __name__ == "__main__":
    main()
