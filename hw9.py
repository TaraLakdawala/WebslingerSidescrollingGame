#################################################
# hw9.py
#
# Your name: Tara Lakdawala
# Your andrew id: tlakdawa
#################################################

import math, copy, random

from cmu_112_graphics import *
from tkinter import *
from PIL import Image

#################################################
# Helper functions
#################################################

def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

#################################################
# Functions for you to write
#################################################

class Bird(object):
    isMigrating=False

    @staticmethod
    def startMigrating():
        Bird.isMigrating=True

    @staticmethod
    def stopMigrating():
        Bird.isMigrating=False

    def __init__(self, species):
        self.species=species
        self.eggs=0

    def __eq__(self, other):
        if isinstance(other, Bird):
            return self.species == other.species
        else: return False
    
    def __repr__(self):
        if self.eggs==1:
            return f'{self.species} has {self.eggs} egg'
        return f'{self.species} has {self.eggs} eggs'

    def __hash__(self):
        return hash(self.species)

    def countEggs(self):
        return self.eggs

    def fly(self):
        #default: can fly
        return "I can fly!"

    def layEgg(self):
        self.eggs+=1

class Penguin(Bird):
    def fly(self):
        return "No flying for me."
    
    def swim(self):
        return "I can swim!"

class MessengerBird(Bird):
    def __init__(self, species, message):
        super().__init__(species)
        self.message=message

    def deliverMessage(self):
        return self.message
# ignore_rest

#the setup for modal classes are closely based off of the modal classes on:
#http://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
#the code for the transposed background is close to the code at:
#http://www.cs.cmu.edu/~112/notes/notes-animations-part2.html#flipImage


