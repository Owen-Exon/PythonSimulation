from MathPlus import *
import time
from random import shuffle
from line_profiler import *

updateCheckKey = GraphWin.checkKey

def noUpdateCheckKey(self):
    """Return last key pressed or None if no key pressed since last call"""
    if self.isClosed():
        raise GraphicsError("checkKey in closed window")
    key = self.lastKey
    self.lastKey = ""
    return key

GraphWin.checkKey = noUpdateCheckKey

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
    
    def setParticle(self, mass:int|float, initialVelocity:Vector2D,angularVelocity:float|int = 0):
        self.isMovable = True
        self.mass = mass
        self.velocity = initialVelocity
        self.angularVelocity = angularVelocity
        self.rotation = Angle(0)
        self.rotationDisplayLine = Line(self.position.point(),(self.position + Vector2D(Angle(0),self.radius)).point())
        self.rotationDisplayLine.setOutline(color_rgb(255,255,255))
        
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
        self.rotation += tickTime * Angle(self.angularVelocity)
        self.rotationDisplayLine.undraw()
        self.rotationDisplayLine = Line(self.position.point(),(self.position + Vector2D(self.rotation,self.radius)).point())
        self.rotationDisplayLine.setOutline(color_rgb(255,255,255))
        
    
    def setPosition(self, vector:Vector2D):
        self.display.move(vector.x-self.position.x,vector.y-self.position.y)
        self.position = vector
        
    def move(self,vector:Vector2D):
        self.position += vector
        self.display.move(vector.x,vector.y)
        
    def draw(self, graphicsWindow:GraphWin):
        self.display.draw(graphicsWindow)
        if self.isMovable:
            self.rotationDisplayLine.draw(graphicsWindow)
    
def isInForceRegion(object,forceRegion) -> bool:
    return distanceBetween2Vector2D(object.position,forceRegion.position) <= forceRegion.forceRadius

def solveCollision(object1:PhysicsObject, object2:PhysicsObject,coefficientOfRestitution:float|int, coefficientOfFriction:float|int):
    if not object1.isMovable:
        obTemp = object1
        object1 = object2
        object2 = obTemp
    if not object1.isMovable and not object2.isMovable:
        raise ValueError("At least one object must be moveable")
    if coefficientOfRestitution < 0 or coefficientOfRestitution > 1:
        raise ValueError("Efficiency must be within the bounds 0 <= e <= 1")
    
    mass1 = object1.mass
    radius1 = object1.radius
    position1 = object1.position
    velocity1 = object1.velocity
    angularVelocity1 = object1.angularVelocity
    momentOfInertia1 = 0.5 * mass1 * (radius1 ** 2)
    
    if object2.isMovable:
        velocity2 = object2.velocity
        mass2 = object2.mass
        angularVelocity2 = object2.angularVelocity
    else:
        velocity2 = Vector2D(0,0)
        mass2 = 9999999999999999999999999999999999999999999999999999999999999999999999999999999
        angularVelocity2 = 0
        
    radius2 = object2.radius
    position2 = object2.position
    momentOfInertia2 =  0.5 * mass2 * (radius2 ** 2)
    
    relativePosition = position1 - position2
    collisionNormal = relativePosition/relativePosition.mod()
    collisionTangent = collisionNormal.normal()
    
    relativeContactPoint1 = radius1 * collisionNormal * -1
    relativeContactPoint2 = radius2 * collisionNormal
    
    contactPointVelocity1 = velocity1 + (angularVelocity1 * relativeContactPoint1.normal())
    contactPointVelocity2 = velocity2 + (angularVelocity2 * relativeContactPoint2.normal())
    
    relativeVelocity = contactPointVelocity1 - contactPointVelocity2
    
    relativeVelocityNormal = dotProduct(relativeVelocity,collisionNormal)
    relativeVelocityTangent = dotProduct(relativeVelocity,collisionTangent)
    
    relContact1DotNormalSquared = dotProduct(relativeContactPoint1.normal(),collisionNormal) ** 2
    relContact2DotNormalSquared = dotProduct(relativeContactPoint2.normal(),collisionNormal) ** 2
    relContact1DotTangentSquared = dotProduct(relativeContactPoint1.normal(),collisionTangent) ** 2
    relContact2DotTangentSquared = dotProduct(relativeContactPoint2.normal(),collisionTangent) ** 2
    
    sumOfInverseMass = 1 / mass1 + 1 / mass2
    normalEffectiveMass = 1 / (sumOfInverseMass + ((relContact1DotNormalSquared) / (momentOfInertia1)) + ((relContact2DotNormalSquared) / (momentOfInertia2)))
    tangentEffectiveMass = 1 / (sumOfInverseMass + ((relContact1DotTangentSquared) / (momentOfInertia1)) + ((relContact2DotTangentSquared) / (momentOfInertia2)))
        
    normalImpulse = -1 * (1 + coefficientOfRestitution) * relativeVelocityNormal * normalEffectiveMass
    tangentImpulse = -1 * relativeVelocityTangent * tangentEffectiveMass       
    
    frictionTimesNormalImpulse = coefficientOfFriction * abs(normalImpulse)
    if abs(tangentImpulse) > frictionTimesNormalImpulse:
        tangentImpulse = frictionTimesNormalImpulse * sign(relativeVelocityTangent) * -1
    
    impulseVector = normalImpulse*collisionNormal + tangentImpulse*collisionTangent
    
    velocity1Dash = velocity1 + (impulseVector / mass1)
    velocity2Dash = velocity2 - (impulseVector / mass2)
    
    angularVelocity1Dash = angularVelocity1 + dotProduct(relativeContactPoint1.normal(),impulseVector)/momentOfInertia1
    angularVelocity2Dash = angularVelocity2 - dotProduct(relativeContactPoint2.normal(),impulseVector)/momentOfInertia2
    
    distance = abs(distanceBetween2Vector2D(position1,position2) - (radius1 + radius2))
    object1.velocity = velocity1Dash
    object1.angularVelocity = angularVelocity1Dash
    if object2.isMovable:
        object2.velocity = velocity2Dash
        object2.angularVelocity = angularVelocity2Dash
        object1.move(collisionNormal*(distance/2))
        object2.move(-1 * collisionNormal*(distance/2))
    else:
        object1.setPosition(position2-((radius2 + radius1)*collisionNormal * -1))

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
    
    def draw(self,graphicsWindow:GraphWin):
        self.display.draw(graphicsWindow)

