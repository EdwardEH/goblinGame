import pygame
import math

class entity:
  def __init__(self,x,y,w,h):
    self.x = x 
    self.y = y
    self.h = h
    self.w = w

  def isColliding(self,other):
    if self.x + self.w > other.x and self.x < other.x + other.w and self.y + self.h > other.y and self.y < other.y + other.h:
      return True
    return False

class tool(entity):
  def __init__(self,image,h,w,c):
    super().__init__(0,0,w,h)
    self.img = pygame.image.load(image)
    self.image = pygame.transform.scale(self.img,(w,h))
    self.useTime = c
    self.coolDown = c
    self.t = 10

  def update(self,user):
    ux,uy = user.x+user.w/2,user.y+user.h/2
    a = math.atan2(uy-mousePos[1],ux-mousePos[0])
    self.x = ux + (40+self.t*2*int(user.using))*math.cos(a+math.pi)
    self.y = uy + (40+self.t*2*int(user.using))*math.sin(a+math.pi)
    img = self.image
    if self.x > ux:
      img = pygame.transform.flip(img,True,False)
    img = pygame.transform.rotate(img,270-(a*180/math.pi))
    screen.blit(img,(self.x-img.get_width()/2,self.y-img.get_height()/2))

    if user.using:
      self.t -= 1
      for obj in objects:
        if self.isColliding(obj):
           print("hello")
      if self.t < 0:
        user.using = False
        self.t = 10
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
    self.using = False

  def animate(self):
    if (self.vel[0] == 0) and (self.vel[1] == 0):
      self.img = 0
      self.walkTime = 0
    else:
      if self.walkTime > int(30/math.sqrt((self.vel[0]**2+self.vel[1]**2))):
        self.img = (self.img+1)%2
        self.walkTime = 0
      self.walkTime += 1

  def updateVel(self):
    self.vel[0] -= self.vel[0] * self.friction 
    self.vel[1] -= self.vel[1] * self.friction
    for i in range(2):
      if self.vel[i]**2 < 0.01:
         self.vel[i] = 0
  
  def draw(self,screen):
    img = self.imgs[self.img]
    if self.reflect:
       img = pygame.transform.flip(img,True,False)
    screen.blit(img,(self.x,self.y)) 
    if len(self.tools) > 0:
       self.tools[self.holding].update(self)

  def bounce(self,objects):
    if self.x<0:
      self.x = 1 
      self.vel[0] = -self.vel[0]
    if self.x+self.w>width:
      self.x = width-self.w
      self.vel[0] = -self.vel[0]
    if self.y<0:
      self.y = 1 
      self.vel[1] = -self.vel[1]
    if self.y+self.h>height:
      self.y = height-self.h
      self.vel[1] = -self.vel[1]

    for obj in objects:
      if self.isColliding(obj):
        vx,vy = obj.vel[0],obj.vel[1]
        obj.vel[0],obj.vel[1] = self.vel[0],self.vel[1]
        self.vel[0],self.vel[1] = vx,vy 

  def update(self):
    self.updateVel()
    self.bounce(objects)
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
    self.bounce(objects)
    self.x += self.vel[0]
    self.y += self.vel[1]
    self.animate()

class player(sprite):
  def __init__(self,x,y,image,width,height,arrows):
    super().__init__(x,y,image,width,height)
    self.k = arrows
  
  def update(self):
    if keys[self.k[0]]:
      self.vel[0] -= 1
    if keys[self.k[1]]:
      self.vel[0] += 1
    if keys[self.k[2]]:
      self.vel[1] -= 1
    if keys[self.k[3]]:
      self.vel[1] += 1
    if keys[self.k[4]] and self.tools[self.holding].useTime < 0:
      self.using = True

    self.updateVel()
    self.bounce(objects)
    self.x += self.vel[0]
    self.y += self.vel[1]
    self.animate()
    self.reflect = mousePos[0] < self.x

pygame.init()
width = 600
height = 600
screen = pygame.display.set_mode((width,height))
pygame.display.set_caption('football')
clock = pygame.time.Clock()
mousePos = (0,0)
keys = []

dagger = tool("images/Knife.png",40,10,20)
goblin = player(200,200,["images/goblin.png","images/goblinRun.png"],54,48,
[pygame.K_a,pygame.K_d,pygame.K_w,pygame.K_s,pygame.K_SPACE])
slime = enemy(300,300,["images/slime.png","images/slime2.png"],40,40,0.01,0.3)
goblin.tools += [dagger]

objects = [goblin,slime]

running = True
while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

  screen.fill((250,250,250))
  keys = pygame.key.get_pressed() #get key presses
  mousePos = pygame.mouse.get_pos()

  for obj in objects: #update and draw all objects
    obj.update()
    obj.draw(screen)
  
  pygame.display.update() 
  clock.tick(40) #use the clock to cap the framerate

pygame.quit()
