__author__ = 'Babylon Horuv'

import os
import random
import pygame

SHIP_CAPACITY = 100

class Card :
    "A generic card, without much detail"
    cost_or_frees = ["Land, God, Afterlife or Event", "Miracle, Building or Mortal"]
    card_types = ["Land", "Afterlife", "God", "Mortal", "Building", "Miracle"]

    def __init__(self, name = '', cost_or_free = 0, card_type = 0):
        self.name = name
        self.cost_or_free = cost_or_free
        self.card_type = card_type

    def __str__(self):
        return (self.name + " is a " + self.card_types[self.card_type])

class Land (Card) :

    "A land card which makes up the playing field"
    types = ["basic", "mountain", "water", "special"]
    specifics = ["plains", "desert", "swamp", "forest", "tundra", "mountain", "storm", "water", "special"]

    def __init__(self, name = '', type = 0, specific = 0, birth_mod = 1.0, death_mod = 1, text = ''):
        self.name = name
        self.type = type
        self.specific = specific
        self.birth_mod = birth_mod
        self.death_mod = death_mod
        self.text = text
        Card.__init__(self, name, 0, 0)

    def __str__(self):
        return (self.name + " is a region of " + self.specifics[self.specific] + " which is a " + self.types[self.type] + " land.\n\n" + self.text)

class Afterlife (Card) :

    "A storage place for souls"

    def __init__(self, gods, name = '', text = ''):
        self.name = name
        self.gods = gods
        self.souls = 0
        self.text = text
        Card.__init__(self, name, 0, 1)


    def __str__(self):
        return (self.name + " is an afterlife accessible to " + " ".join(self.gods) + " and contains " + str(self.souls) + " souls.\n\n" + self.text)

class God (Card) :

    "The key to the game, a deity who amasses worship and directs the souls of the faithful to their afterlives"

    def __init__(self, game, afterlives, name = '', text = ''):
        self.game = game
        self.name = name
        self.afterlives = afterlives
        self.controller = 0
        self.mana = 0
        self.souls = 0
        self.text = text
        Card.__init__(self, name, 0, 2)

    def __str__(self):
        return ( self.name + " is a deity controlled by " + self.game.players[self.controller] + " with " + str(self.mana) + " worshippers and access to " + str(self.souls) + " souls \n\n" + self.text)

    def assign_to_zone(self):
        for god_zone in self.game.god_zones:
            if god_zone.controller == self.controller:
                god_zone.cards_free.append(self)
            else:
                god_zone.remove(self)

    def check_control(self):
        player_mana = {}
        for player in range(len(self.game.players)):
            player_mana[player] = 0
        for player in range(len(self.game.players)):
            for space in self.game.board :
                for mortal in space.mortals:
                    if mortal.controller == player and mortal.worships == self.game.gods.index(self):
                        player_mana[player] += mortal.number
                    else :
                        continue
        controller = self.controller
        total_mana=0
        for key in player_mana:
            total_mana += player_mana[key]
            if player_mana[controller] < player_mana[key]:
                controller = key
            else:
                continue
        if total_mana == 0:
            controller = 0
        self.controller = controller

    def refresh_afterlives(self):
        self.afterlives = []
        for afterlife in self.game.afterlifes:
            if self.name in afterlife.gods:
                self.afterlives.append(afterlife)
            else:
                continue

    def check_souls(self):
        self.souls = 0
        for afterlife in self.afterlives:
            self.souls += afterlife.souls



