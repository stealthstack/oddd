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

Smart Monster AI: Monsters pathfind toward the player through dungeon corridors

Equipment System: Collect and upgrade gear with socketable gems

Character Progression: Level up your hero with improved stats and abilities

Multiple Floors: Descend through increasingly challenging dungeon levels

Combat System
Dice-Based Resolution: Combat outcomes determined by dice rolls + character stats

Multiple Damage Types: Miss, Half Damage, Hit, and Critical Hit results

Ranged Combat: Attack monsters from a distance with line-of-sight mechanics

Monster Variety: Face Goblins, Skeletons, Minotaurs, and the fearsome Red Dragon

Dynamic Encounters: Monsters move toward you and attack through open doors

Equipment & Loot
Gear Types: Helms, Chestplates, Swords, Greatswords, Crossbows, Greatbows, and Shields

Visual Socket System: See filled (●) and empty (○) sockets on your gear

Gem Socketing: Enhance gear with Green (+1), Blue (+2), and Purple (+3) gems

Special Materials: Adamantine and Dragonscale gear with powerful bonuses

Smart Looting: Automatic gem socketing and gear comparison

🕹️ How to Play
Controls
WASD: Move through the dungeon (Up, Left, Down, Right)

R: Perform ranged attacks (line of sight, 1-3 tiles)

F: Use stairs to descend to next floor

Q: Quit game

Movement & Combat
Auto-Attack: Moving into a monster's tile automatically attacks it

Ranged Attacks: Hit monsters from a distance without moving

Monster Behavior: Monsters will pathfind toward you and attack through open doors

Safe Zone: The starting tile (0,0) is safe from monster attacks

Objectives
Explore each 5x5 floor to reveal the map

Defeat monsters to gain experience and loot

Collect gear and gems to strengthen your character

Find and clear the Lair to reveal stairs

Descend deeper to face the final boss

🛠️ Installation
Requirements
Python 3.6 or higher

Windows OS (uses msvcrt for keyboard input)

Terminal/Command Prompt that supports ANSI color codes

Running the Game
Download the oddd.py file

Open a terminal/command prompt

Run: python oddd.py

🎯 Game Mechanics
Combat Resolution
Combat uses a dice-roll plus stat system:

Roll 1d6 + your attack vs monster armor

6: Critical Hit (double damage)

Total > Armor: Normal Hit

Total = Armor: Half Damage

Total < Armor: Miss

Character Stats
Level: Determines base armor and attack

HP: Health points - game over if reaches 0

Attack: Bonus added to combat rolls

Armor: Reduces damage taken from monsters

Experience: Gain from defeating monsters to level up

Monster Types & Stats
Goblin: 5+floor HP, floor ATK/ARM, 2 EXP

Skeleton: 7+floor HP, floor+1 ATK/ARM, 3 EXP

Minotaur: 12+floor HP, floor+4 ATK/ARM, 6 EXP

Red Dragon: 20+floor HP, floor+6 ATK/ARM, 12 EXP

🗺️ Map Symbols & Colors
Colors
🟠 Orange: Player

🟢 Bright Green: Goblins

🔵 Bright Blue: Skeletons

🟡 Gold: Minotaurs

🔴 Bright Red: Red Dragon

🟡 Bright Yellow: Loot

🔵 Bright Blue: Lair

⚪ Gray: Stairs

⚫ Dim Gray: Unexplored areas

Symbols
P: Player position

G: Goblin

S: Skeleton

M: Minotaur

D: Red Dragon

!: Loot

S: Stairs

L: Lair (boss room)

?: Unexplored area

█: Walls


🎨 Technical Features
ANSI Color Support: Enhanced visual accessibility with color-coded elements

Pathfinding AI: Monsters use BFS to find shortest paths to the player

Procedural Generation: Dice-based room shapes and intelligent door placement

Line-of-Sight: Ranged attacks and vision follow dungeon geometry

Smart Equipment: Automatic gear comparison and socket management

🏆 Victory Condition
Defeat the Red Dragon that awaits in the lair to win the game and save your village!

Grab your dice and prepare to delve into the ever-changing dungeon! Your village is counting on you, hero!
