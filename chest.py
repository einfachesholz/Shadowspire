import pygame
import random

#items avaliable in chests
ITEMS = ['potion_1', 'potion_2']

class Chest:
    def __init__(self, pos, chest, frames):
        self.pos = pos
        self.image = chest
        self.frames = frames
        self.opened = False
        self.count = 0

        #selects item from list at random
        self.item = random.choice(ITEMS)

    def rect(self):
        return pygame.Rect(self.pos[0] * 16, self.pos[1] * 16, self.image.get_width(), self.image.get_height())

    def update(self, player_rect, items_list, counter):
        if (self.rect()).colliderect(player_rect):
            #checks whether player has collided with the chest
            self.opened = True

        if self.opened and self.frames.done == False:
            #chest will then have an animation
            self.image = self.frames.animate()

        if self.frames.done == True:
            #once the animation has been completed, the chest's image will be set to an open one
            self.image = self.frames.images[-1]
            if self.count == 0:
                #adds items to items list
                items_list['item' + str(counter)] = {'pos':(((self.pos[0] * 16) + random.randint(-5,5), (self.pos[1] * 16) + random.randint(0,5))),
                                                     'type': self.item}
                self.count = 1

                return counter + 1
        return counter

    def render(self, screen, offset):
        #renders the chest onto the screen
        screen.blit(self.image, (self.pos[0] * 16 - offset[0], self.pos[1] * 16 - offset[1])) 

