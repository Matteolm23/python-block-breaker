import pygame as g
import random as r
import sys as s
from os import path, chdir
from math import cos,sin

chdir(path.dirname(path.realpath(__file__)))
g.init()

WIDTH, HEIGHT = 720,720
WIN = g.display.set_mode((WIDTH,HEIGHT))
screen_rect = WIN.get_rect()

class BALL():
    size = 30
    spd = 6
    vel = [spd,spd]
    collidecooldown = 0
    alive = True
    sprite = g.transform.scale(g.image.load('bricks-wip.png').convert_alpha(), (size,size))
    
    def __init__(self):
        self.x = 120#WIDTH/2 - self.size/2
        self.y = HEIGHT*.85
    
    def step(self,paddle):

        self.collidecooldown-=1

        myrect = g.Rect(self.x,self.y,self.size,self.size)
        paddlerect = g.Rect(paddle.x,paddle.y,paddle.width,paddle.height)

        if myrect.colliderect(paddlerect) and self.collidecooldown < 1:
            self.vel[1]*=-1
            self.collidecooldown = 3

        if self.x + self.size + self.vel[0] > WIDTH or self.x + self.vel[0] < 0:
            self.vel[0]*=-1
        if self.y + self.vel[1] < 0 or self.y + self.vel[1] + self.size > HEIGHT:
            self.vel[1]*=-1
            
        #if self.y + self.yspd > HEIGHT:
        #    self.alive = False

        self.x += self.vel[0]
        self.y += self.vel[1]

        myrect.clamp_ip(screen_rect)

    def draw(self):
        WIN.blit(self.sprite,g.Rect(self.x,self.y,self.size,self.size))

class PADDLE():
    width = 160
    height = 15
    spd = 6
    sprite = g.transform.scale(g.image.load('bricks-wip.png').convert_alpha(), (width,height))

    def __init__(self):
        self.x = WIDTH/2 - self.width/2
        self.y = HEIGHT*.9

    def step(self):
        keys = g.key.get_pressed()
        if (keys[g.K_LEFT] or keys[g.K_a]):
            if self.x - self.spd > 0:
                self.x -= self.spd
        if (keys[g.K_RIGHT] or keys[g.K_d]):
            if self.width + self.x + self.spd < WIDTH:
                self.x += self.spd

    def draw(self):
        WIN.blit(self.sprite,g.Rect(self.x,self.y,self.width,self.height))

class BLOCK():
    width = 75
    height = 40
    sprite = g.transform.scale(g.image.load('greenblock.png').convert_alpha(), (width,height))

    def __init__(self,xx,yy):
        self.x = xx
        self.y = yy
        self.alive = True

    def step(self,ball):

        myrect = g.Rect(self.x,self.y,self.width,self.height)
        ballrect = g.Rect(ball.x,ball.y,ball.size,ball.size)

        if myrect.colliderect(ballrect) and ball.collidecooldown < 1:
            ctop = ball.y - myrect.bottom 
            cbottom = self.y - ballrect.bottom
            cleft = ball.x - myrect.right
            cright = self.x - ballrect.right

            cy = abs(min(ctop,cbottom))
            cx = abs(min(cleft,cright))

            if cy < cx:
                ball.vel[1]*=-1
            else:
                ball.vel[0]*=-1

            self.alive = False 
            ball.collidecooldown = 1
        """
            ctop = ballrect.bottom > myrect.top and ballrect.bottom < myrect.bottom
            cbottom = ballrect.top < myrect.bottom and myrect.top > ballrect.bottom
            cright = ballrect.left < myrect.right and ballrect.left > myrect.left
            cleft = ballrect.right > myrect.left and ballrect.right < myrect.right

            if ctop or cbottom:
                ball.vel[1]*=-1
            if cright or cleft:
                ball.vel[0]*=-1

            self.alive = False 
            ball.collidecooldown = 1
        """
        

    def draw(self):
        WIN.blit(self.sprite,g.Rect(self.x,self.y,self.width,self.height))

class LOGIC():  

    br = 4
    bc = 7
    spacing = 5
    offset = (WIDTH-((BLOCK.width+spacing)*bc))/2

    def __init__(self):
        self.blocks = []
        for i in range(self.bc):
            self.blocks.append(list(BLOCK(i*(BLOCK.width+self.spacing)+self.offset,j*(BLOCK.height+self.spacing)+self.offset/1.2) for j in range(self.br)))

        self.paddle = PADDLE()
        self.ball = BALL()

    def step(self):
        self.paddle.step()
        for i in range(self.bc):
            for j in range(self.br):
                if self.blocks[i][j].alive:
                    self.blocks[i][j].step(self.ball)
        self.ball.step(self.paddle)

    def draw(self):
        WIN.fill((0,0,0))
        for i in range(self.bc):
            for j in range(self.br):
                if self.blocks[i][j].alive:
                    self.blocks[i][j].draw()
        self.paddle.draw()
        self.ball.draw()
        g.display.update()

clock = g.time.Clock()
game = LOGIC()

while(1):

    for event in g.event.get():
        if event.type == g.QUIT:
            s.exit()  

    game.step()
    game.draw()
    clock.tick(60)