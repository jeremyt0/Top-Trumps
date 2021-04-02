
from objects.toptrump import Game
from objects.creator import DeckCreator
import json, os


def deck_creator():
    creator = DeckCreator()
    creator.start()

def top_trumps():
    deck_data = None
    deck_path = os.path.join(os.getcwd(),"src", "decks")  # Directory of decks: containing jsons

    # Setting up game
    game = Game()

    setup = game.setup(decks_path=deck_path)
    if setup:
        game.start()
    else:
        print("Cannot load deck.")
        print("Taking you to Deck Creator!")
        deck_creator()

    # Game finished.


def main():
    print("Start of program")

    main_menu_string = '''
    [0] Deck Creator 
    [1] Top Trumps
    '''
    print(main_menu_string)
    choice = input("Select: ")

    if choice == "0":
        deck_creator()
    elif choice == "1":
        top_trumps()

    print("End of program")

if __name__ == "__main__":
    main()