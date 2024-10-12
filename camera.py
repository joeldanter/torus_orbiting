import numpy as np


class Camera:
    def __init__(self, camera_pos, up, yaw, pitch, fov):
        self.camera_pos=camera_pos
        self.up=up
        self.yaw=yaw
        self.pitch=pitch
        self.fov=fov
    
    def update_camera(self):
        camera_front = np.array([
            np.cos(np.radians(self.yaw)) * np.cos(np.radians(self.pitch)),
            np.sin(np.radians(self.pitch)),
            np.sin(np.radians(self.yaw)) * np.cos(np.radians(self.pitch))
        ])
        right = np.linalg.cross(camera_front, self.up)
        front = np.linalg.cross(self.up, right)
        self.camera_front = camera_front / np.linalg.norm(camera_front)
        self.right = right / np.linalg.norm(right)
        self.front = front / np.linalg.norm(front)
        self.camera_target = self.camera_pos + self.camera_front
    
    def get_look_at_values(self):
        return (self.camera_pos[0], self.camera_pos[1], self.camera_pos[2],
                self.camera_target[0], self.camera_target[1], self.camera_target[2],
                self.up[0], self.up[1], self.up[2])
