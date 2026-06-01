import pygame as g
import random as r
from sys import exit
from os import path, chdir
from math import sin,cos,pi,sqrt,acos,asin,floor,tan,atan,atan2

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

blockcolor = [(145,215,165),(190,40,60),(150, 255, 245),(245, 215, 100),(228, 133, 255)]

hazardsprites = [
    g.image.load('sprites/goldblock.png'),
    g.image.load('sprites/ball.png'),
]

def colorblend(image, color):
    colouredImage = g.Surface(image.get_size())
    colouredImage.fill(color)
    finalImage = image.copy()
    finalImage.blit(colouredImage, (0, 0), special_flags = g.BLEND_MULT)
    return finalImage

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
    strongaurasprite = g.image.load('sprites/strongaura.png').convert_alpha()
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
            if self.y + self.vel[1] < 0: #or self.y + self.vel[1] + self.size > HEIGHT:
                self.vel[1] *= -1
                if self.strong:
                    self.strong = False
                    self.vel[0]/=1.3
                    self.vel[1]/=1.3

            if self.y + self.vel[1] > HEIGHT:
                LOGIC.balls.pop(LOGIC.balls.index(self))
            
            self.x += self.vel[0]
            self.y += self.vel[1]

            myrect.clamp_ip(screen_rect)

    def draw(self):
        if self.strong:
            aurasprite = g.transform.rotate(self.strongaurasprite,(atan2(-self.vel[1],self.vel[0])*180)/pi)
            WIN.blit(aurasprite,aurasprite.get_rect(center = (self.x+self.size/2,self.y+self.size/2)))
        WIN.blit(self.sprite,g.Rect(self.x,self.y,self.size,self.size))