class Mortals (Card) :
    "Fragile and short lived, they power the gods with mana, and souls when they die, and their worship determines control"

    types = ["basic", "special" , "priest 1" , "priest 2", "priest 3", "priest 4", "priest 5", "soldier 1", "soldier 2", "soldier 3", "horse 1", 'horse 2', "horse 3"]
    specifics = ["peasants", "workmen", "monks", "militia", "messiah", "vampire", "prostitute", "jotuns", "assassin", "horses", "oxen", "wolves", "sailors", "crusaders", "Balder's troops", "plague carrier", 'town priest', 'theologian', "reformer", "high priest", "psychopomp", "missionary", "bishop", "inquisitor", "arch bishop", "hierophant", "pope", "dalai lama", "infantry", "sappers", "pike", "catapults", "elite infantry", "mountaineers", "archers", "general", "horsemen", "camels", "cavalry", "horse archers", "knights"]
    def __init__(self, game, birth_rate, death_rate, name = '', type = 0, specific = 0, number = 10, mana_cost = 0, soul_cost = 0, offense = 0, defense = 0, movement = 0, sterile = False, text = ''):
        self.space = self.game.nowhere
        self.game = game
        self.name = name
        self.type = type
        self.specific = specific
        self.number = number
        self.mana_cost = mana_cost
        self.soul_cost = soul_cost
        self.offense = offense
        self.defense = defense
        self.movement = movement
        self.sterile = sterile
        self.birth_rate = birth_rate
        self.death_rate = death_rate
        self.worships = 0
        self.controller = 0
        self.reformation = 0
        self.text = text
        Card.__init__(self, name, 1, 3)

    def __str__(self):
        return (self.name + " is a group of " + str(self.number) + " " + self.specifics[self.specific] + " which are mortals of the type " + self.types[self.type] + " they cost " + str(self.mana_cost) + " mana and " + str(self.soul_cost) + " souls to bring in.  Their offense/defense is " + str(self.offense) + "/" + str(self.defense) + " their movement is " + str(self.movement) + " sterile status is " + str(self.sterile) + " possible birth rate/death rate numbers are " + str(self.birth_rate) + "/" + str(self.death_rate) + " they worship " + self.game.gods[self.worships].name + " and their reformation status is " + str(self.reformation) + ".  They are controlled by " + self.game.players[self.controller] + "\n\n" + self.text)

class Building (Card) :

    "Buildings, either divinely erected or built by workmen"

    specifics = ["road", "temple", "wall", "siege tower", "stables", "barracks", "ship", "castle", "megalith", "sunday school", "docks"]

    def __init__(self, name = '', specific = 0, mana_cost = 0, soul_cost = 0, workers = 0, oxen = 0, text = ''):
        self.name = name
        self.specific = specific
        self.mana_cost = mana_cost
        self.soul_cost = soul_cost
        self.workers = workers
        self.oxen = oxen
        self.text = text
        Card.__init__(self, name, 1, 4)

    def __str__(self):
        return (self.name + " is a " + self.specifics[self.specific] + " it costs " + str(self.mana_cost) + " mana and " + str(self.soul_cost) + " souls to play as a card.  This type of building can be built by " + str(self.workers) + " workers and moved by " + str(self.oxen) + " oxen.\n\n" + self.text)

class Miracle (Card) :

    "a spell played to have an instant effect"

    specifics = ["immaculate conception", "conversion", "reformation", "crusade", "flood", "drought", "move mountains", "part sea", "smite", "transportation", "salvation", "divine orgy", "sacrifice", "solstice", "divine inspiration", "omniscience", "raise dead", "plague", "war cry", "divine reconstruction", "divine destruction", "investiture", "storm", "calm storm", "volcano", "irrigation", "blizzard", "thaw"]

    def __init__(self, name = '', specific = 0, mana_cost = 0, soul_cost = 0, mana_variable = False, soul_variable = False, text = '' ):
        self.name = name
        self.specific = specific
        self.mana_cost = mana_cost
        self.soul_cost = soul_cost
        self.mana_variable = mana_variable
        self.soul_variable = soul_variable
        self.text = text
        Card.__init__(self, name, 1, 5)

    def __str__(self):
        if self.mana_variable :
            if self.soul_variable :
                return (self.specifics[self.specific] + " is a miracle, it costs " + str(self.mana_cost) + "X mana and " + str(self.soul_cost) + "X souls.\n\n" + self.text)
            else :
                return (self.specifics[self.specific] + " is a miracle, it costs " + str(self.mana_cost) + "X mana and " + str(self.soul_cost) + " souls.\n\n" + self.text)
        else :
            return (self.specifics[self.specific] + " is a miracle, it costs " + str(self.mana_cost) + " mana and " + str(self.soul_cost) + " souls.\n\n" + self.text)

