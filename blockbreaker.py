import pygame as g
import random as r
from sys import exit
from os import path, chdir
from math import sin,cos,pi,sqrt,acos,asin,floor

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

powerupsprites = [
    g.image.load('sprites/redblock.png'),
    g.image.load('sprites/purpleblock.png'),
    g.image.load('sprites/greenblock.png'),
    g.image.load('sprites/cyanblock.png')
]

def degtorad(angle):
    return angle * (pi/180)

def rad_from_center_diff(rect1,rect2,incr,mult = 1,anglemax = 70):
    angle = rect1.centerx - rect2.centerx
    angle *= mult
    angle = min(angle, anglemax)
    angle = max(angle, -anglemax)
    if abs(angle) < 10:
        if angle < 0: 
            angle = -10
        else:
            angle = 10
    return degtorad(angle+incr)

def drawtext(text,size,color,x,y):
    font = g.font.Font('HERCULESPIXELFONTREGULAR-OVAX0.OTF', size)
    rtext = font.render(str(text),True,color)
    textrect = rtext.get_rect(topleft = (x,y))
    WIN.blit(rtext, textrect)

class BALL():
    spd = 6
    size = 30
    start = False
    sprite = g.transform.scale(g.image.load('sprites/ball.png').convert_alpha(), (size,size))
    killcooldown = 0
    
    def __init__(self,x,y):
        self.rad = 2.5
        self.alive = True
        self.vel = [self.spd*cos(self.rad),self.spd*sin(self.rad)]
        self.x = x
        self.y = y
        self.strong = False

    def step(self,paddle):

        if LOGIC.balls.index(self) == 0:
            BALL.killcooldown -= 1

        if not BALL.start:
            self.x = paddle.x + paddle.width/2 - self.size/2

            keys = g.key.get_pressed()
            if keys[g.K_UP] or keys[g.K_w]:
                angle = 45
                if keys[g.K_a] or keys[g.K_LEFT]:
                    angle *= -1
                self.rad = degtorad(angle-90)
                self.vel[0] = self.spd*cos(self.rad)
                self.vel[1] = self.spd*sin(self.rad)
                BALL.start = True
        else:
            myrect = g.Rect(self.x+self.vel[0],self.y+self.vel[1],self.size+self.vel[0],self.size+self.vel[1])
            paddlerect = g.Rect(paddle.x,paddle.y,paddle.width,paddle.height)

            if myrect.colliderect(paddlerect):
                if LOGIC.powerup[1] > 0 and not paddle.target == None:
                    b = myrect.centerx - (paddle.target.x+BLOCK.width/2)
                    h = (paddle.target.y+BLOCK.width/2) - myrect.centery
                    dist = sqrt(b**2 + h**2)
                    self.rad = acos(h/dist)+degtorad(90)
                    if b < 0:
                        self.rad = degtorad(180) - self.rad
                    
                    self.vel[0] = self.spd*cos(self.rad)
                    self.vel[1] = self.spd*sin(self.rad)
                else:
                    self.rad = rad_from_center_diff(myrect,paddlerect,-90)
                    self.vel[0] = self.spd*cos(self.rad)
                    self.vel[1] = self.spd*sin(self.rad)

                if LOGIC.powerup[0] > 0:
                    self.strong = True
                    self.vel[0]*=1.3
                    self.vel[1]*=1.3
                
                if LOGIC.powerup[3] > 0 and paddle.shootcooldown == 0:
                    LOGIC.bullets.append(BULLET(paddle.x+10,paddle.y-10))
                    LOGIC.bullets.append(BULLET(paddle.x+paddle.width-20,paddle.y-10))
                    paddle.shootcooldown = 10

            if self.x + self.size + self.vel[0] > WIDTH or self.x + self.vel[0] < 0:
                self.vel[0] *= -1
            if self.y + self.vel[1] < 0 or self.y + self.vel[1] + self.size > HEIGHT:
                self.vel[1] *= -1
                if self.strong:
                    self.strong = False
                    self.vel[0]/=1.3
                    self.vel[1]/=1.3

            #if self.y + self.vel[1] > HEIGHT:
            #    self.alive = False
            
            self.x += self.vel[0]
            self.y += self.vel[1]

            myrect.clamp_ip(screen_rect)

    def draw(self):
        if self.strong:
            g.draw.rect(WIN,(255,255,255),g.Rect(self.x-self.size/2,self.y-self.size/2,self.size*2,self.size*2))
        WIN.blit(self.sprite,g.Rect(self.x,self.y,self.size,self.size))

