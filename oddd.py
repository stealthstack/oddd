import random
import os
import msvcrt
from enum import Enum

class TileType(Enum):
    EMPTY = "."
    WALL = "█"
    DOOR = "D"
    STAIRS = "S"
    LAIR = "L"
    MONSTER = "M"
    LOOT = "!"

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class MonsterType(Enum):
    GOBLIN = "Goblin"
    SKELETON = "Skeleton"
    MINOTAUR = "Minotaur"
    DRAGON = "Red Dragon"
    GELATINOUS_DICE = "Gelatinous Dice"

class GearType(Enum):
    HELM = "Helm"
    CHEST = "Chestplate"
    SWORD = "Sword"
    GREATSWORD = "Greatsword"
    CROSSBOW = "Crossbow"
    GREATBOW = "GreatBow"
    SHIELD = "Kite Shield"

class GemColor(Enum):
    GREEN = "Green"
    BLUE = "Blue" 
    PURPLE = "Purple"

# Add this new enum for tile shapes
class TileShape(Enum):
    DEAD_END = "Dead-end"  # 1 or Aces - Stairs
    LEFT = "Left"          # 2 or Clubs - Left turn
    RIGHT = "Right"        # 3 or Diamonds - Right turn  
    STRAIGHT = "Straight"  # 4 or Hearts - Straight
    T_INTERSECTION = "T-intersection"  # 5 or Spades - T-intersection
    ALL_WAY = "All-way"    # 6 or Royals - 4-way intersection

# Minimal supporting classes so references compile
class DamageResult(Enum):
    MISS = 0
    HALF = 1
    HIT = 2
    CRIT = 3

class Gem:
    def __init__(self, color: GemColor, floor_level=1):
        self.color = color
        # simple bonus mapping
        self.bonus = {GemColor.GREEN: 1, GemColor.BLUE: 2, GemColor.PURPLE: 3}.get(color, 1)
    def __str__(self):
        return f"{self.color.value} Gem +{self.bonus}"

class Gear:
    def __init__(self, gear_type: GearType, floor_level=1):
        self.type = gear_type
        # Set bonus based on gear type according to game rules
        if gear_type == GearType.HELM:
            self.bonus = floor_level
        elif gear_type == GearType.CHEST:
            self.bonus = floor_level
        elif gear_type == GearType.SHIELD:
            self.bonus = floor_level
        elif gear_type == GearType.SWORD:
            self.bonus = floor_level + 1
        elif gear_type == GearType.GREATSWORD:
            self.bonus = floor_level + 2
        elif gear_type == GearType.CROSSBOW:
            self.bonus = floor_level  # rng - could be randomized
        elif gear_type == GearType.GREATBOW:
            self.bonus = floor_level + 1  # rng - could be randomized
        else:
            self.bonus = floor_level
        self.sockets = []
        # Set max sockets based on bonus level (applies to all gear)
        if self.bonus >= 6:
            self.max_sockets = 3
        elif self.bonus >= 3:
            self.max_sockets = 2
        else:
            self.max_sockets = 1
        self.is_adamantine = False
        self.is_dragonscale = False

    def get_total_bonus(self):
        total = self.bonus
        for g in self.sockets:
            total += g.bonus
        if self.is_adamantine:
            total += 4
        if self.is_dragonscale:
            total += 6
        return total

    def add_gem(self, gem: Gem):
        if len(self.sockets) < self.max_sockets:
            self.sockets.append(gem)
            return True
        return False

    def __str__(self):
        socket_str = f" [{len(self.sockets)}/{self.max_sockets} sockets]" if self.sockets else ""
        return f"{self.type.value} +{self.get_total_bonus()}{socket_str}"

class Monster:
    def __init__(self, monster_type: MonsterType, floor_level=1):
        self.type = monster_type
        self.floor_level = floor_level
        # simple stats scaling
        self.armor = floor_level
        self.attack = floor_level
        self.hp = 3 + floor_level
        self.alive = True
        self.exp = 1 + floor_level // 2

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def __str__(self):
        return f"{self.type.value} (HP: {self.hp}, ATK: {self.attack}, ARM: {self.armor})"

