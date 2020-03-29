#!/usr/bin/env python
## Attempt to make monopoly in python with optional text-to-speech, and bots

import random
import pyttsx3
import time
import os
import subprocess
import platform

##---------- FUNCTIONS ----------##
## ---> Position Funcs <--- ##

# handles rolling the dice, checking for double, and returns an array
# containing the result and whether it was a double or not.
def roll():
    d1 = random.randint(1,6)
    d2 = random.randint(1,6)
    if (d1 == d2 and player.doubles < 2):
        speak("Doubles!")
        player.doubles = player.doubles + 1
        res = [d1 + d2, 1]
        return res
    player.doubles = 0
    res = [d1 + d2,0]
    return res

# Called when the player passes Go, it gives them $200.
def passGo(player):
    speak("%s passed Go!" % (player.name))
    player.changeMoney(200)

# Allows changing the position of the player.
def changePos(player, pos, board):
    if (int(pos) < player.position):
        if (player.jail == 0):
            passGo(player)

    if player.position >= board.spaces:
        player.position = player.position - board.spaces

        if (player.jail == 0):
            passGo(player)

    if player.position < 1:
        player.position = board.spaces - player.position

    player.position = int(pos)
    player.posName = board.places[player.position][1]
    whatDo(player, board)

# Determines the position of the player based on their roll.
def detPos(player, roll, board):
    player.position = int(player.position) + int(roll)

    if player.position < 1:
        player.position = board.spaces - player.position

    if player.position >= board.spaces:
        player.position = player.position - board.spaces

        if (player.jail == 0):
            passGo(player)

    currSpace = board.places[player.position]
    player.posName = currSpace[1]
    return currSpace

## ---> Space Specific Funcs <--- ##

# Calls the relevant func based on what type of space they land on.
def whatDo(player, board):
    spot = board.places[player.position][0]
    wholeSpot = board.places[player.position]

    if (spot == "Prop" or spot == "Util" or spot == "RR"):
        if (int(player.bot) == 0):
            landOnProp(player, wholeSpot, board)
        else:
            botLandOnProp(player, wholeSpot, board)

    elif (spot == "Tax"):
        landOnTax(player, wholeSpot)

    elif (spot == "Fate"):
        landOnFate(player, board)

    elif (spot == "Crate"):
        landOnCrate(player, board)

    elif (spot == "GoToJail"):
        landOnJail(player, board)

    return

# Handles when the player lands on the Go To Jail space.
def landOnJail(player, board):
    speak("%s went to jail!" % (player.name))
    player.jail = 1
    return

# Handles when the player lands on a Community Crate space.
def landOnCrate(player, board):
    avail = []
    found = 0
    counter = 0

    for c in board.crate:
        if c[3] == 0:
            avail.append(c)
            found = 1
        counter = counter + 1

    # If all cards are used, reset the card deck.
    if found == 0:
        avail = board.crate
        for c in board.crate:
            c[3] == 1


    randNum = random.randint(0, counter - 1)
    given = avail[randNum]
    useCard(given, player, board)
    return

# Handles when the player lands on a Fate space.
def landOnFate(player, board):
    avail = []
    found = 0
    counter = 0
    for c in board.fate:
        if c[3] == 0:
            avail.append(c)
            found = 1
        counter = counter + 1

    # If all cards are used, reset the card deck.
    if found == 0:
        avail = board.fate
        for c in board.crate:
            c[3] == 1

    randNum = random.randint(0, counter - 1)
    given = avail[randNum]
    useCard(given, player, board)
    return

# Handles when the player lands on a Tax space.
def landOnTax(player, position):
    amt = position[3]
    player.money = int(player.money) - int(amt)
    speak("%s has paid $%s in tax." % (player.name, amt))
    player.taxPaid = int(amt)
    return

