import pygame, sys, math, random, time
from json import dumps as jsonDump
from json import loads as jsonLoad
from  tkinter import Tk, filedialog, messagebox
from pygame.locals import*
from vec2 import Vector2

'''
Author: ChickenHoshi, public domain
sources:
     https://www.youtube.com/user/codingmath
     http://code.tutsplus.com/tutorials/euclidean-vectors-in-flash--active-8192
     http://code.tutsplus.com/series/collision-detection-and-reaction--active-10878
     http://codeflow.org/entries/2010/nov/29/verlet-collision-with-impulse-preservation/
'''

pygame.init()
FPS = 60
fpsClock = pygame.time.Clock()
#set up window
scale = 1
windowX, windowY = int(1280*scale),int(800*scale)
WXh,WYh = windowX//2, windowY//2
DISPLAYSURF = pygame.display.set_mode((windowX,windowY),DOUBLEBUF)
flags=DISPLAYSURF.get_flags()
pygame.display.set_caption('Game')
font = pygame.font.SysFont('consolas',20)
#set up colors

BLACK = ( 0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0,200,0)
BROWN = (100,100,0)
RED = (200,0,0)
BLUE = (0,0,200)

'''
 _______ _       _______ _______ _______ _______ _______ 
(  ____ ( \     (  ___  (  ____ (  ____ (  ____ (  ____ \
| (    \| (     | (   ) | (    \| (    \| (    \| (    \/
| |     | |     | (___) | (_____| (_____| (__   | (_____ 
| |     | |     |  ___  (_____  (_____  |  __)  (_____  )
| |     | |     | (   ) |     ) |     ) | (           ) |
| (____/| (____/| )   ( /\____) /\____) | (____//\____) |
(_______(_______|/     \\_______\_______(_______\_______)
                                                         
'''

class Game():
     def __init__(self,name):
          self.name = name
          self.mpos = (0,0)
          self.lmb = False
          self.keys = False
          self.time = 0
     def update(self, fpsClock):
          if self.time < 1200: self.time += 1
          else: self.time  =0
          if self.time%60==0: pygame.display.set_caption(self.name+' | '+str(int(fpsClock.get_fps()))+' FPS')
          self.mpos = pygame.mouse.get_pos()
          self.lmb = pygame.mouse.get_pressed()[0]
          self.keys = pygame.key.get_pressed()
          


class Stick():
     sticks = []
     def __init__(self, p1,p2, vis = True):
          self.p1 = p1
          self.p2 = p2
          self.distance = (self.p1.pos - self.p2.pos).get_magnitude()
          self.visible = vis
          Stick.sticks.append(self)
     def updateStick(self):
          d = self.p1.pos - self.p2.pos
          dist = d.get_magnitude()
          diff = self.distance - dist
          if dist == 0: dist = 0.00001
          percent = diff/ dist/ 2
          offset = d* percent
          if not self.p1.pinned:
               self.p1.pos += offset
          if not self.p2.pinned:
               self.p2.pos -= offset
     def drawStick(self):
          pygame.draw.line(DISPLAYSURF,(200,100,50), self.p1.pos.get_tuple(),
                           self.p2.pos.get_tuple(), 1)
     
     @classmethod
     def update(cls):
          for s in cls.sticks:
               s.updateStick()
     @classmethod
     def draw(cls):
          for s in cls.sticks:
               if s.visible or True:
                    s.drawStick()  
     
          
          
     