class PADDLE():
    width = 130
    height = 15
    spd = 8
    inverted = False

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
        
        if LOGIC.hazard[1] > 0:
            if r.random() < 0.01:
                self.inverted = not self.inverted
        else:
            self.inverted = False

        if LOGIC.hazard[0] > 0:
            self.spd = 4
        else:
            self.spd = 8

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
        if keys[g.K_0]:
            LOGIC.balls.append(BALL(self.x+self.width/2,HEIGHT*.85))
        if (keys[g.K_LEFT] or keys[g.K_a]):
            if self.inverted:
                if self.width + self.x + self.spd < WIDTH:
                    self.x += self.spd
            else:
                if self.x - self.spd > 0:
                    self.x -= self.spd
        if (keys[g.K_RIGHT] or keys[g.K_d]):
            if self.inverted:
                if self.x - self.spd > 0:
                    self.x -= self.spd
            else:
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

    def __init__(self,xx,yy,specialty):
        i = r.randint(0,4)
        self.sprite = g.transform.scale(blocksprites[i].convert_alpha(), (self.width,self.height))
        self.ghostsprite = g.transform.scale(g.image.load('sprites/ghost.png').convert_alpha(), (self.width,self.height))
        self.powerupsprite = g.transform.scale(colorblend(g.image.load('sprites/powerup.png').convert_alpha(), blockcolor[i]), (self.width,self.height))
        self.skullsprite = g.transform.scale(colorblend(g.image.load('sprites/skull.png').convert_alpha(), blockcolor[i]), (self.width,self.height))
        self.ballsprite = g.transform.scale(colorblend(g.image.load('sprites/ballblock.png').convert_alpha(), blockcolor[i]), (self.width,self.height))
        self.explosivesprite = g.transform.scale(colorblend(g.image.load('sprites/explosive.png').convert_alpha(), blockcolor[i]), (self.width,self.height))
        self.x = xx
        self.y = yy
        self.worth = 125
        if specialty > -1:
            if specialty < 1:    
                self.worth*=2
            else:
                self.worth*=3
        self.alive = True
        self.goindown = 260
        self.targetted = False
        self.specialty = specialty
        self.ghost = False
        self.collidecooldown = 0
        if self.specialty == 5:
            self.ghost = True

    def death(self,myrect,ball = None):
        BALL.killcooldown = 2
        LOGIC.score += self.worth
        if self.specialty > -1:
            if self.specialty == 0:
                LOGIC.powerups.append(POWERUP(myrect.centerx,myrect.centery))
            if self.specialty == 1:
                LOGIC.balls.append(BALL(myrect.centerx,myrect.centery))
            elif self.specialty == 4:
                LOGIC.hazards.append(EXPLOSION(myrect.centerx-(BLOCK.width*3*.9)/2,myrect.centery+BLOCK.height*.05))
            elif self.specialty == 2 or self.specialty == 3:
                LOGIC.hazards.append(HAZARD(myrect.centerx,myrect.centery,self.specialty-2))
        if not ball == None and ball.strong:
            ball.strong = False
            ball.vel[0]/=1.3
            ball.vel[1]/=1.3
        self.alive = False

    def step(self,balls):

        if self.collidecooldown > 0:
            self.collidecooldown-=1

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

            if myrect.colliderect(ballrect) and i.killcooldown < 1 and self.collidecooldown <= 0:
                if not i.strong and not self.ghost:
                    cbot = myrect.bottom > ballrect.top
                    ctop = myrect.top < ballrect.bottom
                    ocbot = myrect.bottom > oballrect.top 
                    octop = myrect.top < oballrect.bottom

                    if (cbot and not ocbot) or (ctop and not octop):
                        i.vel[1]*=-1
                    else:
                        i.vel[0]*=-1

                if not self.ghost:
                    self.death(myrect,i)
                else:
                    self.ghost = False
                    self.collidecooldown = 30

    def draw(self):
        if self.targetted:
            g.draw.rect(WIN,(255,255,255),g.Rect(self.x-2,self.y-2,self.width+4,self.height+4))
            self.targetted = False

        WIN.blit(self.sprite,g.Rect(self.x,self.y,self.width,self.height))
        if self.specialty > -1:
            if self.specialty == 0:
                WIN.blit(self.powerupsprite,g.Rect(self.x,self.y,self.width,self.height))
            if self.specialty >= 1 and not self.specialty == 5:
                if self.specialty == 1:
                    WIN.blit(self.ballsprite,g.Rect(self.x,self.y,self.width,self.height))
                elif self.specialty == 4:
                    WIN.blit(self.explosivesprite,g.Rect(self.x,self.y,self.width,self.height))
                else:
                    WIN.blit(self.skullsprite,g.Rect(self.x,self.y,self.width,self.height))
        if self.ghost:
            WIN.blit(self.ghostsprite,g.Rect(self.x,self.y,self.width,self.height))
        
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
                    if myrect.colliderect(blockrect) and not blocks[i][j].ghost:
                        blocks[i][j].death(blockrect)
                        if self in LOGIC.bullets:
                            LOGIC.bullets.pop(LOGIC.bullets.index(self))

        if self.y < 0:
            if self in LOGIC.bullets:
                LOGIC.bullets.pop(LOGIC.bullets.index(self))

    def draw(self):
        g.draw.rect(WIN,(255,255,255),g.Rect(self.x,self.y,self.width,self.height))

class POWERUP():

    size = 30

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.sprite = g.transform.scale(g.image.load('sprites/greenblock.png').convert_alpha(), (self.size,self.size))
    
    def step(self):
        self.y+=3
        if g.Rect(self.x,self.y,self.size,self.size).colliderect(g.Rect(LOGIC.paddle.x,LOGIC.paddle.y,LOGIC.paddle.width,LOGIC.paddle.height)):
            type = [0,1,2,3]
            for i in type:
                if LOGIC.powerup[i] > 0:
                    type.pop(type.index(i))
            if len(type) > 0:
                type = type[r.randint(0,len(type)-1)]
            else:
                type = r.randint(0,len(LOGIC.powerup)-1)
            LOGIC.powerup[type] += 1200
            LOGIC.powerups.pop(LOGIC.powerups.index(self))
        if self.y > HEIGHT:
            LOGIC.powerups.pop(LOGIC.powerups.index(self))


    def draw(self):
        WIN.blit(self.sprite,g.Rect(self.x,self.y,self.size,self.size))

