import pygame as g
import random as r
from sys import exit
from os import path
from math import sin,cos,pi,sqrt,acos,asin,floor,atan2
from numpy import interp
from json import dump,load

g.init()

g.display.set_caption('Block Breaker')
g.display.set_icon(g.image.load(path.join('sprites\\ball.png')))

WIDTH, HEIGHT = 720,720
WIN = g.display.set_mode((WIDTH,HEIGHT))
screen_rect = WIN.get_rect()

clock = g.time.Clock()

blockw = 75
blockh = 40

blocksprites = [
    g.transform.scale(g.image.load(path.join('sprites\\greenblock.png')).convert_alpha(), (blockw,blockh)),
    g.transform.scale(g.image.load(path.join('sprites\\redblock.png')).convert_alpha(), (blockw,blockh)),
    g.transform.scale(g.image.load(path.join('sprites\\cyanblock.png')).convert_alpha(), (blockw,blockh)),
    g.transform.scale(g.image.load(path.join('sprites\\goldblock.png')).convert_alpha(), (blockw,blockh)),
    g.transform.scale(g.image.load(path.join('sprites\\purpleblock.png')).convert_alpha(), (blockw,blockh)),
]

explodingsprite = g.image.load(path.join('sprites\\explodingcover.png'))
explodingsprite.set_alpha(100)
homingoutline = g.image.load(path.join('sprites\\homingoutline.png'))
ghostblocksprite = g.transform.scale(g.image.load(path.join('sprites\\ghost.png')).convert_alpha(), (blockw,blockh))
powerupsprite = g.image.load(path.join('sprites\\powerupsprite.png'))
strongsprite = g.image.load(path.join('sprites\\strongaura.png'))
ballsprite = g.image.load(path.join('sprites\\ball.png'))
extralifesprite = g.image.load(path.join('sprites\\extralife.png'))
arrowsprite = g.image.load(path.join('sprites\\arrow.png'))

hazardsprites = [
    g.image.load(path.join('sprites\\slowdebuff.png')),
    g.image.load(path.join('sprites\\confusedebuff.png')),
]

def colorblend(image, color):
    colouredImage = g.Surface(image.get_size())
    colouredImage.fill(color)
    finalImage = image.copy()
    finalImage.blit(colouredImage, (0, 0), special_flags = g.BLEND_MULT)
    return finalImage

blockcolor = [(145,215,165),(190,40,60),(150, 255, 245),(245, 215, 100),(228, 133, 255)]
powerupblocksprites = [g.transform.scale(colorblend(g.image.load(path.join('sprites\\powerup.png')).convert_alpha(), blockcolor[i]), (blockw,blockh)) for i in range(len(blockcolor))]
skullsprites = [g.transform.scale(colorblend(g.image.load(path.join('sprites\\skull.png')).convert_alpha(), blockcolor[i]), (blockw,blockh)) for i in range(len(blockcolor))]
ballblocksprites = [g.transform.scale(colorblend(g.image.load(path.join('sprites\\ballblock.png')).convert_alpha(), blockcolor[i]), (blockw,blockh)) for i in range(len(blockcolor))]
explosiveblocksprites = [g.transform.scale(colorblend(g.image.load(path.join('sprites\\explosive.png')).convert_alpha(), blockcolor[i]), (blockw,blockh)) for i in range(len(blockcolor))]
heartblocksprites = [g.transform.scale(colorblend(g.image.load(path.join('sprites\\heart.png')).convert_alpha(), blockcolor[i]), (blockw,blockh)) for i in range(len(blockcolor))]

def degtorad(angle):
    return angle * (pi/180)

def rad_from_center_diff(ballrect,paddlerect,incr,mult = 1,anglemax = 70):
    angle = ballrect.centerx - paddlerect.centerx
    angle *= mult
    angle = interp(angle,[-paddlerect.width/2,paddlerect.width/2],[-anglemax,anglemax])
    if abs(angle) < 10: angle = -10 if angle < 0 else 10
    return degtorad(angle+incr)

def drawtext(text,size,color,x,y,align = "left"):
    font = g.font.Font('HERCULESPIXELFONTREGULAR-OVAX0.OTF', size)
    rtext = font.render(str(text),True,color)
    textrect = rtext.get_rect(topleft = (x,y))
    if align == "right":
        textrect = rtext.get_rect(topright = (x,y))
    elif align == "center":
        textrect = rtext.get_rect(center = (x,y))
    WIN.blit(rtext, textrect)