class Deck :

    "A deck of cards"

    def __init__(self, game, filename = "default.txt"):
        self.game = game
        self.cards_free = []
        self.cards_cost = []
        line_num = 0
        # read the deck from a file
        with open (filename, 'r') as file :
            self.cards_list = file.readlines()
        for card in self.cards_list :
            line_num += 1 #for tracking syntax errors
#encode a land card
            if card[0] == "0":
                name_end = card.find("~")
                card_name = card[1 : name_end]
                card_type = int(card[name_end + 1])
                card_spec = int(card[name_end + 2])
                card_birth = float(card[name_end + 3 : name_end+6])
                card_death = int(card[name_end + 6])
                card_text = card[(name_end+7) : len(card)]
                is_card = Land(card_name, card_type, card_spec, card_birth, card_death, card_text)
                self.cards_free.append(is_card)
# encode an afterlife
            elif card[0] == "1" :
                name_end = card.find("~")
                card_name = card[1 : name_end]
                god_end = card.find("^")
                god_string = card[name_end + 1 : god_end]
                gods = god_string.split()
                card_text = card[god_end + 1 : len(card)]
                is_card = Afterlife(gods, card_name, card_text)
                self.cards_free.append(is_card)
# encode a god
            elif card[0] == "2" :
                name_end = card.find("~")
                card_name = card[1 : name_end]
                life_end = card.find("^")
                life_string = card[name_end + 1 : life_end]
                afterlives = life_string.split()
                card_text = card[life_end + 1 : len(card)]
                is_card = God(self.game, afterlives, card_name, card_text)
                self.cards_free.append(is_card)
#encode a mortal
            elif card[0] == "3" :
                name_end = card.find("~")
                card_name = card[1 : name_end]
                card_type = int(card[name_end + 1 : name_end + 3])
                card_spec = int(card[name_end + 3 : name_end + 5])
                card_num = int(card[name_end + 5 : name_end + 7])
                card_mana = int(card[name_end + 7 : name_end + 9])
                card_souls = int(card[name_end + 9 : name_end + 11])
                offense = int(card[name_end + 11])
                defense = int(card[name_end + 12])
                move = int(card[name_end + 13])
                sterile_num = card[name_end + 14]
                birth_end = card.find("^")
                birth_string = card[name_end + 15 : birth_end]
                death_end = card.find("^", birth_end + 1, len(card))
                death_string = card[birth_end + 1 : death_end]
                card_text = card[death_end + 1 : len(card)]
                if sterile_num == '1' :
                    sterile = True
                else :
                    sterile = False
                birth_list = birth_string.split()
                death_list = death_string.split()
                birth = []
                death = []
                for num in birth_list :
                    birth.append(int(num))
                for num in death_list :
                    death.append(int(num))
                is_card = Mortals(self.game, birth, death, card_name, card_type, card_spec, card_num, card_mana, card_souls, offense, defense, move, sterile, card_text)
                self.cards_cost.append(is_card)
#encode a building
            elif card[0] == "4" :
                name_end = card.find("~")
                card_name = card[1 : name_end]
                card_spec = int(card[name_end + 1 : name_end + 3])
                card_mana = int(card[name_end + 3 : name_end + 5])
                card_souls = int(card[name_end + 5 : name_end + 7])
                card_workers = int(card[name_end + 7 : name_end + 9])
                card_oxen = int(card[name_end + 9 : name_end + 11])
                card_text = card[name_end + 11 : len(card)]
                is_card = Building(card_name, card_spec, card_mana, card_souls, card_workers, card_oxen, card_text)
                self.cards_cost.append(is_card)