class PADDLE():
    width = 130
    height = 15
    spd = 8

    def __init__(self):
        self.x = WIDTH/2 - self.width/2
        self.y = HEIGHT*.9
        self.target = None
        self.shootcooldown = 0

    def step(self):
        
        if self.shootcooldown > 0:
            self.shootcooldown-=1

        if LOGIC.powerup[2] > 0:
            if self.width < 220:
                self.width+=2
                self.x-=1
        else:
            if self.width > 130:
                self.width-=2
                self.x+=1

        if  LOGIC.powerup[1] > 0:
            targetrow = 3
            targetcol = 9001
            blocks = LOGIC.blocks

            while(targetcol == 9001):
                targetcol = []
                for i in range(LOGIC.bc):
                    if blocks[i][targetrow].alive:
                        targetcol.append(abs((blocks[i][0].x+BLOCK.width/2)-(self.x+self.width/2)))
                    else:
                        targetcol.append(9001)

                if min(targetcol) == 9001:
                    targetcol = 9001
                    targetrow -= 1
                    if targetrow < 0:
                        targetrow = 3
                        targetcol = 0
                        exit
                else:
                    targetcol = targetcol.index(min(targetcol))

            self.target = blocks[targetcol][targetrow]
            self.target.targetted = True
        else:
            self.target = None

        keys = g.key.get_pressed()
        if (keys[g.K_LEFT] or keys[g.K_a]):
            if self.x - self.spd > 0:
                self.x -= self.spd
        if (keys[g.K_RIGHT] or keys[g.K_d]):
            if self.width + self.x + self.spd < WIDTH:
                self.x += self.spd

    def draw(self):
        g.draw.rect(WIN,(255,255,255),g.Rect(self.x,self.y,self.width,self.height))
        if LOGIC.powerup[3] > 0:
            g.draw.rect(WIN,(255,255,255),g.Rect(self.x+10,self.y-10,10,10))
            g.draw.rect(WIN,(255,255,255),g.Rect(self.x+self.width-20,self.y-10,10,10))
        #WIN.blit(self.sprite,g.Rect(self.x,self.y,self.width,self.height))

class BLOCK():
    width = 75
    height = 40
    deathcooldown = 0

    def __init__(self,xx,yy,specialty):
        self.sprite = g.transform.scale(blocksprites[r.randint(0,4)].convert_alpha(), (self.width,self.height))
        self.x = xx
        self.y = yy
        self.worth = 125
        if specialty > -1:
            if specialty < len(LOGIC.powerup):    
                self.worth*=2
            else:
                self.worth*=3
        self.alive = True
        self.goindown = 260
        self.targetted = False
        self.specialty = specialty

    def death(self,myrect,ball = None):
        BALL.killcooldown = 2
        LOGIC.score += self.worth
        if self.specialty > -1:
            if self.specialty < len(LOGIC.powerup):
                LOGIC.powerups.append(POWERUP(myrect.centerx,myrect.centery,self.specialty))
            else:
                if self.specialty == len(LOGIC.powerup):
                    LOGIC.balls.append(BALL(myrect.centerx,myrect.centery))
        if not ball == None and ball.strong:
            ball.strong = False
            ball.vel[0]/=1.3
            ball.vel[1]/=1.3
        self.alive = False

    def step(self,balls):

        if self.goindown > 1:
            spd = self.goindown/25
            self.goindown -= spd
            self.y += spd
            if self.goindown <= 1:
                self.y = floor(self.y)

        for i in balls:
            myrect = g.Rect(self.x,self.y,self.width,self.height)
            ballrect = g.Rect(i.x+i.vel[0],i.y+i.vel[1],i.size+i.vel[0],i.size+i.vel[1])
            oballrect = g.Rect(i.x,i.y,i.size,i.size)

            if myrect.colliderect(ballrect) and i.killcooldown < 1:
                if not i.strong:
                    cbot = myrect.bottom > ballrect.top
                    ctop = myrect.top < ballrect.bottom
                    #cright = myrect.right > ballrect.left
                    #cleft = myrect.left < ballrect.right

                    ocbot = myrect.bottom > oballrect.top 
                    octop = myrect.top < oballrect.bottom

                    if (cbot and not ocbot) or (ctop and not octop):
                        i.vel[1]*=-1
                    else:
                        i.vel[0]*=-1

                self.death(myrect,i)

    def draw(self):
        if self.targetted:
            g.draw.rect(WIN,(255,255,255),g.Rect(self.x,self.y,self.width,self.height))
            self.targetted = False
        else: 
            if self.specialty > -1:
                if self.specialty < len(LOGIC.powerup):
                    g.draw.rect(WIN,(0,255,0),g.Rect(self.x,self.y,self.width,self.height))
                else:
                    g.draw.rect(WIN,(255,0,0),g.Rect(self.x,self.y,self.width,self.height))               
            else:
                WIN.blit(self.sprite,g.Rect(self.x,self.y,self.width,self.height))
        
