## Attempt to make monopoly?
## Explanation of places.txt:
## [Type(0),Name(1),Color(2),Cost(3),
## Rent(4),Position(5),Houses(6),Hotels(7),Owned(8),
## NumPerColor(9),Mortgaged[10],MortPrice[11],
## 1House[12], 2House[13], 3House[14], 4House[15], Hotel[16]]

import random
import pyttsx3


##---------- FUNCTIONS ----------##
## ---> Position Funcs <--- ##

#  handles rolling the dice, checking for double, and returns an array
# containing the result and whether it was a double or not.
def roll():
    #return [1, 0]
    d1 = random.randint(1,6)
    d2 = random.randint(1,6)
    #d1 = d2 = 3
    if (d1 == d2 and player.doubles < 2):
        print("Doubles!")
        #print(player.doubles)
        player.doubles = player.doubles + 1
        res = [d1 + d2, 1]
        return res
    player.doubles = 0
    res = [d1 + d2,0]
    return res

# Called when the player passes Go, it gives them $200.
def passGo(player):
    print("%s passed Go!" % (player.name))
    #player.money = player.money + 200
    changeMoney(player, 200)

# Allows changing the position of the player.
def changePos(player, pos, board):
    #print(player.status(), pos)
    if (int(pos) < player.position):
        if (player.jail == 0):
            passGo(player)

    if player.position >= 40:
        player.position = player.position - 40

        if (player.jail == 0):
            passGo(player)

    if player.position < 1:
        player.position = 40 - player.position

    player.position = int(pos)
    player.posName = board.places[player.position][1]
    whatDo(player, board)

# Determines the position of the player based on their roll.
def detPos(player, roll, board):
    #print(player.position)
    player.position = int(player.position) + int(roll)
    #print(player.position)

    if player.position < 1:
        player.position = 40 - player.position

    if player.position >= 40:
        player.position = player.position - 40

        if (player.jail == 0):
            passGo(player)

    #print(player.position)
    currSpace = board.places[player.position]
    player.posName = currSpace[1]
    return currSpace

## ---> Space Specific Funcs <--- ##

# Calls the relevant func based on what type of space they land on.
def whatDo(player, board):
    #print("whatDo: %s" % (player.name))
    #print(player.status())
    spot = board.places[player.position][0]
    wholeSpot = board.places[player.position]
    #print("wholeSpot:", wholeSpot[8])
    #if (spot == "Go"):

    if (spot == "Prop" or spot == "Util" or spot == "RR"):
        landOnProp(player, wholeSpot, board)

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
    print("%s went to jail!" % (player.name))
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
    #print(given)
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
    #print(given)
    return

# Handles when the player lands on a Tax space.
def landOnTax(player, position):
    amt = position[3]
    player.money = int(player.money) - int(amt)
    print("%s has paid $%s in tax." % (player.name, amt))
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

    if (int(position[8]) == 0):
        if (player.money < int(position[3])):
            print("Could not afford this %s." % (typ))
            return

        print("(Color: %s, Owned of this color: %s out of %s available and %s total)" % (position[2], colOwned(player, position), totColOwned(position, board), position[9]))
        choice = input("This %s is not owned and costs $%s (you have $%s), to purchase, press y. To decline, press any other key.\n" % (typ, int(position[3]), player.money))

        if (choice == "y" or choice == "Y"):
            board.places[player.position][8] = 1
            player.properties.append(position)
            player.money = player.money - int(position[3])
            print("%s purchased %s" % (player.name, position[1]))

            if (board.places[player.position][0] == "RR"):
                player.rrs = player.rrs + 1

            if (board.places[player.position][0] == "Util"):
                player.utils = player.utils + 1
            return

    if (int(position[8]) == 1):
        if position in player.properties:
            print("%s owns this %s." % (player.name, typ))

        else:
            payRentProp(player, position, board)
    return

## ---> Other Funcs <--- ##

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
    #print(given, player.status())
    typ = str(given[0])
    #print(typ)
    print("%s" % (given[2]))
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
        whatDo(player, board)
    elif (typ == "Get"):
        player.money = player.money + int(given[1])
    elif (typ == "Back"):
        detPos(player, (0 - int(given[1])), board)
        whatDo(player, board)
    elif (typ == "Pay"):
        player.money = player.money - int(int(given[1]) * len(board.players))
        for p in board.players:
            p.money = player.money + int(given[1])
    elif (typ == "Card"):
        player.cards = player.cards + 1
    elif (typ == "Jail"):
        player.jail = 1
    else:
        print("How did this happen?")