#encode a miracle
            elif card[0] == "5" :
                name_end = card.find("~")
                card_name = card[1 : name_end]
                card_spec = int(card[name_end + 1: name_end + 3])
                card_mana = int(card[name_end + 3 : name_end + 6])
                card_souls = int(card[name_end + 6 : name_end + 8])
                mana_num = card[name_end + 8]
                soul_num = card[name_end + 9]
                card_text = card [name_end + 10 : len(card)]
                if mana_num == "1" :
                    mana_variable = True
                else :
                    mana_variable = False
                if soul_num == "1" :
                    soul_variable = True
                else :
                    soul_variable = False
                is_card = Miracle(card_name, card_spec, card_mana, card_souls, mana_variable, soul_variable, card_text)
                self.cards_cost.append(is_card)
#throw an error if there is a formatting issue
            else :
                print ("Invalid formatting at line " + str(line_num))

    def __str__(self):
        s = ''
        free = ''
        costs = ''
        for i in range (len(self.cards_free)) :
            free = free + str(self.cards_free[i]) + "\n"
        for i in range (len(self.cards_cost)) :
            costs = costs + str(self.cards_cost[i]) + "\n"
        s = "Free Cards\n" + free + "cost cards\n" + costs
        return s

    def shuffle_free(self):
        num_cards = len(self.cards_free)
        for i in range(num_cards):
            j = random.randrange(i, num_cards)
            self.cards_free[i], self.cards_free[j] = self.cards_free[j], self.cards_free[i]

    def shuffle_cost(self):
        num_cards = len(self.cards_cost)
        for i in range(num_cards):
            j = random.randrange(i, num_cards)
            self.cards_cost[i], self.cards_cost[j] = self.cards_cost[j], self.cards_cost[i]

    def remove(self, card):
        if card in self.cards_free :
            self.cards_free.remove(card)
            return True
        elif card in self.cards_cost :
            self.cards_cost.remove(card)
            return True
        else :
            return False

    def pop_free(self):
        return self.cards_free.pop()

    def pop_cost(self):
        return self.cards_cost.pop()

    def is_empty_free(self):
        return (len(self.cards_free) == 0)

    def is_empty_cost(self):
        return (len(self.cards_cost) == 0)

    def deal_free(self, hands, num_cards = 1):
        num_hands = len(hands)
        for i in range (num_cards):
            if self.is_empty_free():
                break
            card = self.pop_free()
            hand = hands[i % num_hands]
            hand.add(card)

    def deal_cost(self, hands, num_cards = 1):
        num_hands = len(hands)
        for i in range(num_cards):
            if self.is_empty_cost():
                break
            card = self.pop_cost()
            hand = hands[i % num_hands]
            hand.add(card)

    def find_all_gods(self):
        all_gods = []
        for card in self.cards_free:
            if card.card_type == 2 :
                all_gods.append(card.name)
            else:
                continue
        return all_gods