class BULLET():

    width = 5
    height = 10

    def __init__(self,x,y):
        self.x = x
        self.y = y
    
    def step(self):
        self.y-=7

        blocks = LOGIC.blocks
        myrect = g.Rect(self.x,self.y,self.width,self.height)
        for i in range(LOGIC.bc):
            for j in range(LOGIC.br):
                if blocks[i][j].alive:
                    blockrect = g.Rect(blocks[i][j].x,blocks[i][j].y,blocks[i][j].width,blocks[i][j].height)
                    if myrect.colliderect(blockrect):
                        blocks[i][j].death(blockrect)
                        if self in LOGIC.bullets:
                            LOGIC.bullets.pop(LOGIC.bullets.index(self))

    def draw(self):
        g.draw.rect(WIN,(255,255,255),g.Rect(self.x,self.y,self.width,self.height))

class POWERUP():

    size = 30

    def __init__(self,x,y,type):
        self.x = x
        self.y = y
        self.type = type
        self.sprite = g.transform.scale(powerupsprites[type].convert_alpha(), (self.size,self.size))
    
    def step(self):
        self.y+=3
    
    def draw(self):
        WIN.blit(self.sprite,g.Rect(self.x,self.y,self.size,self.size))

class LOGIC():  

    blocks = []
    powerups = []
    bullets = []
    paddle = PADDLE()
    balls = [BALL(0,HEIGHT*.85)]
    br = 4
    bc = 7
    score = 0
    powerup = [0,1200,0,0] #stronger, homing, big paddle, shoot

    def blockspawner(self,blocklist,br,bc,spacing,pnum):
        offset = (WIDTH-((BLOCK.width+spacing)*bc))/2

        powerups = r.sample(range(0,len(self.powerup)), pnum)
        specialtydistribution = []

        for _ in range(bc): specialtydistribution.append(list(-1 for _ in range(br)))

        rows = r.sample(range(0,br),pnum)
        for i in range(pnum):
            specialtydistribution[0][rows[i]] = powerups[i]
        
        hazards = r.randint(5,6+BALL.spd-6)
        hazards = [len(self.powerup) + 0 for _ in range(hazards)]

        cl = 1; rw = 0
        for i in hazards:
            specialtydistribution[cl][rw] = i
            rw += 1
            if rw > 3: rw = 0 ; cl += 1
            if cl > 6: exit

        templist = []
        for i in range(br): 
            templist.append(list(specialtydistribution[j][i] for j in range(bc)))
            r.shuffle(templist[i])

        blocklist.clear()
        for i in range(bc):
            blocklist.append(list(BLOCK(i*(BLOCK.width+spacing)+offset,j*(BLOCK.height+spacing)+offset-260,templist[j][i]) for j in range(br)))      

    def __init__(self):
        self.blockspawner(self.blocks,self.br,self.bc,5,2)

    def step(self):

        for i in self.powerups:
            i.step()
            if g.Rect(i.x,i.y,i.size,i.size).colliderect(g.Rect(self.paddle.x,self.paddle.y,self.paddle.width,self.paddle.height)):
                self.powerup[i.type] += 1200
                self.powerups.pop(self.powerups.index(i))
            if i.y > HEIGHT: 
                self.powerups.pop(self.powerups.index(i))

        for i in range(len(self.powerup)):
            if self.powerup[i] > 0:
                self.powerup[i]-=1

        respawnblocks = True

        for i in range(self.bc):
            for j in range(self.br):
                if self.blocks[i][j].alive:
                    respawnblocks = False
                    self.blocks[i][j].step(self.balls)
                    
        if respawnblocks:
            if BALL.spd < 11:
                BALL.spd += 1
            self.blockspawner(self.blocks,self.br,self.bc,5,2)

        for i in self.bullets: i.step()
        self.paddle.step()
        for i in self.balls: i.step(self.paddle)

    def draw(self):
        WIN.fill((15,0,25))
        for i in range(self.bc):
            for j in range(self.br):
                if self.blocks[i][j].alive:
                    self.blocks[i][j].draw()
        for i in self.bullets: i.draw()
        self.paddle.draw()
        for i in self.balls: i.draw()
        for i in self.powerups: i.draw()

        drawtext(self.score,25,"white",25,25)
        for i in range(len(self.powerup)):
            drawtext(self.powerup[i],25,"white",25,50+i*25)
        #drawtext(,25,"white",200,20)
        g.display.update()

clock = g.time.Clock()
game = LOGIC()

while(1):

    for event in g.event.get():
        if event.type == g.QUIT:
            exit()  

    game.step()
    game.draw()
    clock.tick(60)
