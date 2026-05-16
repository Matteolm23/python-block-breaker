import pygame as g
import random as r
import sys as s
from os import path, chdir
from math import sin,cos,pi

chdir(path.dirname(path.realpath(__file__)))
g.init()

WIDTH, HEIGHT = 720,720
WIN = g.display.set_mode((WIDTH,HEIGHT))
screen_rect = WIN.get_rect()

blocksprites = [
    g.image.load('sprites/greenblock.png'),
    g.image.load('sprites/redblock.png'),
    g.image.load('sprites/cyanblock.png'),
    g.image.load('sprites/goldblock.png'),
    g.image.load('sprites/purpleblock.png')
]

def degtorad(angle):
    return angle * (pi/180)

def drawtext(text,size,color,centerx,centery):
    font = g.font.Font('HERCULESPIXELFONTREGULAR-OVAX0.OTF', size)
    rtext = font.render(str(text),True,color)
    textrect = rtext.get_rect(center = (centerx, centery))
    WIN.blit(rtext, textrect)

def checkAABBCollision(A, B):
    AisToTheRightOfB = A.left > B.right
    AisToTheLeftOfB = A.right < B.left
    AisAboveB = A.bottom < B.top
    AisBelowB = A.top > B.bottom
    return not (AisToTheRightOfB or AisToTheLeftOfB or AisAboveB or AisBelowB)

class BALL():
    size = 35
    start = False
    spd = 7
    vel = [spd*cos(0),spd*sin(0)]
    alive = True
    sprite = g.transform.scale(g.image.load('sprites/ball.png').convert_alpha(), (size,size))
    
    def __init__(self):
        self.x = WIDTH/2 - self.size/2
        self.y = HEIGHT*.85
        self.killcooldown = 0
    
    def step(self,paddle):

        self.killcooldown -= 1

        if not BALL.start:
            self.x = paddle.x + paddle.width/2 - self.size/2

            keys = g.key.get_pressed()
            if keys[g.K_UP] or keys[g.K_w]:
                angle = 40
                if keys[g.K_a] or keys[g.K_LEFT]:
                    angle *= -1
                rad = degtorad(angle-90)
                self.vel[0] = self.spd*cos(rad)
                self.vel[1] = self.spd*sin(rad)
                BALL.start = True
        else:
            myrect = g.Rect(self.x+self.vel[0],self.y+self.vel[1],self.size+self.vel[0],self.size+self.vel[1])
            paddlerect = g.Rect(paddle.x,paddle.y,paddle.width,paddle.height)

            if myrect.colliderect(paddlerect):
                angle = myrect.centerx - paddlerect.centerx
                angle = min(angle, 70)
                angle = max(angle, -70)
                if angle > 0 and angle < 5:
                    angle = 5
                if angle < 0 and angle > -5:
                    angle = -5
                rad = degtorad(angle-90)
                self.vel[0] = self.spd*cos(rad)
                self.vel[1] = self.spd*sin(rad)

            if self.x + self.size + self.vel[0] > WIDTH or self.x + self.vel[0] < 0:
                self.vel[0]*=-1
            if self.y + self.vel[1] < 0 or self.y + self.vel[1] + self.size > HEIGHT:
                self.vel[1]*=-1
                
            if self.y + self.vel[1] > HEIGHT:
                self.alive = False

            self.x += self.vel[0]
            self.y += self.vel[1]

            myrect.clamp_ip(screen_rect)

    def draw(self):
        WIN.blit(self.sprite,g.Rect(self.x,self.y,self.size,self.size))

class PADDLE():
    width = 125
    height = 15
    spd = 8

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
        g.draw.rect(WIN,(255,255,255),g.Rect(self.x,self.y,self.width,self.height))
        #WIN.blit(self.sprite,g.Rect(self.x,self.y,self.width,self.height))

class BLOCK():
    width = 75
    height = 40
    deathcooldown = 0

    def __init__(self,xx,yy):
        self.sprite = g.transform.scale(blocksprites[r.randint(0,4)].convert_alpha(), (self.width,self.height))
        self.x = xx
        self.y = yy
        self.alive = True
        self.goindown = 260

    def step(self,ball):
        
        if self.goindown > 1:
            spd = self.goindown/25
            self.goindown -= spd
            self.y += spd

        myrect = g.Rect(self.x,self.y,self.width,self.height)
        ballrect = g.Rect(ball.x+ball.vel[0],ball.y+ball.vel[1],ball.size+ball.vel[0],ball.size+ball.vel[1])

        if myrect.colliderect(ballrect) and ball.killcooldown < 1:
            cbottom = abs(myrect.bottom - ballrect.top)
            ctop = abs(myrect.top - ballrect.bottom)
            cright = abs(myrect.right - ballrect.left)
            cleft = abs(myrect.left - ballrect.right)

            cy = min(ctop,cbottom)
            cx = min(cleft,cright)

            if cy < cx:
                ball.vel[1]*=-1
            else:
                ball.vel[0]*=-1

            self.alive = False
            ball.killcooldown = 2

    def draw(self):
        WIN.blit(self.sprite,g.Rect(self.x,self.y,self.width,self.height))

class LOGIC():  

    blocks = []
    br = 4
    bc = 7

    def blockspawner(self,blocklist,br,bc,spacing):
        offset = (WIDTH-((BLOCK.width+spacing)*bc))/2
        blocklist.clear()
        for i in range(bc):
            blocklist.append(list(BLOCK(i*(BLOCK.width+spacing)+offset,j*(BLOCK.height+spacing)+offset-260) for j in range(br)))      

    def __init__(self):
        self.blockspawner(self.blocks,self.br,self.bc,5)
        self.paddle = PADDLE()
        self.ball = BALL()

    def step(self):
        respawnblocks = True
        for i in range(self.bc):
            for j in range(self.br):
                if self.blocks[i][j].alive:
                    respawnblocks = False
                    self.blocks[i][j].step(self.ball)

        if respawnblocks:
            BALL.spd += 1
            self.blockspawner(self.blocks,self.br,self.bc,5)

        self.paddle.step()
        self.ball.step(self.paddle)

    def draw(self):
        WIN.fill((15,0,25))
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