class Hand(Deck):
    "A hand of cards, owned by a player"

    def __init__(self, game, controller = 0):
        self.cards_free = []
        self.cards_cost = []
        self.controller = controller
        self.game = game

    def add(self, card):
        if card.cost_or_free == 0 :
            self.cards_free.append(card)
        elif card.cost_or_free == 1:
            self.cards_cost.append(card)
        else:
            print ("Invalid Card")

    def __str__(self):
        s = "Hand " + self.game.players[self.controller]
        if self.is_empty_cost() and self.is_empty_free():
            s = s + " is empty\n"
        else:
            s = s + " contains\n"
        return s + Deck.__str__(self)

    def play_land (self, card, space):
        if space.has_land == True:
            return ("That space already has a land")
        else:
            self.remove(card)
            space.add_land(card)

    def play_afterlife(self, card, zone):
        if card in zone :
            print ("That afterlife is already in play.")
            return False
        else :
            self.remove(card)
            zone.add(card)

    def play_god(self, card):
        if card in self.game.gods :
            print ("That God is already in play")
            return False
        else :
            self.remove(card)
            self.game.god_zones[0].add(card)
            card.controller = 0
            self.game.gods.append(card)

    def play_mortal(self, card, space, god, afterlife_souls):
        god.check_souls()
        if god.mana < card.mana_cost or god.souls < card.soul_cost :
            return ("You don't have enough mana or souls to play that.")
        elif space.can_play_mortals():
            god.mana -= card.mana_cost
            for afterlife in afterlife_souls:
                afterlife.souls -= afterlife_souls[afterlife]
            self.remove(card)
            space.mortals.append(card)
        else:
            return ("You cannot play mortals in that space.")

    def play_building(self, card, space, god, afterlife_souls):
        god.check_souls()
        if god.mana < card.mana_cost or god.souls < card.soul_cost :
            return ("You don't have enough mana or souls to play that.")
        else:
            god.mana -= card.mana_cost
            for afterlife in afterlife_souls:
                afterlife.souls -= afterlife_souls[afterlife]
            self.remove(card)
            space.buildings.append(card)

class God_Zone(Hand) :
    "Where the player keeps gods in play"
    def __init__(self, game, controller = 0):
        Hand.__init__(self, game, controller)
        self.souls = 0

    def allocate_souls(self, allocation):
        for afterlife in allocation:
            afterlife.souls += allocation[afterlife]
            self.souls -= allocation[afterlife]

class Afterlife_Zone(Hand) :
    "Where afterlives are kept"
    def __init__(self, game):
        Hand.__init__(self, game, 0)
        all_gods = self.game.deck.find_all_gods()
        limbo = Afterlife(all_gods, "Limbo", "A formless place, accessible to all gods")
        self.cards_free.append(limbo)

class Discard_Pile(Hand):
    "The Discard Pile"
    pass

