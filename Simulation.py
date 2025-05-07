from MathPlus import *
#IMAGE from PIL import Image as NewImage
import time

#IMAGE startTime = int(time.time())

class graphicArrow():
    
    def __init__(self, position:Vector2D,direction:Vector2D):
        arrowVector = 0.25*direction
        endPoint = position+arrowVector
        arrowBody = Line(position.point(),endPoint.point())
        arrowL = Line(endPoint.point(),(endPoint + Vector2D(Angle(160,"Deg")+arrowVector.arg(),0.5)).point())
        arrowR = Line(endPoint.point(),(endPoint + Vector2D(Angle(-160,"Deg")+arrowVector.arg(),0.5)).point())
        
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



def generateDisplay(position:Vector2D,radius:float|int,lineColour,fillColour="none") -> Circle:
    tempCircle = Circle(position.point(),radius)
    tempCircle.setOutline(lineColour)
    if fillColour != "none": tempCircle.setFill(fillColour)
    return tempCircle

class pointParticle:
    
    """A particle with size of 0, a mass, and movement vectors, it is affected by force regions"""
    # Add Colour and Display to init
    def __init__(self, mass:float|int, position:Vector2D, initialVelocity:Vector2D,displayColour,displayRadius:float|int):
        self.mass = mass
        self.position = position
        self.velocity = initialVelocity
        self.display = generateDisplay(position,displayRadius,displayColour,displayColour)
        
    def tick(self,tickTime:float, resultantForce:Vector2D=Vector2D(0,0), acceleration:Vector2D=Vector2D(0,0)):
        acceleration += resultantForce / self.mass
        self.velocity += tickTime * acceleration
        dPosition = tickTime * self.velocity
        self.position += dPosition
        self.display.move(dPosition.x,dPosition.y)

class singleDirectionForceRegion:
    
    """This is a force region which applies a force in a single direction in a circle around a point"""
    
    def __init__(self, radius:float|int, position:Vector2D, effect:Vector2D, type:str="Force"):
        self.radius = radius
        self.position = position
        self.effect = effect
        self.type = type
        self.display = generateDisplay(position,radius,color_rgb(255,0,0))

class radialForceRegion:
    
    """This is a force region which applies a force around its centre"""
    
    def __init__(self, position:Vector2D, strength:float|int, atDistance:float|int, displayRadius,displayColour, type:str="Acceleration"):
        
        """Inits a radial force region
        
        Args:
            radius (float|int): radius of the force region
            position (Vector2D): Position of the force region
            strength
        """
        
        self.position = position
        self.type = type
        self.strengthConstant = strength*atDistance**2
        self.display = generateDisplay(position,displayRadius,displayColour,displayColour)
    
def isInForceRegion(object,forceRegion) -> bool:
    return distanceBetween2Vector2D(object.position,forceRegion.position) <= forceRegion.radius

class radialForcePointParticle:
    def __init__(self, mass:float|int, position:Vector2D, initialVelocity:Vector2D, strength:float|int, atDistance:float|int,displayColour,displayRadius:float|int,type:str="Acceleration"):
        self.mass = mass
        self.position = position
        self.velocity = initialVelocity
        self.display = generateDisplay(position,displayRadius,displayColour,displayColour)
        self.type = type
        self.strengthConstant = strength*atDistance**2
        
    def tick(self,tickTime:float, resultantForce:Vector2D=Vector2D(0,0), acceleration:Vector2D=Vector2D(0,0)):
        acceleration += resultantForce / self.mass
        self.velocity += tickTime * acceleration
        dPosition = tickTime * self.velocity
        self.position += dPosition
        self.display.move(dPosition.x,dPosition.y)

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
        for actor in self.actors:
            if isinstance(actor,pointParticle|radialForcePointParticle):
                resultantAcceleration = self.gravity
                resultantForce = Vector2D(0,0)
                for effector in self.actors:
                    if actor == effector: continue
                    if isinstance(effector,singleDirectionForceRegion) and isInForceRegion(actor,effector):
                        match effector.type:
                            case "Force":
                                resultantForce += effector.effect
                            case "Acceleration":
                                resultantAcceleration += effector.effect
                    elif isinstance(effector, radialForceRegion|radialForcePointParticle):
                        distance = distanceBetween2Vector2D(actor.position,effector.position)
                        direction = (effector.position - actor.position).unitVector()
                        effect = direction * (effector.strengthConstant/(distance**2))
                        match effector.type:
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