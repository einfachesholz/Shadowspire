import pygame
from collections import deque
from sword import Sword
from utils import return_distance

class Entity:
    def __init__(self, pos, size, game, entity_type, health):
        self.pos = list(pos)
        self.size = size
        self.game = game
        self.entity_type = entity_type
        self.health = health
        self.dead = False

        self.action = 'idle'
        #allows the enitity to be animated
        self.frames = self.game.images[self.entity_type + '/' + self.action].copy()

        self.entity = self.frames.animate()
        #colorkey removes any colours, in this case we remove any transparent background
        self.entity.set_colorkey((0, 0, 0, 0))

        self.flip = False

    def rect(self):
        #returns a rect object of the entity, this can be used to check for collosions
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        #changes the frames used for animation
        if self.action != action:
            self.frames = self.game.images[self.entity_type + '/' + action].copy()
            self.action = action
    
    def update(self,tilemap, fmovement=(0,0,0,0), velocity=(0,0)):
        self.entity = self.frames.animate() #gets a new frame for animation
        self.entity.set_colorkey((0, 0, 0, 0))
        velocity = list(velocity)

        movement = (fmovement[1] - fmovement[0], fmovement[3] - fmovement[2])
        
        #checks whether the entity is moving or not and which animation moveset to implement
        if movement[0] != 0 or movement[1] != 0:
            self.set_action('run') 
        else:
            self.set_action('idle')

        #gets the tiles surrounding the entity
        collide_array = tilemap.get_rects_around(self.pos)
        
        #ensures that entity can not just walk out of the map
        self.pos[0] += int(movement[0] + velocity[0])  
        for rect in collide_array:
            entity_rect = self.rect()
            if entity_rect.colliderect(rect):
                #calculates an overlap and adjusts the entities's position accordingly
                if movement[0] > 0:  
                    #going right
                    overlap = entity_rect.right - rect.left
                    self.pos[0] -= overlap  
                    velocity[0] = 0
                if movement[0] < 0:
                    #going left
                    overlap = rect.right - entity_rect.left
                    self.pos[0] += overlap 
                    velocity[0] = 0 
   
        self.pos[1] += int(movement[1] + velocity[1]) 
        for rect in collide_array:
            entity_rect = self.rect()
            if entity_rect.colliderect(rect):
                if movement[1] > 0: 
                    #going down
                    overlap = entity_rect.bottom - rect.top
                    self.pos[1] -= overlap  
                    velocity[1] = 0
                if movement[1] < 0: 
                    #going up 
                    overlap = rect.bottom - entity_rect.top
                    self.pos[1] += overlap
                    velocity[1] = 0

        #checks whether the player is moving left or right and will adjust the value of self.flip
        if movement[0] < 0:
            self.flip = True
        elif movement[0] > 0:
            self.flip = False

    def render(self, screen, offset):
        #draws the player onto the screen
        screen.blit(pygame.transform.flip(self.entity, self.flip, False), (self.pos[0] - offset[0], self.pos[1] - offset[1] - 5))

    def apply_red_tint(self,image, colour):
        #applies a red filter to the current image being used
        tint = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        tint.fill(colour)

        tinted_image = image.copy()
        tinted_image.blit(tint, (0,0), special_flags=pygame.BLEND_RGB_MULT)

        return tinted_image
   