class Board_Space :
    "A space on the board, it may have one land card and any number of mortals and buildings"
    lands = ["plains", "desert", "swamp", "forest", "tundra", "mountain", "storm", "water", "special"]
    def __init__(self, game):
        self.game = game
        empty = Land("empty")
        self.land = empty
        self.has_land = False
        self.mortals = []
        self.buildings = []
        self.mana = {}
        self.gods = []
        self.solstice = 1
        self.orgy = 1

    def __str__(self):
        mortals_string = ''
        for group in self.mortals:
            mortals_string += str(group)
        if self.has_land :
            return ("This space has a " + str(self.land) +" in it and " + str(len(self.mortals)) +" groups of mortals, "+ mortals_string +" worth " +str(self.mana) +" mana and "+str(len(self.buildings))+" buildings "+str(self.buildings))
        else:
            return ("This space has no land in it and " + str(len(self.mortals)) +" groups of mortals, "+ mortals_string+" and "+str(len(self.buildings))+" buildings "+str(self.buildings))

    def get_gods(self):
        self.gods = []
        for group in self.mortals:
            god = self.game.gods[group.worships]
            self.gods.append(god)

    def can_play_mortals(self):
        if self.land.type == 1 :
            return False
        elif self.land.type == 2:
            for building in self.buildings:
                if building.specific == 6:
                    total = 0
                    for mortal in self.mortals:
                        total += mortal.number
                    if total > SHIP_CAPACITY :
                        return False
                    else:
                        return True
        else:
            return True

    def priest_bonus(self, god):
        for group in self.mortals:
            if group.specific == 19 and group.worships == god:
                return 2.0
            elif group.specific == 16 and group.worships == god:
                return 1.5
            else:
                continue
        return 1.0

    def has_psychopomp(self):
        random.shuffle(self.mortals)
        for group in self.mortals:
            if group.specific == 20:
                return group.controller
            else:
                continue
        return False

    def count_mana (self):
        god_mana = {}
       # self.get_gods() #might not need this
        for god in self.game.gods:
            god_mana[god] = 0
        for group in self.mortals:
            if group.specific == 2:
                god_mana[self.game.gods[group.worships]] += group.number*2
            else:
                god_mana[self.game.gods[group.worships]] += group.number
        for god in self.gods:
            god_mana[god] = int(god_mana[god] * self.priest_bonus(self.game.gods.index(god))*self.solstice)
        self.mana = god_mana

    def breed(self):
        for group in self.mortals:
            birth_roll = random.choice(group.birth_rate)
            if group.number < 4:  #this is for game balance
                break
            elif group.number < 6 :
                babies = int((birth_roll/2)*self.land.birth_mod*self.orgy)
            else:
                multiple = round(group.number, -1)/10
                if multiple > 3 :
                    multiple = 3
                babies = int(multiple*birth_roll*self.land.birth_mod*self.orgy)
            group.number = group.number + babies

    def death(self):
        for group in self.mortals:
            death_roll = random.choice(group.death_rate)
            if group.number < 6 :
                dead = int((death_roll/2)*self.land.death_mod)
            else:
                multiple = round(group.number, -1)/10
                dead = int(multiple*death_roll*self.land.death_mod)
            if dead > group.number:
                dead = group.number
            else:
                pass
            if not self.has_psychopomp():
                for god_zone in self.game.god_zones :
                    if group.controller == god_zone.controller:
                        god_zone.souls += dead
                    else:
                        continue
            else:
                for god_zone in self.game.god_zones:
                    if self.has_psychopomp() == god_zone.controller:
                        god_zone.souls += dead
                    else:
                        continue
            group.number -= dead
            self.clean_dead()

    def change_mortal(self, original, new):
        original.number -= new.number
        self.mortals.append(new)
        self.clean_dead()

    def join_mortals(self, first, second):
        if (first.specific == second.specific) and  (first.worships == second.worships) and (first.controller == second.controller) and (first.reformation == second.reformation):
            first.number += second.number
            second.number = 0
            self.clean_dead()
        else:
            return ("these are not the same kind of mortal")


    def clean_dead(self):
        for group in self.mortals:
            if group.number < 1:
                self.game.discard.add(group)
            else:
                continue
        self.mortals[:] = [group for group in self.mortals if group.number >= 1 ]

    def add_land(self, land):
        if self.has_land :
            return False
        else :
            self.land = land
            self.has_land = True

    def add_mortal(self, mortal):
        self.mortals.append(mortal)

    def add_building(self, building):
        self.buildings.append(building)

    def build_building(self, building, player):
        workmen_total = 0
        for group in self.mortals:
            if group.controller == player and group.specific == 1 :
                workmen_total += group.number
        if workmen_total >= building.workers :
            self.buildings.append(building)

    def fight (self, attack_group, defend_religion):
        if attack_group.worships == defend_religion[0] and attack_group.reformation == defend_religion[1]:
            return "Cannot attack mortals of the same religion"
        attack_offense = attack_group.offense * attack_group.number
        attack_defense = attack_group.defense * attack_group.number
        defend_offense = 0
        defend_defense = 0
        for group in self.mortals :
            if group.worships == defend_religion[0] and group.reformation == defend_religion[1]:
                defend_offense += group.offense * group.number
                defend_defense += group.defense * group.number
        defend_killed = attack_offense - defend_defense
        attack_killed = defend_offense - attack_defense
        attack_dead = int(attack_killed/attack_group.defense)
        if not self.has_psychopomp():
            for god_zone in self.game.god_zones :
                    if attack_group.controller == god_zone.controller:
                        god_zone.souls += attack_dead
                    else:
                        continue
            else:
                for god_zone in self.game.god_zones:
                    if self.has_psychopomp() == god_zone.controller:
                        god_zone.souls += attack_dead
                    else:
                        continue
            attack_group.number -= attack_dead
            self.pick_kill(defend_religion, defend_killed)
            self.clean_dead()



