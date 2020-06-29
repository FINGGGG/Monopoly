class Player(object):
    def __init__(self, name, money, bot):
        self.properties = []
        self.monopolies = []
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
        self.checkMonopolies(prop)

    def resetSummary(self):
        self.cardUsed = ""
        self.taxPaid = 0
        self.rentPaid = 0
        self.rentPaidTo = ""
        self.rentGot = 0
        self.rentGotFrom = ""

    def status(self, board):
        phrase = ("%s: Money: $%s, Position: %s (%d of %d)" %
                (self.name, self.money, self.posName, self.position, board.spaces))
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
                        if (int(p[6]) > 1):
                            phrase = phrase + (" with %d houses, " % (p[6]))
                        else:
                            phrase = phrase + (" with %d house, " % (p[6]))
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

    def checkMonopolies(self, prop):
        props = self.getProps()
        color = prop[2]
        if (color in self.monopolies):
            self.monopolies.remove(color)

        if (int(props[color]) == int(prop[9])):
            self.monopolies.append(color)
