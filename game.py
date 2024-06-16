import pygame
import math
import random

def real(n,X):
  if X:
    return n-goblin.x+width/2
  return n-goblin.y+height/2

class entity:
  def __init__(self,x,y,w,h):
    self.x = x 
    self.y = y
    self.h = h
    self.w = w

  def isColliding(self,other,pos=[]):
    pos = [self.x,self.y] if len(pos) == 0 else pos
    if pos[0] + self.w > other.x and pos[0] < other.x + other.w and pos[1] + self.h > other.y and pos[1] < other.y + other.h:
      return True
    return False

  def plot(self,img):
    x = real(self.x,1)
    y = real(self.y,0)
    if not (x+self.w < 0 or y+self.h < 0 or x > width or y > height):
      screen.blit(img,(x,y))

class block:
  def __init__(self,images,drop,n):
    self.images = images
    self.drop = drop
    self.next = n

class tile(entity):
  width = 100
  height = 100

  images = ["grass","grass2","flowers","tree","stump","fence","fenceUp","corner","corner2","crossing","crossing2","intersection"]
  blocks = {"tree":block([3],"wood",4),"fence":block([5,6,7,8,9,10,11],"wood",0)}
  for i in range(len(images)):
    images[i] = pygame.image.load("images/"+images[i]+".png")
    images[i] = pygame.transform.scale(images[i],(width,height))

  def __init__(self,img,x,y):
    super().__init__(x,y,self.width,self.height)
    self.changeTile(img)

  def orient(self,Map):
     x,y = self.x//self.width,self.y//self.height
     neibors = [Map[x-1][y],Map[x+1][y],Map[x][y-1],Map[x][y+1]]
     for i in range(4):
       neibors[i] = neibors[i].block == self.block
     if neibors[0] and neibors[1] and neibors[2] and neibors[3]:
       return self.blocks[self.block].images[-1]
     if neibors[0] and neibors[1] and neibors[2]:
       return self.blocks[self.block].images[5]
     if neibors[0] and neibors[1] and neibors[3]:
       return self.blocks[self.block].images[4]
     if neibors[1] and neibors[2]:
       return self.blocks[self.block].images[2]
     if neibors[1] and neibors[3]:
       return self.blocks[self.block].images[3]
     if neibors[0] and neibors[3]:
       self.reflect = [True,False]
       return self.blocks[self.block].images[3]
     if neibors[0] and neibors[2]:
       self.reflect = [True,False]
       return self.blocks[self.block].images[2]
     if neibors[2] or neibors[3]:
       return self.blocks[self.block].images[1]
     return self.blocks[self.block].images[0]

  def changeTile(self,img):
    self.img = img
    self.reflect = [False,False]
    if img in self.blocks:
      self.drop  = self.blocks[img].drop
      self.next  = self.blocks[img].next
      self.block = img
      self.img = self.orient(Map) if len(self.blocks[img].images)>1 else self.blocks[img].images[0]
      self.solid = True
    else:
      self.solid = False
      self.block = ""

  def draw(self):
    image = self.images[self.img]
    if self.reflect == [False,True]:
      print("hello")
    if self.reflect != [False,False]:
      image = pygame.transform.flip(image,self.reflect[0],self.reflect[1])
    self.plot(image)

