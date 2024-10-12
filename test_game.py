import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from game import Game
from camera import Camera
from Physics.physics_world import PhysicsWorld


class TestGame(Game):
    def __init__(self, window_width, window_height, window_title):
        super().__init__(window_width, window_height, window_title)
    
    def load(self):
        self.camera=Camera(np.array([0.0, 7.0, 13.0]), np.array([0.0, 1.0, 0.0]), -90, -30.0, 60)
        self.physics_world = PhysicsWorld()
        self.physics_world.draw_torus(5, 2, 32, 32)

        glfw.set_key_callback(self.window, self.key_callback)
        glfw.set_scroll_callback(self.window, self.scroll_callback)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)

        self.mouse_sensitivity=10
        self.movement_speed=8

        self.first_mouse = True
    
    def update(self):
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
        for object in self.physics_world.quad_stripes:
            glBegin(GL_QUAD_STRIP)
            for point in object:
                glVertex3f(point[0], point[1], point[2])
                glColor3f(point[3], point[4], point[5])
            glEnd()
        
        # Show it to the screen
        glfw.swap_buffers(self.window)

    # Zoom
    def scroll_callback(self, window, xoffset, yoffset):
        if self.camera.fov >= 1.0 and self.camera.fov <= 45.0:
            self.camera.fov -= yoffset
        if self.camera.fov <= 1.0:
            self.camera.fov = 1.0
        if self.camera.fov >= 45.0:
            self.camera.fov = 45.0

    # Close
    def key_callback(self, window, key, scancode, action, mods):
        if key == 256 and action == 1:
            glfw.set_window_should_close(window, True)
