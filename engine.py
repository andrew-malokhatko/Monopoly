from icecream import install
install()
import pathlib
import pygame 
import json
from pathlib import Path
import random
from server import *

dice = Dice()
timer = pygame.time.Clock()

players = pygame.sprite.Group()


while True:
    if color_initialized[0]:
        player = Player(player_args[0] ,100, 100, player_args[1], blocks, screen)
        players.add(player)
        break

def roll_dice():
    player.move()

def twoK():
    giveaway(2000)

def fivK():
    giveaway(5000)

def giveaway(money):
    global player_bal
    bal = player_bal[0]
    player_bal[0] = (bal + money)

def chance():
    giveaway(random.randint(-1000, 1000))

def bet():
    pass

def duti():
    player.balance -= player.companies*200

def skip_turn():
    pass


lbls = pygame.sprite.Group()
btns = pygame.sprite.Group()
evblocks = pygame.sprite.Group()
btn = Button(750, 400, 95, 50, (255,255,255), screen, roll_dice, "ROLL", (0,0,0))
balLabel = Label(100, 100, 200, 200, (255,255,255,), screen, str(player.balance), (100, 100, 100))
start = eventBlock(1150, 600, (255,20,0), screen, 0, "START", skip_turn, (255,255,255))
twoT = eventBlock(1075, 600, (100,200,0), screen, 1, "+2000", twoK, (255,255,255))
ch = eventBlock(775, 600, (100,200,0), screen, 5, "chance", chance, (255,255,255))
ch1 = eventBlock(475, 75, (100,200,0), screen, 18, "chance", chance, (255,255,255))
ch2 = eventBlock(1075, 75, (100,200,0), screen, 26, "chance", chance, (255,255,255))
twoT1 = eventBlock(475, 600, (100,200,0), screen, 9, "+2000", twoK, (255,255,255))
fivB = eventBlock(775, 75, (100,200,0), screen, 22, "+5000", fivK, (255,255,255))
tavern = eventBlock(400, 600, (255,20,0), screen, 10, "tavern", bet, (255,255,255))
duties = eventBlock(400, 75, (255,20,0), screen, 17, "duties", duti, (255,255,255))
skipturn = eventBlock(1150, 75, (255,20,0), screen, 27, "skip", skip_turn, (255,255,255))
btns.add(btn)
lbls.add(balLabel)
evblocks.add(start, twoT, twoT1, ch, ch1, ch2, fivB, tavern, duties, skipturn)
blocks.add(start, twoT, twoT1, ch, ch1, ch2, fivB, tavern, duties, skipturn)
player.getBtns(btns)

game_on = True
click = False

while game_on:
    screen.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT or game_over[0]:
            game_on = False
        if event.type == MOUSEBUTTONDOWN:
            click = True
    btns.update(click)
    lbls.update(str(player.balance) + " $")
    companies.update()
    enemies.update()
    evblocks.update(player.tile)
    enemies.draw(screen)
    players.update(screen)
    click = False
    timer.tick(60)
    pygame.display.flip()