class Player(Entity):
    #player class inherits from entitiy class
    def __init__(self, pos, size, game, entity_type, health):
        super().__init__(pos, size, game, entity_type, health)
        self.damage_cooldown = 0

        self.weapon = Sword(self.game.images['sword'], self.game.images['sword/swing']) 
        self.inventory = [['sword', 1], [None, 1 ], [None, 1]] #inventory array
        self.active_spot = 0
        self.item = self.inventory[self.active_spot][0] #gets the item currently accepted
        self.full = True

        self.escaped = False

    def check_attack(self, enemypos):
        #Checks if the enemy has collided with the player
        if self.pos[0] in range(enemypos[0] - 8, enemypos[0] + 8) and self.pos[1] in range(enemypos[1] - 8, enemypos[1] + 8):
            return True
        return False
    
    def check_escape(self, end):
        #check if the player has escaped
        if self.pos[0] in range(end[0] - 8, end[0] + 8) and self.pos[1] in range(end[1] - 8, end[1] + 8):
            return True
        return False
    
    def heal(self, increment):
        if self.health < 3:
            #we increase the player's health based on potion healing, health cannot go above 3
            self.game.sfx['heal'].set_volume(0.6)
            self.game.sfx['heal'].play(0)
            self.health = min(3, self.health + increment)
            #decrease the number of potions the player selected by 1
            self.inventory[self.active_spot][1] = max(0, self.inventory[self.active_spot][1] - 1)

            if self.inventory[self.active_spot][1] == 0:
                #if there are no more of this item left, we set it's slot in the inventory to be None which represents an empty slot
                self.inventory[self.active_spot] = [None, 1]
    
    def update(self, tilemap, movement, enemies, end):
        super().update(tilemap, movement)
        if self.check_escape(end):
            self.escaped = True

        #the item the player has currently selected
        self.item = self.inventory[self.active_spot][0]
        #renders our sword to the player
        if self.item == 'sword':
            if not self.flip:   
                self.weapon.update(self.flip, (self.pos[0] + 22, self.pos[1] + 16))
            else:
                self.weapon.update(self.flip, (self.pos[0] - 6, self.pos[1] + 16))    
        else:
            #resets the sword animations and status 
            self.weapon.frames.pointer = 0
            self.weapon.attacking = False
            self.weapon.image = self.weapon.original_image     
        
        for enemy in enemies:
            if self.check_attack(enemy.pos):
                #applied red filter when enemy has collided with the player/ attacked player
                if not enemy.dead: 
                    #if the enemy is not dead but is attacking the player, we apply a red filter to the player      
                    self.entity = self.apply_red_tint(self.entity, (255,0,0))

                if self.damage_cooldown == 0 and not enemy.dead:
                    #if enemy is not dead and our damage cooldown is 0, we reduce enemies health
                    self.game.sfx['enemy_attack'].set_volume(0.6)
                    self.game.sfx['enemy_attack'].play(0)
                    #we decrease the player's health by the enemy attack damage
                    self.health -= enemy.damage
                    self.game.sfx['hit'].play(0)
                    #damage cooldown is so that the enemy attacks the player every 60 seconds
                    self.damage_cooldown = 60
            
        self.damage_cooldown = max(0, self.damage_cooldown - 1 )

    def render(self, screen, offset):
        super().render(screen, offset)
        if self.item != None:
            #handles the rendering of items the player is holding
            if self.item == 'sword':
                self.weapon.render(screen, offset)
            elif self.flip:
                screen.blit(self.game.images[self.item], (self.pos[0] - 10 - offset[0], self.pos[1] - offset[1]))
            else:
                screen.blit(self.game.images[self.item], (self.pos[0] + 10 - offset[0], self.pos[1] - offset[1]))              
     
