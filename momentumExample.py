from SimulationPy.Simulation import *

World = universe("World",[1000,1000],[-10,-10,10,10],Vector2D(0,0),1,0.5)

points = []
p1 = PhysicsObject(Vector2D(-5,0),.25)
p1.setParticle(1,Vector2D(5,0))
p2 = PhysicsObject(Vector2D(5,5),.5)
p2.setParticle(4,Vector2D(-5,-5))


World.addObjects(p1,p2)
World.run()