def lineSeries(*points):
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
    
    def __init__(self,name:str,resolutionX:float|int,coordLimits:list,gravity:Vector2D,timeMultiplier:float|int=1,timeIncrement=0.1, airDensity:float|int=0,collisionEfficiency:float|int=1, collideWithBounds:bool = False, frictionCoefficient:float|int = 0,framerate:int = 120):
        width = coordLimits[2] - coordLimits[0]
        height = coordLimits[3]-coordLimits[1]
        resolution = [resolutionX, (resolutionX/(width)) * (height)]
        self.graphicsWindow = GraphWin(name,*resolution,autoflush=False)
        self.graphicsWindow.setCoords(*coordLimits)

        self.gravity = gravity
        self.actors = []
        self.frame = 0
        self.adjustedLastTime = 0.001*timeMultiplier
        self.timeMultiplier = timeMultiplier
        self.timeIncrement = timeIncrement
        self.timeSinceLastFrame = 0
        self.frameTime = 1/framerate
        
        self.timeText = Text(Point((coordLimits[0]+coordLimits[2])/2,coordLimits[3]-height/80),self.timeMultiplier)
        self.timeText.draw(self.graphicsWindow)
        
        self.airDensity = airDensity
        self.collisionEfficiency = collisionEfficiency
        self.frictionCoefficient = frictionCoefficient
        
        if collideWithBounds:
            self.addObjects(*lineSeries(Vector2D(coordLimits[0],coordLimits[1]),Vector2D(coordLimits[2],coordLimits[1]),Vector2D(coordLimits[2],coordLimits[3]),Vector2D(coordLimits[0],coordLimits[3]),Vector2D(coordLimits[0],coordLimits[1])))
    
    def addObjects(self,*actors):
        for actor in actors:
            self.actors.append(actor)
            actor.draw(self.graphicsWindow)
    
    @profile
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
                            angle2 = effector.difference.arg() - Angle(90,"Deg")
                            pointOfCollision1 = actor.position + Vector2D(angle1,actorDistance) 
                            pointOfCollision2 = actor.position + Vector2D(angle2,actorDistance) 
                            
                            if effector.distanceToPoint(pointOfCollision1) < effector.distanceToPoint(pointOfCollision2) and isInBounds(pointOfCollision1,effector.start,effector.end):
                                solveCollision(actor,PhysicsObject(pointOfCollision1 + Vector2D(angle1,1),1),self.collisionEfficiency,self.frictionCoefficient)
                            elif isInBounds(pointOfCollision2,effector.start,effector.end):
                                solveCollision(actor,PhysicsObject(pointOfCollision2 + Vector2D(angle2,1),1),self.collisionEfficiency,self.frictionCoefficient)
                        
                if self.airDensity != 0: resultantForce += SimpleDragCalculator(actor.velocity,self.airDensity,actor.radius,1.2)
                actor.tick(self.adjustedLastTime,resultantForce,resultantAcceleration)
                actor.rotationDisplayLine.draw(self.graphicsWindow)
        if self.timeSinceLastFrame >= self.frameTime:
            update()
            self.timeSinceLastFrame = (self.timeSinceLastFrame % self.frameTime)
        realTimeDifference = (time.time() - startTime)
        self.timeSinceLastFrame += realTimeDifference
        self.adjustedLastTime = realTimeDifference * self.timeMultiplier
        
    def updateTimeText(self):
        self.timeText.setText(self.timeMultiplier)
    
    def increaseTimeMultiplier(self):
        self.timeMultiplier += self.timeIncrement
        self.updateTimeText()

    def decreaseTimeMultiplier(self):
        self.timeMultiplier = max(self.timeMultiplier - self.timeIncrement,self.timeIncrement)
        self.updateTimeText()
        
    def run(self):
        self.graphicsWindow.getMouse()
        done = False
        while not done:
            self.tick()
            keyStroke = self.graphicsWindow.checkKey()
            if keyStroke == "Escape" : done = True
            elif keyStroke == "Up" : self.increaseTimeMultiplier()
            elif keyStroke == "Down" : self.decreaseTimeMultiplier()
            elif keyStroke == "p" : 
                pausedKeyStroke = ""
                while pausedKeyStroke != "p" and not done:
                    pausedKeyStroke = self.graphicsWindow.getKey()
                    if pausedKeyStroke == "Escape" : done = True
                    elif pausedKeyStroke == "Up" : self.increaseTimeMultiplier()
                    elif pausedKeyStroke == "Down" : self.decreaseTimeMultiplier()
                     
        
        self.graphicsWindow.close()
        
if __name__ == "__main__":
    World = universe("World",1000,[-10,-10,10,10],Vector2D(0,0),1,0.5)

    p1 = PhysicsObject(Vector2D(-5,0),.25)
    p1.setParticle(1,Vector2D(5,0))
    p2 = PhysicsObject(Vector2D(5,5),.5)
    p2.setParticle(4,Vector2D(-5,-5))
    
    World.addObjects(p1,p2)
    World.run()