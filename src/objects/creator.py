import json, os

class DeckCreator(object):
    
    def __init__(self):
        super().__init__()

        self.edition = None
        self.date = None
        self.deck = []
        self.stats = []
        self.output_filepath = None


    def set_edition(self):
        name = input("Name of edition: ")
        self.edition = name.capitalize()

    def set_date(self):
        self.date = "2021"

    def input_stat_names(self):
        s = []
        try:
            print("_STATS_")
            for n in range(1,6):
                stat_name = input(f"Name of stat {n}: ")
                s.append(stat_name)

            self.stats = s
        except Exception as e:
            print(e)
            return False
        return True

    def set_stat_values(self):
        print("_CARD CREATOR_")
        new_card_bool = True
        # Loop creating continous cards
        while new_card_bool:
            card_filled = False
            v = {}
            card_name = None
            try:
                card_name = input("Name:")
                for s_name in self.stats:
                    stat_value = input(f"Value of {s_name}: ")
                    v[s_name] = stat_value
                    # Add optional win if high/low
                
                card_filled = True
            except Exception as e:
                print(e)
            
            # If card data successfully input
            if card_filled:
                card = Card(card_name)
                for name in v:
                    card.add_stat(name=name, value=v[name])  # Can add optional win
                self.deck.append(card)

            new_card_answer = input("Create another new card?\n")
            new_card_bool = True if new_card_answer.lower() in ["yes", "y"] else False

        print("Finished creating cards")

        
    def export(self):
        print("Exporting...")
        output_dict = {}

        output_dict['edition'] = self.edition
        output_dict['date'] = self.date
        
        output_dict['deck'] = [card.__json__() for card in self.deck]
        output_dict['deck_size'] = len(self.deck)

        try:
            with open(self.output_filepath, 'w') as outfile:
                json.dump(output_dict, outfile)
        except Exception as e:
            print(e)


    def set_output_path(self):
        output_path = os.path.join(os.getcwd(), "decks")
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        output_file = f"{self.edition}.json"
        self.output_filepath = os.path.join(output_path, output_file)


    def start(self):
        print("START")
        self.set_edition()
        self.set_date()

        self.input_stat_names()
        self.set_stat_values()

        self.set_output_path()
        self.export()
        print("FINISH")







class Card(object):
    def __init__(self, title):
        super().__init__()

        self.title = title
        self.stats = []

    def add_stat(self, name="", value="", win="high"):
        self.stats.append({"name": name, "value": value, "win": win})

    def __json__(self):
        return {"title": self.title, "stats": self.stats}
        



def main():
    print("Start")

    creator = DeckCreator()
    creator.start()


    




    print("End")

if __name__ == "__main__":
    main()