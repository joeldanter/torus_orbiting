import numpy as np
from scipy.integrate import dblquad
import time
from multiprocessing import Pool, Process, JoinableQueue
from threading import Thread

class PhysicsWorld:
    grav_const=6.6743e-11
    def __init__(self, torus, sphere):
        self.torus=torus
        self.sphere=sphere

    def run_torus_simulation(self, delta_times):
        # TODO RK4 instead of explicit euler
        # fasteeeer
        self.should_stop=False
        q=JoinableQueue(1)
        p = Process(target=self.donut_loop, args=(q,delta_times))
        p.start()
        while not self.should_stop:
        # TODO better stopping mechanizm
            start = time.time()
            Fdonut=q.get()

            self.torus.apply_force(-Fdonut)
            self.sphere.apply_force(Fdonut)
            self.tick(delta_times)
            print('F:', Fdonut, 'in', time.time()-start)
            
            q.task_done()

    def stop(self):
        self.should_stop=True

    def donut_loop(self, queue, delta_times):
        while True:
            queue.join()
            Fdonut=self.donut_force()
            self.torus.apply_force(-Fdonut)
            self.sphere.apply_force(Fdonut)
            self.tick(delta_times)
            queue.put(Fdonut)

    def tick(self, delta_time):
        #grav_force=self.grav_accel()
        #self.torus.apply_force(-grav_force)
        #self.sphere.apply_force(grav_force)
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
        '''
        with Pool(processes=3) as pool:
            Fx=pool.starmap_async(self.torus_Fx, ((x,y,z,r,R,multiplier),))
            Fy=pool.starmap_async(self.torus_Fy, ((x,y,z,r,R,multiplier),))
            Fz=pool.starmap_async(self.torus_Fz, ((x,y,z,r,R,multiplier),))
            print('async init:', time.time()-start)
            Fx.get()
            print('x:', time.time()-start)
            Fy.get()
            print('y:', time.time()-start)
            Fz.get()
            print('z:', time.time()-start)
            F=np.array((Fx.get()[0], Fy.get()[0], Fz.get()[0]))
            print('Done after ', time.time()-start, 's')
            print(F)
            #return F
        '''
        #print('sequential init:', time.time()-start)
        
        Fx=self.torus_Fx(x,y,z,r,R,multiplier)
        #print('x:', time.time()-start)

        Fy=self.torus_Fy(x,y,z,r,R,multiplier)
        #print('y:', time.time()-start)
        
        Fz=self.torus_Fz(x,y,z,r,R,multiplier)
        #print('z:', time.time()-start)

        F=np.array((Fx,Fy,Fz))
        #print(F)
        return F

    def torus_Fx(self,x,y,z,r,R,multiplier):
        return multiplier*dblquad(lambda l,phi:self.x_quad(x,y,z,phi,l,-np.sqrt(r**2-(l-R)**2),np.sqrt(r**2-(l-R)**2)),
                                0, 2*np.pi,
                                lambda phi: R-r, lambda phi: R+r)[0]
        
    def torus_Fy(self,x,y,z,r,R,multiplier):
        return multiplier*dblquad(lambda l,phi:self.y_quad(x,y,z,phi,l,-np.sqrt(r**2-(l-R)**2),np.sqrt(r**2-(l-R)**2)),
                                0, 2*np.pi,
                                lambda phi: R-r, lambda phi: R+r)[0]
    
    def torus_Fz(self,x,y,z,r,R,multiplier):
        return multiplier*dblquad(lambda l,phi:self.z_quad(x,y,z,phi,l,-np.sqrt(r**2-(l-R)**2),np.sqrt(r**2-(l-R)**2)),
                                0, 2*np.pi,
                                lambda phi: R-r, lambda phi: R+r)[0]

    def x_quad(self, x,y,z,phi,l,h1,h2):
        v=(x-l*np.cos(phi))**2+(z-l*np.sin(phi))**2
        a=(h1-y)/(v*np.sqrt((h1-y)**2+v))
        b=(h2-y)/(v*np.sqrt((h2-y)**2+v))
        int=b-a
        return int*l*(l*np.cos(phi)-x)
    
    def y_quad(self,x,y,z,phi,l,h1,h2):
        a= -l / np.sqrt((l*np.cos(phi)-x)**2+(h1-y)**2+(l*np.sin(phi)-z)**2)
        b= -l / np.sqrt((l*np.cos(phi)-x)**2+(h2-y)**2+(l*np.sin(phi)-z)**2)
        return b-a

    def z_quad(self, x,y,z,phi,l,h1,h2):
        v=(x-l*np.cos(phi))**2+(z-l*np.sin(phi))**2
        a=(h1-y)/(v*np.sqrt((h1-y)**2+v))
        b=(h2-y)/(v*np.sqrt((h2-y)**2+v))
        int=b-a
        return int*l*(l*np.sin(phi)-z)
    