# Handles when the player lands on a Property space.
def landOnProp(player, position, board):
    typ = position[0]
    if (typ == "Prop"):
        typ = "property"
    elif (typ == "Util"):
        typ = "utility"
    elif (typ == "RR"):
        typ = "railroad"

    # Property not owned, but player does not have enough money for it
    if (int(position[8]) == 0):
        if (player.money < int(position[3])):
            speak("Could not afford this %s." % (typ))
            return

    # Other player owns this property
    if (int(position[8]) == 1):
        if position in player.properties:
            speak("%s owns this %s." % (player.name, typ))
            return
        else:
            payRentProp(player, position, board)
            return

    # Property is vacant and player can afford it
    print("(Color: %s, Owned of this color: %s out of %s available and %s total)"
    % (position[2], colOwned(player, position), totColOwned(position, board), position[9]))
    say("Color is %s, %s owns %s out of %s available and %s total."
    % (position[2], player.name, colOwned(player, position), totColOwned(position, board), position[9]))
    if (instructions == 1):
        say("This %s is not owned and costs $%s (you have $%s), to purchase, press 'Y'. To decline, press any other key.\n"
        % (typ, int(position[3]), player.money))
    else:
        say("It costs $%s, and you have %s." % (int(position[3]), player.money))
    choice = input("This %s is not owned and costs $%s (you have $%s), to purchase, press 'Y'. To decline, press any other key.\n"
    % (typ, int(position[3]), player.money))

    # Player chooses to purchase the property
    if (choice == "y" or choice == "Y"):
        board.places[player.position][8] = 1
        player.properties.append(position)
        player.money = player.money - int(position[3])
        speak("%s purchased %s" % (player.name, position[1]))

        if (board.places[player.position][0] == "RR"):
            player.rrs = player.rrs + 1

        if (board.places[player.position][0] == "Util"):
            player.utils = player.utils + 1
        return

    return

## ---> Other Funcs <--- ##
# Player runs out of money and is removed from game
# TODO: Force player to mortgage owned properties when out of cash
def bankrupt(player, board):
    speak("%s has gone bankrupt!" % player.name)
    for x in players:
        if x.name == player.name:
            players.remove(x)

    # Ensure that the proper order of player turns is preserved after removal
    board.counter += 1

# Returns the number of a certain Color are owned by all players based on
# the Color from the current position.
def totColOwned(position, board):
    counter = int(position[9])
    col = position[2]

    for pla in board.players:
        for prop in pla.properties:
            if prop[2] == col:
                counter = counter - 1
    return counter

# Returns the number of a certain Color are owned by THE player based on
# the Color from the current position.
def colOwned(player, position):
    counter = 0
    col = position[2]

    for prop in player.properties:
        if prop[2] == col:
            counter = counter + 1
    return counter

# Called when the player uses a card.
def useCard(given, player, board):
    typ = str(given[0])
    player.cardUsed = given
    speak("%s" % (given[2]))

    # GoTo cards will have a "U" or "R" if they move a player to the closest
    # utility or railroad respectively, or a number for a specific spot on board,
    # if "U" or "R", find the numerical position of it and set the position.
    if (typ == "GoTo"):
        if (given[1] == "U"):
            if (player.position > 28 or player.position <= 12):
                given[1] = 12
            elif (player.position > 12 or player.position <= 28):
                given[1] = 28
        if (given[1] == "R"):
            if (player.position > 35 or player.position <= 5):
                given[1] = 5
            elif (player.position > 5 or player.position <= 15):
                given[1] = 15
            elif (player.position > 15 or player.position <= 25):
                given[1] = 25
            elif (player.position > 25 or player.position <= 35):
                given[1] = 35

        changePos(player, given[1], board)

    # Handles cards that either give or take a flat value to the player without
    # affecting the other players. (Take money is done by using a negative #)
    elif (typ == "Get"):
        player.money = player.money + int(given[1])

    # Handles cards that move a player backwards a certain number of spaces
    # Could easily be used to move players forward via negative numbers
    elif (typ == "Back"):
        detPos(player, (0 - int(given[1])), board)
        whatDo(player, board)

    # Handles cards that either make the player pay all other players, or make
    # all other players pay them. Negative numbers make the player get money
    # from others, and visa versa.
    elif (typ == "Pay"):
        player.money = player.money - int(int(given[1]) * len(board.players))
        for p in board.players:
            if not (p.name == player.name):
                p.money = p.money + int(given[1])

    # Handles Get out of Jail Free cards
    elif (typ == "Card"):
        player.cards = player.cards + 1

    # Handles cars that send player straight to jail
    elif (typ == "Jail"):
        player.jail = 1

    # If a card doesn't fit the above categories, this should never happen.
    else:
        print("How did this happen?")