class Point():
     points = []
     bounce = 0.9
     GRAV = 0.5
     FRIC = 0.98
     def __init__(self, pos, size, pinned = False):
          self.pinned = pinned
          self.color = (200,100,50) if not pinned else BLUE
          self.pos = pos
          self.oldPos = pos
          self.size = size
          self.isMotor = False
          self.spinPos = None
          self.spinRad = None
          self.spinSpeed = None
          self.currentSpin = None
          Point.points.append(self)
     def motorize(self, pos, speed = math.pi/50, current = 0):
          self.isMotor = True
          self.pinned = True
          self.spinPos = pos
          self.spinSpeed = speed
          self.currentSpin = (self.pos - pos).angle()
          self.spinRad = (self.pos - self.spinPos).get_magnitude()
          self.color = GREEN
     def drawPoint(self):
          pygame.draw.circle(DISPLAYSURF, self.color, self.pos.get_tuple(True), self.size,1)
     def updatePoint(self):
          v = (self.pos - self.oldPos) * Point.FRIC
          self.oldPos = self.pos
          self.pos += v
          self.pos.y += Point.GRAV
     def updateMotor(self):
          self.currentSpin += self.spinSpeed
          self.pos = self.spinPos + Vector2(self.spinRad * math.cos(self.currentSpin),
                                            self.spinRad * math.sin(self.currentSpin))
     def constrainPoint(self):
          #border collision
          v = (self.pos - self.oldPos) * Point.FRIC
          if self.pos.x > windowX - self.size:
               self.pos.x = windowX - self.size
               self.oldPos.x = self.pos.x + v.x * Point.bounce
          elif self.pos.x < 0 + self.size:
               self.pos.x = 0 + self.size
               self.oldPos.x = self.pos.x + v.x * Point.bounce
          if self.pos.y > windowY - self.size:
               self.pos.y = windowY - self.size
               self.oldPos.y = self.pos.y + v.y * Point.bounce
          elif self.pos.y < 0 + self.size:
               self.pos.y = 0 + self.size
               self.oldPos.y = self.pos.y + v.y * Point.bounce
     @classmethod
     def update(cls):
          for p in cls.points:
               if not p.pinned:
                    p.updatePoint()
               elif p.isMotor:
                    p.updateMotor()
     @classmethod
     def updateBorders(cls):
          for p in cls.points:
               if not p.pinned:
                    p.constrainPoint()
     @classmethod
     def draw(cls):
          for p in cls.points:
               p.drawPoint()
     @classmethod
     def collide(cls):
          lb = len(cls.points)
          for i in range(lb):
               b1 = cls.points[i]
               for j in range(i+1, lb):
                    b2 = cls.points[j]
                    d = b1.pos - b2.pos
                    l = d.get_magnitude()
                    target = b1.size + b2.size
                    if l < target:
                         if l == 0: l = 0.0000001
                         factor = (l-target)/l
                         q = 0.5
                         if not b1.pinned:
                              b1.pos -= d*factor*q
                         if not b2.pinned:
                              b2.pos += d*factor*q
     @classmethod
     def collideLine(cls):
          for i in range(len(cls.points)):
               p = cls.points[i]
               for j in range(len(Stick.sticks)):
                    s1 = Stick.sticks[j].p1
                    s2 = Stick.sticks[j].p2
                    if not(p == s1 or p == s2):
                         cVec = p.pos - s1.pos
                         line = s2.pos - s1.pos
                         cVec_norm = cVec.project(line.leftNormal())
                         cVec_line = cVec.project(line)
                         if abs(cVec_norm) < p.size and line.dot(cVec) > 0 \
                            and cVec_line < line.get_magnitude():
                              normPos = (line * (cVec.dot(line)/line.dot(line))) + s1.pos 
                              newOld = normPos - p.oldPos
                              factor = (p.size - abs(cVec_norm))/p.size
                              q = .2
                              if not p.pinned:
                                   p.pos -= newOld*factor*q
                              if not s1.pinned:
                                   factor2 = (s1.pos - normPos).get_magnitude()/Stick.sticks[j].distance
                                   s1.pos += newOld*factor*q/factor2
                              if not s2.pinned:
                                   factor2 = (s2.pos - normPos).get_magnitude()/Stick.sticks[j].distance
                                   s2.pos += newOld*factor*q/factor2
          
     




'''        
 _______         _       _______________________________ _       _______ 
(  ____ |\     /( (    /(  ____ \__   __\__   __(  ___  ( (    /(  ____ \
| (    \| )   ( |  \  ( | (    \/  ) (     ) (  | (   ) |  \  ( | (    \/
| (__   | |   | |   \ | | |        | |     | |  | |   | |   \ | | (_____ 
|  __)  | |   | | (\ \) | |        | |     | |  | |   | | (\ \) (_____  )
| (     | |   | | | \   | |        | |     | |  | |   | | | \   |     ) |
| )     | (___) | )  \  | (____/\  | |  ___) (__| (___) | )  \  /\____) |
|/      (_______|/    )_(_______/  )_(  \_______(_______|/    )_\_______)
                                                                         
'''
def load():
     root = Tk()
     root.withdraw()
     root.filename =  filedialog.askopenfilename(title = "choose your file",
                  filetypes = [("JSON files", ".json"),("All files", "*")])
     pbackup = None
     sbackup = None
     with open(root.filename, 'r') as myfile:
          data=myfile.read()
     try:
          d = jsonLoad(data)
          pbackup = Point.points[1:]
          sbackup = Stick.sticks[:]
          del Point.points[1:]
          del Stick.sticks[:]
          for p in d['points']:
               a = Point(Vector2(p['pos']['x'], p['pos']['y']), p['size'], p['pinned'])
               if p['isMotor']:
                    a.motorize(Vector2(p['spinPos']['x'], p['spinPos']['y']), p['spinSpeed'], p['currentSpin'])
                    a.currentSpin = p['currentSpin']
          for s in d['lines']:
               b = Stick(Point.points[s['p1']], Point.points[s['p2']], s['visible'])
     except Exception:
          messagebox.showinfo("Error", "Invalid JSON")
          if pbackup and sbackup:
               Point.points += pbackup
               Stick.sticks += sbackup
          
     

