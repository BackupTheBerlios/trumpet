import ode

class World:

    def __init__(self):
        # Create a world object
        self.world = ode.World()
        self.world.setGravity( (0,-9.81,0) )


    def simulate(self):
        # Create a body inside the world
        body = ode.Body(self.world)
        M = ode.Mass()
        M.setSphere(2500.0, 0.05)
        M.mass = 1.0
        body.setMass(M)

        body.setPosition( (0,2,0) )
        body.addForce( (0,200,0) )

        # Do the simulation...
        total_time = 0.0
        dt = 0.04
        while total_time<2.0:
            x,y,z = body.getPosition()
            u,v,w = body.getLinearVel()
            print '%1.2fsec: pos=(%6.3f, %6.3f, %6.3f)  vel=(%6.3f, %6.3f, %6.3f)' % (total_time, x, y, z, u,v,w)
            self.world.step(dt)
            total_time+=dt
        
if __name__ == "__main__":
    world = World()
    world.simulate()
        
        
        
