import pygame
import os
import random
import math

class Animation:
    #class used for 'animating' frames
    def __init__(self, images, increment, kill=False):
        self.images = images
        self.pointer = 0
        self.increment = increment 
        self.kill = kill
        self.done = False  

    def animate(self):
        self.pointer += self.increment

        if self.pointer >= (len(self.images) - 1) + 0.5 or self.done:
            #makes sure that animations that arent loopable do not loop
            self.done = True
            image = self.images[-1]
        if self.kill and not self.done:
            image = self.images[int(self.pointer)]
        elif not self.kill:
        #self.images behaves like a circular queue
            if self.pointer > len(self.images):
                self.pointer = 0

            image = self.images[int(self.pointer)]

        return image
    
    def copy(self):
        #returns a copy of the class
        return Animation(self.images, self.increment, self.kill)
    
class PlayerDetails:
    #implements player account record
    def __init__(self, username, userid, high_score):
        self.username = username
        self.userid = userid
        self.high_score = high_score
   
def get_image(path):
    #will return an image in a form that be easily manipulated with python
    image = pygame.image.load('images/' + path).convert_alpha() 
    image.set_colorkey((0,0,0))
    
    return image

def get_images(path):
    #creates a list fulls of images from the given path which is a folder containing images
    images_list = []

    for image in os.listdir('images/' + path):
        #calls get_image to convert our image into a form that can be easily manipulated with python
        images_list.append(get_image(path + '/' + image))

    return images_list

def generate_rects(room_number):
    #function generates a queue of rect objects which will be used for generating rooms
    room_queue = Queue()
    #starter rect/ room at random coordinates and random width/ height
    count = 0

    while count <= room_number:
        #acts as a flag to see if a rect/ room gets added to the rooms list
        collision = False
        #generates a room at random coordinates and random width/ height
        room = pygame.Rect(random.randint(0, 320) , random.randint(0, 240) , random.randrange(64, 161,16), random.randrange(64, 161, 16))

        for r in room_queue.queue:
            #checks if any of the previous rooms overlap with this newly generated room
            if r.colliderect(room):
                collision = True
                break
                
        if not collision:
            #if collision if false, we add the room to our queue
            room_queue.enqueue(room)
        count += 1

    return room_queue

#class for implementing queue data structure
class Queue:
    def __init__(self):
        self.front_pointer = 0
        self.rear_pointer = 0
        self.queue = []

    def enqueue(self, data):
        #adds data to end of queue
        self.queue.append(data)
        self.rear_pointer += 1

    def dequeue(self):
        #remove data from beginning of queue
        x = self.queue.pop(0)
        self.front_pointer += 1

        return x 
    
def move_towards(pos1, pos2, fraction):
    #calculates new positions for items
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]

    distance = math.sqrt(dx**2 + dy**2)

    if distance < 1:
        return pos2
    
    dx /= distance
    dy /= distance
    
    new_x = pos2[0] + dx * fraction
    new_y = pos2[1] + dy * fraction

    return (new_x, new_y)

def return_distance(pos1, pos2):
    #calculates distance between two positions
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]

    distance = math.sqrt(dx**2 + dy**2)

    return distance  

def inventory(screen, player_inventory, images, active_spot):
    #renders an inventory bar to the screen
    pygame.draw.rect(screen, (80, 50, 50), pygame.Rect(220, 410, 192, 64))
    #draws the main rectangle

    for x in range(len(player_inventory)):
        if x == active_spot:
            #changes colour of the rectangle we draw so that the item we are selecting is a different colour
            pygame.draw.rect(screen, (110, 50, 50), pygame.Rect(220 + (x*64), 410, 64, 64))

        #essentially draws an outline for each item rectangle
        pygame.draw.rect(screen, 'black', pygame.Rect(220 + (x*64), 410, 64, 64), 2)

        if player_inventory[x][0] != None:

            if player_inventory[x][0] != 'sword':
                #for potions, we add the image based on the appropiate position in inventory
                font = pygame.font.Font('font.ttf', 16)
                image = pygame.transform.scale_by(images[player_inventory[x][0]], (2,2))
                text = font.render(str(player_inventory[x][1]), True, 'white')
                screen.blit(image, (220 + (64 * x) + 16, 428))
                screen.blit(text, (220 + (64 * x) + 8, 422))
            else:
                #this performs the same task but for the sword
                image = pygame.transform.scale_by(images[player_inventory[x][0]], (1.4,1.4))
                screen.blit(image, (220 + (64 * x) + 16, 416))

    #this draws an outline for our larger inventory rectangle
    pygame.draw.rect(screen, 'black', pygame.Rect(220, 410, 192, 64), 4)
            
def health_bar(screen, player_health, images):
    #our positions for rendering the hearts
    pos = [[24, 426], [88, 426], [152, 426]]
    count = 0

    for x in range(1, int(player_health) + 1):
        #renders the 'full' hearts we have
        image = pygame.transform.scale_by(images[2], (3,3))
        count += 1
        screen.blit(image, pos[x - 1])

    if player_health - int(player_health) == 0.5:
        #then renders any 'half' hearts we have left over
        image = pygame.transform.scale_by(images[1], (3,3))
        count += 1
        screen.blit(image, pos[int(player_health)])

    for x in range(3):
        #handles the rendering of 'empty' hearts
        if x >= count:
            image = pygame.transform.scale_by(images[0], (3,3))
            screen.blit(image, pos[x])

def levels(screen, levels):
    #draws an interface for displaying what level the user is on
    pygame.draw.rect(screen, (80, 50, 50), pygame.Rect(440, 410, 192, 64))
    font = pygame.font.SysFont('Courier', 32)
    text = 'level:' + str(levels)
    display_text = font.render(text, True, 'white')

    screen.blit(display_text, (450, 426))
    pygame.draw.rect(screen, 'black', pygame.Rect(440, 410, 192, 64), 4)

def valid_account(username, password, email):
    #checks if an account is valid or not
    if not(username) or not(password) or not(email):
        #checks if username or password or email empty
        return False
    
    numbers_list = ['0','1','2','3','4','5','6','7','8','9']
    capitals = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
                'W', 'X', 'Y', 'Z']
    password_check = 0

    if len(username) >= 16:
        #if username longer than 16 characters in length 
        return False

    if len(password) >= 6 and len(password) <= 30:
        #if password between 6 and 30 characters in length (inclusive) we tick off one of our checks
        password_check += 1
    
    for letter in password:
        #check if password has a number
        if letter in numbers_list:
            password_check += 1
            break
    
    for letter in password:
        #check if password has a capital letter
        if letter in capitals:
            password_check += 1
            break

    if password_check == 3:
        #True if password is valid otherwise returns False
        return True
    return False




    

    

    
    