import numpy as np
from scipy.integrate import dblquad
import time


class PhysicsWorld:
    grav_const=6.6743e-11
    def __init__(self, torus, sphere):
        self.torus=torus
        self.sphere=sphere
        # TODO add trace lines

    def run_alone(self, delta_times):
        while True:
            self.tick(delta_times)

    def tick(self, delta_time):
        # TODO RK4 instead of explicit euler
        #grav_force=self.grav_accel()
        #self.torus.apply_force(-grav_force)
        #self.sphere.apply_force(grav_force)

        Fdonut=self.donut_force()
        print('F:', Fdonut)
        self.torus.apply_force(-Fdonut)
        self.sphere.apply_force(Fdonut)
        time.sleep(0.1) # TODO fix this
        self.torus.tick(delta_time)
        self.sphere.tick(delta_time)

    def grav_accel(self):
        vec_dist=self.torus.pos-self.sphere.pos
        dist_sq=np.dot(vec_dist, vec_dist)
        dist=np.sqrt(dist_sq)
        grav_magnitude=self.grav_const*self.torus.mass*self.sphere.mass/dist_sq
        grav_dir=vec_dist/dist
        return grav_magnitude*grav_dir

    def donut_force(self):
        multiplier=self.grav_const*self.sphere.mass*self.torus.mass/self.torus.volume
        x,y,z=self.sphere.pos-self.torus.pos
        R=self.torus.outer_radius
        r=self.torus.inner_radius
        # TODO faster

        #start = time.time()
        Fx = multiplier*dblquad(lambda l,phi:self.xinner(x,y,z,phi,l,-np.sqrt(r**2-(l-R)**2),np.sqrt(r**2-(l-R)**2)),
                                0, 2*np.pi,
                                lambda phi: R-r, lambda phi: R+r)[0]
        #print(f'Fx={Fx} after {time.time()-start}s')
        
        Fy = multiplier*dblquad(lambda l,phi:self.yinner(x,y,z,phi,l,-np.sqrt(r**2-(l-R)**2),np.sqrt(r**2-(l-R)**2)),
                                0, 2*np.pi,
                                lambda phi: R-r, lambda phi: R+r)[0]
        #print(f'Fy={Fy} after {time.time()-start}s')
        
        Fz = multiplier*dblquad(lambda l,phi:self.zinner(x,y,z,phi,l,-np.sqrt(r**2-(l-R)**2),np.sqrt(r**2-(l-R)**2)),
                                0, 2*np.pi,
                                lambda phi: R-r, lambda phi: R+r)[0]
        #print(f'Fz={Fz} after {time.time()-start}s')
        
        return np.array((Fx, Fy, Fz))

    def xinner(self, x,y,z,phi,l,h1,h2):
        v=(x-l*np.cos(phi))**2+(z-l*np.sin(phi))**2
        a=(h1-y)/(v*np.sqrt((h1-y)**2+v))
        b=(h2-y)/(v*np.sqrt((h2-y)**2+v))
        int=b-a
        return int*l*(l*np.cos(phi)-x)
    
    def yinner(self,x,y,z,phi,l,h1,h2):
        a= -l / np.sqrt((l*np.cos(phi)-x)**2+(h1-y)**2+(l*np.sin(phi)-z)**2)
        b= -l / np.sqrt((l*np.cos(phi)-x)**2+(h2-y)**2+(l*np.sin(phi)-z)**2)
        return b-a

    def zinner(self, x,y,z,phi,l,h1,h2):
        v=(x-l*np.cos(phi))**2+(z-l*np.sin(phi))**2
        a=(h1-y)/(v*np.sqrt((h1-y)**2+v))
        b=(h2-y)/(v*np.sqrt((h2-y)**2+v))
        int=b-a
        return int*l*(l*np.sin(phi)-z)