# Takes the appropriate amount of money from a player who lands on another player's
# property, then gives that amount to the property owner.
def payRentProp(player, position, board):
    amt = position[4]
    for p in board.players:
        if position in p.properties:

            #Handles standard properties
            #TODO: Change amount based on houses/hotel on property
            if (position[0] == "Prop"):
                player.money = int(player.money) - int(amt)
                p.money = int(p.money) + int(amt)
                speak("%s has paid %s $%s in rent." % (player.name, p.name, amt))

                # Add summaries
                player.rentPaid = int(amt)
                player.rentPaidTo = p.name
                p.rentGot = int(amt)
                p.rentGotFrom = player.name

                return

            # Handles rent for utility spaces, including if property owner owns both.
            elif (position[0] == "Util"):
                if (p.utils == 1):
                    player.money = int(player.money) - int(player.roll * 4)
                    p.money = int(p.money) + int(player.roll * 4)
                    speak("%s has paid %s $%s in rent." % (player.name, p.name,
                    player.roll * 4))

                    # Add summaries
                    player.rentPaid = int(player.roll * 4)
                    player.rentPaidTo = p.name
                    p.rentGot = int(player.roll * 4)
                    p.rentGotFrom = player.name

                    return
                if (p.utils == 2):
                    player.money = int(player.money) - int(player.roll * 10)
                    p.money = int(p.money) + int(player.roll * 10)
                    speak("%s has paid %s $%s in rent." % (player.name, p.name,
                    player.roll * 10))

                    # Add summaries
                    player.rentPaid = int(player.roll * 10)
                    player.rentPaidTo = p.name
                    p.rentGot = int(player.roll * 10)
                    p.rentGotFrom = player.name

                    return

            # Handles rent for railroad properties, including changing amount
            # based on number of RR the property owner has
            elif (position[0] == "RR"):
                amt = int(amt) * int(p.rrs)
                player.money = int(player.money) - int(amt)
                p.money = int(p.money) + int(amt)
                speak("%s has paid %s $%s in rent." % (player.name, p.name, amt))

                # Add summaries
                player.rentPaid = int(amt)
                player.rentPaidTo = p.name
                p.rentGot = int(amt)
                p.rentGotFrom = player.name

                return