class Board(list) :
    "The board, made up of all spaces."
    def __init__(self, game, players):
        super(Board, self).__init__()
        self.cols = players + 1
        self.game = game
        self.spaces = []
        self.mana = {}
        for i in range (players+1):
            for j in range (players+1):
                space = Board_Space(self.game)
                self.append(space)

    def __getitem__(self, coord):
        if coord[0] < self.cols :
            return list.__getitem__(self, coord[0] + coord[1] * self.cols)
        else:
            return ("index out of bounds")

    def __setitem__(self, coord, space):
        if coord[0] < self.cols :
            return list.__setitem__(self, coord[0] + coord[1] * self.cols, space)
        else:
            return("Index out of bounds")

    def __delitem__(self, coord):
        if coord[0] < self.cols :
            return list.__delitem__(self, coord[0] + coord[1] * self.cols)
        else:
            return ("Index out of bounds")

    def index(self, space):
        list_index = list.index(self, space)
        x = list_index % self.cols
        y = int((list_index - x)/self.cols)
        result = [x,y]
        return result

    def add_mana_list(self, mana_list):
        result = {}
        for god in self.game.gods:  #this is a list of all the gods in play
            result[god] = 0
        for space in mana_list:
            for key in space:
              result[key] += space[key]
        return result


    def count_mana(self):
        space_mana_list = []
        for space in self:
            space.count_mana()
            space_mana_list.append(space.mana)
        return self.add_mana_list(space_mana_list)

    def refresh_mana(self):
        mana_list = self.count_mana()
        for god in mana_list:
            god.mana = mana_list[god]


    def neighbors(self, id):
        neighbor_list = []
        for i in range (-1,1):
            if i +id[0] < 0 : continue
            elif i + id[0] > self.cols : continue
            for j in range (-1,1):
                if (j + id[1]) < 0 : continue
                elif j + id[1] > self.cols : continue
                elif i == 0 and j == 0 : continue
                else :
                    neighbor_list.append(self.__getitem__([id[0] + j, id[1] + i]))
        return neighbor_list


    def move_cost(self, start, end, group):  #needs work
        total = 0
        for i in range (-1, 1) :
            for j in range(-1,1):
                if (self.index(end)[0] == self.index(start)[0] + j) and (self.index(end)[1] == self.index(start) + i):
                    return 1
        if group.specific == 7 or group.specific == 33:
            for i in range (-1,1):
                for j in range (-1,1):
                    if self[(start[0]+j), start[1]+i].type == 1:
                        continue
                    else:




class Card_Game :
    def __init__(self, players):
        self.nobody = God(self, [], "Nobody (The dirty Atheists)", "this is not really a god")
        self.gods = [self.nobody]
        self.nowhere = Board_Space(self)
        self.players = ["Nobody"]
        player_num = 0
        self.god_zones = []
        self.hands = []
        for player in players:
            self.players.append(player)
        for player in self.players :
            god_zone = God_Zone(self, player_num)
            hand = Hand(self, player_num)
            self.god_zones.append(god_zone)
            self.hands.append(hand)
            player_num += 1
        self.board = Board(self, player_num)
        self.deck = Deck(self)
        self.deck.shuffle_cost()
        self.deck.shuffle_free()
        self.afterlives = Afterlife_Zone(self)
        self.discard = Discard_Pile(self)
        self.deck.deal_cost(self.hands[1:], 7)

    def choose_god(self, god, player):
        self.deck.remove(god)
        for god_zone in self.god_zones:
            if god_zone.controller == self.players.index(player):
                god_zone.add(god)
                god.controller = self.players.index(player)
            else:
                continue
        self.gods.append(god)

    def choose_afterlife(self, afterlife):
        self.deck.remove(afterlife)
        self.afterlives.add(afterlife)

    def choose_basic_mortal(self, player, group, space, god):
        self.deck.remove(group)
        group.controller = self.players.index(player)
        group.worships = self.gods.index(god)
        space.mortals.append(group)



goo = Card_Game(["Bob", "Joe", "Nancy"])

for hand in goo.hands:
    print (hand)
