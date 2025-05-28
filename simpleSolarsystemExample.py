from Simulation import *


MainUniverse = universe("Test",1000,[-180000,-180000,180000,180000],Vector2D(0,0),1000,100)


sun = PhysicsObject(Vector2D(0,0),10000,{"Fill":color_rgb(255,255,0)})
sun.setRadialForce(274,696.3)

earth = PhysicsObject(Vector2D(-149000,0),2000,{"Fill":color_rgb(0,255,0)})
earth.setParticle(1,Vector2D(0,29.8))
earth.setRadialForce(9.81,800)

moon = PhysicsObject(Vector2D(-160000,0),750,{"Fill":color_rgb(100,100,100)})
moon.setParticle(1,Vector2D(0,51))
moon.setRadialForce(1.62,1.7)

otherPlanet0 = PhysicsObject(Vector2D(50000,0),1000,{"Fill":color_rgb(100,0,0)})
otherPlanet0.setParticle(1,Vector2D(0,-50))
otherPlanet0.setRadialForce(1.62,1.7)

MainUniverse.addObjects(sun,earth,moon,otherPlanet0)
MainUniverse.run()