class Player:
    def __init__(self):
        self.level = 1
        self.max_hp = 6
        self.current_hp = 6
        self.exp = 0
        self.exp_needed = 6
        self.floor_level = 1
        self.max_floor_mapped = 0
        
        # Starting gear - use dictionary for the initial sword
        self.gear = {
            'helm': None,  # No starting helm
            'chest': None,
            'weapon1': Gear(GearType.SWORD, 1),
            'weapon2': None,
            'ranged1': None,
            'ranged2': None
        }
        
        self.inventory = []
        self.x = 0
        self.y = 0
        
        # Calculate initial stats
        self.armor = self.calculate_armor()
        self.attack = self.calculate_attack()
        
    def calculate_armor(self):
        """Calculate total armor from level and gear"""
        total = self.level  # Base armor from level

        # Add gear bonuses (gems are already included in get_total_bonus())
        if self.gear['helm']:
            if isinstance(self.gear['helm'], Gear):
                total += self.gear['helm'].get_total_bonus()
            else:
                total += self.gear['helm'].get('bonus', 0)

        if self.gear['chest']:
            if isinstance(self.gear['chest'], Gear):
                total += self.gear['chest'].get_total_bonus()

        # Add shield bonus if equipped in weapon2
        if self.gear['weapon2'] and isinstance(self.gear['weapon2'], Gear):
            if self.gear['weapon2'].type == GearType.SHIELD:
                total += self.gear['weapon2'].get_total_bonus()

        # REMOVED: The double-counting of gem bonuses
        # for slot in ['helm', 'chest']:
        #     if self.gear[slot] and isinstance(self.gear[slot], Gear):
        #         for gem in self.gear[slot].sockets:

        return total

    def calculate_attack(self, ranged=False):
        """Calculate attack bonus for melee or ranged"""
        attack = self.level
        if ranged:
            w = self.gear.get('ranged1') or self.gear.get('ranged2')
            if isinstance(w, Gear):
                attack += w.get_total_bonus()
            elif isinstance(w, dict):
                attack += w.get('bonus', 0)
        else:
            w = self.gear.get('weapon1') or self.gear.get('weapon2')
            if isinstance(w, Gear):
                attack += w.get_total_bonus()
            elif isinstance(w, dict):
                attack += w.get('bonus', 0)
        return attack

    
    def take_damage(self, amount):
        """Apply damage to the player. Returns True if the player died."""
        self.current_hp -= amount
        print(f"You take {amount} damage. HP: {self.current_hp}/{self.max_hp}")
        if self.current_hp <= 0:
            self.current_hp = 0
            print("You have died.")
            return True
        return False
    
    def heal(self, amount):
        """Heal the player, not exceeding max_hp."""
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        healed = self.current_hp - old_hp
        if healed > 0:
            print(f"You heal {healed} HP. HP: {self.current_hp}/{self.max_hp}")
    
    def gain_exp(self, amount):
        """Gain experience and check for level up"""
        self.exp += amount
        print(f"You gain {amount} experience!")
        while self.exp >= self.exp_needed:
            self.level_up()
    
    def level_up(self):
        """Handle player level up"""
        self.level += 1
        self.max_hp += 1
        self.current_hp = self.max_hp  # Full heal on level up
        excess_exp = self.exp - self.exp_needed
        self.exp_needed += 1
        self.exp = excess_exp
        print(f"🎉 Level up! You are now level {self.level}")
        print(f"Max HP: {self.max_hp}, Next level in {self.exp_needed} exp")
    
    def move(self, dx, dy):
        # Simple movement for player: update coordinates
        self.x += dx
        self.y += dy
        # end Player.move


class Tile:
    def __init__(self, x, y, tile_type=TileType.EMPTY, shape=None):
        self.x = x
        self.y = y
        self.type = tile_type
        self.shape = shape
        self.monster = None
        self.loot = None
        self.revealed = False
        self.doors = {Direction.UP: False, Direction.DOWN: False,
                     Direction.LEFT: False, Direction.RIGHT: False}
        self.entrance_direction = None

    def configure_doors_from_shape(self, entrance_direction):
        """Configure doors based on tile shape and entrance direction"""
        self.entrance_direction = entrance_direction
        
        # Clear all doors first
        for direction in Direction:
            self.doors[direction] = False
            
        # Always have door back to where we came from
        self.doors[entrance_direction] = True
        
        # Add additional doors based on shape
        if self.shape == TileShape.DEAD_END:
            pass  # Only the entrance door
            
        elif self.shape == TileShape.LEFT:
            left_dir = self.get_left_turn(entrance_direction)
            self.doors[left_dir] = True
            
        elif self.shape == TileShape.RIGHT:
            right_dir = self.get_right_turn(entrance_direction)
            self.doors[right_dir] = True
            
        elif self.shape == TileShape.STRAIGHT:
            straight_dir = self.get_opposite_direction(entrance_direction)
            self.doors[straight_dir] = True
            
        elif self.shape == TileShape.T_INTERSECTION:
            left_dir = self.get_left_turn(entrance_direction)
            right_dir = self.get_right_turn(entrance_direction)
            self.doors[left_dir] = True
            self.doors[right_dir] = True
            
        elif self.shape == TileShape.ALL_WAY:
            for direction in Direction:
                self.doors[direction] = True
        
        # CRITICAL FIX: Always ensure two-way connections
        # If tile A has a door to tile B, tile B should have a door back to tile A
        # We'll handle this in the movement/generation logic
                
    def get_grid_representation(self):
        pass

    def get_3x3_representation(self, show_player=False):
        """Clean 3x3 representation with proper shape visualization"""
        # Start with walls
        grid = [
            ['█', '█', '█'],
            ['█', '█', '█'],
            ['█', '█', '█']
        ]

        # Center character - show player or tile contents
        center_char = 'P' if show_player else self.get_center_symbol()
        grid[1][1] = center_char

        # Show doors based on actual connections
        if self.doors[Direction.UP]:
            grid[0][1] = ' '  # Open passage up
        if self.doors[Direction.DOWN]:
            grid[2][1] = ' '  # Open passage down
        if self.doors[Direction.LEFT]:
            grid[1][0] = ' '  # Open passage left
        if self.doors[Direction.RIGHT]:
            grid[1][2] = ' '  # Open passage right

        return grid

    def get_5x3_representation(self, show_player=False):
        """Clean 5x3 representation with proper shape visualization"""
        # Start with walls
        grid = [
            ['█', '█', '█', '█', '█'],
            ['█', ' ', ' ', ' ', '█'],
            ['█', '█', '█', '█', '█']
        ]

        # Center character - show player or tile contents
        center_char = 'P' if show_player else self.get_center_symbol()
        grid[1][2] = center_char

        # Show doors based on actual connections
        if self.doors[Direction.UP]:
            grid[0][2] = ' '  # Open passage up
        if self.doors[Direction.DOWN]:
            grid[2][2] = ' '  # Open passage down
        if self.doors[Direction.LEFT]:
            grid[1][0] = ' '  # Open passage left
        if self.doors[Direction.RIGHT]:
            grid[1][4] = ' '  # Open passage right

        return grid

    def get_center_symbol(self):
        """Get symbol that represents the tile type and shape"""
        if not self.revealed:
            return '?'  # Unexplored

        # Show content priority: monster > loot > special
        if self.monster and self.monster.alive:
            return 'M'  # Monster
        if self.loot:
            return '!'  # Loot
        if self.type == TileType.STAIRS:
            return 'S'  # Stairs
        if self.type == TileType.LAIR:
            return 'L'  # Lair

        # For empty rooms, no shape symbol needed since walls show the shape
        return ' '  # Default empty

    def get_opposite_direction(self, direction):
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        return opposites[direction]

    def get_left_turn(self, direction):
        left_turns = {
            Direction.UP: Direction.LEFT,
            Direction.LEFT: Direction.DOWN,
            Direction.DOWN: Direction.RIGHT,
            Direction.RIGHT: Direction.UP
        }
        return left_turns[direction]

    def get_right_turn(self, direction):
        right_turns = {
            Direction.UP: Direction.RIGHT,
            Direction.RIGHT: Direction.DOWN,
            Direction.DOWN: Direction.LEFT,
            Direction.LEFT: Direction.UP
        }
        return right_turns[direction]

    def add_door(self, direction):
        self.doors[direction] = True
        
    def has_door(self, direction):
        return self.doors.get(direction, False)
        
    def __str__(self):
        if not self.revealed:
            return "?"
        if self.monster and self.monster.alive:
            return "M"
        if self.loot:
            return "!"
        if self.type == TileType.STAIRS:
            return "S"
        if self.type == TileType.LAIR:
            return "L"
        
        # Show different symbols for different shapes when revealed
        if self.shape == TileShape.DEAD_END:
            return "╳"
        elif self.shape == TileShape.LEFT:
            return "╰"
        elif self.shape == TileShape.RIGHT:
            return "╯"
        elif self.shape == TileShape.STRAIGHT:
            return "│"
        elif self.shape == TileShape.T_INTERSECTION:
            return "┬"
        elif self.shape == TileShape.ALL_WAY:
            return "┼"
        return "."