def save():
     root = Tk()
     root.withdraw()
     filename = filedialog.asksaveasfilename( filetypes = [("JSON files", ".json"),("All files", "*")],defaultextension='.json')
     if filename:
          
          d = {'points':[], 'lines':[]}
          for ppp in range(1,len(Point.points)):
               p = Point.points[ppp]
               pd = {
                    'pos': {'x': p.pos.x, 'y': p.pos.y},
                    'pinned' : p.pinned,
                    'size' : p.size,
                    'isMotor' : p.isMotor,
                    'spinPos': p.spinPos if p.spinPos == None else {'x': p.spinPos.x, 'y': p.spinPos.y},
                    'spinSpeed' : p.spinSpeed,
                    'currentSpin' : p.currentSpin
                    }
               d['points'].append(pd)
          for s in Stick.sticks:
               sd = {
                         'p1': save_helper_point_finder(s.p1),
                         'p2': save_helper_point_finder(s.p2),
                         'visible' : s.visible
                    }
               d['lines'].append(sd)
          f = open(filename, 'w')
          f.write(jsonDump(d, indent = 4))
          f.close()
def save_helper_point_finder(p):
     for pp in range(len(Point.points)):
          if Point.points[pp] == p:
               return pp
def stick_make(points, connections):
     '''points, a list of Points,
        connections, a list of '2 indices in points , in a tuple' '''
     for c in connections:
          Stick(points[c[0]], points[c[1]], c[2])
          
     


     
     
     
          
def polyPoints(pts, lines = False):
     l = [p.pos.get_tuple() for p in pts]
     if not lines: pygame.draw.polygon(DISPLAYSURF,(200,100,50),l)
     else: pygame.draw.lines(DISPLAYSURF,(200,100,50),False,l)
