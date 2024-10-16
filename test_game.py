import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from game import Game
from camera import Camera
from Physics.physics_world import PhysicsWorld
from Physics.bodies import Torus, TracedSphere
from threading import Thread


class TestGame(Game):
    def __init__(self, window_width, window_height, window_title):
        super().__init__(window_width, window_height, window_title)
    
    def load(self):
        self.camera=Camera(np.array([0.0, 7.0, 13.0]), np.array([0.0, 1.0, 0.0]), -90, -30.0, 70)
        torus = Torus(np.array((0,0,0)), np.array((0,0,0)), 1e+13, 5, 1.5, 16, 32)
        sphere = TracedSphere(np.array((7,0,0)), np.array((0,6,2)), 1, 0.2, 16, 16)
        self.physics_world = PhysicsWorld(torus, sphere)
        t = Thread(target=self.physics_world.run_torus_simulation, args=(0.04,))
        t.start()

        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_scroll_callback(self.window, self.scroll_callback)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

        self.mouse_sensitivity=10
        self.movement_speed=8

        self.first_mouse = True
    
    def update(self):
        # physics if it hasn't been launched at the beginning
        #self.physics_world.tick(self.delta_time)

        # movement, keyboard
        if glfw.get_key(self.window, glfw.KEY_W) == 1:
            self.camera.camera_pos +=self.camera.front *  self.movement_speed * self.delta_time
        if glfw.get_key(self.window, glfw.KEY_S) == 1:
            self.camera.camera_pos -= self.camera.front * self.movement_speed * self.delta_time

        if glfw.get_key(self.window, glfw.KEY_A) == 1:
            self.camera.camera_pos -= self.camera.right * self.movement_speed * self.delta_time
        if glfw.get_key(self.window, glfw.KEY_D) == 1:
            self.camera.camera_pos += self.camera.right * self.movement_speed * self.delta_time

        if glfw.get_key(self.window, glfw.KEY_SPACE) == 1:
            self.camera.camera_pos += self.camera.up * self.movement_speed * self.delta_time
        if glfw.get_key(self.window, glfw.KEY_LEFT_SHIFT) == 1:
            self.camera.camera_pos -= self.camera.up * self.movement_speed * self.delta_time

        # looking around, mouse
        cursor_pos=np.array(glfw.get_cursor_pos(self.window))
        if self.first_mouse:
            self.last_cursor_pos=cursor_pos
            self.first_mouse=False
        cursor_offset = cursor_pos-self.last_cursor_pos
        self.last_cursor_pos=cursor_pos

        cursor_offset*=self.mouse_sensitivity*self.delta_time
        self.camera.yaw += cursor_offset[0]
        self.camera.pitch -= cursor_offset[1]
        
        if self.camera.pitch > 89.0:
            self.camera.pitch = 89.0
        if self.camera.pitch < -89.0:
            self.camera.pitch = -89.0

    def render(self):
        # clear screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Camera control
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.camera.fov, glfw.get_window_size(self.window)[0] / glfw.get_window_size(self.window)[1], 0.1, 1000.0)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        self.camera.update_camera()
        gluLookAt(*self.camera.get_look_at_values())

        # Draw the objects
        self.physics_world.torus.render()
        self.physics_world.sphere.render()
        
        # Show it to the screen
        glfw.swap_buffers(self.window)

    # Zoom
    def scroll_callback(self, window, xoffset, yoffset):
        if self.camera.fov >= 1.0 and self.camera.fov <= 70.0:
            self.camera.fov -= yoffset
        if self.camera.fov <= 1.0:
            self.camera.fov = 1.0
        if self.camera.fov >= 70.0:
            self.camera.fov = 70.0

    # Close
    def key_callback(self, window, key, scancode, action, mods):
        if key == 256 and action == 1:
            glfw.set_window_should_close(window, True)
    
    def terminate(self):
        self.physics_world.stop()