#only allows spritesheets in one horizontal line
def get_anim_frame(sheet,realw,realh,totanimtime,animtime,framenum):
    framew = sheet.get_width()/framenum
    frameh = sheet.get_height()
    frame = floor(interp(animtime,[0,totanimtime],[0,framenum-1]))
    img = g.Surface((framew,frameh)).convert_alpha()
    img.fill((0,0,0,0))
    img.blit(sheet, (0,0), (framew*frame,0,framew,frameh))
    return g.transform.scale(img,(realw,realh))

def three_slice_horizontal(sprite,cornerw,cornerh,initialrect,realrect):
    s = g.transform.scale(sprite,(initialrect.width,initialrect.height))
    centerimg = g.Surface((initialrect.width-cornerw*2,initialrect.height)).convert_alpha()
    centerimg.fill((0,0,0,0))
    centerimg.blit(s, (0,0), (cornerw,0,(initialrect.width-cornerw*2),realrect.height))
    centerimg = g.transform.scale(centerimg,(realrect.width-cornerw*2,realrect.height))
    img = g.Surface((realrect.width,realrect.height)).convert_alpha()
    img.fill((0,0,0,0))
    img.blit(s, (0,0))
    img.blit(centerimg, (cornerw,0))
    img.blit(s, (centerimg.get_width()+cornerw,0), (s.get_width()-cornerw,0,cornerw,cornerh))
    return img

class BALL():
    spd = 6
    size = 30
    start = False
    sprite = g.transform.scale(ballsprite.convert_alpha(), (size,size))
    strongaurasprite = strongsprite.convert_alpha()
    killcooldown = 0

    def __init__(self,x,y):
        self.rad = 2.5
        self.alive = True
        self.vel = [self.spd*cos(self.rad),self.spd*sin(self.rad)]
        self.x = x
        self.y = y
        self.strong = False
        self.beforestartsize = 30
        if not BALL.start:
            self.beforestartsize = 0

    def startgame(self,mult = 1):
        if self.beforestartsize >= 30:
            angle = 45 * mult
            self.rad = degtorad(angle-90)
            self.vel[0] = self.spd*cos(self.rad)
            self.vel[1] = self.spd*sin(self.rad)
            BALL.start = True

    def step(self,paddle):

        if LOGIC.balls.index(self) == 0:
            BALL.killcooldown -= 1

        if self.beforestartsize < 30:
            self.beforestartsize += 1

        if not BALL.start:
            self.x = paddle.x + paddle.width/2 - self.size/2

            keys = g.key.get_pressed()
            if (keys[g.K_UP] or keys[g.K_w]) and not BALL.start:
                m = 1
                if keys[g.K_a] or keys[g.K_LEFT]:
                    m = -1
                self.startgame(m)
  
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
                    LOGIC.bullets.append(BULLET(paddle.x+5,paddle.y-10))
                    LOGIC.bullets.append(BULLET(paddle.x+paddle.width-9,paddle.y-10))
                    paddle.shootcooldown = 10

            if self.x + self.size + self.vel[0] > WIDTH or self.x + self.vel[0] < 0:
                self.vel[0] *= -1
            if self.y + self.vel[1] < 0: # or self.y + self.vel[1] + self.size > HEIGHT:
                self.vel[1] *= -1
                if self.strong:
                    self.strong = False
                    self.vel[0]/=1.3
                    self.vel[1]/=1.3

            if self.y + self.vel[1] > HEIGHT:
                LOGIC.balls.pop(LOGIC.balls.index(self))
            
            self.x += self.vel[0]
            self.y += self.vel[1]

            if self.y < 0:
                self.y += self.size

            myrect.clamp_ip(screen_rect)

    def draw(self):
        sprite = self.sprite
        if LOGIC.paused:
            arrow = g.transform.rotate(arrowsprite,(atan2(-self.vel[1],self.vel[0])*180)/pi)
            WIN.blit(arrow,arrow.get_rect(center = (self.x+self.size/2,self.y+self.size/2)))
        if self.strong:
            sprite = colorblend(sprite,(200,30,0))
            aurasprite = g.transform.rotate(self.strongaurasprite,(atan2(-self.vel[1],self.vel[0])*180)/pi)
            WIN.blit(aurasprite,aurasprite.get_rect(center = (self.x+self.size/2,self.y+self.size/2)))
        if self.beforestartsize >= 30:
            WIN.blit(sprite,g.Rect(self.x,self.y,self.size,self.size))
        else:
            WIN.blit(g.transform.scale(sprite,(self.beforestartsize,self.beforestartsize)),g.Rect(self.x+self.size/2-self.beforestartsize/2,self.y+self.size/2-self.beforestartsize/2,self.beforestartsize,self.beforestartsize))