G = Game('Point Physics Simulator')
def main():
     global flags

     ##instructions
     ins = ['This is a verlet based physics simulator(work in progress)',
            'It is based on POINTS and LINES.',
            'Instructions',
            'A starting POINT(_s) is given the position of the mouse and is collidable ',
            'Moving the MOUSEWHEEL, changes the size of _s',
            'Z toggles LINE MODE, a white square appears at _s',
            'X toggles PINNED MODE, _s turns blue' ,
            'M toggles in MOTOR MODE, a green sqare appears at _s',
            'SPACE toggles pause of the simulation, a white border appears',
            'C clears all',
            'Clicking produces a POINT with size _s (not in LINE or MOTOR mode) ',
            'In LINE mode, click on 2 POINTS to join them',
            'In Motor mode, click 1 puts a POINT(_m) at _s, ',
            '    click 2 rotates _m clockwise around a new POINT at _s ',
            'Ctrl-S to save the current creation',
            'Ctrl-O to load a creation, JSON file',
            'Ctrl-Z to undo last action']
     ins = [font.render(ins[i], True, (150,150,150)) for i in range(len(ins))]
     
     insSurf = pygame.Surface((windowX, windowY))
     insSurf.fill((100,100,100))
     for i in range(len(ins)):
          insSurf.blit(ins[i],(5, i*20))

     


     undo = []
     paused = False
     stickMode = False
     motorMode = False
     pinMode = False
     stickTemp = []
     pushp = Point(Vector2(),50,pinned = True)
     save_helper_point_finder(pushp)
     pushp.color = (200,100,50)
     while True: ##main game loop
          DISPLAYSURF.blit(insSurf,(0,0))
          G.update(fpsClock)
          
          if stickMode or motorMode:
               indColor = WHITE if stickMode else GREEN
               if len(stickTemp) == 0:
                    pygame.draw.rect(DISPLAYSURF, indColor, [G.mpos[0]-5,G.mpos[1]-5,10,10],1)
               else:
                    pygame.draw.rect(DISPLAYSURF, indColor, [G.mpos[0]-5,G.mpos[1]-5,10,10],1)
                    if stickMode: somePos = stickTemp[0].pos
                    else: somePos = stickTemp[0]
                    pygame.draw.rect(DISPLAYSURF, indColor, [somePos.x-5,somePos.y-5,10,10],1)
                    pygame.draw.line(DISPLAYSURF,indColor,G.mpos,somePos.get_tuple(),1)
                              
          if not paused:
               Point.update()
               Point.collideLine()
               Point.collide()
               for i in range(4):
                    Stick.update()
                    Point.updateBorders()
               
          else:
               pygame.draw.rect(DISPLAYSURF,WHITE,(0,0,windowX, windowY), 5)
          pushp.oldPos = pushp.pos 
          pushp.pos = Vector2(G.mpos[0], G.mpos[1])
          Stick.draw()
          Point.draw()
          mods = pygame.key.get_mods()
          for event in pygame.event.get():
               if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                         paused = not paused
                         if stickMode :
                              stickMode = not stickMode
                              del stickTemp[:]
                    if event.key == K_s:
                         if mods & KMOD_CTRL:
                              save()
                    if event.key == K_o:
                         if mods & KMOD_CTRL:
                              load()
                    if event.key == K_z:
                         if mods & KMOD_CTRL:
                              if len(undo) > 0:
                                   del stickTemp[:]
                                   if undo[-1] == 's':
                                        del Stick.sticks[-1]
                                   elif undo[-1] == 'p':
                                        del Point.points[-1]
                                   del undo[-1]
                         else:
                              stickMode = not stickMode
                              
                              if not stickMode or motorMode: del stickTemp[:]
                              motorMode = False
                    if event.key == K_m:
                         motorMode = not motorMode
                         
                         if not motorMode and stickMode: del stickTemp[:]
                         stickMode =  False
                    if event.key == K_x:
                         pinMode = not pinMode
                         if not pinMode: pushp.color = (200,100,50)
                         else: pushp.color = BLUE
                    if event.key == K_c:
                         del Point.points[1:]
                         del Stick.sticks[:]
                    if event.key == K_ESCAPE:
                         pygame.quit()
                         sys.exit()
                    if event.key == K_f:
                         if flags&FULLSCREEN == False:
                              flags |= FULLSCREEN
                              pygame.display.set_mode((windowX,windowY), flags)
                         else:
                              flags ^= FULLSCREEN
                              pygame.display.set_mode((windowX,windowY), flags)
               if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1: #LMB
                         
                         if stickMode:
                              
                              if len(stickTemp) == 0:
                                   for pp in range(1,len(Point.points)):
                                        p = Point.points[pp]
                                        d = math.hypot(event.pos[0] - p.pos.x, event.pos[1] - p.pos.y)
                                        if d < p.size :
                                             
                                             stickTemp.append(p)
                                             stickTemp.append(pp)
                                             
                                             break
                              elif len(stickTemp) == 2:
                                   for pp in range(1,len(Point.points)):
                                        p = Point.points[pp]      
                                        if math.hypot(event.pos[0] - p.pos.x, event.pos[1] - p.pos.y) < p.size:
                                             if p != stickTemp[0]:
                                                  Stick(Point.points[stickTemp[1]],Point.points[pp] ,True)
                                                  undo.append('s')
                                                  del stickTemp[:]
                                             break
                         elif motorMode:
                              if len(stickTemp) == 0:
                                   motorP = Vector2(event.pos[0], event.pos[1])
                                   stickTemp.append(motorP)
                              else:
                                   Point(stickTemp[0], pushp.size, True).motorize(Vector2(event.pos[0],event.pos[1]))
                                   undo.append('p')
                                   del stickTemp[:]
                                   
                                   
                         else:
                              Point(Vector2(event.pos[0], event.pos[1]), pushp.size, pinMode)
                              undo.append('p')
                    elif event.button == 4:
                         pushp.size += 1 if pushp.size <= 100 else 0
                    elif event.button == 5:
                         pushp.size -= 1 if pushp.size >= 5 else 0

                                   
                                   
                                             
               if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
          pygame.display.update()
          fpsClock.tick(FPS)


if __name__ == '__main__':
     main()