def payRentProp(player, position, board):
    #print("%s is paying on %s" %(player.name, position[1]))
    amt = position[4]
    for p in board.players:
        if position in p.properties:
            if (position[0] == "Prop"):
                player.money = int(player.money) - int(amt)
                p.money = int(p.money) + int(amt)
                print("%s has paid %s $%s in rent." % (player.name, p.name, amt))
                return
                ## TODO: add house/hotel rent
            elif (position[0] == "Util"):
                if (p.utils == 1):
                    player.money = int(player.money) - int(player.roll * 4)
                    p.money = int(p.money) + int(player.roll * 4)
                    print("%s has paid %s $%s in rent." % (player.name, p.name, player.roll * 4))
                    return
                if (p.utils == 2):
                    player.money = int(player.money) - int(player.roll * 10)
                    p.money = int(p.money) + int(player.roll * 10)
                    print("%s has paid %s $%s in rent." % (player.name, p.name, player.roll * 10))
                    return
            elif (position[0] == "RR"):
                amt = int(amt) * int(p.rrs)
                player.money = int(player.money) - int(amt)
                p.money = int(p.money) + int(amt)
                print("%s has paid %s $%s in rent." % (player.name, p.name, amt))
                return

#  handles a player's turn while they are in jail.
def jail(player, board):
    changePos(player, 10, board)

    # If player has been in jail for 3 or more turns, release them.
    if (player.jail >= 3):
        print("Jail time served.")
        player.jail = 0
        turn(player, board)
        return

    # If they haven't, they can choose to roll for doubles, use GooJF Card, or Pay.
    while True:
        choice = input("(R)oll dice, (U)se card, or (P)ay $50 fine.\n")
        if (choice == "R" or choice == "r"):
            result = roll()
            player.roll = result[0]

            # Checks for double, releases player and moves them.
            if (result[1]):
                player.jail = 0
                print("Doubles rolled!")
                pos = detPos(player,result[0],board)
                currSpace = pos[1]
                print("%s is now on %s" % (player.name, currSpace))
                whatDo(player,board)
                return

            else:
                print("Doubles not rolled.")
                player.jail = player.jail + 1
                return

        # Checks if player has a card, uses and releases them if they do.
        elif (choice == "U" or choice == "u"):
            if (player.cards > 0):
                print("Card used!")
                player.cards = player.cards - 1
                player.jail = 0
                turn(player,board)
                return

            # If not, notify them and reset jail func w/o increasing jail count.
            else:
                print("No cards available.")
                jail(player,board)

        # Releases the player if they can afford the $50 fee.
        elif (choice == "P" or choice == "p"):
            if (player.money >= 50):
                print("$50 fine paid!")
                player.money = player.money - 50
                player.jail = 0
                turn(player,board)
                return
            else:
                print("Not enough money for the fee!")
                jail(player,board)

        else:
            print("Please enter an R, U, or P")

def botTurn(player, board):
        if (player.jail > 0):
            print("\n%s is in jail." % (player.name))
            #botJail(player, board) TODO
            return

# Handles the player's turn, where they can view the status, properties, and
# roll the dice.
def turn(player, board):
    if (player.bot == 1):
        print(player.name, "\ntakes their turn!")
        botTurn(player, board)

    doub = 0
    if (player.jail > 0):
        print("\n%s is in jail." % (player.name))
        jail(player, board)
        return

    while True:
        print("\nIt's %s's turn!" % (player.name))
        print("Enter <S> to view status, <P> to view your properties, <A> to view every player's properties, or <R> to roll dice.")
        choice = input()

        if choice == "S" or choice == "s":
            for p in board.players:
                print(p.status())

        elif choice == "P" or choice == "p":
            print(player.viewProps())

        elif choice == "A" or choice == "a":
            board.viewProps()

        elif choice == "R" or choice == "r":
            result = roll()
            player.roll = result[0]
            doub = result[1]
            #print(result)
            pos = detPos(player,result[0],board)

            if result == 8 or result == 11:
                print("%s rolled an %d!" % (player.name, result[0]))

            else:
                print("%s rolled a %d!" % (player.name, result[0]))
            currSpace = pos[1]
            print("%s is now on %s" % (player.name, currSpace))
            break

        else:
            print("Please enter an S, P, A, or R")

    whatDo(player,board)
    player.prevPos = player.position

    if (doub):
        turn(player,board)
    return