class PADDLE():
    width = 130
    height = 15
    spd = 10
    inverted = False
    sprite = g.image.load(path.join('sprites\\paddle.png'))
    cannonsprite = g.image.load(path.join('sprites\\paddlecannons.png'))
    cannonheight = 30
    playingwithmouse = False

    def __init__(self):
        self.x = WIDTH/2 - self.width/2
        self.y = HEIGHT*.9
        self.target = None
        self.shootcooldown = 0

    def step(self):
        
        if self.shootcooldown > 0:
            self.shootcooldown-=1

        if LOGIC.powerup[2] > 0:
            if PADDLE.width < 220:
                PADDLE.width+=2
                self.x-=1
        else:
            if PADDLE.width > 130:
                PADDLE.width-=2
                self.x+=1
        
        if LOGIC.hazard[0] > 0:
            if r.random() < 0.01:
                self.inverted = not self.inverted
        else:
            self.inverted = False

        if PADDLE.spd < 10:
            PADDLE.spd += 0.08

        if  LOGIC.powerup[1] > 0:
            targetrow = 3
            targetcol = 9001
            blocks = LOGIC.blocks

            while(targetcol == 9001):
                targetcol = []
                for i in range(LOGIC.bc):
                    if blocks[i][targetrow].alive:
                        targetcol.append(abs((blocks[i][0].x+BLOCK.width/2)-(self.x+PADDLE.width/2)))
                    else:
                        targetcol.append(9001)

                if min(targetcol) == 9001:
                    targetcol = 9001
                    targetrow -= 1
                    if targetrow < 0:
                        targetrow = 3
                        targetcol = 0
                        break
                else:
                    targetcol = targetcol.index(min(targetcol))

            self.target = blocks[targetcol][targetrow]
            self.target.targetted = True
        else:
            self.target = None

        keys = g.key.get_pressed()
        if (keys[g.K_LEFT] or keys[g.K_a]):
            PADDLE.playingwithmouse = False
            if self.inverted:
                if self.width + self.x + self.spd < WIDTH:
                    self.x += PADDLE.spd
            else:
                if self.x - self.spd > 0:
                    self.x -= PADDLE.spd
        if (keys[g.K_RIGHT] or keys[g.K_d]):
            PADDLE.playingwithmouse = False
            if self.inverted:
                if self.x - self.spd > 0:
                    self.x -= PADDLE.spd
            else:
                if self.width + self.x + self.spd < WIDTH:
                    self.x += PADDLE.spd

        if PADDLE.playingwithmouse:
            mpos = g.mouse.get_pos()
            cx = self.x + PADDLE.width/2
            if mpos[0] > cx:
                if not self.inverted:
                    if self.width + self.x + self.spd < WIDTH:
                        self.x += min(PADDLE.spd,mpos[0]-cx)
                else:
                    if self.x - self.spd > 0:
                        self.x += min(-PADDLE.spd,mpos[0]-cx)
            if mpos[0] < cx:
                if not self.inverted:
                    if self.x - self.spd > 0:
                        self.x += max(-PADDLE.spd,mpos[0]-cx)
                else:    
                    if self.width + self.x + self.spd < WIDTH:
                        self.x += max(PADDLE.spd,mpos[0]-cx)

    def draw(self):
        drawrect = g.Rect(self.x-10,self.y,self.width+20,self.height+15)
        WIN.blit(three_slice_horizontal(self.sprite,30,30,g.Rect(self.x,self.y,130,30),drawrect),drawrect)
        
        if LOGIC.powerup[3] > 0 and self.cannonheight < 42:
            self.cannonheight += .5
        elif LOGIC.powerup[3] <= 0 and self.cannonheight > 30:
            self.cannonheight -= .5

        if self.cannonheight > 30:
            WIN.blit(g.transform.scale(self.cannonsprite,(15,self.cannonheight)),g.Rect(self.x,self.y-(self.cannonheight-30),11,10))
            WIN.blit(g.transform.flip(g.transform.scale(self.cannonsprite,(15,self.cannonheight)),True,False),g.Rect(self.x+self.width-13,self.y-(self.cannonheight-30),10,10))

