from MathPlus import *

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



class pointParticle:
    
    """A particle with size of 0, a mass, and movement vectors, it is affected by force regions"""
    # Add Colour and Display to init
    def __init__(self, mass:float|int, position:Vector2D, initialVelocity:Vector2D):
        self.mass = mass
        self.position = position
        self.velocity = initialVelocity
        self.displayPoint = Circle(position.point(),0.1)
        
    def tick(self,tickTime:float, resultantForce:Vector2D):
        acceleration = resultantForce / self.mass
        self.velocity += tickTime * acceleration
        dPosition = tickTime * self.velocity
        self.position += dPosition
        self.displayPoint.move(dPosition.x,dPosition.y)

class singleDirectionForceRegion:
    
    """This is a force region which applies a force in a single direction in a circle around a point"""
    
    def __init__(self, radius:float|int, position:Vector2D, force:Vector2D):
        self.radius = radius
        self.position = position
        self.force = force