#  handles a player's turn while they are in jail.
def jail(player, board):
    changePos(player, 10, board)

    # If player has been in jail for 3 or more turns, release them.
    if (player.jail >= 3):
        speak("Jail time served.")
        player.jail = 0
        turn(player, board)
        return

    # If they haven't, they can choose to roll for doubles, use GooJF Card, or Pay.
    while True:
        choice = input("Enter 'R' to roll dice, 'U' to use card, or 'P' to pay $50 fine.\n")

        # Player attempts to escape jail by rolling doubles
        if (choice == "R" or choice == "r"):
            result = roll()
            player.roll = result[0]

            # Checks for double, releases player and moves them.
            if (result[1]):
                player.jail = 0
                speak("Doubles rolled! Jail escaped!")
                pos = detPos(player,result[0],board)
                currSpace = pos[1]
                speak("%s is now on %s (%d of %d)" % (player.name, currSpace,
                player.postion, board.spaces))
                whatDo(player,board)
                return

            # Player failed to roll a double and continues their sentence
            else:
                speak("Doubles not rolled. Jail time continues.")
                player.jail = player.jail + 1
                return

        # Checks if player has a card, uses and releases them if they do.
        elif (choice == "U" or choice == "u"):
            if (player.cards > 0):
                speak("Get out of jail free card used!")
                player.cards = player.cards - 1
                player.jail = 0
                turn(player,board)
                return

            # If not, notify them and reset jail func w/o increasing jail count.
            else:
                speak("No get out of jail free cards available.")
                continue

        # Releases the player if they can afford the $50 fee.
        elif (choice == "P" or choice == "p"):
            if (player.money >= 50):
                speak("$50 fine paid!")
                player.money = player.money - 50
                player.jail = 0
                turn(player,board)
                return

            # if they attempt to pay the fee, and cannot afford it, allow them
            # to make another choice.
            else:
                speak("Not enough money for the fee!")
                continue

        else:
            speak("Please enter an R, U, or P")

# Handles the player's turn, where they can view the status, properties, and
# roll the dice.
def turn(player, board):
    if (player.bot == 1):
        time.sleep(1)
        speak("\n%s takes their turn!" % player.name)
        botTurn(player, board)
        if (player.money < 1):
            bankrupt(player, board)
        return

    doub = 0
    if (player.jail > 0):
        speak("\n%s is in jail." % (player.name))
        jail(player, board)
        return

    while True:
        speak("\nIt's %s's turn!" % (player.name))
        choice = ask("Enter 'S' to view all player statuses, 'Y' to view your own status, 'P' to view your properties, 'A.' to view every player's properties, or 'R' to roll dice.",
         "Please enter an S, P, A, or R", ["s","p","a","r","y"], True, True)

        # view status of all players, which includes money, position, and
        # overview of properties
        if choice == "s":
            for p in board.players:
                speak(p.status(board))

        # view only their own status (added mainly for when narration is on and
        # player only wants to remember what they have)
        if choice == "y":
            speak(player.status(board))

        # view only current player's own properties
        elif choice == "p":
            speak(player.viewProps())

        # view all players properties, in a more detailed fashion than status
        elif choice == "a":
            board.viewProps()

        # roll the dice!
        elif choice == "r":
            result = roll()
            player.roll = result[0]
            doub = result[1]

            # If player rolls 3 doubles, they go to jail
            if player.doubles > 2:
                speak("%s rolled 3 doubles in a row!\n")
                player.doubles = 0
                landOnJail(player, board)
                return

            pos = detPos(player,result[0],board)

            if result[0] == "8" or result[0] == "11":
                speak("%s rolled an %d!" % (player.name, result[0]))

            else:
                speak("%s rolled a %d!" % (player.name, result[0]))
            currSpace = pos[1]
            if currSpace != "Jail":
                speak("%s is now on %s (%d of %d)" % (player.name, currSpace,
                player.position, board.spaces))
            else:
                if player.jail == 0:
                    speak("%s is now on Just Visiting %s (%d of %d)" % (player.name,
                    currSpace, player.position, board.spaces))
            break

    # After moving the player based on their roll, determine what happens based
    # on the spot they landed on.
    whatDo(player,board)
    player.prevPos = player.position
    if (player.money < 1):
        bankrupt(player, board)
        return

    # If player rolled doubles, they get another turn.
    if (doub):
        turn(player,board)
    return

def generateSummary(before, after, player):
    #TODO
    x = 1

## ---> Bot Funcs <--- ##
def botTurn(player, board):
        if (player.jail > 0):
            speak("\n%s is in jail." % (player.name))
            #botJail(player, board) TODO
            return

        result = roll()
        player.roll = result[0]
        doub = result[1]
        pos = detPos(player,result[0],board)

        if result[0] == "8" or result[0] == "11":
            speak("%s rolled an %d!" % (player.name, result[0]))

        else:
            speak("%s rolled a %d!" % (player.name, result[0]))
        currSpace = pos[1]
        speak("%s is now on %s (%d of %d)" % (player.name, currSpace,
        player.position, board.spaces))

        whatDo(player,board)
        player.prevPos = player.position

        if (doub):
            turn(player,board)
        return