class HAZARD():

    size = 30

    def __init__(self,x,y,type):
        self.x = x
        self.y = y
        self.type = type
        self.sprite = g.transform.scale(hazardsprites[type].convert_alpha(), (self.size,self.size))

    def step(self):   
        myrect = g.Rect(self.x,self.y,self.size,self.size)
        paddlerect = g.Rect(LOGIC.paddle.x,LOGIC.paddle.y,LOGIC.paddle.width,LOGIC.paddle.height)
        self.y += 4
        if myrect.colliderect(paddlerect):
            LOGIC.hazard[self.type] += 200 + self.type*100
            LOGIC.hazards.pop(LOGIC.hazards.index(self))    
        if self.y > HEIGHT:
            LOGIC.hazards.pop(LOGIC.hazards.index(self))

    def draw(self):
        WIN.blit(self.sprite,g.Rect(self.x,self.y,self.size,self.size))

class EXPLOSION():

    width = BLOCK.width*3*.9
    height = BLOCK.height*2*.9

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.timer = 30
        self.sprite = g.transform.scale(g.image.load('sprites/redblock.png').convert_alpha(), (self.width,self.height))

    def step(self):
        if self.timer == 30:
            blocks = LOGIC.blocks
            myrect = g.Rect(self.x,self.y,self.width,self.height)
            for i in range(LOGIC.bc):
                for j in range(LOGIC.br):
                    blockrect = g.Rect(blocks[i][j].x,blocks[i][j].y,blocks[i][j].width,blocks[i][j].height)
                    if myrect.colliderect(blockrect) and blocks[i][j].alive and not blocks[i][j].ghost:
                        blocks[i][j].death(blockrect)
        self.timer-=1
        if self.timer < 0:
            LOGIC.hazards.pop(LOGIC.hazards.index(self))

    def draw(self):
         WIN.blit(self.sprite,g.Rect(self.x,self.y,self.width,self.height))

class LOGIC():  
    blocks = []
    powerups = []
    bullets = []
    hazards = []
    paddle = PADDLE()
    balls = [BALL(0,HEIGHT*.85)]
    extralives = 2
    br = 4
    bc = 7
    score = 0
    hazard = [0,0] #slower, confused
    powerup = [0,0,0,0] #stronger, homing, big paddle, shoot

    def blockspawner(self,blocklist,br,bc,spacing,pnum):
        offset = (WIDTH-((BLOCK.width+spacing)*bc))/2

        specialtydistribution = []

        for _ in range(bc): specialtydistribution.append(list(-1 for _ in range(br)))

        rows = r.sample(range(0,br),pnum)
        for i in range(pnum):
            specialtydistribution[0][rows[i]] = 0

        ballnum = r.randint(1,2)
        hazards = r.randint(5,6+floor(BALL.spd)-6)
        hazards = [r.randint(2,5) for _ in range(hazards-ballnum)]
        # 0 powerups 1 ball 2 slow 3 confuse 4 explosion 5 ghost
        for _ in range(ballnum): hazards.append(1)

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

        for i in range(len(self.powerup)): 
            if self.powerup[i] > 0: self.powerup[i]-=1
        for i in range(len(self.hazard)):
            if self.hazard[i] > 0: self.hazard[i]-=1

        respawnblocks = True

        for i in range(self.bc):
            for j in range(self.br):
                if self.blocks[i][j].alive:
                    respawnblocks = False
                    self.blocks[i][j].step(self.balls)
                    
        if respawnblocks:
            if BALL.spd < 10:
                BALL.spd += .5
            self.blockspawner(self.blocks,self.br,self.bc,5,2)

        for i in self.bullets: i.step()
        self.paddle.step()
        for i in self.balls: i.step(self.paddle)

        if len(self.balls) == 0:
            self.extralives -= 1
            if self.extralives < 0: exit()
            BALL.start = False
            self.balls.append(BALL(-100,HEIGHT*.85))

        for i in self.hazards: i.step()
        for i in self.powerups:i.step()

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
        for i in self.hazards: i.draw()

        drawtext(self.score,25,"white",25,25)
        for i in range(len(self.hazard)):
            drawtext(self.hazard[i],25,"white",25,50+i*25)
        for i in range(len(self.powerup)):
            drawtext(self.powerup[i],25,"white",25,150+i*25)
        drawtext(self.extralives,25,"white",WIDTH-50,25)
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
