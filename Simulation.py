from MathPlus import *
from graphics import *

# Size mass position force

class pointParticle:
    
    """A particle with size of 0, a mass, and movement vectors, it is affected by force regions"""
    # Add Colour and Display to init
    def __init__(self, mass:float|int, position:Vector2D, initialVelocity:Vector2D):
        self.mass = mass
        self.position = position
        self.velocity = initialVelocity
        
        self.displayPoint = Circle(Point(position.x,position.y),0.1) 
        
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