class tool(entity):
  def __init__(self,image,w,h,c,kb,d,des = False):
    super().__init__(0,0,w,h)
    self.img = pygame.image.load(image)
    self.image = pygame.transform.scale(self.img,(w,h))
    self.useTime = c
    self.coolDown = c
    self.t = int(c*0.75)
    self.using = False
    self.angle = 0
    self.kb = kb
    self.dis = d
    self.destructive = des

  def use(self,user):
    if self.useTime > 0 or self.using:
       return
    ux,uy = user.x+user.w/2,user.y+user.h/2
    a = math.atan2(height/2-mousePos[1],width/2-mousePos[0])
    self.angle = 180-(a*180/math.pi)
    self.using = True
    self.draw(user)
    for obj in objects:
      if self.isColliding(obj) and obj != user:
         x = self.kb*math.cos((-self.angle)*math.pi/180)
         y = self.kb*math.sin((-self.angle)*math.pi/180)
         obj.hit(1,x,y)
    if self.destructive:
      for x in range(int(self.x/tile.width)-2,int(self.x/tile.width)+2):
        for y in range(int(self.y/tile.height)-2,int(self.y/tile.height)+2):
          if self.isColliding(Map[x][y]) and Map[x][y].solid:
            if Map[x][y].drop != "NA":
              user.invent[Map[x][y].drop] += 1
            Map[x][y].changeTile(Map[x][y].next)

  def draw(self,user):
    ux,uy = user.x+user.w/2,user.y+user.h/2
    self.x = ux + self.dis*math.cos((-self.angle)*math.pi/180)
    self.y = uy + self.dis*math.sin((-self.angle)*math.pi/180)
    img = self.image if self.x > ux else pygame.transform.flip(self.image,False,True)
    img = pygame.transform.rotate(img,self.angle)
    self.x -= img.get_width()/2
    self.y -= img.get_height()/2
    self.plot(img)

  def update(self,user):
    if self.using:
      self.t -= 1
      self.draw(user)
      if self.t < 0:
        self.using = False
        self.t = int(self.coolDown*0.75)
        self.useTime = self.coolDown
    else:
      self.useTime -= 1

class sprite(entity):
  def __init__(self,x,y,images,width,height):
    super().__init__(x,y,width,height)
    self.vel = [0,0]
    self.friction = 0.1
    
    self.reflect = False
    self.imgs    = []
    for image in images:
      img = pygame.image.load(image)
      self.imgs += [pygame.transform.scale(img,(width,height))]
    self.img = 0
    self.walkTime = 0

    self.tools = []
    self.holding = 0

    self.health = 10

  def animate(self):
    if (self.vel[0] == 0) and (self.vel[1] == 0):
      self.img = 0
      self.walkTime = 0
    else:
      if self.walkTime > int(30/math.sqrt((self.vel[0]**2+self.vel[1]**2))):
        self.img = (self.img+1)%2
        self.walkTime = 0
      self.walkTime += 1

  def hit(self,damage,xKnock,yKnock):
    self.vel[0],self.vel[1] = 0,0
    self.vel[0] += xKnock
    self.vel[1] += yKnock
    self.health -= damage
    if self.health < 0:
       objects.remove(self)

  def updateVel(self):
    self.vel[0] -= self.vel[0] * self.friction 
    self.vel[1] -= self.vel[1] * self.friction
    for i in range(2):
      if self.vel[i]**2 < 0.01:
         self.vel[i] = 0
  
  def draw(self,screen):
    if len(self.tools) > 0:
       self.tools[self.holding].update(self)
    img = self.imgs[self.img]
    if self.reflect:
       img = pygame.transform.flip(img,True,False)
    self.plot(img) 

  def bounce(self,objects,Map):
    for obj in objects:
      if self.isColliding(obj,[self.x+self.vel[0],self.y+self.vel[1]]) and obj != self:
        vx,vy = obj.vel[0],obj.vel[1]
        obj.vel[0],obj.vel[1] = self.vel[0],self.vel[1]
        self.vel[0],self.vel[1] = vx,vy
    for col in Map:
      for t in col:
        if t.solid:
          if self.isColliding(t,[self.x+self.vel[0],self.y]):
            self.vel[0] = -self.vel[0]
          if self.isColliding(t,[self.x,self.y+self.vel[1]]):
            self.vel[1] = -self.vel[1]

  def update(self):
    self.updateVel()
    self.bounce(objects,Map)
    self.x += self.vel[0]
    self.y += self.vel[1]
    self.animate()
    self.reflect = (self.vel[0]<0) if self.vel[0]**2>0 else self.reflect

