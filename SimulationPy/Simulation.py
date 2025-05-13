from SimulationPy.MathPlus import *
#IMAGE from PIL import Image as NewImage
import time
from random import shuffle

#IMAGE imageStartTime = int(time.time())

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
    def __init__(self,position:Vector2D, radius:float|int, display:dict={"Fill":color_rgb(0,0,0)},isPermeable:bool=False):
        self.position = position
        self.isMovable = False
        self.hasForce = False
        self.radius = radius
        self.display = generateDisplay(position, radius, display)
        self.isPermeable = isPermeable
    
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
        self.move(dPosition)
        
    
    def setPosition(self, vector:Vector2D):
        self.display.move(vector.x-self.position.x,vector.y-self.position.y)
        self.position = vector
        
    def move(self,vector:Vector2D):
        self.position += vector
        self.display.move(vector.x,vector.y)
    
def isInForceRegion(object,forceRegion) -> bool:
    return distanceBetween2Vector2D(object.position,forceRegion.position) <= forceRegion.forceRadius

def dotProduct(a:Vector2D,b:Vector2D):
    return (a.x * b.x) + (a.y * b.y)

def solveCollision(object1:PhysicsObject, object2:PhysicsObject):
    if not object1.isMovable:
        raise ValueError("Object1 must be moveable")
    if not object1.isMovable and not object2.isMovable:
        raise ValueError("At least one object must be moveable")
    
    v1 = object1.velocity
    m1 = object1.mass
    
    if object2.isMovable:
        v2 = object2.velocity
        m2 = object2.mass
    else:
        v2 = Vector2D(0,0)
        m2 = 9999999999999999999999999999999999999999999999999999999999999999999999999999999
    
    p1 = object1.position
    p2 = object2.position

    normalUnit = (p2-p1).unitVector()
    tangentUnit = Vector2D(-normalUnit.y,normalUnit.x)
    v1Normal = dotProduct(v1,normalUnit)
    v2Normal = dotProduct(v2,normalUnit)
    v1Tangent = dotProduct(v1,tangentUnit)
    v2Tangent = dotProduct(v2,tangentUnit)
    
    v1NormalDash = (v1Normal * (m1 - m2) + 2 * m2 * v2Normal) / (m1 + m2)
    v2NormalDash = (v2Normal * (m2 - m1) + 2 * m1 * v1Normal) / (m1 + m2)
    v1TangentDash = v1Tangent
    v2TangentDash = v2Tangent
    
    v1Dash = v1NormalDash * normalUnit + v1TangentDash * tangentUnit
    v2Dash = v2NormalDash * normalUnit + v2TangentDash * tangentUnit
    
    object1.velocity = v1Dash
    if object2.isMovable:
        object2.velocity = v2Dash
    else:
        object1.setPosition(p2-((object2.radius + object1.radius)*normalUnit))

class universe:
    
    def __init__(self,name:str,resolution:list,coordLimits:list,gravity:Vector2D,timeMultiplier:float|int,slowTimeMultiplier=None):
        self.graphicsWindow = GraphWin(name,*resolution,autoflush=False)
        self.graphicsWindow.setCoords(*coordLimits)
        self.gravity = gravity
        self.actors = []
        self.frame = 0
        self.lastTime = 0.01*timeMultiplier
        self.timeMultiplier = timeMultiplier
        self.otherTimeMultiplier = slowTimeMultiplier
    
    def addObjects(self,*actors):
        for actor in actors:
            self.actors.append(actor)
            actor.display.draw(self.graphicsWindow)
            
    def tick(self):
        startTime = time.time()
        self.frame += 1
        shuffle(self.actors)
        for actor in self.actors:
            if isinstance(actor , PhysicsObject) and actor.isMovable:
                resultantAcceleration = self.gravity
                resultantForce = Vector2D(0,0)
                for effector in self.actors:
                    if actor == effector:continue
                    if isinstance(effector,PhysicsObject):
                        if distanceBetween2Vector2D(actor.position,effector.position) <= (actor.radius + effector.radius) and not actor.isPermeable and not effector.isPermeable: 
                            solveCollision(actor,effector)
                        if effector.hasForce:
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

                actor.tick(self.lastTime,resultantForce,resultantAcceleration)
        #IMAGE if self.frame % 3 == 0:
        #IMAGE     self.graphicsWindow.postscript(file="frames/tempImage.eps", colormode='color')
        #IMAGE     img = NewImage.open("frames/tempImage.eps")
        #IMAGE     img.save(f"frames/Time{imageStartTime}Sim{self.frame}.bmp", "bmp")
        self.graphicsWindow.flush()
        self.lastTime = (time.time() - startTime) * self.timeMultiplier
        
    def run(self):
        self.graphicsWindow.getMouse()
        done = False
        while not done:
            self.tick()
            if self.graphicsWindow.checkMouse(): done = True
            if self.graphicsWindow.checkKey() == "s" and self.otherTimeMultiplier != None:
                tempTime = self.timeMultiplier
                self.timeMultiplier = self.otherTimeMultiplier
                self.otherTimeMultiplier = tempTime
        self.graphicsWindow.close()