class BLOCK():
    width = blockw
    height = blockh

    def __init__(self,xx,yy,specialty):
        i = r.randint(0,4)
        self.sprite = blocksprites[i]
        self.powerupsprite = powerupblocksprites[i]
        self.skullsprite = skullsprites[i]
        self.ballsprite = ballblocksprites[i]
        self.explosivesprite = explosiveblocksprites[i]
        self.heartsprite = heartblocksprites[i]
        self.hominganimtime = 0
        
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
        self.ghost = -1
        self.collidecooldown = 0
        if self.specialty == 5:
            self.ghost = 255
        self.exploding = -1

    def death(self,myrect,death = None):
        BALL.killcooldown = 2
        if self.exploding == -1:
            LOGIC.score += self.worth
        if self.specialty > -1:
            if self.specialty == 0:
                LOGIC.powerups.append(POWERUP(myrect.centerx,myrect.centery))
            if self.specialty == 1:
                LOGIC.balls.append(BALL(myrect.centerx,myrect.centery))
            elif self.specialty == 4 and self.exploding == -1:
                if death == -1:
                    self.alive = False
                    LOGIC.hazards.append(EXPLOSION(myrect.centerx-(BLOCK.width*3*.9)/2,self.y+BLOCK.height*.05))
                else:
                    self.exploding = 120
            elif self.specialty == 2 or self.specialty == 3:
                LOGIC.hazards.append(HAZARD(myrect.centerx-HAZARD.size/2,myrect.centery-HAZARD.size/2,self.specialty-2))
            elif self.specialty == 6:
                LOGIC.lifehearts.append(LIFEHEART(myrect.centerx,myrect.centery))
        if not death == None and not death == -1:
            if death.strong:
                death.strong = False
                death.vel[0]/=1.3
                death.vel[1]/=1.3
        if not self.specialty == 4:
            self.alive = False

    def step(self,balls):

        myrect = g.Rect(self.x,self.y,self.width,self.height)
        if self.ghost > 0 and self.ghost < 255:
            self.ghost -= 8.5

        if self.exploding > 0:
            self.exploding -= 1
            if self.exploding < 1:
                self.alive = False
                LOGIC.hazards.append(EXPLOSION(myrect.centerx-(BLOCK.width*3*.9)/2,self.y+BLOCK.height*.05))

        if self.collidecooldown > 0:
            self.collidecooldown-=1

        if self.goindown > 1:
            spd = self.goindown/25
            self.goindown -= spd
            self.y += spd
            if self.goindown <= 1:
                self.y = floor(self.y)

        for i in balls:
            ballrect = g.Rect(i.x+i.vel[0],i.y+i.vel[1],i.size+i.vel[0],i.size+i.vel[1])
            oballrect = g.Rect(i.x,i.y,i.size,i.size)

            if myrect.colliderect(ballrect) and BALL.killcooldown < 1 and self.collidecooldown <= 0:
                if not i.strong and self.ghost == -1 or self.specialty == 4:
                    cbot = myrect.bottom > ballrect.top
                    ctop = myrect.top < ballrect.bottom
                    ocbot = myrect.bottom > oballrect.top
                    octop = myrect.top < oballrect.bottom

                    if (cbot and not ocbot) or (ctop and not octop):
                        i.vel[1]*=-1
                    else:
                        i.vel[0]*=-1

                if self.ghost == -1:
                    self.death(myrect,i)
                else:
                    self.ghost -= 1
                    self.collidecooldown = 30

    def draw(self):
        
        myrect = g.Rect(self.x,self.y,self.width,self.height)

        if self.targetted:
            self.hominganimtime = self.hominganimtime + 1 if self.hominganimtime < 20 else 0
            WIN.blit(get_anim_frame(homingoutline,self.width+4,self.height+4,20,self.hominganimtime,3),g.Rect(self.x-2,self.y-2,self.width+4,self.height+4))
            self.targetted = False

        WIN.blit(self.sprite,myrect)

        if self.specialty > -1:
            if self.specialty == 0:
                WIN.blit(self.powerupsprite,myrect)
            if self.specialty >= 1 and not self.specialty == 5:
                if self.specialty == 1:
                    WIN.blit(self.ballsprite,myrect)
                elif self.specialty == 4:
                    WIN.blit(self.explosivesprite,myrect)
                elif self.specialty == 6:
                    WIN.blit(self.heartsprite,myrect)
                else:
                    WIN.blit(self.skullsprite,myrect)
        if not self.ghost == -1:
            ghostblocksprite.set_alpha(self.ghost)
            WIN.blit(ghostblocksprite,myrect)

        if self.exploding > 0:
            if self.exploding % 30 > 15:
                WIN.blit(explodingsprite,myrect)
            