class Dungeon:
    def __init__(self, floor_level=1):
        self.floor_level = floor_level
        self.grid = {}
        self.player_start = (0, 0)
        self.lair_location = None
        self.lair_revealed = False
        self.generate_starting_room()
        
    def generate_starting_room(self):
        # Generate the starting room
        start_x, start_y = self.player_start
        start_tile = Tile(start_x, start_y, TileType.EMPTY, TileShape.ALL_WAY)
        self.grid[(start_x, start_y)] = start_tile

        # All directions have doors in the starting room
        for direction in Direction:
            start_tile.add_door(direction)

        # Reveal the starting room
        start_tile.revealed = True
        # Generate ONLY the 4 adjacent tiles with proper shapes
        for direction in Direction:
            dx, dy = direction.value
            new_x, new_y = start_x + dx, start_y + dy

            # Check distance limit
            distance = max(abs(new_x), abs(new_y))
            if distance <= 4:
                # Roll for tile shape based on card system
                shape = self.roll_tile_shape()
                adjacent_tile = Tile(new_x, new_y, TileType.EMPTY, shape)
                self.grid[(new_x, new_y)] = adjacent_tile

                # Configure doors based on shape and entrance direction
                entrance_direction = self.get_opposite_direction(direction)
                adjacent_tile.configure_doors_from_shape(entrance_direction)

                # Populate the adjacent tile
                self.populate_tile(adjacent_tile)

                # Reveal these starting tiles
                adjacent_tile.revealed = True
        


    def roll_tile_shape_for_entrance(self, entrance_direction):
        """Roll for tile shape that makes sense with the entrance direction"""
        roll = random.randint(1, 6)
        
        # Ensure the shape makes sense with how we entered
        if roll == 1:
            # Dead-end - only valid if we're at boundary
            return TileShape.DEAD_END
        elif roll == 2:
            return TileShape.LEFT
        elif roll == 3:
            return TileShape.RIGHT
        elif roll == 4:
            return TileShape.STRAIGHT
        elif roll == 5:
            return TileShape.T_INTERSECTION
        else:  # roll == 6
            return TileShape.ALL_WAY

    # --- Helper methods kept from previous implementation ---
    def populate_tile(self, tile):
        if tile.type in [TileType.STAIRS, TileType.LAIR]:
            return
            
        roll = random.randint(1, 6)
        if roll in [1, 2]:  # Monster
            tile.monster = self.generate_monster()
        elif roll in [5, 6]:  # Loot
            tile.loot = self.generate_loot()

    def populate_lair(self, tile):
        """Populate a lair tile with a boss monster and special loot."""
        if self.floor_level <= 5:
            tile.monster = Monster(MonsterType.MINOTAUR, self.floor_level)
        else:
            tile.monster = Monster(MonsterType.DRAGON, self.floor_level)
        # Lair has special loot
        tile.loot = self.generate_gear()
        if isinstance(tile.loot, Gear):
            tile.loot.is_adamantine = True

    def roll_tile_shape(self):
        """Roll for tile shape based on card system from rulesheet"""
        roll = random.randint(1, 6)
        
        if roll == 1:
            return TileShape.DEAD_END    # Aces - Dead-end/Stairs
        elif roll == 2:  
            return TileShape.LEFT        # Clubs - Left turn
        elif roll == 3:
            return TileShape.RIGHT       # Diamonds - Right turn
        elif roll == 4:
            return TileShape.STRAIGHT    # Hearts - Straight
        elif roll == 5:
            return TileShape.T_INTERSECTION  # Spades - T-intersection
        else:  # roll == 6
            return TileShape.ALL_WAY     # Royals - All-way

    def generate_monster(self):
        roll = random.randint(1, 6)
        if roll in [1, 2, 3]:
            return Monster(MonsterType.GOBLIN, self.floor_level)
        elif roll in [4, 5]:
            return Monster(MonsterType.SKELETON, self.floor_level)
        else:  # roll == 6
            if self.floor_level <= 5:
                return Monster(MonsterType.MINOTAUR, self.floor_level)
            else:
                return Monster(MonsterType.DRAGON, self.floor_level)

    def generate_loot(self):
        roll = random.randint(1, 6)
        if roll == 1:
            return Gear(GearType.SHIELD, self.floor_level)
        elif roll in [2, 3, 4]:
            gem_color = [GemColor.GREEN, GemColor.BLUE, GemColor.PURPLE][roll - 2]
            return Gem(gem_color, self.floor_level)
        else:  # roll in [5, 6]
            return self.generate_gear()

    def generate_gear(self):
        roll = random.randint(1, 6)
        if roll == 1:
            return Gear(GearType.HELM, self.floor_level)
        elif roll == 2:
            return Gear(GearType.CHEST, self.floor_level)
        elif roll == 3:
            return Gear(GearType.CROSSBOW, self.floor_level)
        elif roll == 4:
            return Gear(GearType.SWORD, self.floor_level)
        elif roll == 5:
            return Gear(GearType.GREATBOW, self.floor_level)
        else:  # roll == 6
            return Gear(GearType.GREATSWORD, self.floor_level)
        
    def reveal_tile(self, x, y):
        """Reveal a tile if it exists, return the tile or None"""
        if (x, y) in self.grid:
            tile = self.grid[(x, y)]
            tile.revealed = True
            
            # Handle lair special case
            if tile.type == TileType.LAIR and not self.lair_revealed:
                self.lair_revealed = True
                self.populate_lair(tile)
            
            return tile
        return None
    
    def ensure_two_way_connection(self, from_x, from_y, to_x, to_y, direction):
        """Ensure that if tile A connects to tile B, tile B connects back to tile A"""
        from_tile = self.grid.get((from_x, from_y))
        to_tile = self.grid.get((to_x, to_y))
        
        if from_tile and to_tile:
            # If from_tile has a door in this direction, to_tile should have door in opposite direction
            if from_tile.doors.get(direction):
                opposite_dir = self.get_opposite_direction(direction)
                to_tile.doors[opposite_dir] = True

    def get_opposite_direction(self, direction):
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT
        }
        return opposites[direction]