class Enemy(Entity):
    def __init__(self, pos, size, game, entity_type, health, damage, range):
        super().__init__(pos, size, game, entity_type, health)
        self.cooldown = 0
        self.watch_cooldown = 0
        
        self.count = 0
        self.velocity = [0,0]

        self.hit = False
        self.despawn = False
        self.damage = damage
        self.range = range

        self.death_animation = self.game.images[self.entity_type + '/death'].copy()

    def update(self, tilemap, player, weapon):
        """
        
        player_pos = pygame.Vector2(pos)
        enemy_pos = pygame.Vector2(self.pos)
        
        
        if (pos[0] - self.pos[0]) in range(-50, 50) or (pos[1] - self.pos[1]) in range(-2,2):
            if (player_pos - enemy_pos) != (0,0):
                self.direction = (player_pos - enemy_pos).normalize()
            else:
                self.direction = (0,0)

            movement = []

            for z in self.direction:
                if z < 0:
                    movement.append(True)
                    movement.append(False)
                else:
                    movement.append(False)
                    movement.append(True) 
        else:
            movement = [False, False, False, False]
        
        super().update(tilemap, movement)             
        """
        self.tile = []
        movement = []
        move = (0,0)
    
        if self.health == 0:
            self.dead = True
            #allows for an enemy death animation to occur after an enemy has been killed
            self.frames = self.death_animation
        
        if self.frames.done and self.dead:
            self.despawn = True
        
        check = self.attack(player)
        if not self.dead:
            #check if player is within valid range to pathfind
            if return_distance(self.pos, player.pos) < self.range and self.cooldown == 0:
                if self.count == 0 and self.cooldown == 0:
                    self.count += 1
                    self.watch_cooldown = 15

                start = (int(self.pos[0] // 16), int(self.pos[1] //16))
                end = (int(player.pos[0] // 16), int(player.pos[1] //16))
                self.tile = self.pathfind(start, end, tilemap.tilemap)
                #This will generate movement velocities which we can manipulate in order to use with the entitites standard movement code
                if self.tile:
                    self.next_tile = self.tile[0]
                    #checks if the enemy is at the next tile
                    if (self.next_tile[0] * 16, self.next_tile[1] * 16) == (self.pos):
                        self.tile.pop(0)
                        #if so it will get a new tile from the path list
                        self.next_tile = self.tile[0]
                    
                    move = ((self.next_tile[0] * 16 - self.pos[0]), (self.next_tile[1] * 16 - self.pos[1]))
                elif not self.tile:
                    #prevents enemy from stopping once near to player, will continue towards the player
                    move = ((player.pos[0] - self.pos[0], player.pos[1] - self.pos[1])) 
            else:
                self.count = 0

        if self.cooldown < 40:
            self.hit = False 
           
        if self.cooldown != 0:
            self.cooldown = max(0, self.cooldown - 1)

        for z in move:
            if z < 0:
                movement.append(1)
                movement.append(0)
            elif z > 0:
                movement.append(0)
                movement.append(1)
            else:
                movement.append(0)
                movement.append(0)

        self.check_attacked(weapon)
        super().update(tilemap, movement, self.velocity)


        if self.hit or self.dead:
            #we apply a red tint if the enemy has been hit or is dead
            self.entity = self.apply_red_tint(self.entity, (230, 84, 128))

        elif self.watch_cooldown != 0:
            self.entity = self.game.images[self.entity_type + '/' + 'alert'] 
        
        self.watch_cooldown = max(0, self.watch_cooldown - 1)

    def pathfind(self, start, end, tilemap):
        tile_queue = deque()
        discovered = set()
        trackback = {start : None }

        found = False
        tile_queue.append(start)
        discovered.add(start)
        #performs BFS on the tilemap to find a path towards the player
        while tile_queue:
            current = tile_queue.popleft()

            for shift in [(1,0), (-1,0), (0,1), (0,-1)]:
                neighbour = (current[0] + shift[0], current[1] + shift[1])
                neighbour_check = str(current[0] + shift[0]) + ';'+ str(current[1] + shift[1])

                if neighbour_check in tilemap and neighbour not in discovered and tilemap[neighbour_check]['type'] == 'floor':
                    if neighbour == end:
                        found = True
                        break                   
                    else:
                        tile_queue.append(neighbour)
                        discovered.add(neighbour)
                        trackback[neighbour] = current
            if found:
                break

        path = []
        if found:
            #we use traceback to build our path, starting from finish and ending at the start
            while current != None:
                path.append(current)
                current = trackback[current]

        path = path[:-1]
        return path[::-1] if path else []
    
    def check_attacked(self, weapon):
        if self.cooldown == 0:
            if (self.rect()).colliderect(weapon.weaponrect) and weapon.attacking:
                #checks if the weapon has collided with the enemy and weapon is in attacking mode
                self.cooldown = 60
                self.hit = True
                
                self.game.sfx['attack'].set_volume(0.6)
                self.game.sfx['attack'].play(0)
                self.health = max(0, self.health - 1)

    def attack(self, player):
        #Once the enemy has 'attacked' the player it will go on an attack cooldown
        if not self.dead:
            if self.pos[0] in range(player.pos[0] - 6, player.pos[0] + 6) and self.pos[1] in range(player.pos[1] - 6, player.pos[1] + 6):
                self.cooldown = 60
                self.count = 0
                return True
        
        return False



                        





        


