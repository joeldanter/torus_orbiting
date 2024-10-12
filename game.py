import glfw
from OpenGL.GL import *

class Game:
    def __init__(self, window_width, window_height, window_title):
        self.window_width=window_width
        self.window_height=window_height
        self.window_title=window_title
    
    def run(self):
        if not glfw.init():
            return

        glfw.window_hint(glfw.FOCUSED, glfw.TRUE)
        glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)

        self.window = glfw.create_window(self.window_width, self.window_height, self.window_title, None, None)
        if not self.window:
            glfw.terminate()
            return
        
        glfw.make_context_current(self.window)
        glfw.swap_interval(1) # Vsync on or something like that (idk)
        glEnable(GL_DEPTH_TEST)
        
        self.elapsed=glfw.get_time()
        self.load()
        while not glfw.window_should_close(self.window):
            self.delta_time = glfw.get_time() - self.elapsed
            self.elapsed = glfw.get_time()
            
            # poll events so the window doesn't freeze
            glfw.poll_events()

            self.update()
            self.render()
        glfw.terminate()


    def load(self):
        pass

    def update(self):
        pass

    def render(self):
        pass