class Game:
    def __init__(self):
        self.player = Player()
        self.current_floor = 1
        self.dungeon = Dungeon(self.current_floor)
        self.game_over = False
        self.victory = False
        self.monsters_attacked_this_turn = set()

    def get_single_key(self):
        """Get a single key press and return as uppercase string"""
        key = msvcrt.getch()
        return key.decode('utf-8').upper()
        
    def display_map(self):
        print(f"\n=== Floor {self.current_floor} ===")

        # First, reveal vision from current position
        self.reveal_vision(self.player.x, self.player.y)

        # Find map boundaries - include ALL revealed tiles
        revealed_coords = [(x, y) for (x, y), tile in self.dungeon.grid.items() if tile.revealed]
        all_coords = revealed_coords + [(self.player.x, self.player.y)]

        if not all_coords:
            all_coords = [(self.player.x, self.player.y)]

        xs = [x for x, y in all_coords]
        ys = [y for x, y in all_coords]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # Add padding
        min_x -= 1
        max_x += 1
        min_y -= 1
        max_y += 1

        # Build the composite map
        map_rows = []

        for y in range(min_y, max_y + 1):
            row_lines = [[], [], []]

            for x in range(min_x, max_x + 1):
                if (x, y) in self.dungeon.grid:
                    tile = self.dungeon.grid[(x, y)]
                    show_player = (x == self.player.x and y == self.player.y)
                    tile_grid = tile.get_5x3_representation(show_player)

                    for i in range(3):
                        row_lines[i].extend(tile_grid[i])
                else:
                    # Unexplored area
                    unexplored_grid = [
                        [' ', ' ', ' ', ' ', ' '],
                        [' ', '?', ' ', ' ', ' '],
                        [' ', ' ', ' ', ' ', ' ']
                    ]
                    for i in range(3):
                        row_lines[i].extend(unexplored_grid[i])

            # Add spacing between tiles (removed horizontal spacing for touching walls)
            for i in range(3):
                map_rows.append(''.join(row_lines[i]))

        # Print the final map
        for row in map_rows:
            print(row)
    
    def display_player_status(self):
        print(f"\nPlayer: Level {self.player.level}")
        print(f"HP: {self.player.current_hp}/{self.player.max_hp}")
        print(f"Attack: {self.player.calculate_attack()} (Melee), {self.player.calculate_attack(ranged=True)} (Ranged)")
        print(f"Armor: {self.player.calculate_armor()}")
        print(f"Exp: {self.player.exp}/{self.player.exp_needed}")
        print(f"Position: ({self.player.x}, {self.player.y})")
    
    def display_gear(self):
        print("\n--- Equipment ---")
        for slot, item in self.player.gear.items():
            if item:
                # Nicely format Gear objects or dict-based starting gear
                if isinstance(item, Gear):
                    print(f"{slot}: {item}")
                elif isinstance(item, dict):
                    name = item.get('name', 'Unknown')
                    bonus = item.get('bonus', 0)
                    sockets = item.get('sockets', [])
                    socket_str = f" [{len(sockets)} sockets]" if sockets else ""
                    print(f"{slot}: {name} +{bonus}{socket_str}")
                else:
                    print(f"{slot}: {item}")
            else:
                print(f"{slot}: Empty")
    
    def combat_roll(self, attacker_attack, defender_armor, dice_roll):
        """Calculate combat result based on rules"""
        total_attack = dice_roll + attacker_attack
        
        if dice_roll == 6:
            return DamageResult.CRIT, 2  # Double damage
        elif total_attack < defender_armor:
            return DamageResult.MISS, 0
        elif total_attack == defender_armor:
            return DamageResult.HALF, 0.5
        else:  # total_attack > defender_armor
            return DamageResult.HIT, 1
    
    def player_attack_monster(self, monster, ranged=False):
        print(f"\nYou attack the {monster.type.value}!")
        dice_roll = random.randint(1, 6)
        player_attack = self.player.calculate_attack(ranged)

        result, multiplier = self.combat_roll(player_attack, monster.armor, dice_roll)

        damage = player_attack * multiplier
        if result == DamageResult.CRIT:
            print(f"CRITICAL HIT! (Rolled {dice_roll} + {player_attack} = {dice_roll + player_attack})")
        elif result == DamageResult.HIT:
            print(f"Hit! (Rolled {dice_roll} + {player_attack} = {dice_roll + player_attack} vs Armor {monster.armor})")
        elif result == DamageResult.HALF:
            print(f"Glancing blow! (Rolled {dice_roll} + {player_attack} = {dice_roll + player_attack} vs Armor {monster.armor})")
        else:  # MISS
            print(f"Miss! (Rolled {dice_roll} + {player_attack} = {dice_roll + player_attack} vs Armor {monster.armor})")
        
        if damage > 0:
            monster_killed = monster.take_damage(damage)
            print(f"You deal {damage} damage to the {monster.type.value}!")
            if monster_killed:
                print(f"You defeated the {monster.type.value}!")
                self.player.gain_exp(monster.exp)
                # Heal after defeating monster
                self.player.heal(self.player.max_hp - self.player.current_hp)
                # Get loot from monster
                if random.randint(1, 6) >= 3:  # 50% chance for loot
                    loot = self.dungeon.generate_loot()
                    self.get_loot(loot)
            return monster_killed
        return False
    
    def monster_attack_player(self, monster):
        # Prevent the same monster from attacking multiple times per turn
        if monster in self.monsters_attacked_this_turn:
            return False

        print(f"\nThe {monster.type.value} attacks you!")
        dice_roll = random.randint(1, 6)
        player_armor = self.player.calculate_armor()

        result, multiplier = self.combat_roll(monster.attack, player_armor, dice_roll)

        damage = 1 * multiplier
        if result == DamageResult.CRIT:
            print(f"CRITICAL HIT! (Monster rolled {dice_roll} + {monster.attack} = {dice_roll + monster.attack})")
            damage = 2
        elif result == DamageResult.HIT:
            print(f"Hit! (Monster rolled {dice_roll} + {monster.attack} = {dice_roll + monster.attack} vs your Armor {player_armor})")
        elif result == DamageResult.HALF:
            print(f"Glancing blow! (Monster rolled {dice_roll} + {monster.attack} = {dice_roll + monster.attack} vs your Armor {player_armor})")
            damage = 0.5
        else:  # MISS
            print(f"Miss! (Monster rolled {dice_roll} + {monster.attack} = {dice_roll + monster.attack} vs your Armor {player_armor})")
            damage = 0

        if damage > 0:
            died = self.player.take_damage(damage)
            if died:
                self.game_over = True
                print("You have been defeated...")

        # Mark this monster as having attacked this turn
        self.monsters_attacked_this_turn.add(monster)
        return True
    
    def get_loot(self, loot):
        print(f"\nYou found: {loot}")
        
        if isinstance(loot, Gem):
            # Auto-socket if possible
            socketed = False
            for slot, item in self.player.gear.items():
                if item and isinstance(item, Gear) and len(item.sockets) < item.max_sockets:
                    item.add_gem(loot)
                    print(f"Socketed {loot} into {item.type.value}")
                    socketed = True
                    break
            
            if not socketed:
                print("No available sockets for this gem.")
                
        elif isinstance(loot, Gear):
            # Let player decide what to do with gear
            print("\nWhat would you like to do?")
            print("1. Equip it")
            print("2. Leave it")
            
            choice = input("Choose (1-2): ").strip()
            if choice == "1":
                self.equip_gear(loot)
    
    def equip_gear(self, gear):
        slot = None

        if gear.type in [GearType.HELM]:
            slot = 'helm'
        elif gear.type in [GearType.CHEST]:
            slot = 'chest'
        elif gear.type in [GearType.SHIELD]:
            # For shield, we need to handle weapon slots
            current = self.player.gear['weapon1']
            if current and isinstance(current, Gear) and current.type in [GearType.SWORD, GearType.GREATSWORD]:
                slot = 'weapon2'  # Shield goes in off-hand
        elif gear.type in [GearType.SWORD, GearType.GREATSWORD]:
            slot = 'weapon1'
        elif gear.type in [GearType.CROSSBOW, GearType.GREATBOW]:
            slot = 'ranged1'

        if slot and self.player.gear[slot] is None:
            self.player.gear[slot] = gear
            print(f"Equipped {gear} in {slot}")
        else:
            print("Cannot equip this item - no suitable slot or slot occupied")
    
    def reveal_tile_and_adjacent(self, x, y):
        """Reveal the tile at (x,y) and all adjacent tiles"""
        # Reveal the current tile
        current_tile = self.dungeon.reveal_tile(x, y)
        
        # Reveal all adjacent tiles (for vision)
        for direction in Direction:
            dx, dy = direction.value
            adj_x, adj_y = x + dx, y + dy
            self.dungeon.reveal_tile(adj_x, adj_y)

    def reveal_vision(self, x, y):
        """Reveal tiles based on player vision from current position using flood fill and line of sight"""
        visited = set()
        queue = [(x, y)]
        while queue:
            cx, cy = queue.pop(0)
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            tile = self.dungeon.grid.get((cx, cy))
            if tile:
                tile.revealed = True
                for direction in Direction:
                    if tile.doors[direction]:
                        dx, dy = direction.value
                        nx, ny = cx + dx, cy + dy
                        if (nx, ny) not in visited:
                            queue.append((nx, ny))

        # Additionally reveal line of sight in all directions up to 3 tiles
        for direction in Direction:
            self.reveal_line_of_sight(direction)



    def check_adjacent_monsters(self, x, y):
        """Check for monsters in adjacent tiles and return True if any are found"""
        for direction in Direction:
            dx, dy = direction.value
            adj_x, adj_y = x + dx, y + dy
            adj_tile = self.dungeon.grid.get((adj_x, adj_y))
            if adj_tile and adj_tile.revealed and adj_tile.monster and adj_tile.monster.alive:
                return True
        return False

    def handle_adjacent_monster_attacks(self):
        """Check for adjacent monsters and have them attack the player"""
        current_tile = self.dungeon.grid.get((self.player.x, self.player.y))
        adjacent_monsters = []
        for direction in Direction:
            if current_tile and current_tile.doors[direction]:  # Only attack through doors
                dx, dy = direction.value
                check_x, check_y = self.player.x + dx, self.player.y + dy
                adj_tile = self.dungeon.grid.get((check_x, check_y))
                if adj_tile and adj_tile.revealed and adj_tile.monster and adj_tile.monster.alive:
                    adjacent_monsters.append(adj_tile.monster)

        # Have each adjacent monster attack
        for monster in adjacent_monsters:
            if not self.game_over:  # Stop if player died
                self.monster_attack_player(monster)

    def handle_move(self, direction):
        dx, dy = direction.value
        new_x, new_y = self.player.x + dx, self.player.y + dy
        
        current_tile = self.dungeon.grid.get((self.player.x, self.player.y))
        
        if current_tile and current_tile.has_door(direction):
            # Check if target tile exists
            if (new_x, new_y) not in self.dungeon.grid:
                # Generate new tile
                new_tile = self.generate_new_tile(new_x, new_y, direction)
                if not new_tile:
                    print("Cannot generate tile in that direction!")
                    return
            else:
                new_tile = self.dungeon.grid[(new_x, new_y)]

            # Reveal the tile before moving to show any monsters
            new_tile.revealed = True

            # Check if there's a monster blocking the way
            if new_tile.monster and new_tile.monster.alive:
                print("You cannot move there - there's a monster blocking the way!")
                return

            # Move player
            self.player.move(dx, dy)

            # Update max floor mapped
            self.player.max_floor_mapped = max(self.player.max_floor_mapped, self.current_floor)

            # Ensure two-way connection
            opposite_dir = self.dungeon.get_opposite_direction(direction)
            new_tile.doors[opposite_dir] = True

            # Generate and reveal connected tiles based on the new tile's shape
            self.generate_and_reveal_connected_tiles(new_x, new_y, new_tile)

            shape_name = new_tile.shape.value if new_tile.shape else "Room"
            print(f"You move {direction.name} to ({new_x}, {new_y}) - {shape_name}")

            # Check for immediate combat
            if (new_x, new_y) != self.dungeon.player_start and new_tile.monster and new_tile.monster.alive:
                print(f"You encounter a {new_tile.monster.type.value}!")
                # Monster gets first attack
                self.monster_attack_player(new_tile.monster)
                return

            # Check for loot
            if new_tile.loot:
                self.get_loot(new_tile.loot)
                new_tile.loot = None
                # If this was a lair, it becomes stairs after looting
                if new_tile.type == TileType.LAIR:
                    new_tile.type = TileType.STAIRS
                    print("The lair has been looted and becomes stairs!")

            # Reveal vision from new position
            self.reveal_vision(new_x, new_y)
            
        else:
            print("There's no door in that direction!")
    
    def generate_and_reveal_connected_tiles(self, x, y, tile):
        """Generate and reveal tiles connected to this tile based on its doors"""
        for direction in Direction:
            if direction != tile.entrance_direction and tile.doors[direction]:
                self.generate_connected_tile_in_direction(x, y, direction)
    
    def generate_connected_tile_in_direction(self, x, y, direction):
        """Generate a tile in the specified direction if it doesn't exist"""
        dx, dy = direction.value
        new_x, new_y = x + dx, y + dy
        
        # Check if we're within bounds
        if abs(new_x) > 4 or abs(new_y) > 4:
            return None
            
        # Check if tile already exists
        if (new_x, new_y) in self.dungeon.grid:
            return self.dungeon.grid[(new_x, new_y)]
        
        # Generate the tile
        new_tile = self.generate_new_tile(new_x, new_y, direction)
        if new_tile:
            new_tile.revealed = True
            return new_tile
        return None
    
    def get_left_turn(self, direction):
        """Get left turn relative to current facing direction"""
        left_turns = {
            Direction.UP: Direction.LEFT,
            Direction.LEFT: Direction.DOWN,
            Direction.DOWN: Direction.RIGHT,
            Direction.RIGHT: Direction.UP
        }
        return left_turns[direction]
    
    def get_right_turn(self, direction):
        """Get right turn relative to current facing direction"""
        right_turns = {
            Direction.UP: Direction.RIGHT,
            Direction.RIGHT: Direction.DOWN,
            Direction.DOWN: Direction.LEFT,
            Direction.LEFT: Direction.UP
        }
        return right_turns[direction]

    def generate_new_tile(self, x, y, direction):
        """Generate a new tile only when moving through a door to unexplored area"""
        # Check distance from start
        distance = abs(x) + abs(y)
        if distance > 4:
            return None
            
        # Determine if this should be boundary tile
        if distance == 4:
            if not self.dungeon.lair_location:
                self.dungeon.lair_location = (x, y)
                tile_type = TileType.LAIR
            else:
                tile_type = TileType.STAIRS
        else:
            tile_type = TileType.EMPTY
        # Roll for tile shape based on card system
        if tile_type in [TileType.STAIRS, TileType.LAIR]:
            shape = TileShape.DEAD_END
        else:
            # Use entrance-aware roll to favor shapes that make sense
            entrance_direction = self.dungeon.get_opposite_direction(direction)
            shape = self.dungeon.roll_tile_shape_for_entrance(entrance_direction)

        # Create the tile with proper shape
        new_tile = Tile(x, y, tile_type, shape)
        self.dungeon.grid[(x, y)] = new_tile

        # Configure doors based on shape and entrance direction
        entrance_direction = self.dungeon.get_opposite_direction(direction)
        new_tile.configure_doors_from_shape(entrance_direction)

        # Populate if needed
        if tile_type == TileType.LAIR:
            self.dungeon.populate_lair(new_tile)
        elif tile_type == TileType.EMPTY:
            self.dungeon.populate_tile(new_tile)
        
        return new_tile

    def display_map_legend(self):
        print("\n--- Map Legend ---")
        print("P = Player")
        print("M = Monster")
        print("! = Loot")
        print("S = Stairs")
        print("L = Lair")
        print("? = Unexplored")
        print("# = Wall")
    
    def handle_attack(self):
        current_tile = self.dungeon.grid.get((self.player.x, self.player.y))

        # Check for adjacent monsters
        adjacent_monsters = []
        for direction in Direction:
            if current_tile and current_tile.doors[direction]:  # Only attack through doors
                dx, dy = direction.value
                check_x, check_y = self.player.x + dx, self.player.y + dy
                adj_tile = self.dungeon.grid.get((check_x, check_y))
                if adj_tile and adj_tile.monster and adj_tile.monster.alive:
                    adjacent_monsters.append((adj_tile.monster, direction))
        
        if adjacent_monsters:
            print("\nAdjacent monsters:")
            for i, (monster, direction) in enumerate(adjacent_monsters, 1):
                print(f"{i}. {monster.type.value} to the {direction.name}")
            
            try:
                choice = int(input("Choose monster to attack (number): ")) - 1
                if 0 <= choice < len(adjacent_monsters):
                    monster, _ = adjacent_monsters[choice]
                    self.player_attack_monster(monster)
                    
                    # Monster counter-attacks if still alive
                    if monster.alive:
                        self.monster_attack_player(monster)
                else:
                    print("Invalid choice!")
            except ValueError:
                print("Please enter a number!")
        else:
            print("No monsters in adjacent tiles to attack!")
    
    def reveal_line_of_sight(self, direction, max_distance=9):
        """Reveal tiles in a straight line in the given direction up to max_distance, stopping at walls"""
        dx, dy = direction.value
        for distance in range(1, max_distance + 1):
            # Check the previous tile to see if line of sight is blocked
            prev_x = self.player.x + dx * (distance - 1)
            prev_y = self.player.y + dy * (distance - 1)
            prev_tile = self.dungeon.grid.get((prev_x, prev_y))

            # If the previous tile doesn't have a door in this direction, line of sight is blocked
            if prev_tile and not prev_tile.doors[direction]:
                break

            check_x = self.player.x + dx * distance
            check_y = self.player.y + dy * distance

            # Check bounds
            if abs(check_x) > 4 or abs(check_y) > 4:
                break

            # Reveal this tile (generate if doesn't exist)
            tile = self.dungeon.grid.get((check_x, check_y))
            if tile is None:
                # Generate new tile for line of sight
                boundary_distance = max(abs(check_x), abs(check_y))
                if boundary_distance == 4:
                    # Boundary tiles are either LAIR (first one) or STAIRS
                    if self.dungeon.lair_location is None:
                        tile_type = TileType.LAIR
                        self.dungeon.lair_location = (check_x, check_y)
                    else:
                        tile_type = TileType.STAIRS
                    shape = TileShape.DEAD_END
                else:
                    tile_type = TileType.EMPTY
                    shape = TileShape.STRAIGHT
                tile = Tile(check_x, check_y, tile_type, shape)
                entrance_direction = self.dungeon.get_opposite_direction(direction)
                tile.configure_doors_from_shape(entrance_direction)
                self.dungeon.grid[(check_x, check_y)] = tile
                # Populate the new tile
                if tile_type == TileType.LAIR:
                    self.dungeon.populate_lair(tile)
                elif tile_type == TileType.EMPTY:
                    self.dungeon.populate_tile(tile)
                # STAIRS tiles are not populated
            tile.revealed = True

    def handle_ranged_attack(self):
        """Handle ranged attacks in straight lines up to 3 tiles away"""
        # First, reveal line of sight in all directions
        for direction in Direction:
            self.reveal_line_of_sight(direction)

        # Find all monsters in straight lines within range
        ranged_targets = []

        for direction in Direction:
            dx, dy = direction.value
            for distance in range(1, 4):  # 1-3 tiles away
                check_x = self.player.x + dx * distance
                check_y = self.player.y + dy * distance

                # Check if tile exists and is revealed
                tile = self.dungeon.grid.get((check_x, check_y))
                if tile and tile.revealed:
                    if tile.monster and tile.monster.alive:
                        ranged_targets.append((tile.monster, direction, distance))
                        break  # Stop at first monster in this line
                    # Continue checking further if no monster but tile exists
                else:
                    break  # Stop if tile doesn't exist or isn't revealed

        if ranged_targets:
            print("\nRanged attack targets:")
            for i, (monster, direction, distance) in enumerate(ranged_targets, 1):
                print(f"{i}. {monster.type.value} {distance} tiles to the {direction.name}")

            try:
                choice = int(input("Choose target to attack (number): ")) - 1
                if 0 <= choice < len(ranged_targets):
                    monster, _, _ = ranged_targets[choice]
                    self.player_attack_monster(monster, ranged=True)

                    # Monster counter-attacks if still alive and adjacent
                    if monster.alive:
                        # Check if monster is adjacent (distance 1)
                        monster_tile = None
                        for (x, y), tile in self.dungeon.grid.items():
                            if tile.monster == monster:
                                monster_tile = tile
                                break

                        if monster_tile:
                            dx = abs(monster_tile.x - self.player.x)
                            dy = abs(monster_tile.y - self.player.y)
                            if dx + dy == 1:  # Adjacent
                                self.monster_attack_player(monster)
                else:
                    print("Invalid choice!")
            except ValueError:
                print("Please enter a number!")
        else:
            print("No monsters in range for ranged attack!")
    
    def use_stairs(self):
        if self.dungeon.grid.get((self.player.x, self.player.y)).type == TileType.STAIRS:
            print("\nYou descend to the next floor...")
            self.current_floor += 1
            self.dungeon = Dungeon(self.current_floor)
            self.player.floor_level = self.current_floor
            # Reset player position to start of new floor
            self.player.x, self.player.y = self.dungeon.player_start
        else:
            print("There are no stairs here!")
    
    def game_loop(self):
        print("=== One Dice Dungeon Delve ===")
        print("Your village needs a hero! Map the dungeon and slay the Red Dragon!")
        self.display_map_legend()

        while not self.game_over and not self.victory:
            # Clear monsters attacked this turn at start of each player turn
            self.monsters_attacked_this_turn = set()

            self.display_map()
            self.display_player_status()
            self.display_gear()

            print("\nActions: WASD to move, T to attack, R for ranged attack, F for stairs, Q to quit")

            choice = self.get_single_key()

            if choice in ['W', 'A', 'S', 'D']:
                direction_map = {'W': Direction.UP, 'A': Direction.LEFT,
                               'S': Direction.DOWN, 'D': Direction.RIGHT}
                self.handle_move(direction_map[choice])

            elif choice == "T":
                self.handle_attack()

            elif choice == "R":
                self.handle_ranged_attack()

            elif choice == "F":
                self.use_stairs()

            elif choice == "Q":
                print("Thanks for playing!")
                break
            else:
                print("Invalid action! Use WASD for movement, T/R/F for actions, Q to quit.")

            # Handle adjacent monster attacks after player action
            if not self.game_over:
                self.handle_adjacent_monster_attacks()

            # Check for game over
            if self.player.current_hp <= 0:
                self.game_over = True
                print(f"\nGame Over! You reached floor {self.current_floor}")
                print(f"Max floor mapped: {self.player.max_floor_mapped}")

        if self.victory:
            print("\n*** VICTORY! ***")
            print("You have slain the Red Dragon and saved your village!")

# Run the game
if __name__ == '__main__':
    game = Game()
    game.game_loop()