def botJail(player, board):
    changePos(player, 10, board)

    # If bot has been in jail for 3 or more turns, release them.
    if (player.jail >= 3):
        speak("Jail time served.")
        player.jail = 0
        turn(player, board)
        return

    if (player.cards > 0):
        speak("Get out of jail free card used!")
        player.cards = player.cards - 1
        player.jail = 0
        turn(player,board)
        return

    if (player.money > 200):
        speak("$50 fine paid!")
        player.money = player.money - 50
        player.jail = 0
        turn(player,board)
        return

    result = roll()
    player.roll = result[0]

    # Checks for double, releases bot and moves them.
    if (result[1]):
        player.jail = 0
        speak("Doubles rolled! Jail escaped!")
        pos = detPos(player,result[0],board)
        currSpace = pos[1]
        speak("%s is now on %s (%d of %d)" % (player.name, currSpace,
        player.postion, board.spaces))
        whatDo(player,board)
        return

    # Bot failed to roll a double and continues their sentence
    else:
        speak("Doubles not rolled. Jail time continues.")
        player.jail = player.jail + 1
        return


def botLandOnProp(player, position, board):
    typ = position[0]
    if (typ == "Prop"):
        typ = "property"
    elif (typ == "Util"):
        typ = "utility"
    elif (typ == "RR"):
        typ = "railroad"

    if (int(position[8]) == 0):
        if (player.money < int(position[3])):
            speak("Could not afford this %s." % (typ))
            return

    if (int(position[8]) == 1):
        if position in player.properties:
            speak("%s owns this %s." % (player.name, typ))
            return
        else:
            payRentProp(player, position, board)
            return

    if typ == "property":
        print("(Color: %s, Owned of this color: %s out of %s available and %s total)"
        % (position[2], colOwned(player, position), totColOwned(position, board), position[9]))

        say("Color is %s, %s owns %s out of %s available and %s total"
        % (position[2], player.name, colOwned(player, position),
        totColOwned(position, board), position[9]))

    else:
        print("(Type: %s, Owned of this color: %s out of %s available and %s total)"
        % (position[2], colOwned(player, position), totColOwned(position, board), position[9]))

        say("Type is %s, %s owns %s out of %s available and %s total" % (position[2], player.name,
        colOwned(player, position), totColOwned(position, board), position[9]))


    choice = botPropertyChoice(player, position, board)
    if (choice == 1):
        board.places[player.position][8] = 1
        player.properties.append(position)
        player.money = player.money - int(position[3])
        speak("%s purchased %s" % (player.name, position[1]))

        if (board.places[player.position][0] == "RR"):
            player.rrs = player.rrs + 1

        if (board.places[player.position][0] == "Util"):
            player.utils = player.utils + 1
        return
    else:
        speak("%s chose not to purchase %s" % (player.name, position[1]))

    return

def botPropertyChoice(player, position, board):
    ownSituation = {player.name:player.getProps()}
    otherSituation = {}
    for other in players:
        if other.name != player.name:
            otherSituation[other.name] = other.getProps()

    # Chance that the bot will buy a property will be decided by choosing a random
    # number between 1 and totalChance, if the number is less than chance, the
    # bot will buy the property.

    chance = 80
    totalChance = 100

    # The number of currently owned properties of the color will greatly increase
    # the bots chance to buy the property
    color = position[2]
    ownedOfColor = ownSituation[player.name][str(color)]
    if ownedOfColor > 0:
        chance + 40

    # Additionally, other players/bots owning properties of the color will increase
    # the bots chance to buy the property.
    otherOwnedOfColor = 0
    for x in otherSituation:
        otherOwnedOfColor += int(otherSituation[x][str(color)])

    chance += 20 * otherOwnedOfColor

    # If the cost of the property would leave the bot with less than half of
    # their money, it greatly reduces the chance to buy the property
    price = position[3]
    if int(price) >= (int(player.money) * 2):
        chance - 40

    decision = random.randint(1, totalChance)
    if decision <= chance:
        return 1
    else:
        return 0

