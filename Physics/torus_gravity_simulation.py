import numpy as np
from scipy.integrate import dblquad
import time
from multiprocessing import Process, Queue


class TorusGravitySimulation:
    grav_const=6.6743e-11
    def __init__(self, torus, sphere):
        self.torus=torus
        self.sphere=sphere

    def run_simulation(self, delta_times):
        # TODO possibly RK4 instead of velocity verlet
        self.should_stop=False
        functions=[self.torus_Fx, self.torus_Fy, self.torus_Fz]
        params_queues=[Queue(), Queue(), Queue()]
        F_out_queues=[Queue(), Queue(), Queue()]
        processes=[]
        for i in range(3):
            p=Process(target=self.executor, args=(functions[i], params_queues[i], F_out_queues[i]))
            processes.append(p)
            p.start()
        
        while not self.should_stop:
            #start = time.time()

            # Verlet integration step 1
            self.torus.update_pos(delta_times)
            self.sphere.update_pos(delta_times)

            # put in params
            multiplier=self.grav_const*self.sphere.mass*self.torus.mass/self.torus.volume
            x,y,z=self.sphere.pos-self.torus.pos
            R=self.torus.outer_radius
            r=self.torus.inner_radius
            for q in params_queues:
                q.put((x,y,z,r,R,multiplier))
            
            # get results
            F=np.array((0.0,0.0,0.0))
            for i in range(3):
                F[i]=F_out_queues[i].get()
            
            # Verlet integration step 3, applying results
            self.torus.apply_force(-F)
            self.sphere.apply_force(F)
            self.torus.update_vel(delta_times)
            self.sphere.update_vel(delta_times)
            #print(f'F: {F} in {time.time()-start}s')
        
        for p in processes:
            p.terminate()

    def stop(self):
        self.should_stop=True

    def executor(self, f, params_in_queue, F_out_queue):
        while True:
            params=params_in_queue.get()
            F=f(*params)
            F_out_queue.put(F)

    def torus_Fx(self,x,y,z,r,R,multiplier):
        return multiplier*dblquad(lambda l,phi:self.torus_x_quad(x,y,z,phi,l,-np.sqrt(r**2-(l-R)**2),np.sqrt(r**2-(l-R)**2)),
                                0, 2*np.pi,
                                lambda phi: R-r, lambda phi: R+r)[0]
        
    def torus_Fy(self,x,y,z,r,R,multiplier):
        return multiplier*dblquad(lambda l,phi:self.torus_y_quad(x,y,z,phi,l,-np.sqrt(r**2-(l-R)**2),np.sqrt(r**2-(l-R)**2)),
                                0, 2*np.pi,
                                lambda phi: R-r, lambda phi: R+r)[0]
    
    def torus_Fz(self,x,y,z,r,R,multiplier):
        return multiplier*dblquad(lambda l,phi:self.torus_z_quad(x,y,z,phi,l,-np.sqrt(r**2-(l-R)**2),np.sqrt(r**2-(l-R)**2)),
                                0, 2*np.pi,
                                lambda phi: R-r, lambda phi: R+r)[0]

    def torus_x_quad(self, x,y,z,phi,l,h1,h2):
        v=(x-l*np.cos(phi))**2+(z-l*np.sin(phi))**2
        a=(h1-y)/(v*np.sqrt((h1-y)**2+v))
        b=(h2-y)/(v*np.sqrt((h2-y)**2+v))
        int=b-a
        return int*l*(l*np.cos(phi)-x)
    
    def torus_y_quad(self,x,y,z,phi,l,h1,h2):
        a= -l / np.sqrt((l*np.cos(phi)-x)**2+(h1-y)**2+(l*np.sin(phi)-z)**2)
        b= -l / np.sqrt((l*np.cos(phi)-x)**2+(h2-y)**2+(l*np.sin(phi)-z)**2)
        return b-a

    def torus_z_quad(self, x,y,z,phi,l,h1,h2):
        v=(x-l*np.cos(phi))**2+(z-l*np.sin(phi))**2
        a=(h1-y)/(v*np.sqrt((h1-y)**2+v))
        b=(h2-y)/(v*np.sqrt((h2-y)**2+v))
        int=b-a
        return int*l*(l*np.sin(phi)-z)
    