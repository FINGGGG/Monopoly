# Text-to-Monopoly
Hello! This is a simple side project of mine to recreate Monopoly in Python using only text.
My dream is to one day become a game developer, so this is my first attempt at creating a game,
albeit an already existing game in a purely text based format.

To make this project a bit more interesting however, I am trying to implement two additional features...

## Text-to-Speech
After I took a class in UC Davis about culture and video games, I was made more aware about the plight of
blind gamers. So, while there do exist fully 3D as well as text-based renditions of Monopoly out there, I wanted
to add a purely optional text-to-speech narrator so that vision is not a requirement to play the game.

I also wanted it to be a bit more robust than simply reading out the exact information being displayed in text,
so there are two planned additional features to that end:

### Optional Instruction Speech
If a player chooses to turn narration on, they will be asked a follow-up question if they want instructions
to also be narrated for them. I want to include this option because the instruction texts tend to be much
longer than the other text lines in the game, and if a player has played the game alot, it could get
tedious hearing the prompts over and over when they already know what to press.

### Text Summaries
This is currently only a planned feature that I am working on, and it may be integrated into the visual text as well.
The idea is that the way I originally made the game, each thing that happens in the game gets its own line of text,
but I want to condense those lines into one to make the game go faster and sound more natural. For example, at the moment,
when a player takes their turn, rolling the dice, moving to a new location, displaying information about that location, etc,
each gets individual lines. I think this would get tedious to listen to after a while.

## Bots
Unless I am able to make this game have online multiplayer, the only way to play with other people would be to share the
computer running the game. But what if you're alone and want to play? That's what bots are for. My reach goal is to have
multiple "personalities" for bots that determines the choices they make, but for the moment I am integrating a simple
numerical probability for bot's decisions so they won't make the same exact choices each round. For example, if a bot lands
on an open property that would cost almost all their money, there is a high probability they will decide not to buy it in
order to save money.

## To Do List
- Negotiations
-- Allow players to make offers to others during their turn.
-- Player that recieves the offer can accept or deny it, possbily make counter offer
-- Bots accept, deny, possibly counter offer based on probabiliy calculations using their current stats

- Text Summaries

- Bot personalities

- Streamline text-to-speech code to make game flow better and faster

- Once game is finished, put it somewhere people can play! Maybe [audiogames.net](https://www.audiogames.net/)

places.txt legend:
[Type(0),Name(1),Color(2),Cost(3),
Rent(4),Position(5),Houses(6),Hotels(7),Owned(8),
NumPerColor(9),Mortgaged[10],MortPrice[11],
1House[12], 2House[13], 3House[14], 4House[15], Hotel[16]]