## ---------- CLASSES ---------- ##

class Board:
    places = []
    players = []
    fate = []
    crate = []
    counter = 0
    def __init__(self, spaces, places, fate, crate):
        self.spaces = spaces
        self.places = places
        self.fate = fate
        self.crate = crate
        self.counter = 0

    def viewProps(self):
        for pla in self.players:
            speak(pla.viewProps())

class Player:
    def __init__(self, name, money, bot):
        self.properties = []
        self.cards = 0
        self.doubles = 0
        self.rrs = 0
        self.utils = 0
        self.position = 0
        self.posName = "Start"
        self.prevPos = 0
        self.roll = 0
        self.jail = 0
        self.name = name
        self.money = int(money)
        self.bot = bot

        self.cardUsed = ""
        self.taxPaid = 0
        self.rentPaid = 0
        self.rentPaidTo = ""
        self.rentGot = 0
        self.rentGotFrom = ""


    def changeMoney(self, amount):
        self.money = self.money + amount

    def changeProperty(self, prop, add):
        if add == 1:
            self.properties.append(prop)
        if add == 0:
            if prop in self.properties:
                self.properties.remove(prop)

    def resetSummary(self):
        self.cardUsed = ""
        self.taxPaid = 0
        self.rentPaid = 0
        self.rentPaidTo = ""
        self.rentGot = 0
        self.rentGotFrom = ""

    def status(self, board):
        phrase = ("%s: Money: $%s, Position: %s (%d of %d)" %
                (self.name, self.money, self.posName, self.position + 1, board.spaces))
        props = ", and no properties."
        counter = 0
        if (len(self.properties)):
            props = ", Properties: "
            for p in self.properties:
                if len(self.properties) > 1 and counter < len(self.properties) - 1:
                    props = props + str(p[1]) + ", "
                else:
                    props = props + str(p[1])
                counter = counter + 1
        phrase = phrase + props
        return phrase

    def vpassist(self, count, color, phrase):
        totCnt = 3
        if (color == "Brown" or color == "Blue" or color == "Util"):
            totCnt = 2
        elif (color == "RR"):
            totCnt = 4
        if(count > 0):
            phrase = phrase + ("\n%ss(%d of %s): " % (color, count, totCnt))
            counter = 1
            for p in self.properties:
                if color in p:
                    phrase = phrase + ("%s" % (p[1]))
                    if (int(p[6]) > 0):
                        phrase = phrase + (" with %d houses, " % (p[6]))
                    elif (int(p[7]) > 0):
                        phrase = phrase + (" with a hotel, ")
                    elif (count > 1 and counter < count):
                        phrase = phrase + ("%s" % (', '))
                    counter = counter + 1
        return phrase

    def viewProps(self):
        phrase = ("\n%s's properties: " % (self.name))
        brnCnt = 0
        ltbCnt = 0
        pnkCnt = 0
        orgCnt = 0
        redCnt = 0
        ylwCnt = 0
        grnCnt = 0
        bluCnt = 0
        utlCnt = 0
        rrdCnt = 0

        for p in self.properties:
            if (p[2] == "Brown"):
                brnCnt = brnCnt + 1
            elif (p[2] == "Light Blue"):
                ltbCnt = ltbCnt + 1
            elif (p[2] == "Pink"):
                pnkCnt = pnkCnt + 1
            elif (p[2] == "Orange"):
                orgCnt = orgCnt + 1
            elif (p[2] == "Red"):
                redCnt = redCnt + 1
            elif (p[2] == "Yellow"):
                ylwCnt = ylwCnt + 1
            elif (p[2] == "Green"):
                grnCnt = grnCnt + 1
            elif (p[2] == "Blue"):
                bluCnt = bluCnt + 1
            elif (p[0] == "Util"):
                utlCnt = utlCnt + 1
            elif (p[0] == "RR"):
                rrdCnt = rrdCnt + 1

        if(brnCnt > 0):
            phrase = self.vpassist(brnCnt, "Brown", phrase)
        if(ltbCnt > 0):
            phrase = self.vpassist(ltbCnt, "Light Blue", phrase)
        if(pnkCnt > 0):
            phrase = self.vpassist(pnkCnt, "Pink", phrase)
        if(orgCnt > 0):
            phrase = self.vpassist(orgCnt, "Orange", phrase)
        if(redCnt > 0):
            phrase = self.vpassist(redCnt, "Red", phrase)
        if(ylwCnt > 0):
            phrase = self.vpassist(ylwCnt, "Yellow", phrase)
        if(grnCnt > 0):
            phrase = self.vpassist(grnCnt, "Green", phrase)
        if(bluCnt > 0):
            phrase = self.vpassist(bluCnt, "Blue", phrase)
        if(utlCnt > 0):
            phrase = self.vpassist(utlCnt, "Util", phrase)
        if(rrdCnt > 0):
            phrase = self.vpassist(rrdCnt, "RR", phrase)
        if (phrase == ("\n%s's properties: " % (self.name))):
            phrase = phrase + "\nNone"
        return phrase

    def getProps(self):
        brnCnt = 0
        ltbCnt = 0
        pnkCnt = 0
        orgCnt = 0
        redCnt = 0
        ylwCnt = 0
        grnCnt = 0
        bluCnt = 0
        utlCnt = 0
        rrdCnt = 0
        for p in self.properties:
            if (p[2] == "Brown"):
                brnCnt = brnCnt + 1
            elif (p[2] == "Light Blue"):
                ltbCnt = ltbCnt + 1
            elif (p[2] == "Pink"):
                pnkCnt = pnkCnt + 1
            elif (p[2] == "Orange"):
                orgCnt = orgCnt + 1
            elif (p[2] == "Red"):
                redCnt = redCnt + 1
            elif (p[2] == "Yellow"):
                ylwCnt = ylwCnt + 1
            elif (p[2] == "Green"):
                grnCnt = grnCnt + 1
            elif (p[2] == "Blue"):
                bluCnt = bluCnt + 1
            elif (p[0] == "Util"):
                utlCnt = utlCnt + 1
            elif (p[0] == "RR"):
                rrdCnt = rrdCnt + 1
        result = {'Brown':brnCnt, 'Light Blue':ltbCnt, 'Pink':pnkCnt, 'Orange':orgCnt,
        'Red':redCnt, 'Yellow':ylwCnt, 'Green':grnCnt, 'Blue':bluCnt, 'Utility':utlCnt,
        'Railroad':rrdCnt}

        return result



