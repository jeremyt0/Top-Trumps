import os, json, random

class Game(object):

    instance = None

    @staticmethod
    def getInstance():
        if Game.instance is None:
            Game.instance = Game()
        return Game.instance

    def __init__(self):
        super(Game, self).__init__()

        self.players = []
        self.deck = None
        self.pile = None
        
        self.player_1_turn = True   # False if player 2 turn
        self.round_count = 0        # Round counter
        self.round_winner = None    # Round winner

        self.winner = None


    ## Setup functions below ##

    def add_players(self):
        # Player 1
        self.players.append(Player("YOU"))
        # Player 2
        self.players.append(Player("COMPUTER"))

    def choose_deck(self, deck_path):
        # Given 'decks' filepath, print out possible "decks" json
        decks = [file for file in os.listdir(deck_path) if file.endswith(".json")]

        if not decks:
            print("No decks found.")
            print("Please go to Top Trumps Deck Creator to create a deck to load")
            return None

        print("Loaded decks:")
        for i, d in enumerate(decks):
            print(f"[{i}]: {d}")

        deck_choice = input("\nSelect: ")
        deck_choice = int(deck_choice)  # TODO Validation

        # Get data from selected json
        deck_filepath = os.path.join(deck_path, decks[deck_choice])
        deck_data = None
        with open(deck_filepath) as json_file:
            deck_data = json.load(json_file)

        return deck_data
    

    def add_deck(self, deck_data=None):
        if deck_data:
            self.deck = Deck(deck_data)
        else:
            self.deck = Deck()  # TODO Add deck with sample data if none chosen


    def setup(self, decks_path=None):
        # Add players
        self.add_players()

        # Add deck
        selected_deck = None

        if decks_path:
            try:
                # Ask user to select a deck from given directory path containing jsons
                selected_deck = self.choose_deck(deck_path=decks_path)
                if not selected_deck:
                    return False
            except Exception as e:
                print(e)
                selected_deck = None

        # Add selected deck to self
        self.add_deck(deck_data=selected_deck)

        # Add empty pile
        self.pile = Deck()

        print("Finished setup.")
        return True

    # Game start
    def start(self):
        print("Commence.")
        active_game = True

        while active_game:
            self.play_game()
            self.update_player_scores()
            self.reset_round()

            choice = input("Play another round?\n")
            if choice.lower() not in ["y", "yes"]:
                active_game = False
                print("Final scores:")
            else:
                print("Current scores:")
            print(f'{self.players[0].name}: W:{self.players[0].wins} D:{self.players[0].draws} L:{self.players[0].losses}')
            print(f'{self.players[1].name}: W:{self.players[1].wins} D:{self.players[1].draws} L:{self.players[1].losses}')
            
        print("Finished game.")


    def play_game(self):
        print("Play.")
        active_round = True  # Keep track if game in play

        print("Shuffling deck...")
        self.deck.shuffle()

        print("Dealing cards to players")
        self.deal_to_players()

        print("All setup - Starting game.")
        while active_round:
            self.round_count += 1

            print(f"\n_Round: {self.round_count}_")
            
            # Take both players' card and add to pile
            p1_card = self.players[0].remove_last_card()
            p2_card = self.players[1].remove_last_card()
            self.add_to_pile(p1_card, p2_card)
            
            # Show player's card
            print("Your card:",p1_card.name)
            p1_card.print_stats()
            # print("AI's card:",p2_card.name)
            # p2_card.print_stats()
            
            # Select a move
            if self.player_1_turn:
                chosen_stat = input("Select a stat: ")
                while chosen_stat.lower() not in p1_card.get_list_stat_names():
                    chosen_stat = input(f"{chosen_stat} not found. \nSelect another stat: ")
            else:
                # TODO Choose highest stat method
                chosen_stat = self.players[1].choose_random_stat()
            
            # Get round winner
            self.get_winner(chosen_stat)

            if self.round_winner == "draw":
                # Cards get left in pile
                pass
            elif self.round_winner == "player1":
                loot = self.pile.deal_all()
                self.players[0].add_cards(loot)
            elif self.round_winner == "player2":
                loot = self.pile.deal_all()
                self.players[1].add_cards(loot)

            print()
            print(self.round_winner)
            print(f'Pile: {self.pile._size()} cards')

            # Update turn
            self.update_turn()
            input("Enter to continue..")

            # If there is an winner ultimate
            if not self.players_still_have_cards():
                self.winner = self.players[0].name if self.player_1_turn else self.players[1].name
                active_round = False

        print("There is a winner!", self.winner)


    ## Game functions below ##

    # Deal cards from self.deck to each player
    def deal_to_players(self):
        while self.deck._size():
            for player in self.players:
                card = self.deck.deal()
                player.add_card(card)

    # Add 2 given cards to self.pile (Deck object)
    def add_to_pile(self, card1, card2):
        self.pile.add_card(card1)
        self.pile.add_card(card2)

    # Update player turn 
    def update_turn(self):
        if self.round_winner == "player2":
            self.player_1_turn = False
        elif self.round_winner == "player1":
            self.player_1_turn = True

    # Compare current cards in self.pile to update round details
    def get_winner(self, chosen_stat):
        print("Comparing", chosen_stat)
        # Get current cards in play
        p1_card = self.pile.get_card_at(-2)  # [-2] is second last append
        p2_card = self.pile.get_card_at(-1)  # [-1] is last append
        # Get card values
        p1_val = p1_card.get_stat_value(chosen_stat)
        p2_val = p2_card.get_stat_value(chosen_stat)

        print(f"{self.players[0].name} Card - {p1_card.name} {p1_val} | {p2_val} {p2_card.name} - {self.players[1].name} Card")
        # print(f"{self.players[1].name} Card: {p2_card.name} - {chosen_stat}: {p2_val}")
        
        # Compare card values
        if p1_val > p2_val:
            self.round_winner = "player1"
            return 0
        elif p1_val < p2_val:
            self.round_winner = "player2"
            return 1
        elif p1_val == p2_val:
            self.round_winner = "draw"
            return 2

        return None

    # Return True if both players still have cards; False if 1 has none left
    def players_still_have_cards(self):
        for player in self.players:
            print(f'{player.name} cards left:{player._cards_left()}')
            if not player._cards_left():
                return False
        return True

    def update_player_scores(self):
        if self.winner == self.players[0].name:
            self.players[0].update_score("win")
            self.players[1].update_score("loss")
        elif self.winner == self.players[1].name:
            self.players[0].update_score("loss")
            self.players[1].update_score("win")


    # Reset round stats
    def reset_round(self):
        self.round_count = 0

        # Retrieve player cards and add them to pile
        for player in self.players:
            self.pile.add_cards(player.remove_all_cards())
        # Add all cards from pile back into deck
        self.deck.add_cards(self.pile.deal_all())


        



