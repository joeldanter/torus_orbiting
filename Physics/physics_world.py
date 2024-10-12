import numpy as np


class PhysicsWorld:
    def __init__(self):
        self.quad_stripes=[]
    
    def draw_torus(self, outer_radius, inner_radius, sides, rings):
        for i in range(sides):
            self.quad_stripes.append([])
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
                    self.quad_stripes[-1].append((x, y, z, color[0], color[1], color[2]))
