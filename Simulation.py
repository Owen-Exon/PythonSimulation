from MathPlus import *
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

def solveCollision(object1:PhysicsObject, object2:PhysicsObject,efficiency:float|int, frictionCoefficient:float|int):
    if not object1.isMovable:
        raise ValueError("Object1 must be moveable")
    if not object1.isMovable and not object2.isMovable:
        raise ValueError("At least one object must be moveable")
    if efficiency < 0 or efficiency > 1:
        raise ValueError("Efficiency must be within the bounds 0 <= e <= 1")
    
    v1 = object1.velocity
    m1 = object1.mass
    r1 = object1.radius
    r2 = object2.radius
    
    if object2.isMovable:
        v2 = object2.velocity
        m2 = object2.mass
    else:
        v2 = Vector2D(0,0)
        m2 = 9999999999999999999999999999999999999999999999999999999999999999999999999999999
    
    p1 = object1.position
    p2 = object2.position

    distance = abs(distanceBetween2Vector2D(p1,p2) - (r1 + r2))
    normalUnit = (p2-p1).unitVector()
    tangentUnit = Vector2D(-normalUnit.y,normalUnit.x)
    v1Normal = dotProduct(v1,normalUnit)
    v2Normal = dotProduct(v2,normalUnit)
    v1Tangent = dotProduct(v1,tangentUnit)
    v2Tangent = dotProduct(v2,tangentUnit)
    
    v1NormalDash = (v1Normal * (m1 - efficiency * m2) + (efficiency + 1) * m2 * v2Normal) / (m1 + m2)
    v2NormalDash = (v2Normal * (m2 - efficiency * m1) + (efficiency + 1) * m1 * v1Normal) / (m1 + m2)
    
    vRelT = v1Tangent - v2Tangent
    sumInverseMass = (1/m1) + (1/m2)
    effectiveMass = 1/sumInverseMass
    Jn = (-1 * (1 + efficiency) * (vRelT))/(sumInverseMass)
    Jt = -1 * min(frictionCoefficient * abs(Jn),effectiveMass) * sign(vRelT)
    
    
    v1TangentDash = v1Tangent + (Jt / m1)
    v2TangentDash = v2Tangent - (Jt / m2)
    
    v1Dash = v1NormalDash * normalUnit + v1TangentDash * tangentUnit
    v2Dash = v2NormalDash * normalUnit + v2TangentDash * tangentUnit
    
    object1.velocity = v1Dash
    if object2.isMovable:
        object2.velocity = v2Dash
        object1.move(-1 * normalUnit*(distance/2))
        object2.move(normalUnit*(distance/2))
        
    else:
        object1.setPosition(p2-((object2.radius + object1.radius)*normalUnit))

class ImmovableLine:
    def __init__(self,p1:Vector2D,p2:Vector2D):
        if p1.x <= p2.x:
            self.start = p1
            self.end = p2
        else:
            self.start = p2
            self.end = p1
        self.difference = self.end - self.start
        self.display = Line(p1.point(),p2.point())
        
    def distanceToPoint(self,point:Vector2D):
        return abs(self.difference.x * (point.y-self.start.y)- self.difference.y * (point.x-self.start.x))/self.difference.mod()

def lineSeries(points):
    lines = []
    for i in range(len(points)-1):
        lines.append(ImmovableLine(points[i],points[i+1]))
    return lines

def SimpleDragCalculator(Velocity:Vector2D,FluidDensity:float|int,radius:float|int,dragCoefficient):
    VelocityMod = Velocity.mod()
    DragMod = dragCoefficient*( ( FluidDensity * (VelocityMod ** 2) ) / 2) * (2*radius)
    Drag = Vector2D(Velocity.arg()+Angle(pi),DragMod)
    return Drag

class universe:
    
    def __init__(self,name:str,resolutionX:float|int,coordLimits:list,gravity:Vector2D,timeMultiplier:float|int=1,timeIncrement=0.1, airDensity:float|int=0,collisionEfficiency:float|int=1, collideWithBounds:bool = False, frictionCoefficient:float|int = 0):
        width = coordLimits[2] - coordLimits[0]
        height = coordLimits[3]-coordLimits[1]
        resolution = [resolutionX, (resolutionX/(width)) * (height)]
        self.graphicsWindow = GraphWin(name,*resolution,autoflush=False)
        self.graphicsWindow.setCoords(*coordLimits)

        self.gravity = gravity
        self.actors = []
        self.frame = 0
        self.lastTime = 0.001*timeMultiplier
        self.timeMultiplier = timeMultiplier
        self.timeIncrement = timeIncrement
        
        self.timeText = Text(Point((coordLimits[0]+coordLimits[2])/2,coordLimits[3]-height/80),self.timeMultiplier)
        self.timeText.draw(self.graphicsWindow)
        
        self.airDensity = airDensity
        self.collisionEfficiency = collisionEfficiency
        self.frictionCoefficient = frictionCoefficient
        
        if collideWithBounds:
            self.addObjects(*lineSeries([Vector2D(coordLimits[0],coordLimits[1]),Vector2D(coordLimits[2],coordLimits[1]),Vector2D(coordLimits[2],coordLimits[3]),Vector2D(coordLimits[0],coordLimits[3]),Vector2D(coordLimits[0],coordLimits[1])]))
    
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
                            solveCollision(actor,effector,self.collisionEfficiency,self.frictionCoefficient)
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
                    elif isinstance(effector, ImmovableLine):
                        actorDistance = effector.distanceToPoint(actor.position) 
                        if actorDistance <= actor.radius:
                            angle1 = effector.difference.arg() + Angle(90,"Deg")
                            angle2 =effector.difference.arg() - Angle(90,"Deg")
                            pointOfCollision1 = actor.position + Vector2D(angle1,actorDistance) 
                            pointOfCollision2 = actor.position + Vector2D(angle2,actorDistance) 
                            
                            if effector.distanceToPoint(pointOfCollision1) < effector.distanceToPoint(pointOfCollision2) and isInBounds(pointOfCollision1,effector.start,effector.end):
                                solveCollision(actor,PhysicsObject(pointOfCollision1 + Vector2D(angle1,1),1),self.collisionEfficiency,self.frictionCoefficient)
                            elif isInBounds(pointOfCollision2,effector.start,effector.end):
                                solveCollision(actor,PhysicsObject(pointOfCollision2 + Vector2D(angle2,1),1),self.collisionEfficiency,self.frictionCoefficient)
                        
                if self.airDensity != 0: resultantForce += SimpleDragCalculator(actor.velocity,self.airDensity,actor.radius,1.2)
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
            keyStroke = self.graphicsWindow.checkKey()
            if keyStroke == "Escape" : done = True
            elif keyStroke == "Up" : 
                self.timeMultiplier += self.timeIncrement
                self.timeText.setText(self.timeMultiplier)
            elif keyStroke == "Down" : 
                self.timeMultiplier = max(self.timeMultiplier - self.timeIncrement,self.timeIncrement)
                self.timeText.setText(self.timeMultiplier)
            elif keyStroke == "p" : 
                while self.graphicsWindow.getKey() != "p": pass
        
        self.graphicsWindow.close()
        
if __name__ == "__main__":
    World = universe("World",1000,[-10,-10,10,10],Vector2D(0,0),1,0.5)

    p1 = PhysicsObject(Vector2D(-5,0),.25)
    p1.setParticle(1,Vector2D(5,0))
    p2 = PhysicsObject(Vector2D(5,5),.5)
    p2.setParticle(4,Vector2D(-5,-5))
    
    World.addObjects(p1,p2)
    World.run()