class Player(object):
    
    def __init__(self, name="Bob"):
        self.name = name
        self.cards = []
        self.wins = 0
        self.draws = 0
        self.losses = 0

    # Add given card to their self.card list
    def add_card(self, card):
        self.cards.append(card)

    # Add all cards from given list to self.card list
    def add_cards(self, cards):
        self.cards.extend(cards)

    # Remove and return their last card (first)
    def remove_last_card(self):
        return self.cards.pop(0)

    # Remove and return all their cards
    def remove_all_cards(self):
        all_cards = self.cards.copy()
        self.cards.clear()
        return all_cards

    # Choose a random card stat
    def choose_random_stat(self):
        idx = random.randint(0,4)
        stat_names = self.cards[0].get_list_stat_names()
        stat = stat_names[idx] 
        return stat

    # Method to update their score tally given a result code
    def update_score(self, result):
        if result == "win":
            self.win += 1
        elif result == "draw":
            self.draw += 1
        elif result == "loss":
            self.loss +=1

    # Returns number of cards left in their hand
    def _cards_left(self):
        return len(self.cards)


        
class Deck(object):
    
    def __init__(self, data=None):
        self.cards = []

        # Add cards if given cards data; else is empty deck
        if data:
            self.add_cards_json(data)

    # Create and add cards from given json data (dict)
    def add_cards_json(self, data):
        deck = data['deck']
        for card_obj in deck:
            new_card = Card(name=card_obj['title'], stats=card_obj['stats'])
            self.cards.append(new_card)

    # Shuffle cards in deck
    def shuffle(self):
        for i in range(len(self.cards)-1, 0, -1):
            j = random.randint(0, i+1)
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]
        return True

    # Add given card to self.cards
    def add_card(self, card):
        self.cards.append(card)

    # Add given list of cards to self.cards
    def add_cards(self, cards):
        self.cards.extend(cards)

    # Return card at given index
    def get_card_at(self, index=0):
        return self.cards[index]

    # Remove and return first card in deck
    def deal(self):
        return self.cards.pop(0)

    # Returns a list of current cards; empties existing list
    def deal_all(self):
        all_cards = self.cards.copy()
        self.cards.clear()
        return all_cards
        
    # Returns number of cards left in deck
    def _size(self):
        return len(self.cards)
    
    def _to_string(self):
        str_list = str([card.name for card in self.cards])[1:-1]

        return str_list




class Card(object):
    
    def __init__(self, name, stats=None):
        self.name = name
        self.stat_1 = {"stat 1": 0}
        self.stat_2 = {"stat 2": 0}
        self.stat_3 = {"stat 3": 0}
        self.stat_4 = {"stat 4": 0}
        self.stat_5 = {"stat 5": 0}

        # If given stats data to create a card with
        if stats:
            self.update_card(stats)

    # Update card stats with given stats data
    def update_card(self, stats):
        self.stat_1 = stats[0]
        self.stat_2 = stats[1]
        self.stat_3 = stats[2]
        self.stat_4 = stats[3]
        self.stat_5 = stats[4]

    # Get stat value of card given stat name
    def get_stat_value(self, stat_name):
        self_attributes = vars(self)
        selected_stat = None

        for attribute in self_attributes:
            if attribute == "name":
                continue  # If self.name
            if stat_name.lower() == self_attributes[attribute]['name']:
                selected_stat_value = self_attributes[attribute]['value']
                break
        # Will return value None if argument 'stat_name' cannot be found
        return selected_stat_value

    def get_list_stat_names(self):
        return [self.stat_1['name'],self.stat_2['name'], self.stat_3['name'], self.stat_4['name'], self.stat_5['name']]


    # Prints all stats in formatted string
    def print_stats(self):
        print(f"{self.stat_1['name']}: {self.stat_1['value']}")
        print(f"{self.stat_2['name']}: {self.stat_2['value']}")
        print(f"{self.stat_3['name']}: {self.stat_3['value']}")
        print(f"{self.stat_4['name']}: {self.stat_4['value']}")
        print(f"{self.stat_5['name']}: {self.stat_5['value']}")


def run_test():
    print("Start test.")

    decks_path = os.path.join(os.getcwd(),"src", "decks")
    deck_path = os.path.join(decks_path, "Sample.json")

    example_deck_data = None
    with open(deck_path) as json_file:
        example_deck_data = json.load(json_file)

    deck = Deck(data=example_deck_data)

    print(deck._to_string())

    deck.shuffle()

    print(deck._to_string())



    print("End test")


if __name__ == "__main__":
    run_test()

