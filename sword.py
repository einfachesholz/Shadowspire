import pygame

class Sword:
    def __init__(self, image, frames):
        self.original_image = image
        self.sword_image = image
        self.frames = frames
        self.cooldown = 0
        self.attacking = False

    def update(self, flip, pos):
        self.image = self.sword_image
        #the below code handles our attack animations
        if self.attacking:
            self.image = self.frames.animate()
            if self.frames.done == True:
                self.attacking = False
                self.frames.pointer = 0
                self.sword_image = self.original_image

        #this is our attack cooldown
        self.cooldown = max(0, self.cooldown - 1)
        
        self.pos = list(pos)
        self.center_pos = [self.pos[0] - int(self.image.get_width() / 2), self.pos[1] - int(self.image.get_height() / 2)]

        if flip:
            self.image = pygame.transform.flip(self.image, flip, False)
        else:
            self.image = pygame.transform.flip(self.image, False, False)

        self.weaponrect = pygame.Rect(self.center_pos[0], self.center_pos[1], self.image.get_width() / 2, self.image.get_height() / 2)
    
    def attack(self):
        #handles attack logic
        if self.cooldown == 0:
            self.cooldown = 60
            self.attacking = True
            self.frames.done = False

    def render(self, screen, offset):
        #draws sword to player
        screen.blit(self.image, (self.pos[0] - offset[0] - int(self.image.get_width() / 2), self.pos[1] - offset[1] - int(self.image.get_height())))