class enemy(sprite):
  def __init__(self,x,y,images,w,h,f,a):
    super().__init__(x,y,images,w,h)
    self.friction = f
    self.acceleration = a

  def update(self):
    self.vel[0] += self.acceleration*(1-2*int(goblin.x<self.x))
    self.vel[1] += self.acceleration*(1-2*int(goblin.y<self.y))
    self.updateVel()
    self.bounce(objects,Map)
    self.x += self.vel[0]
    self.y += self.vel[1]
    self.animate()

class player(sprite):
  def __init__(self,x,y,image,width,height,arrows):
    super().__init__(x,y,image,width,height)
    self.k = arrows
    self.rolling = 0
    self.invent = {"wood":0}

  def roll(self):
    if self.rolling < 1 and (self.vel[0] != 0 or self.vel[1] != 0):
      a = math.atan2(self.vel[1],self.vel[0])
      self.x += 100*math.cos(a)
      self.y += 100*math.sin(a)
      self.rolling = 20

  def update(self):
    if keys[self.k[0]]:
      self.vel[0] -= 1
    if keys[self.k[1]]:
      self.vel[0] += 1
    if keys[self.k[2]]:
      self.vel[1] -= 1
    if keys[self.k[3]]:
      self.vel[1] += 1
    if pygame.mouse.get_pressed()[0]:
      self.tools[self.holding].use(self)
    if keys[self.k[4]]:
      self.roll()
    if pygame.mouse.get_pressed()[2] and self.invent["wood"] >0:
      x = int((self.x+mousePos[0]-width/2)/tile.width)
      y = int((self.y+mousePos[1]-height/2)/tile.height)
      Map[x][y].changeTile("fence")
      self.invent[Map[x][y].drop] -= 1

    self.updateVel()
    self.bounce(objects,Map)
    self.x += self.vel[0]
    self.y += self.vel[1]
    if self.rolling > 0:
       self.rolling -= 1
       if self.rolling > 10:
         self.img = 2
       else:
         self.img = 0
    else:
       self.animate()
    self.reflect = mousePos[0] < width/2

def generateMap(w,h):
  Map = []
  for x in range(w):
    col = []
    for y in range(h):
      col += [tile(random.choice([0,1,2,"tree"]),x*tile.width,y*tile.height)]
    Map += [col]
  return Map

pygame.init()
width = 1000
height = 600
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption('football')

mapWidth = 100
mapHeight = 100
Map = generateMap(mapWidth,mapHeight)

clock = pygame.time.Clock()
mousePos = (0,0)
keys = []

sword = tool("images/sword.png",76,28,10,10,65)
axe = tool("images/axe.png",92,124,20,30,41,True)
hammer = tool("images/hammer.png",111,153,20,50,30)
goblin = player(tile.width*mapWidth/2,tile.height*mapHeight/2,["images/goblin.png","images/goblinRun.png","images/goblinRolling.png"],54,48,[pygame.K_a,pygame.K_d,pygame.K_w,pygame.K_s,pygame.K_SPACE,pygame.K_e])
goblin.tools += [hammer,sword,axe]

objects = [goblin]
for i in range(3):
   slime = enemy(random.randint(0,width),random.randint(0,height),
           ["images/slime.png","images/slime2.png"],40,40,0.05,0.3)
   objects += [slime]

running = True
while running:
  mousePos = pygame.mouse.get_pos()
  screen.fill((250,250,250))
  keys = pygame.key.get_pressed()

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_q:
        goblin.holding = (goblin.holding+1)%len(goblin.tools)

  for col in Map:
    for t in col:
      t.draw()

  for obj in objects:
    obj.update()
    obj.draw(screen)
  
  pygame.display.update() 
  clock.tick(40) #use the clock to cap the framerate

pygame.quit()