def runCreativeSidescroller():
    class SplashScreenMode(Mode):
        def appStarted(mode):
            #splash screen background
            url = 'https://tinyurl.com/spidermanbackground'
            mode.background = mode.loadImage(url)
            mode.backX=900
            mode.backY=500

        def redrawAll(mode, canvas):
            font = 'Arial 20'
            canvas.create_image(mode.backX, mode.backY,
                        image=ImageTk.PhotoImage(mode.background))
            canvas.create_text(mode.width/2, 150, 
                        text='Welcome to Webslinger Royale!', font=font, 
                        fill='white')
            canvas.create_text(mode.width/2, 200,
                        text='Sling your spiderwebs to shoot your enemies!', 
                        font=font, fill='white')
            canvas.create_text(mode.width/2, 250, 
                        text='Press any key to begin!', font=font, fill='white')

        def keyPressed(mode, event):
            if event.key=='S':
                print('''The objective of the game is to shoot down 
all obstacles and enemy fire. Start running by pressing the right arrow.
To stop running, press left arrow. To shoot, drag the mouse to the right. 
You can't shoot anything unless you're running, so the left arrow essentially
pauses gameplay. Two hits from fire or obstacles cause you to lose 1 life''')
            else:
                mode.app.setActiveMode(mode.app.gameMode)

    class GameMode(Mode):
        def getImages(mode):
            url1 = 'https://tinyurl.com/spideyboisprite'
            mode.spritesheet = mode.loadImage(url1)
            url2 = 'https://tinyurl.com/spidermanbackground'
            mode.background1 = mode.loadImage(url2)
            mode.background2 = mode.background1.transpose(Image.FLIP_LEFT_RIGHT)
            url3 = 'https://tinyurl.com/y54m9rc6'
            mode.enemyfire = mode.loadImage(url3)

        def setRunning(mode):
            mode.backX = 900
            mode.backY = 500
            mode.sprites=[]
            spriteX=377
            mode.spriteSize=70
            mode.starterSprite=mode.spritesheet.crop((
                        spriteX-(mode.spriteSize+10), 
                        0, spriteX-5, mode.spriteSize+10))
            for i in range(3):
                runningSprite=mode.spritesheet.crop((spriteX+mode.spriteSize*i, 
                        0, spriteX+mode.spriteSize*(i+1), mode.spriteSize+10))
                mode.sprites.append(runningSprite)
            mode.spriteCounter=0
            mode.run=False
            
        def setWebShoot(mode):
            mode.shoot=False
            shooterWidth=250
            shooterY=215
            mode.shooterSprite=mode.spritesheet.crop((0, shooterY, 
                        shooterWidth, shooterY+mode.spriteSize+10)) 
            mode.shootCount=-1   

        def randomObstacles(mode, SmallObstacles, BigObstacles):
            mode.obst=[]
            mode.obstStart=1000
            for i in range(10):
                rand=random.choice([0,1])
                if rand==0:
                    mode.obst.append((rand, SmallObstacles()))
                else:
                    mode.obst.append((rand, BigObstacles()))  

        def randomFire(mode, EnemyFire):
            mode.fire=[]
            for i in range(5):
                rand=random.choice([0,1]) 
                mode.fire.append(rand)

        def appStarted(mode):
            mode.app._root.configure(cursor='spider')
            mode.player=Player()
            GameMode.getImages(mode)
            GameMode.setRunning(mode)
            GameMode.setWebShoot(mode)
            GameMode.randomObstacles(mode, SmallObstacles, BigObstacles)
            GameMode.randomFire(mode, EnemyFire)
            mode.scrollX=0
            mode.counter=0
            mode.gameOver=False
            mode.counter2=0
            mode.health=3
            
        def drawObstacles(mode, canvas):
            height=mode.height
            smallSize=20
            bigSize=50
            mode.obstSpace=750
            count=0
            for (size, obs) in mode.obst:
                count+=1
                if size==0:
                    x=mode.obstStart+mode.obstSpace*count-mode.scrollX
                    y=height*5/7
                    if x==mode.width/2:
                        mode.player.loseLife()
                        mode.health-=1
                        if mode.health<=0:
                            mode.gameOver=True
                    canvas.create_rectangle(x, y-smallSize, 
                        x+smallSize, y, fill='black')
                else:
                    x=mode.obstStart+mode.obstSpace*count-mode.scrollX
                    y=height*5/7
                    if x==mode.width/2:
                        mode.player.loseLife()
                        mode.health-=1
                        if mode.health<=0:
                            mode.gameOver=True
                    canvas.create_rectangle(x, y-smallSize, x+bigSize,
                        y, fill='black')
        
        
        def shoot(mode):
            if mode.run==True:
                mode.obst.pop(0)
                if mode.fire==[]:
                    pass
                else:
                    mode.fire.pop(0)
                if mode.obst==[]:
                    mode.gameOver=True
                mode.obstStart+=mode.obstSpace

        def drawEnemyFire(mode, canvas):
            height=mode.height
            mode.fireSpace=666
            count=0
            edgeX=190
            edgeY=92
            edgeX1=235
            edgeY1=112
            for fire in mode.fire:
                count+=1
                if fire==1:
                    x=mode.obstStart+mode.fireSpace*count-mode.scrollX
                    y=height*5/7-10
                    if x==mode.width/2:
                        mode.gameOver=True
                        mode.health=0
                    mode.firesprite=mode.enemyfire.crop((edgeX,edgeY,
                        edgeX1,edgeY1)) 
                    canvas.create_image(x, y, 
                        image=ImageTk.PhotoImage(mode.firesprite), anchor='w')

        def timerFired(mode):
            if mode.gameOver==True:
                return
            elif mode.run==True:
                mode.spriteCounter = ((1+mode.spriteCounter)%len(mode.sprites))
                mode.scrollX+=20
            mode.counter+=1
            if mode.counter>2:
                mode.shoot=False

        def mouseDragged(mode, event):
            if mode.gameOver==True:
                return
            mode.counter=0

        def mouseReleased(mode, event):
            if mode.gameOver==True:
                return
            mode.shoot=True
            GameMode.shoot(mode)

        def keyPressed(mode, event):
            if event.key=='r':
                GameMode.appStarted(mode)
            elif mode.gameOver==True:
                return
            elif event.key=='Right':
                mode.run=True
            elif event.key=='Left':
                mode.run=False
            elif (event.key == 'h'):
                mode.app.setActiveMode(mode.app.helpMode)


        def redrawAll(mode, canvas):
            font = 'Arial 26 bold'
            fill='red'
            obsWidth=20
            #I was having issues with loading the background,
            #it heavily slowed my app,so I am using a basic floor now
            canvas.create_rectangle(0, mode.height*5/7+25, mode.width*50, 
                    mode.height*5/7+35, fill='black')
            canvas.create_text(mode.width/2, mode.height/3,
                    text=f'Lives: {mode.health}', font=font, fill=fill)
            if mode.gameOver==True:
                mode.sprite=mode.starterSprite
                if mode.obst==[]:
                    canvas.create_text(mode.width/2, mode.height/2, 
                            text='WINNER WINNER SPIDER DINNER!',
                            font=font, fill='red')
                else:
                    canvas.create_text(mode.width/2, mode.height/2, 
                            text='YOU LOSE!',
                            font=font, fill=fill)
            elif mode.shoot==True:
                mode.sprite=mode.shooterSprite
            elif mode.run==True:
                mode.sprite=mode.sprites[mode.spriteCounter]
                GameMode.drawObstacles(mode, canvas)
                GameMode.drawEnemyFire(mode, canvas)
            else:
                mode.sprite=mode.starterSprite
            canvas.create_image(mode.width//2, (mode.height*5)/7,
                    image=ImageTk.PhotoImage(mode.sprite), anchor='w')

    class HelpMode(Mode):
        def redrawAll(mode, canvas):
            font = 'Arial 26 bold'
            canvas.create_text(mode.width/2, 250, 
                        text='''Press the right arrow to run forward.
Drag to the right to shoot webs at enemy fire and obstacles!
Two hits cost 1 life!
Don't get shot!''', font=font)
            canvas.create_text(mode.width/2, 350, 
                        text='Press any key to return to the game!', font=font)

        def keyPressed(mode, event):
            mode.app.setActiveMode(mode.app.gameMode)

    class WebslingerRoyale(ModalApp):
        def appStarted(self):
            self.splashScreenMode = SplashScreenMode()
            self.gameMode = GameMode()
            self.helpMode = HelpMode()
            self.setActiveMode(self.splashScreenMode)
            self.timerDelay = 50

    class Player(WebslingerRoyale):
        def __init__(self):
            self.health=3
        
        def loseLife(self):
            self.health-=1
            mode=GameMode()
            if self.health<=0:
                mode.gameOver=True

    class Obstacles(WebslingerRoyale):
        #create list of obstacles, containing tuples of position, (x,y)
        def __init__(self):
            self.streng=1
        def __eq__(self, other):
            if isinstance(other, Obstacles):
                return self.streng==other.streng
            else:
                return False

        def __hash__(self):
            return hash(self.streng)
        
        def getHit(self, x,y):
            self.streng-=1
        
        def makeObstacles(self):
            self.obstacles = dict()
            w=self.gameMode.width
            self.obstacles[w]=self.streng
            return self.obstacles
        
    class SmallObstacles(Obstacles):
        def __init__(self):
            super().__init__()
            self.size=20 
        
    class BigObstacles(Obstacles):
        def __init__(self):
            super().__init__()
            self.size=70

            
    class EnemyFire(WebslingerRoyale):
        def __init__(self):
            w=self.gameMode.width
            h=self.gameMode.height
            self.posX=random.randrange(w/2+10, w)
            self.posY=h*5/7-20

        def makeFire(self):
            self.fire=[]
            w=self.gameMode.width
            for i in range(5):
                rand=random.choice([0,1])
                self.fire.append(rand)

    app = WebslingerRoyale(width=1680, height=960)


