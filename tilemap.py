import random
import pygame

#Dictionary Constant for handling autotiling based on neighbours surrouding a tile
AUTOTILE_MAP = {
    tuple(sorted([(0,1), (1,0)])): 3,
    tuple(sorted([(0,-1), (1,0)])): 2,
    tuple(sorted([(0,1), (-1,0)])): 4,
    tuple(sorted([(0,-1), (-1,0)])): 5,
    tuple(sorted([(0,-1), (0,1), (1,0)])): 3,
    tuple(sorted([(0,-1), (0,1), (-1,0)])): 4,
     
}

#handles special cases - where walls spawn within dungeon
SPECIAL_CASES = {
    tuple(sorted([(1,0), (-1,0), (0,1)])): 6,
    tuple(sorted([(1,0), (0,1)])): 6,
    tuple(sorted([(-1,0), (0,1)])): 6
}

#key constants used for generating walls surrounding corridors
X_KEYS = [(0,1), (0,-1), (1,0), (-1,0), (1,-1), (-1,-1), (1,1), (-1,1)]
Y_KEYS = [(1,0),(-1,0)]

class Tilemap:
    def __init__(self, rooms, chest_count):
        #using dictionaries since they are fast and we will only store the tiles required
        self.rects = {}
        self.tilemap = {}
        self.rooms = rooms
        #stores the locations where enemies will spawn
        self.enemies_spawn = {}

        #stores the locations where chests will spawn
        self.chest_locations = {}
        self.chest_count = chest_count #we use a count to limit the number of chests that can spawn

        self.start_room = rooms.queue[rooms.front_pointer]
        self.end_room = rooms.queue[rooms.rear_pointer - 1]
    
    def generate_rectsmap(self):
        #the purpose of this function is to store the position of the rooms topleft and bottomright
        x = 0
        #the coordinates get divided by 16 in order to go to tilemap coordinates
        while len(self.rooms.queue) != 0:
            #rooms positions get stored in the self.rects dictionary
            room = self.rooms.dequeue()
            self.rects[x] = {'x': int(room.x // 16), 'y': int(room.y // 16), 
                             'x2': int(room.bottomright[0] // 16), 'y2': int(room.bottomright[1] // 16)}
            x += 1
    
    def generate_tiles(self, value):
        #generates the required tile type information based on x, y position of all the possible tiles within a room
        for x in range(value['x'], value['x2']):
            for y in range(value['y'], value['y2']):
                if x == value['x'] or x == value['x2'] - 1:
                    self.tilemap[str(x) + ';' + str(y)] = {'type': 'wall','variant': 1, 'pos': (x, y)}
                elif y == value['y'] or y == value['y2'] - 1:
                    self.tilemap[str(x) + ';' + str(y)] = {'type': 'wall','variant': 1, 'pos': (x, y)}
                else:
                    self.tilemap[str(x) + ';' + str(y)] = {'type': 'floor','variant': 1, 'pos': (x, y)}
 
    def generate_tilemap(self, min_enemies):
        #generates tilemap
        centre_list = self.centres_list()
        self.generate_rectsmap()
        for rect in self.rects:
            self.generate_tiles(self.rects[rect])

        self.generate_corridors(centre_list)
        self.autotile(min_enemies)

    def centres_list(self):
        #goes through every room in the rooms list and generates tilemap centre location
        centres = []
        for room in self.rooms.queue:
            centres.append((int(room.center[0] // 16), int(room.center[1] // 16)))
            #this tilemap centre location gets added to the centres list

        return centres
    
    def generate_corridors(self, centre_list):
        centres = sorted(centre_list)

        for num in range(len(centres) - 1):
            centre_1 = centres[num]
            centre_2 = centres[num + 1]
            #gets the centre of the first room and the centre of the second room

            pos = centre_1
            #our inital position

            x_difference = (centre_2[0] - centre_1[0])
            #handles x direction generation of corridors
            for x in range(abs(x_difference)):
                if x_difference < 0:
                    pos = (centre_1[0] - (x + 1), centre_1[1])
                elif x_difference > 0:
                    pos = (centre_1[0] + (x + 1), centre_1[1])
                #the above code will generate a position for our corridor
        
                key = (str(pos[0]) + ';' + str(pos[1]))
                #this is the key for the floor tile
                self.tilemap[key] = {'type': 'floor','variant': 1, 'pos': (pos[0], pos[1])}

                for xcoord in X_KEYS:
                    #this will generate positions for the wall surrounding the corridors
                    xkey = (str(pos[0] + xcoord[0]) + ';' + str(pos[1] + xcoord[1]))

                    if xkey not in self.tilemap:
                        #adds the tile to our tilemap if there isnt a tile in that position
                        self.tilemap[xkey] =  {'type': 'wall','variant': 1, 'pos': (pos[0] + xcoord[0], pos[1] + xcoord[1])}

            if pos:
                new_x = pos[0]
            else:
                new_x = centre_1[0]
            #the above code ensures that coordinate is updated (specifcally the x coordinate)

            y_difference = (centre_2[1] - centre_1[1])
            #handles corridors being generated in the y direction
            for y in range(abs(y_difference)):
                if y_difference < 0:
                    pos = (new_x, centre_1[1] - (y + 1))
                elif y_difference > 0:
                    pos = (new_x, centre_1[1] + (y + 1))

                key = (str(pos[0]) + ';' + str(pos[1]))
                self.tilemap[key] = {'type': 'floor','variant': 1, 'pos': (pos[0], pos[1])}

                for ycoord in Y_KEYS:
                    ykey = (str(pos[0] + ycoord[0]) + ';' + str(pos[1] + ycoord[1]))

                    if ykey not in self.tilemap:
                        self.tilemap[ykey] =  {'type': 'wall','variant': 1, 
                                    'pos': (pos[0] + ycoord[0], pos[1] + ycoord[1])}

    def autotile(self, min_enemies):
        #this will go through every tile in self.tilemap and 'autotile' it
        enemy_count = 0
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            #handles autotiling for floor variant
            if tile['type'] == 'floor':

                if loc == (str(int((self.end_room.center[0] // 16)))) + ';' + str(int((self.end_room.center[1] // 16))):
                    #if location is our escape tile, we change the tile variant to match this status
                    tile['variant'] = 4

                elif self.check_valid_chestspawn((tile['pos'][0], tile['pos'][1])):
                    #if this location is valid for spawning chests, we add it to our chest locations
                    self.chest_locations[loc] = (tile['pos'][0], tile['pos'][1])

                elif abs(random.random()) < 0.05 and enemy_count < min_enemies:
                    #tile has random chance to spawn an enemy
                    self.enemies_spawn[loc] = (tile['pos'][0] * 16, tile['pos'][1] * 16)
                    enemy_count += 1

                elif abs(random.random()) < 0.15:
                    #random chance for a floor tile variant to change
                    tile['variant'] = random.choice([2,3])
                continue

            #handles autotiling for wall variant    
            neighbours = set()

            #will get tiles that are above, below, to the right or to the left of the current tile that has been selected
            for shift in [(1,0), (-1,0), (0,1), (0,-1)]:
            #essentially we are finding the wall tile's neighbours

                #generates a location based on the value of shift
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])

                #we check whether the generated location is a valid one (it is in self.tilemap)
                if check_loc in self.tilemap:
                    neighbours.add(shift)

            #puts neighbours into a format so that we can easily extract a tile variant value from AUTOTILE_MAP dictionary
            neighbours = tuple(sorted(neighbours))
            if neighbours in AUTOTILE_MAP:
                #We change the variant of the wall tile
                tile['variant'] = AUTOTILE_MAP[neighbours]

        self.specialcases()

    def specialcases(self):
         #this function handles walls that are within the dungeon, not the outer walls surrounding each room/ corrider
         for loc in self.tilemap:
            #follows similar logic to autotile function
            tile = self.tilemap[loc]

            #ensures that only wall with default variant - 1 are handled
            if tile['type'] == 'wall' and tile['variant'] in [1]:
                neighbours = set()

                for shift in [(1,0), (-1,0)]:
                    #handles left/ right
                    xcheck_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1]) 
                    if xcheck_loc in self.tilemap:
                        neighbours.add(shift)
                    
                ycheck_loc = str(tile['pos'][0] + 0) + ';' + str(tile['pos'][1] + 1)
                #checks if theres a wall tile below 
                if ycheck_loc in self.tilemap and self.tilemap[ycheck_loc]['type'] == 'wall' and self.tilemap[ycheck_loc]['variant'] in [1,6]:
                    neighbours.add((0,1))
            else:
                continue

            neighbours = tuple(sorted(neighbours))
            if neighbours in SPECIAL_CASES:
                tile['variant'] = SPECIAL_CASES[neighbours]

    def get_rects_around(self, pos):
        #creates a list containing the rectangles that have the same properties as the wall tiles
        tile_pos = (int(pos[0] // 16), int(pos[1] // 16))
        collide_rects = []
        #we check the tiles surrounding the player and see if they're walls to handle collosions
        for coord in [(-1,0), (-1,-1), (0,-1), (1,-1), (1,0), (-1,1), (0,1), (1,1)]:
            tile_key = (str(tile_pos[0] + coord[0]) + ';' + str(tile_pos[1] + coord[1]))
            tile = ((tile_pos[0] + coord[0]), (tile_pos[1] + coord[1]))

            if tile_key in self.tilemap:
                if self.tilemap[tile_key]['type'] == 'wall':
                    collide_rects.append(pygame.Rect((tile[0] * 16), (tile[1] * 16), 16, 16))

        return collide_rects 
    
    def check_valid_chestspawn(self, tile):
        #checks whether report a location can spawn a chest or not based on if it's surrounded by floor tiles
        count = 0

        for coord in [(-1,0), (-1,-1), (0,-1), (1,-1), (1,0), (-1,1), (0,1), (1,1)]:
            #we check the surrounding tiles and see if they are all floor tiles
            if len(self.chest_locations) + 1 > self.chest_count or random.random() > 0.75:
                #random chance for a location to be a valid chest location
                continue

            tile_key = (str(tile[0] + coord[0]) + ';' + str(tile[1] + coord[1]))
            if tile_key not in self.chest_locations:
                if tile_key in self.tilemap and self.tilemap[tile_key]['type'] == 'floor':
                    count += 1

        if count == 8:
            #all surrounding tiles are floor tiles so a chest can spawn
            return True
        return False

    def render(self, game, offset):
        #responsible for rendering the tilemap onto the screen
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            variant = self.tilemap[loc]['variant']
            #tiles will rendered with an offset, this gives the illusion of a camera
            game.screen.blit(game.images[tile['type']][variant - 1], (tile['pos'][0] * 16 - offset[0], tile['pos'][1] * 16 - offset[1]))
        