class BULLET():

    width = 6
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
                    if myrect.colliderect(blockrect) and blocks[i][j].ghost == -1:
                        blocks[i][j].death(blockrect)
                        if self in LOGIC.bullets:
                            LOGIC.bullets.pop(LOGIC.bullets.index(self))

        if self.y < 0:
            if self in LOGIC.bullets:
                LOGIC.bullets.pop(LOGIC.bullets.index(self))

    def draw(self):
        g.draw.rect(WIN,(255,255,255),g.Rect(self.x,self.y,self.width,self.height))

class POWERUP():

    size = 35

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.sprite = g.transform.scale(powerupsprite.convert_alpha(), (self.size,self.size))
    
    def step(self):
        self.y+=3
        if g.Rect(self.x,self.y,self.size,self.size).colliderect(g.Rect(LOGIC.paddle.x,LOGIC.paddle.y,LOGIC.paddle.width,LOGIC.paddle.height)):
            t = r.randint(0,len(LOGIC.powerup)-1)
            while(1):
                if LOGIC.powerup[t] == 0:
                    break
                t-=1
                if t < -len(LOGIC.powerup):
                    t = r.randint(0,len(LOGIC.powerup)-1)
                    break
            LOGIC.powerup[t] += 1200
            LOGIC.powerups.pop(LOGIC.powerups.index(self))
        if self.y > HEIGHT:
            LOGIC.powerups.pop(LOGIC.powerups.index(self))


    def draw(self):
        WIN.blit(self.sprite,g.Rect(self.x,self.y,self.size,self.size))

class HAZARD():

    size = 35

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
            if self.type == 0: PADDLE.spd = 0
            if self.type == 1: LOGIC.hazard[0] += 400
            LOGIC.hazards.pop(LOGIC.hazards.index(self))
        if self.y > HEIGHT:
            LOGIC.hazards.pop(LOGIC.hazards.index(self))

    def draw(self):
        WIN.blit(self.sprite,g.Rect(self.x,self.y,self.size,self.size))

class EXPLOSION():

    width = BLOCK.width*3*.9
    height = BLOCK.height*2*.9
    maxtimer = 30

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.timer = self.maxtimer
        self.sprite = g.image.load(path.join('sprites\\exploding_anim.png')).convert_alpha()
        self.explosionballs = []
    
    def addexplosionball(self):
        w = r.randint(75,125)
        hw = floor(self.width/2)
        hh = floor(self.height/2)
        self.explosionballs.append([self.x+self.width/2-w/2+r.randint(-hw,hw),self.y+self.height/2-w/2+r.randint(-hh,hh),w,0])
            

    def step(self):
        if self.timer == self.maxtimer:
            blocks = LOGIC.blocks
            myrect = g.Rect(self.x,self.y,self.width,self.height)
            for i in range(LOGIC.bc):
                for j in range(LOGIC.br):
                    blockrect = g.Rect(blocks[i][j].x,blocks[i][j].y,blocks[i][j].width,blocks[i][j].height)
                    if myrect.colliderect(blockrect) and blocks[i][j].alive and blocks[i][j].ghost == -1:
                        blocks[i][j].death(blockrect,-1)
        self.timer-=1
        if self.timer < 0:
            LOGIC.hazards.pop(LOGIC.hazards.index(self))

    def draw(self):
        if self.timer > self.maxtimer-11:
            self.addexplosionball()
            if self.timer == 5:
                for _ in range(5): self.addexplosionball()

        for i in self.explosionballs:
            i[3]+=1
            WIN.blit(get_anim_frame(self.sprite,i[2],i[2],20,i[3],8),g.Rect(i[0],i[1],i[2],i[2]))
            if i[3] > 19:
                self.explosionballs.pop(self.explosionballs.index(i))
            