## ---------- SET UP ---------- ##
##(program execution begins here)##

## read places.txt
spaces_inf = open("places.txt", "r")
sinf = spaces_inf.readlines()
spaces = []
counter = 0
for index in sinf:
    spaces.append(sinf[counter].strip().split(','))
    counter = counter + 1
spaces_inf.close()

## read fate.txt
fate_inf = open("fate.txt", "r")
finf = fate_inf.readlines()
counter = 0
for index in finf:
    finf[counter] = finf[counter].strip().split(',')
    counter = counter + 1
fate_inf.close()

## read crate.txt
crate_inf = open("crate.txt", "r")
cinf = crate_inf.readlines()
counter = 0
for index in cinf:
    cinf[counter] = cinf[counter].strip().split(',')
    counter = counter + 1
crate_inf.close()

## use board.txt to make Board instance to be used all game
gameBoard = Board(len(spaces), spaces, finf, cinf)

## read player.txt
play_inf = open("player.txt", "r")
pinf = play_inf.readlines()
counter = 0
for index in pinf:
    pinf[counter] = pinf[counter].strip()
    counter = counter + 1
play_inf.close()

ttsEnabled = 1
engine = pyttsx3.init()
secondEngine = ""
if platform.system() == "Darwin":
    engine = "Mac"
    secondEngine = pyttsx3.init()

