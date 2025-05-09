from MathPlus import *
#IMAGE from PIL import Image as NewImage
import time
from random import shuffle
#IMAGE startTime = int(time.time())

class graphicArrow():
    
    def __init__(self, position:Vector2D,direction:Vector2D):
        endPoint = position+direction
        argument = direction.arg()
        arrowBody = Line(position.point(),endPoint.point())
        arrowL = Line(endPoint.point(),(endPoint + Vector2D(Angle(160,"Deg")+argument,0.5)).point())
        arrowR = Line(endPoint.point(),(endPoint + Vector2D(Angle(-160,"Deg")+argument,0.5)).point())
        
        self.arrowBody = arrowBody
        self.arrowL = arrowL
        self.arrowR = arrowR
    
    def draw(self,win):
        self.arrowBody.draw(win)
        self.arrowL.draw(win)
        self.arrowR.draw(win)
        
    def undraw(self):
        self.arrowBody.undraw()
        self.arrowL.undraw()
        self.arrowR.undraw()

def generateDisplay(position:Vector2D,radius:float|int,configs:dict):
    tempCircle = Circle(position.point(),radius)
    for item in configs:
        match item:
            case "Fill":
                tempCircle.setFill(configs[item])
            case "Line":
                tempCircle.setOutline(configs[item])
            case "Width":
                tempCircle.setWidth(configs[item])
    return tempCircle

class PhysicsObject:
    def __init__(self,position:Vector2D, radius:float|int, display:dict):
        self.position = position
        self.isMovable = False
        self.hasForce = False
        self.radius = radius
        self.display = generateDisplay(position, radius, display)
    
    def setParticle(self, mass:int|float, initialVelocity:Vector2D):
        self.isMovable = True
        self.mass = mass
        self.velocity = initialVelocity
        
    def setRadialForce(self, strength:float|int, atDistance:float|int, forceType:str="Acceleration"):
        self.hasForce = True
        self.forceType = f"radial:{forceType}"
        self.strengthConstant = strength*atDistance**2
    
    def setSingleDirectionForce(self, radius:float|int, effect:Vector2D, forceType:str="Force"):
        self.hasForce = True
        self.forceRadius = radius
        self.effect = effect
        self.forceType = f"singleDirection:{forceType}"
    
    def tick(self,tickTime:float, resultantForce:Vector2D=Vector2D(0,0), acceleration:Vector2D=Vector2D(0,0)):
        acceleration += resultantForce / self.mass
        self.velocity += tickTime * acceleration
        dPosition = tickTime * self.velocity
        self.position += dPosition
        self.display.move(dPosition.x,dPosition.y)
    
def isInForceRegion(object,forceRegion) -> bool:
    return distanceBetween2Vector2D(object.position,forceRegion.position) <= forceRegion.forceRadius

class universe:
    
    def __init__(self,name:str,resolution:list,coordLimits:list,gravity:Vector2D):
        self.graphicsWindow = GraphWin(name,*resolution)
        self.graphicsWindow.setCoords(*coordLimits)
        self.gravity = gravity
        self.actors = []
        self.frame = 0
    
    def addObjects(self,*actors):
        for actor in actors:
            self.actors.append(actor)
            actor.display.draw(self.graphicsWindow)
            
    def tick(self,tickTime,sleepTime):
        self.frame += 1
        shuffle(self.actors)
        for actor in self.actors:
            if isinstance(actor , PhysicsObject) and actor.isMovable:
                resultantAcceleration = self.gravity
                resultantForce = Vector2D(0,0)
                for effector in self.actors:
                    if actor == effector:continue
                    if isinstance(effector,PhysicsObject) and effector.hasForce:
                        effect = Vector2D(0,0)
                        match effector.forceType.split(":")[0]:
                            case "radial":
                                distance = distanceBetween2Vector2D(actor.position,effector.position)
                                direction = (effector.position - actor.position).unitVector()
                                effect = direction * (effector.strengthConstant/(distance**2))
                            case "singleDirection":
                                if isInForceRegion(actor,effector): effect = effector.effect
                        match effector.forceType.split(":")[1]:
                            case "Force":
                                resultantForce += effect
                            case "Acceleration":
                                resultantAcceleration += effect

                actor.tick(tickTime,resultantForce,resultantAcceleration)
        #IMAGE if self.frame % 3 == 0:
        #IMAGE     self.graphicsWindow.postscript(file="frames/tempImage.eps", colormode='color')
        #IMAGE     img = NewImage.open("frames/tempImage.eps")
        #IMAGE     img.save(f"frames/Time{startTime}Sim{self.frame}.bmp", "bmp")
        time.sleep(sleepTime)