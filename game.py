import pygame
import sys
import random

import utils
import menus
import databases
from tilemap import Tilemap
from entity import Player, Enemy
from chest import Chest

#initialises pygame, the display we will use and the clock
pygame.init()
display = pygame.display.set_mode((640,480))
clock = pygame.time.Clock()


images = {
    #dictionaries containing our images
    'floor': utils.get_images('floors'),
    'wall': utils.get_images('walls'),

    'background': pygame.transform.scale(utils.get_image('background.png'), (640,480)),
    'menu': pygame.transform.scale(utils.get_image('menu.png'), (640, 480)),
    'login/create_menu': pygame.transform.scale(utils.get_image('logincreate.png'), (640, 480)),
    'instructions': pygame.transform.scale(utils.get_image('instructions.png'), (640, 480)),
    'death': pygame.transform.scale(utils.get_image('death.png'), (640, 480)),
    'leaderboard': pygame.transform.scale(utils.get_image('leaderboard.png'), (640, 480)),
    'leaderboard_logo': utils.get_image('leaderboard_logo.png'),
    'logo': utils.get_image('logo.png'),

    'player/idle': utils.Animation(utils.get_images('player/idle'), 0.1),
    'player/run': utils.Animation(utils.get_images('player/run'), 0.2),

    'goblin/idle': utils.Animation(utils.get_images('goblin/idle'), 0.1),
    'goblin/run': utils.Animation(utils.get_images('goblin/run'), 0.2),
    'goblin/death': utils.Animation(utils.get_images('goblin/death'), 0.15, True),
    'goblin/alert': utils.get_image('goblin/alert.png'),

    'skeleton/idle': utils.Animation(utils.get_images('skeleton/idle'), 0.1),
    'skeleton/run': utils.Animation(utils.get_images('skeleton/run'), 0.2),
    'skeleton/death': utils.Animation(utils.get_images('skeleton/death'), 0.15, True),
    'skeleton/alert': utils.get_image('skeleton/alert.png'),
            
    'sword': utils.get_image('weapons/sword.png'),
    'sword/swing': utils.Animation(utils.get_images('weapons/sword_swing'), 0.15, True),

    'chest': utils.get_image('chests/chest.png'),
    'chest_open': utils.Animation(utils.get_images('chests/chest_open'), 0.1, True),

    'potion_1': utils.get_image('items/potion_1.png'),
    'potion_2': utils.get_image('items/potion_2.png'),

    'death_particles': utils.Animation(utils.get_images('particles'), 0.1, True),

    'heart_bar': utils.get_images('heart_bar'),
}