#TTS and print the given line while waiting for it to finish
def speak(line):
    print(line)
    if ttsEnabled == 1:
        if secondEngine == "":
            engine.say(str(line))
            engine.runAndWait()
            return
        secondEngine.say(str(line))
        secondEngine.runAndWait()
        return

#TTS and print the given line without waiting
def speakFast(line):
    print(line)
    say(line)

#TTS the given line
def say(line):
    if ttsEnabled == 1:
        if engine != "Mac":
            engine.say(str(line))
            engine.runAndWait()
            return
        subprocess.Popen(["say", line])

#TTS the given line and take input, and loop until input is correct
# include is True of False if allowedInputs should be checked for inclusion (True)
# or not (False)
# inst is True or False if the ask is an instruction or not.
def ask(line, errorLine, allowedInputs, include, inst):
    asked = 0
    result = ""
    #if not(line.endswith("\n")):
    #    line = line + "\n"
    #if not(errorLine.endswith("\n")):
    #    errorLine = errorLine + "\n"

    while True:
        if asked == 0:
            print(line)
            if (not inst) or (instructions == 1):
                say(line)
            result = input()
            if inst:
                result = result.lower()
            asked = 1
        else:
            result = input("")
        if (include):
            if result in allowedInputs:
                break
            else:
                speakFast(errorLine)
                continue
        else:
            if result not in allowedInputs:
                break
            else:
                speakFast(errorLine)
                continue

    return result

## Introduce Game
speakFast("Welcome to Text-to-Monopoly, hit T to enable narration, or enter to play.")
startChoice = input()
instructions = 0
if (startChoice.lower() == "t"):
    ttsEnabled = 1
    speakFast("Would you like instructions narrated too? Press y to accept, or any other key to decline.")
    instructions = input()
    if (instructions.lower() == "y"):
        instructions = 1
else:
    ttsEnabled = 0
    instructions = 0

## create players
players = []
asked = 0
playerNum = int(ask("How many human players?", "Please enter a number between 1 and 8",
["1","2","3","4","5","6","7","8"], include=True, inst=False))

botNumList = list(map(str, range(1, 9 - int(playerNum) + 1)))
botError = "Please enter a number between 0 and %d" % (9 - int(playerNum))
botNum = int(ask("How many bots?", botError, botNumList, include=True, inst=False))


counter = 0
names = []
for x in range(playerNum):
    name = ask("What is Player %d's name?" % (counter+1), "Please choose a unique name.",
    names, include=False, inst=False)

    player = Player(name, pinf[0], 0)
    players.append(player)
    names.append(name)
    counter = counter + 1

for x in range(botNum):
    nameString = "Bot " + str(x+1)
    for y in range(playerNum):
        if players[y].name == nameString:
            nameString = "Real Bot " + str(x+1)
    bot = Player(nameString, pinf[0], 1)
    players.append(bot)
    names.append(nameString)

if (botNum > 1):
    speak("Added %d bots to the game" % botNum)
elif (botNum == 1):
    speak("Added 1 bot to the game")


gameBoard.players = players
while True:
    if (len(players) == 1):
        speak("%s is the only remaining player! Game over." % (players[0].name))
        break
    choice = gameBoard.counter % len(players)

    # Store players as "before" to generate a summary
    before = players
    turn(players[choice], gameBoard)

    # generate and speak the summaries, then reset the summary class variables
    generateSummary(before, players, players[choice])
    for p in players:
        p.resetSummary()

    gameBoard.counter += 1