class LIFEHEART():

    r = 150
    size = 35  
    sprite = g.transform.scale(extralifesprite.convert_alpha(), (size,size))

    def __init__(self,x,y,collidecooldown = 0,angle = 3.2,bounces = 0,xmult = 1,ymult = 1,bspdmult = -1, rot = 0):
        self.bouncespd = 0.025*bspdmult
        self.c = angle
        self.xmult = xmult
        self.ymult = ymult
        self.cx = x+self.r*xmult
        self.cy = y
        self.x = self.cx + self.r * cos(self.c) * xmult
        self.y = self.cy + self.r * sin(self.c) * ymult
        self.bouncing = True
        self.bounces = bounces
        self.cc = collidecooldown
        self.angle = rot

    def death(self,addlife = False):
        if addlife:
            LOGIC.extralives += 1
        if self in LOGIC.lifehearts:
            LOGIC.lifehearts.pop(LOGIC.lifehearts.index(self))

    def step(self):
        if self.cc > 0: self.cc -= 1

        self.angle = self.angle - 5 if self.bouncespd > 0 else self.angle + 5

        if self.bouncing:
            self.c += self.bouncespd    
        else:
            self.cy += 3

        self.x = self.cx + self.r * cos(self.c) * self.xmult
        self.y = self.cy + self.r * sin(self.c) * self.ymult

        if self.y >= self.cy:
            self.bouncing = False
        
        myrect = g.Rect(self.x,self.y,self.size,self.size)
        paddlerect = g.Rect(LOGIC.paddle.x,LOGIC.paddle.y,LOGIC.paddle.width,LOGIC.paddle.height)

        if self.x + self.size > WIDTH or self.x < 0:
            self.bouncespd*=-1

        if myrect.colliderect(paddlerect):
            if self.cc == 0:
                self.cc = 30
                self.bounces += 1
            if r.random() > .5 and self.cx > WIDTH/3 and self.cx < (WIDTH/3)*2:
                self.bouncespd*=-1
                self.bouncing = True
            else:
                self.death()
                diff = myrect.centerx - paddlerect.centerx
                self.xmult = interp(abs(diff),[0,PADDLE.width/2],[0.7,1.3])
                self.ymult = 2.2-self.xmult
                if self.bounces < 4:
                    if self.x > self.cx:
                        LOGIC.lifehearts.append(LIFEHEART(self.x,self.y,self.cc,3.2,self.bounces,self.xmult,self.ymult,1,self.angle))
                    else:
                        LOGIC.lifehearts.append(LIFEHEART(self.x-(self.r*(2*self.xmult)),self.y,self.cc,6.2,self.bounces,self.xmult,self.ymult,-1,self.angle))
        
        if self.bounces == 4:
            self.death(True)

        if self.y > HEIGHT or self.cy > HEIGHT:
            self.death()

    def draw(self):
        s = g.transform.rotate(self.sprite, self.angle)
        WIN.blit(s,s.get_rect(center=g.Rect(self.x,self.y,self.size,self.size).center))

