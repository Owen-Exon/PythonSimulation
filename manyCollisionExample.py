from SimulationPy.Simulation import *

World = universe("World",[1000,1000],[-10,-5,10,15],Vector2D(0,0),.5,0.1)

e1 = PhysicsObject(Vector2D(0,5),1,{"Line":color_rgb(255,0,0)})
e1.setRadialForce(10,5)
points = []
for i in range(45,135,4):
    pointt = PhysicsObject((Vector2D(0,-10) + Vector2D(Angle(i,"Deg"),10)),.1)
    pointt.setParticle(1,Vector2D(0,3))
    points.append(pointt)

World.addObjects(e1,*points)
World.run()