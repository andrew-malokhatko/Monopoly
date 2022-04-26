import random
from unicodedata import name
import pygame
from pygame.locals import *
from collections import namedtuple
import json
from pathlib import Path
from threading import Lock
pygame.font.init()

print_lock = Lock()

myfont = pygame.font.SysFont(pygame.font.get_default_font(), 25)
payfont = pygame.font.SysFont(pygame.font.get_default_font(), 15)
btnFont = pygame.font.SysFont(pygame.font.get_default_font(), 50)
bought_companies = []
player_pos = [300, 300]
player_bal = [15000]
SCREENSIZE = (1600, 900)
self_color = [0,0,0]
self_name = ""
player_args = []
tile = [0]
game_over = [False]
color_initialized = [False]
screen = pygame.display.set_mode(SCREENSIZE)
enemies = pygame.sprite.Group()
Event = namedtuple("Event", ["type", "data"])
buffer: list[Event] = []
game_in_progress = [False]

class Player(pygame.sprite.Sprite):
    def __init__(self,name, pos_x, pos_y, color, blocks, surf):
        super().__init__()
        self.pos = (pos_x, pos_y)
        self.color = color
        self.surf = surf
        self.name = name
        self.blocks = blocks
        self.balance = 15000
        self.companies = 0
        self.tile = 0
        self.paid = False
        self.buyBtn = Button(100, 200, 100, 100, (200,200,200), self.surf, self.buy, "BUY", (255,255,255))
        self.image = pygame.Surface((30, 30))
        self.image.fill(color)
        self.rect = self.image.get_rect(center = self.pos)

    def update(self, surface):
        global tile
        global player_bal
        self.tile = tile[0]
        self.balance = player_bal[0]

        for block in self.blocks:
            if block.index == self.tile:
                self.pos = (block.pos[0] + 40, block.pos[1] + 20)
                surface.blit(self.image, self.pos)
                try:
                    block.group = block.group
                    surface.blit(self.buyBtn.image, self.buyBtn.pos)
                    surface.blit(self.buyBtn.textsurface, self.buyBtn.pos)
                except:
                    pass

    def getBtns(self, btns):
        self.btns = btns
        self.btns.add(self.buyBtn)
                
    def buy(self):
        global player_args
        block = self.zaloopa()
        if block != None:
            try:
                with print_lock:
                    ic(player_args)
                buffer.append(Event(type = "buy", data = (self.balance, block.name, block.group, player_args[0])))
            except:
                with print_lock:
                    ic("tried to buy chance")

    def pay(self):
        block = self.zaloopa()
        if block != None:
            try:
                block.group = block.group
            except:
                return
            buffer.append(Event(type = "pay", data = (self.balance, block.name, block.pays, player_args[0])))################

    def dima(self, block):
        for company in bought_companies:
                if company[1] == block.name:
                    return False
        return True

    def zaloopa(self):
        for block in self.blocks:
            if block.index == self.tile:
                return block
        return None

    def move(self):
        global player_args
        buffer.append(Event(type = "move", data = (self.tile, random.randint(1,6))))
        self.pay()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, color, surf, name):
        super().__init__()
        self.pos = [pos_x, pos_y]
        self.color = color
        self.tile = 0
        self.surf = surf
        self.name = name
        self.image = pygame.Surface((30,30))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self):
        for block in blocks:
            if self.tile == block.index:
                self.pos = list(block.pos)
                break
        self.rect = self.image.get_rect(center=self.pos)

class Dice(pygame.sprite.Sprite):
    def roll(self):
        return random.randint(1, 6)

class Block(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, width, height, color, surface, index = None):
        super().__init__()
        self.index = index
        self.pos = (pos_x, pos_y)
        self.size = (width, height)
        self.color = tuple(color)
        self.surface = surface
        self.image = pygame.Surface(self.size)
        self.image.fill(self.color)
        self.surface.blit(self.image, self.pos)

class Label(Block):
    def __init__(self, pos_x, pos_y,width, height, color, surface, text, textcolor):
        super().__init__(pos_x, pos_y,width, height, color, surface)
        self.text = text
        self.textcolor = textcolor
        self.surface = surface
        self.textsurf = btnFont.render(self.text, True, self.textcolor, None)
        
    def update(self, text):
        self.textsurf = btnFont.render(text, True, self.textcolor, None)
        self.surface.blit(self.textsurf, self.pos)
        



class Button(Block):
    def __init__(self, pos_x, pos_y,width, height, color, surface, func, text, textcolor):
        super().__init__(int(pos_x), int(pos_y), width, height, color, surface)
        self.func = func
        self.text = text
        self.textcolor = textcolor
        self.surf = pygame.Surface(self.size)
        self.textsurface = btnFont.render(self.text, True, (self.textcolor), None)
        self.rect = self.surf.get_rect(topleft = self.pos)

    def update(self,wereclicked = False):
        self.draw()
        if wereclicked:
            point = pygame.mouse.get_pos()
            if(self.rect.collidepoint(point)):
                self.func()

    def draw(self):
        self.surface.blit(self.image, self.pos)
        self.surface.blit(self.textsurface, self.pos)

class Company(Block):
    def __init__(self, pos_x, pos_y, color, price, name, group, pay1, pay2, pay3, surface, index):
        super().__init__(int(pos_x), int(pos_y), 75, 75, color, surface, int(index))
        self.rect = self.image.get_rect(center=self.pos)
        self.price = price
        self.name = name
        self.group = group
        self.pays = (pay1, pay2, pay3)
        

    def update(self):
        for company in bought_companies:
            if self.name == company[1]:
                self.color = company[2]
        self.draw()

    def draw(self):
        self.image.fill(self.color)
        self.surface.blit(self.image, self.pos)

        self.textsurface = myfont.render(self.name, True, (255,255,255), None)
        self.surface.blit(self.textsurface, self.pos)

        self.paysurf1 = myfont.render(str(self.pays[0]), True, (255,255,255), None)
        self.surface.blit(self.paysurf1, (self.pos[0],self.pos[1]+20))

        self.paysurf2 = myfont.render(str(self.pays[1]), True, (255,255,255), None)
        self.surface.blit(self.paysurf2, (self.pos[0],self.pos[1]+40))

        self.paysurf3 = myfont.render(str(self.pays[2]), True, (255,255,255), None)
        self.surface.blit(self.paysurf3, (self.pos[0],self.pos[1]+60))


class eventBlock(Block):
    def __init__(self, pos_x, pos_y, color, surface, index, text, func, textcolor):
        super().__init__(pos_x, pos_y, 75, 75, color, surface, index)
        self.text = text
        self.textcolor = textcolor
        self.done = False
        self.textsurf = myfont.render(self.text, True, self.textcolor, None)
        self.func = func

    def update(self, player_pos):
        self.draw()
        if player_pos == self.index:
            if not self.done:
                self.func()
            self.done = True
        if player_pos != self.index:
            self.done = False

    def draw(self):
        self.surface.blit(self.image, self.pos)
        self.surface.blit(self.textsurf, self.pos)

companies = pygame.sprite.Group()
blocks = pygame.sprite.Group()

folder = Path(__file__).parent
file = folder / "companies.txt"
with open(file, 'r') as f:
    f = json.loads(f.read())
    for element in f:
        companies.add(Company(element["pos_x"],element["pos_y"], element["color"], element["price"], element["name"], element["group"], element["pay1"], element["pay2"], element["pay3"], screen, element["index"]))
        blocks.add(Company(element["pos_x"],element["pos_y"], element["color"], element["price"], element["name"], element["group"], element["pay1"], element["pay2"], element["pay3"], screen, element["index"]))