class LOGIC():
    lifeslotsprite = g.transform.scale(g.image.load(path.join('sprites\\lifeslot.png')).convert_alpha(),(34,34))
    lifesprite = g.transform.scale(g.image.load(path.join('sprites\\life.png')).convert_alpha(),(34,34))
    tutorialsprite = [g.transform.scale(g.image.load(path.join('sprites\\tutorial1.png')).convert_alpha(),(180,120)),g.transform.scale(g.image.load(path.join('sprites\\tutorial2.png')).convert_alpha(),(180,120)),g.transform.scale(g.image.load(path.join('sprites\\tutorial3.png')).convert_alpha(),(180,120))]
    blink = 0
    blocks = []
    powerups = []
    bullets = []
    hazards = []
    lifehearts = []
    paddle = PADDLE()
    balls = [BALL(0,HEIGHT*.85)]
    extralives = 2
    br = 4
    bc = 7
    paused = False
    score = 0
    highscore = 0
    with open('highscore.json') as f:
        highscore = load(f)
        f.close()
    hazard = [0] #confused
    powerup = [0,0,0,0] #stronger, homing, big paddle, shoot
    tutorialtimer = 60

    def blockspawner(self,blocklist,br,bc,spacing,pnum):
        offset = (WIDTH-((BLOCK.width+spacing)*bc))/2

        specialtydistribution = []

        for _ in range(bc): specialtydistribution.append(list(-1 for _ in range(br)))

        rows = r.sample(range(0,br),pnum)
        for i in range(pnum):
            specialtydistribution[0][rows[i]] = 0

        ballnum = r.randint(1,2)
        lifeheart = 1 if LOGIC.extralives < 3 and len(LOGIC.lifehearts) == 0 and r.random() > .33 else 0
        hazards = r.randint(5,6+floor(BALL.spd)-6)
        hazards = [r.randint(2,5) for _ in range(hazards-ballnum-lifeheart)]
        # 0 powerups 1 ball 2 slow 3 confuse 4 explosion 5 ghost 6 lifeheart
        for _ in range(ballnum): hazards.append(1)
        if lifeheart: hazards.append(6)

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

        if not self.paused:
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
                if BALL.spd < 11:
                    BALL.spd += .5
                self.blockspawner(self.blocks,self.br,self.bc,5,r.randint(1,2))

            for i in self.bullets: i.step()
            self.paddle.step()
            for i in self.balls: i.step(self.paddle)
            for i in self.hazards:i.step()
            for i in self.powerups:i.step()
            for i in self.lifehearts:i.step()

            if len(LOGIC.balls) == 0:
                LOGIC.extralives -= 1
                LOGIC.powerups.clear()
                LOGIC.hazards.clear()
                LOGIC.lifehearts.clear()
                LOGIC.bullets.clear()
                LOGIC.powerup = [0,0,0,0]
                LOGIC.hazard = [0]
                LOGIC.paused = False
                if LOGIC.extralives < 0: 
                    if LOGIC.score > LOGIC.highscore: 
                        with open(path.join('highscore.json'), 'w') as f: dump(LOGIC.score, f); f.close()
                    exit()
                BALL.start = False
                self.balls.append(BALL(-100,HEIGHT*.85))

            if BALL.start and LOGIC.tutorialtimer > 0: LOGIC.tutorialtimer -= 1

    def draw(self):
        self.blink = self.blink+1 if self.blink < 50 else 0

        WIN.fill((15,0,25))
        for i in range(self.bc):
            for j in range(self.br):
                if self.blocks[i][j].alive:
                    self.blocks[i][j].draw()
        for i in self.bullets: i.draw()
        self.paddle.draw()
        for i in self.balls:i.draw()
        for i in self.powerups:i.draw()
        for i in self.hazards:i.draw()
        for i in self.lifehearts:i.draw()

        for i in range(3): 
            WIN.blit(self.lifeslotsprite,g.Rect(WIDTH-144+40*i,21,32,32))
            if i < LOGIC.extralives: WIN.blit(self.lifesprite,g.Rect(WIDTH-144+40*i,21,32,32))

        drawtext(self.score,30,"white",WIDTH/2-3,40,"center")
        
        if self.paused and self.blink % 50 > 25:
            drawtext("PAUSED",50,"white",WIDTH/2,HEIGHT/2,"center")
            drawtext("HIGH SCORE:",50,"white",WIDTH/2,HEIGHT/2+100,"center")
            drawtext(LOGIC.highscore,50,"white",WIDTH/2,HEIGHT/2+150,"center")

        if LOGIC.tutorialtimer > 0:
            s = g.Surface((WIDTH,HEIGHT))
            s.set_alpha(interp(LOGIC.tutorialtimer,[0,60],[0,100]))
            WIN.blit(s,g.Rect(0,0,WIDTH,HEIGHT))
            for i in range(len(self.tutorialsprite)):
                self.tutorialsprite[i].set_alpha(interp(LOGIC.tutorialtimer,[0,60],[0,255]))
                WIN.blit(self.tutorialsprite[i],g.Rect(WIDTH/2-300+230*i,HEIGHT/2,180,120))

        g.display.update()

game = LOGIC()

while(1):

    for event in g.event.get():
        if event.type == g.QUIT:
            exit()
        if event.type == g.KEYUP:
            if event.key == g.K_ESCAPE and BALL.start:
                LOGIC.paused = not LOGIC.paused
        if event.type == g.MOUSEBUTTONUP:
            if event.button == 1:
                PADDLE.playingwithmouse = True
            if event.button == 3 and BALL.start:
                LOGIC.paused = not LOGIC.paused
        if event.type == g.MOUSEWHEEL and event.y == 1:
            if len(game.balls) == 1:
                if not BALL.start:
                    LOGIC.balls[0].startgame()

    game.step()
    game.draw()
    clock.tick(60)