class Game:
    def __init__(self, display, assets):         
        #sets up the display
        pygame.display.set_caption('Shadowspire')
        self.display = display
        #we use 2 surfaces, we will use self.screen for adding the map and other things and then scale it up to self.display
        self.screen = pygame.Surface((160,120))
        #this creates a 'zoomed' effect for the camera, the camera is zoomed in

        self.images = assets
        self.sfx = {
            #dictionary containing our sound effects
            'attack': pygame.mixer.Sound('audio/attack.wav'),
            'death': pygame.mixer.Sound('audio/death.wav'),
            'heal': pygame.mixer.Sound('audio/heal.wav'),
            'hit': pygame.mixer.Sound('audio/hit.wav'),
            'enemy_attack': pygame.mixer.Sound('audio/enemy_attack.wav'),
            'sword': pygame.mixer.Sound('audio/sword.wav'),
            'escape': pygame.mixer.Sound('audio/escape.wav')
        }

        #our lists of background music paths 
        self.background_music = ['audio/background_1.wav','audio/background_2.wav','audio/background_3.wav',]

        self.account_record = ''

        #controls x/y movement
        self.movement = [0,0,0,0]
        #stores offset
        self.scroll = [0,0]
        self.screenshake = False
        self.level = 1

        #these variables help make the game get progressively harder
        self.rects = 4
        self.number_of_rooms = [2]
        self.number_of_chests = [1]
        self.enemies_count = [1,2,3]

        self.setup()
        #creates an instance of the player class
        self.player = Player(self.start, (16,13), self, 'player', 3)
        self.clock = pygame.time.Clock()

        self.running = True

    def reset(self):
        #this subroutine 'resets' many of the variables so that the player starts back from square 1
        self.running = True
        self.level = 1

        self.setup()
        #self.movement = [left, right, up, down], 0 means not moving in that direction, 1 means moving in that direction
        self.movement = [0,0,0,0]
        self.screenshake = False

        self.player.pos = list(self.start)
        self.player.dead = False
        self.player.inventory = [['sword', 1], [None, 1 ], [None, 1]]
        self.player.escaped = False
        self.player.health = 3

        self.rects = 4
        self.number_of_rooms = [2]
        self.number_of_chests = [1]
        self.enemies_count = [1,2,3]
  
    def setup(self):
        #this subroutine is used for generating new maps once players have escaped a level
        if self.level % 5 == 0 and self.level <= 30:
            #adds more rooms but also adds more enemies every 5 levels
            self.rects += 5
            self.number_of_rooms.append(self.number_of_rooms[-1] + 1)
            self.enemies_count.append(self.enemies_count[-1] + 1)

            if self.level % 10 == 0:
                #we split the array in half, since the array is ordered we use the sub-array to the right of the split point
                midpointr = len(self.number_of_rooms) // 2  
                midpointe = len(self.enemies_count) // 2
                #This makes the game harder since we use chance to pick how many rooms/enemies
                self.number_of_rooms = self.number_of_rooms[midpointr:]
                self.enemies_count = self.enemies_count[midpointe:]
                #we add more chests every 10 levels
                self.number_of_chests.append(len(self.number_of_chests) + 1)

        rooms = utils.generate_rects(self.rects)
        #only generates rooms if there are more than x rooms in the rooms list
        while len(rooms.queue) < random.choice(self.number_of_rooms):
            rooms = utils.generate_rects(self.rects)

        #creates an instance of the Tilemap class
        self.tilemap = Tilemap(rooms, random.choice(self.number_of_chests))
        #responsible for generating a tilemap for our rooms    
        self.tilemap.generate_tilemap(random.choice(self.enemies_count))
    
        self.chests = []
        self.items = {}
        self.particles = []
        self.enemies = []

        #gives each chest a unique number to identify itself in the chest dictionary
        self.counter = 0

        for location in self.tilemap.chest_locations:
            #adds chests to self.chests based on the locations generated
            position = self.tilemap.chest_locations[location]
            self.chests.append(Chest(position, self.images['chest'], self.images['chest_open'].copy()))

        #starting room centre location and ending room centre location
        self.start = ((int(self.tilemap.start_room.center[0] // 16)) * 16, (int(self.tilemap.start_room.center[1] // 16)) * 16)
        self.end = ((int(self.tilemap.end_room.center[0] // 16)) * 16, (int(self.tilemap.end_room.center[1] // 16)) * 16)
        
        self.enemies_health = [1,2,3]
        self.enemies_damage = [0.5, 1]
        if self.level > 30:
            self.enemies_health = [2,3]
            self.enemies_damage = [1, 1.5]

        for spawn in self.tilemap.enemies_spawn:
            if abs(random.random()) < 0.7:
                #pick a random type of enemy
                entity = random.choice(['goblin', 'skeleton'])
                #pick a random range for the enemy
                range = random.choice([75, 100, 125, 150])
                position = self.tilemap.enemies_spawn[spawn]
                #add new instance of enemy class to self.enemies
                self.enemies.append(Enemy(position, (16,13), self, entity, random.choice(self.enemies_health), 
                                          random.choice(self.enemies_damage), range))

        self.transition = -30
        self.screenshake = False

    def run(self):
        if self.account_record.high_score == 0:
            #we add a new leaderboard record for our account if this is the player's first time playing
            databases.upsert_highscore(self.account_record.userid, self.account_record.high_score)

        #this loads in a random background music
        pygame.mixer.music.load(random.choice(self.background_music))
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(0)

        while self.running:
            if not pygame.mixer.music.get_busy():
                #if the current music has finised playing, we select a new background music to play
                pygame.mixer.music.load(random.choice(self.background_music))
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(0)

            self.attack_count = 0
            if self.player.escaped:
                #if the player has escaped, we play an escape sound effect
                if self.transition == 0:
                    #this ensures the sound effect is played only once
                    self.sfx['escape'].set_volume(0.4)
                    self.sfx['escape'].play(0)

                self.transition += 1
                if self.transition > 30:
                    #once the first stage of the transition has ended, we generate the next level
                    self.level += 1
                    self.setup()
                    self.player.escaped = False
                    self.player.pos = list(self.start)

            if self.transition < 0:
                self.transition += 1

            #self.screen.fill 'refreshes' the screen
            self.screen.fill((0,0,0))
   
            #responsible for calculating the offsets that allow our camera to move
            self.scroll[0] += (self.player.rect().centerx - self.screen.get_width() / 2 - self.scroll[0]) / 15
            self.scroll[1] += (self.player.rect().centery - self.screen.get_height() / 2 - self.scroll[1]) / 15
            #offsets are calculated where player is always at centre of screen
            render_scroll = list((int(self.scroll[0]), int(self.scroll[1])))

            if self.screenshake:
                #adds a screenshake when the player is under attack
                render_scroll[0] += random.randint(-5, 5) 
                render_scroll[1] += random.randint(-5, 5) 
                
            #renders background image to screen
            self.screen.blit(self.images['background'], (0,0))
            #renders the tilemap onto the screens
            self.tilemap.render(self, offset=render_scroll)

            for chest in self.chests:
                #responsible for rendering and updating chests
                self.counter = chest.update(self.player.rect(), self.items, self.counter)
                chest.render(self.screen, render_scroll)

            inv_count = 0
            for item in self.items.copy():
                #responsible for updating and rendering items spawned by open chests
                item_type = self.items[item]['type']
                #gets the distance between item and player
                distance = utils.return_distance(self.player.pos, self.items[item]['pos'])
                if distance < 30:
                    #items move towards player if they're nearby
                    new_pos = utils.move_towards(self.player.pos, self.items[item]['pos'], 0.3)
                    self.items[item]['pos'] = new_pos
                
                self.screen.blit(self.images[item_type] ,
                    (self.items[item]['pos'][0] - render_scroll[0], self.items[item]['pos'][1] - render_scroll[1]))
                
                if distance < 5:
                    #if items are within range, they are added to player inventory and removed from the items dictionary
                    for x in range(len(self.player.inventory)):
                        #handles occasion that there is same item already in players inventory
                        if self.player.inventory[x][0] == self.items[item]['type'] and self.player.inventory[x][1] <= 8:
                            self.player.inventory[x][1] += 1
                            break
                        #if there is an empty space in inventory, item will fill up that space
                        elif self.player.inventory[x][0] == None:
                            self.player.inventory[x] = [self.items[item]['type'], 1]
                            break
                        else:
                            #inventory slot already taken by another item
                            inv_count += 1
                    if inv_count != 3:
                        #we remove item from self.items since it is now in the player's inventory
                        del self.items[item]

            self.player.update(self.tilemap, self.movement, self.enemies, self.end)

            for enemy in self.enemies:
                #responsible for rendering/ updating enemies
                enemy.update(self.tilemap, self.player, self.player.weapon)
                if not enemy.despawn:
                    #we keep rendering the enemy until it has despawned (killed)
                    enemy.render(self.screen, render_scroll)
                else:
                    #once the enemy has despawned, we remove it from self.enemies and add death particles to self.particles
                    self.enemies.remove(enemy)
                    self.particles.append([self.images['death_particles'].copy(), enemy.pos])

                if self.player.check_attack(enemy.pos) and not enemy.dead:
                    #creates screenshake if player under attack
                    self.screenshake = True
                    self.attack_count = 1
                elif self.attack_count == 0: 
                    #ensures screenshake ends once player is no longer under attack
                    self.screenshake = False
                    
            for particle in self.particles:
                #renders the particles
                particle_image = particle[0].animate()
                self.screen.blit(particle_image, (particle[1][0] - render_scroll[0], particle[1][1] - render_scroll[1]))
                if particle[0].done:
                    #particles has finished their animation
                    self.particles.remove(particle)

            if not(self.player.escaped and self.transition > 25):
                self.player.render(self.screen, render_scroll)

            self.display.blit(pygame.transform.scale(self.screen, self.display.get_size()), (0,0))
            
            #these functions are responsible for 'drawing' our inventory, health bar and levels player has beaten to the screen
            utils.inventory(self.display, self.player.inventory, self.images, self.player.active_spot)
            utils.health_bar(self.display, self.player.health, self.images['heart_bar'])
            utils.levels(self.display, self.level)

            if self.transition:
                #adds a transition effect when going from one level to another
                transition_surf = pygame.Surface(self.display.get_size())
                pygame.draw.circle(transition_surf, (255,255,255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 14)
                transition_surf.set_colorkey((255,255,255))
                self.display.blit(transition_surf, (0,0))

            #handles user events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    #scenario for closing the application/ exiting out of application
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    #handles movement/ allows players to move based on WASD keys
                    # 1 means the player is moving in that direction, 0 means the player is not moving in that direction
                    if event.key == pygame.K_a and self.player.health > 0:
                        self.movement[0] = 1
                     
                    if event.key == pygame.K_d and self.player.health > 0:
                        self.movement[1] = 1
                       
                    if event.key == pygame.K_w and self.player.health > 0:
                        self.movement[2] = 1
                      
                    if event.key == pygame.K_s and self.player.health > 0:
                        self.movement[3] = 1

                    if event.key == pygame.K_q and self.player.health > 0: 
                        #handles our attack/ healing action once the player has pressed 'q'
                        #we check what item the player is currently holding and decide what action to do
                        if self.player.item == 'sword':
                            self.player.weapon.attack()
                        elif self.player.item == 'potion_1':
                            self.player.heal(1)
                        elif self.player.item == 'potion_2':
                            self.player.heal(0.5)
                        
                    if event.key == pygame.K_t:
                        #handles the player wanting to throw an item except for sword
                        if self.player.item != 'sword' and self.player.item != None:
                            self.player.inventory[self.player.active_spot][1] = max(
                                0, self.player.inventory[self.player.active_spot][1] - 1)
                            #adds the item being thrown to our items dictionary
                            self.items[self.counter] = {'pos': ((self.player.pos[0] + random.randint(-10,10), self.player.pos[1] + random.randint(-8,8))),
                                                        'type': self.player.item}
                            self.counter += 1

                        if self.player.inventory[self.player.active_spot][1] == 0:
                            #if we have no more of that item left, we ensure that it's spot in the inventory is made empty
                            self.player.inventory[self.player.active_spot] = [None, 1]
                            
                    if event.key == pygame.K_RIGHT:
                        #allows for the player to change the item they have selected
                        if self.player.active_spot == 2:
                            self.player.active_spot = 0
                        else:
                            self.player.active_spot += 1

                        if self.player.active_spot == 0:
                            #sword will always be first item in inventory slot so we will play sword sfx once we reach this first slot
                            self.sfx['sword'].set_volume(0.6)
                            self.sfx['sword'].play(0)

                    if event.key == pygame.K_LEFT:
                        #allows for the player to change the item they have selected
                        if self.player.active_spot == 0:
                            self.player.active_spot = 2
                        else:
                            self.player.active_spot -= 1

                        if self.player.active_spot == 0:
                            self.sfx['sword'].set_volume(0.6)
                            self.sfx['sword'].play(0)
          
                if event.type == pygame.KEYUP:
                    #handles movement/ allows players to move based on WASD keys
                    if event.key == pygame.K_a and self.player.health > 0:
                        self.movement[0] = 0
          
                    if event.key == pygame.K_d and self.player.health > 0:
                        self.movement[1] = 0 

                    if event.key == pygame.K_w and self.player.health > 0:
                        self.movement[2] = 0

                    if event.key == pygame.K_s and self.player.health > 0:
                        self.movement[3] = 0

            if self.player.health <= 0:
                #the player has died
                self.movement = [0,0,0,0]
                #we stop the music and player movement
                pygame.mixer.music.stop()
                if self.transition == 0:
                    #we play the death sfx and ensure it is only played once
                    self.sfx['death'].play(0)

                self.transition += 1
                
                if self.level > self.account_record.high_score:
                    #we check to see if player has beaten their highscore, if so we update their highscores to match the new value
                    self.account_record.high_score = self.level # updates player record
                    databases.upsert_highscore(self.account_record.userid, self.account_record.high_score) 
                    #updates player entry in leaderboard database

                if self.transition > 45:
                    #we display the death ui to the user
                    menus.death(self.display, self.clock, self.images, self)
 
            #updates the display
            pygame.display.update()
            #self.clock.tick(60) will mean that the def run() code will run 60 times in a second!
            self.clock.tick(60)

menus.access(display, clock, images, Game(display, images))
