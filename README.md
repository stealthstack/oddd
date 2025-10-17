One Dice Dungeon Delve
A text-based roguelike dungeon crawler where every room is shaped by the roll of a dice! Explore procedurally generated dungeons, battle monsters, collect powerful gear, and descend deeper to face the mighty Red Dragon.

🎲 Game Concept
In One Dice Dungeon Delve, each dungeon tile is generated based on dice rolls that determine room shapes, encounters, and loot. The game combines traditional roguelike elements with a unique card-inspired room generation system where dice rolls (1-6) correspond to different room layouts:

1 (Aces): Dead-end rooms with stairs

2 (Clubs): Left turns

3 (Diamonds): Right turns

4 (Hearts): Straight passages

5 (Spades): T-intersections

6 (Royals): 4-way intersections

🎮 Features
Core Gameplay
Procedural Generation: Every floor is uniquely generated using dice-based room shapes

Turn-Based Combat: Strategic combat with dice-roll resolution system

Equipment System: Collect and upgrade gear with socketable gems

Character Progression: Level up your hero with improved stats and abilities

Multiple Floors: Descend through increasingly challenging dungeon levels

Combat System
Dice-Based Resolution: Combat outcomes determined by dice rolls + character stats

Multiple Damage Types: Miss, Half Damage, Hit, and Critical Hit results

Melee & Ranged Options: Choose between close-quarters and distance attacks

Monster Variety: Face Goblins, Skeletons, Minotaurs, and the fearsome Red Dragon

Equipment & Loot
Gear Types: Helms, Chestplates, Swords, Greatswords, Crossbows, Greatbows, and Shields

Gem Socketing: Enhance gear with Green, Blue, and Purple gems for bonus stats

Special Materials: Adamantine and Dragonscale gear with powerful bonuses

Inventory Management: Strategic equipment choices for optimal builds

🕹️ How to Play
Controls
WASD: Move through the dungeon (Up, Left, Down, Right)

T: Attack adjacent monsters (melee)

R: Perform ranged attacks (line of sight)

F: Use stairs to descend to next floor

Q: Quit game

Objectives
Explore each floor to reveal the map

Defeat monsters to gain experience and loot

Collect gear and gems to strengthen your character

Find and clear the Lair to reveal stairs

Descend deeper to face the final boss

Game Mechanics
Vision System: Rooms are revealed as you explore adjacent areas

Monster Awareness: Adjacent monsters will attack you on their turn

Healing: Fully heal after defeating monsters

Leveling: Gain experience to increase level, max HP, and base stats

🛠️ Installation
Requirements
Python 3.6 or higher

Windows OS (uses msvcrt for keyboard input)

Running the Game
Download the one_dice_dungeon_delve.py file

Open a terminal/command prompt

Run: python one_dice_dungeon_delve.py

🏆 Victory Condition
Defeat the Red Dragon that awaits on the deepest floor to win the game and save your village!

📊 Character Stats
Level: Determines base armor and attack

HP: Health points - game over if reaches 0

Attack: Bonus added to combat rolls

Armor: Reduces damage taken from monsters

Experience: Gain from defeating monsters to level up

🎯 Combat Resolution
Combat uses a dice-roll plus stat system:

Roll 1d6 + your attack vs monster armor

6: Critical Hit (double damage)

Total > Armor: Normal Hit

Total = Armor: Half Damage

Total < Armor: Miss

🗺️ Map Symbols
P: Player position

M: Monster

!: Loot

S: Stairs

L: Lair (boss room)

?: Unexplored area

█: Walls

␣: Open passages

🎨 Technical Details
Pure Python: No external dependencies required

Object-Oriented Design: Clean class structure for game entities

Procedural Generation: Dice-based room shapes and content placement

ASCII Graphics: Text-based visualization using extended ASCII characters

📝 Development
This game was developed as a Python implementation of a dice/card-based dungeon crawling concept, featuring:

Modular room generation system

Expandable monster and gear types

Comprehensive combat mechanics

Intuitive text-based interface

Grab your dice and prepare to delve into the ever-changing dungeon! Your village is counting on you, hero!
