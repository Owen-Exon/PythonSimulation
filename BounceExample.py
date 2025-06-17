from Simulation import *

World = universe("World",1800,[-10,-5,50,15],Vector2D(0,-9.81),1,0.1,0.009,.9,True,0.3)

p1 = PhysicsObject(Vector2D(-8,3),.2)
p2 = PhysicsObject(Vector2D(-7,3),.2)
p3 = PhysicsObject(Vector2D(-6,3),.2)
p4 = PhysicsObject(Vector2D(-5,3),.2)
p5 = PhysicsObject(Vector2D(-4,3),.2)
p1.setParticle(1,Vector2D(5,0))
p2.setParticle(1,Vector2D(5,0))
p3.setParticle(1,Vector2D(5,0))
p4.setParticle(1,Vector2D(5,0))
p5.setParticle(1,Vector2D(5,0))
l1 = ImmovableLine(Vector2D(-10,-4),Vector2D(50,-4))

World.addObjects(p1,p2,p3,p4,p5,l1)
World.run()