class Board(object):
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
