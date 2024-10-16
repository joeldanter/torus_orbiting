from abc import ABC, abstractmethod
import numpy as np
from OpenGL.GL import *


class Body(ABC):
    # TODO make this thread safe
    def __init__(self, init_pos, init_vel, mass):
        self.pos=init_pos
        self.vel=init_vel
        self.mass=mass
        self.accel=np.array((0.0,0.0,0.0))
        # TODO add rotation
    
    def tick(self, delta_time):
        # TODO remove the need for giving dt in params
        self.vel=self.vel+self.accel*delta_time
        self.pos=self.pos+self.vel*delta_time
        self.accel=np.array((0.0,0.0,0.0))

    def apply_force(self, force):
        self.accel=self.accel+force/self.mass

    def apply_accel(self, accel):
        self.accel=self.accel+accel

    @abstractmethod
    def render(self):
        pass


class Sphere(Body):
    def __init__(self, init_pos, init_vel, mass, radius, segments, rings):
        super().__init__(init_pos, init_vel, mass)
        self.radius=radius
        self.volume=4/3*np.pi*radius**3
        self.__draw_mesh(radius, segments, rings)

    def __draw_mesh(self, radius, segments, rings):
        self.triangles=[]
        self.quad_strips=[]
        for i in range(segments):
            phi=2*np.pi*i/segments
            next_phi=2*np.pi*(i+1)/segments
            theta=np.pi*1/rings
            
            # top and bottom triangles
            top_triangle_points=((0,radius,0),
                                  (radius*np.sin(theta)*np.sin(phi), radius*np.cos(theta), np.sin(theta)*radius*np.cos(phi)),
                                  (radius*np.sin(theta)*np.sin(next_phi), radius*np.cos(theta), np.sin(theta)*radius*np.cos(next_phi)))
            self.triangles.append(top_triangle_points)
            bottom_triangle_points=((0,-radius,0),
                                  (radius*np.sin(theta)*np.sin(phi), -radius*np.cos(theta), np.sin(theta)*radius*np.cos(phi)),
                                  (radius*np.sin(theta)*np.sin(next_phi), -radius*np.cos(theta), np.sin(theta)*radius*np.cos(next_phi)))
            self.triangles.append(bottom_triangle_points)
            
            # middle quadrilaterals
            self.quad_strips.append([])
            for j in range(1, rings):
                theta=np.pi*j/rings
                for k in [phi, next_phi]:
                    x=radius*np.sin(theta)*np.sin(k)
                    y=radius*np.cos(theta)
                    z=radius*np.sin(theta)*np.cos(k)
                    self.quad_strips[-1].append((x,y,z))


    def render(self):
        glColor3f(81/255, 81/255, 85/255)
        glBegin(GL_TRIANGLES)
        for triangle in self.triangles:
            for point in triangle:
                glVertex3f(point[0]+self.pos[0], point[1]+self.pos[1], point[2]+self.pos[2])
        glEnd()
        
        for strip in self.quad_strips:
            glBegin(GL_QUAD_STRIP)
            for point in strip:
                glVertex3f(point[0]+self.pos[0], point[1]+self.pos[1], point[2]+self.pos[2])
            glEnd()

class TracedSphere(Sphere):
    def __init__(self, init_pos, init_vel, mass, radius, segments, rings):
        super().__init__(init_pos, init_vel, mass, radius, segments, rings)
        self.trace_points=[init_pos]
    
    def tick(self, delta_time):
        super().tick(delta_time)
        self.trace_points.append(self.pos)
    
    def render(self):
        super().render()
        glBegin(GL_LINE_STRIP)
        for point in self.trace_points:
            glVertex3f(point[0], point[1], point[2])
        glEnd()


class Torus(Body):
    def __init__(self, init_pos, init_vel, mass, outer_radius, inner_radius, sides, rings):
        super().__init__(init_pos, init_vel, mass)
        self.inner_radius=inner_radius
        self.outer_radius=outer_radius
        self.volume=2*np.pi**2*inner_radius**2*outer_radius
        self.__draw_mesh(outer_radius, inner_radius, sides, rings)
    
    def __draw_mesh(self, outer_radius, inner_radius, sides, rings):
        self.quad_strips=[]
        for i in range(sides):
            self.quad_strips.append([])
            c1 = (1+np.sin(2*np.pi*(i+1)/(sides)))/2
            for j in range(rings+1):
                c2 = 0.75+(np.sin(2*np.pi*(j)/(rings/3)))/4
                for k in [i, i+1]:
                    theta = 2 * np.pi * k / sides
                    phi = 2 * np.pi * j / rings
                    x = (outer_radius + inner_radius * np.cos(theta)) * np.cos(phi)
                    y = inner_radius * np.sin(theta)
                    z = (outer_radius + inner_radius * np.cos(theta)) * np.sin(phi)

                    color=np.array((23,57,61))/256*c1#*c2 # TODO normal colors
                    self.quad_strips[-1].append((x, y, z, color[0], color[1], color[2]))

    def render(self):
        for strip in self.quad_strips:
            glBegin(GL_QUAD_STRIP)
            for point in strip:
                glColor3f(point[3], point[4], point[5])
                glVertex3f(point[0]+self.pos[0], point[1]+self.pos[1], point[2]+self.pos[2])
            glEnd()