## ---------- CLASSES ---------- ##

class Board:
    places = []
    players = []
    fate = []
    crate = []
    def __init__(self, spaces, places, fate, crate):
        self.spaces = spaces
        self.places = places
        self.fate = fate
        self.crate = crate

    def viewProps(self):
        #mainPhrase = ""
        for pla in self.players:
            print(pla.viewProps())
        #return mainPhrase

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


    def changeMoney(self, amount):
        self.money = self.money + amount

    def changeProperty(self, prop, add):
        if add == 1:
            properties.append(prop)
        if add == 0:
            if prop in properties:
                properties.remove(prop)
    def status(self): ## 40 represents # of spaces, change if modded
        phrase = ("%s: Money: $%s, Position: %s (%d/40)" %
                (self.name, self.money, self.posName, self.position + 1))
        props = ", Properties: "
        counter = 0
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
            phrase = phrase + (" %ss(%d/%s): " % (color, count, totCnt))
            counter = 0
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
        phrase = ("%s's properties: " % (self.name))
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
        return phrase




## ---------- SET UP ---------- ##
##(program begins here)##

## read places.txt
spaces_inf = open("places.txt", "r")
sinf = spaces_inf.readlines()
spaces = []
counter = 0
for index in sinf:
    spaces.append(sinf[counter].strip().split(','))
    counter = counter + 1
spaces_inf.close()
#print(spaces)

## read board.txt
board_inf = open("board.txt", "r")
binf = board_inf.readlines()
counter = 0
for index in binf:
    binf[counter] = binf[counter].strip()
    counter = counter + 1
board_inf.close()

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
gameBoard = Board(binf[0], spaces, finf, cinf)

## read player.txt
play_inf = open("player.txt", "r")
pinf = play_inf.readlines()
counter = 0
for index in pinf:
    pinf[counter] = pinf[counter].strip()
    counter = counter + 1
play_inf.close()

# Prepare TTS
def say(line):
    if ttsEnabled == 1:
        engine.say(str(line))
        engine.runAndWait()

engine = pyttsx3.init()
ttsEnabled = 1
while True:
    say("Would you like Text to Speech?")
    ttsEnabled = input("\nWould you like Text to Speech? (y/n)")
    if ttsEnabled == "y" or ttsEnabled == "Y":
        ttsEnabled = 1
        break

    elif ttsEnabled == "n" or ttsEnabled == "N":
        ttsEnabled = 0
        break

    else:
        print("Please enter y (yes) or n (no)")
        say("Please enter y or n")

## create players
players = []
#playerNum = input("How many players?\n")
while True:
    say("How many human players?")
    playerNum = input("How many human players?\n")
    try:
        int(playerNum) > 0 and int(playerNum) < 9
    except ValueError:
        say("Please enter a number between 1 and 8")
        print("Please enter a number between 1 and 8")
        continue
    else:
        if (int(playerNum) > 0 and int(playerNum) < 9):
            playerNum = int(playerNum)
            break
        else:
            print("Please enter a number between 1 and 8")
            continue

while True:
    say("How many bots?\n")
    botNum = input("How many bots?\n")
    try:
        int(botNum) > -1 and int(botNum) < (9 - playerNum)
    except ValueError:
        print("Please enter a number between 0 and ", 9 - playerNum)
        continue
    else:
        if (int(botNum) > -1 and int(botNum) < (9 - playerNum)):
            botNum = int(botNum)
            break
        else:
            print("Please enter a number between 0 and ", 9 - playerNum)
            continue

counter = 0
names = []
for x in range(playerNum):
    print("What is Player %d's name?" % (counter+1))
    name = input()
    while name in names:
        print("Please choose a unique name.")
        print("What is Player %d's name?" % (counter+1))
        name = input()
    player = Player(name, pinf[0], 0)
    players.append(player)
    names.append(name)
    counter = counter + 1

for x in range(botNum):
    nameString = "Bot " + str(x+1)
    bot = Player(nameString, pinf[0], 1)
    players.append(bot)
    names.append(nameString)
    print("Added bot", nameString, "to the game.")

gameBoard.players = players
counter = 0
for x in range(9999999):
    #print("loop: %d" % (x))
    choice = counter % len(players)
    turn(players[choice], gameBoard)
    counter = counter + 1