#################################################
# Test Functions
#################################################

def getLocalMethods(clss):
    import types
    # This is a helper function for the test function below.
    # It returns a sorted list of the names of the methods
    # defined in a class. It's okay if you don't fully understand it!
    result = [ ]
    for var in clss.__dict__:
        val = clss.__dict__[var]
        if (isinstance(val, types.FunctionType)):
            result.append(var)
    return sorted(result)

def testBirdClasses():
    print("Testing Bird classes...", end="")
    # A basic Bird has a species name, can fly, and can lay eggs
    bird1 = Bird("Parrot")
    assert(type(bird1) == Bird)
    assert(isinstance(bird1, Bird))
    assert(bird1.fly() == "I can fly!")
    assert(bird1.countEggs() == 0)
    assert(str(bird1) == "Parrot has 0 eggs")
    bird1.layEgg()
    assert(bird1.countEggs() == 1)
    assert(str(bird1) == "Parrot has 1 egg")
    bird1.layEgg()
    assert(bird1.countEggs() == 2)
    assert(str(bird1) == "Parrot has 2 eggs")
    tempBird = Bird("Parrot")
    assert(bird1 == tempBird)
    tempBird = Bird("Wren")
    assert(bird1 != tempBird)
    nest = set()
    assert(bird1 not in nest)
    assert(tempBird not in nest)
    nest.add(bird1)
    assert(bird1 in nest)
    assert(tempBird not in nest)
    nest.remove(bird1)
    assert(bird1 not in nest)
    assert(getLocalMethods(Bird) == ['__eq__','__hash__','__init__', 
                                     '__repr__', 'countEggs', 
                                     'fly', 'layEgg'])
    
    # A Penguin is a Bird that cannot fly, but can swim
    bird2 = Penguin("Emperor Penguin")
    assert(type(bird2) == Penguin)
    assert(isinstance(bird2, Penguin))
    assert(isinstance(bird2, Bird))
    assert(not isinstance(bird1, Penguin))
    assert(bird2.fly() == "No flying for me.")
    assert(bird2.swim() == "I can swim!")
    bird2.layEgg()
    assert(bird2.countEggs() == 1)
    assert(str(bird2) == "Emperor Penguin has 1 egg")
    assert(getLocalMethods(Penguin) == ['fly', 'swim'])
    
    # A MessengerBird is a Bird that carries a message
    bird3 = MessengerBird("War Pigeon", "Top-Secret Message!")
    assert(type(bird3) == MessengerBird)
    assert(isinstance(bird3, MessengerBird))
    assert(isinstance(bird3, Bird))
    assert(not isinstance(bird3, Penguin))
    assert(not isinstance(bird2, MessengerBird))
    assert(not isinstance(bird1, MessengerBird))
    assert(bird3.deliverMessage() == "Top-Secret Message!")
    assert(str(bird3) == "War Pigeon has 0 eggs")
    assert(bird3.fly() == "I can fly!")

    bird4 = MessengerBird("Homing Pigeon", "")
    assert(bird4.deliverMessage() == "")
    bird4.layEgg()
    assert(bird4.countEggs() == 1)
    assert(getLocalMethods(MessengerBird) == ['__init__', 'deliverMessage'])

    # Note: all birds are migrating or not (together, as one)
    assert(bird1.isMigrating == bird2.isMigrating == bird3.isMigrating == False)
    assert(Bird.isMigrating == False)

    bird1.startMigrating()
    assert(bird1.isMigrating == bird2.isMigrating == bird3.isMigrating == True)
    assert(Bird.isMigrating == True)

    Bird.stopMigrating()
    assert(bird1.isMigrating == bird2.isMigrating == bird3.isMigrating == False)
    assert(Bird.isMigrating == False)
    print("Done!")



#################################################
# testAll and main
#################################################

def testAll():
    testBirdClasses()


def main():
    testAll()
    runCreativeSidescroller()

if __name__ == '__main__':
    main()
