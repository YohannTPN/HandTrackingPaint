import numpy as np


class Layer:

    def __init__(self, data, name, visible=True):
        self.data = data
        self.name = name
        self.visible = visible

    def toggle_visibility(self):
        self.visible = not self.visible

    def _blend(self, region, target, opacity):

        alpha = opacity / 255.0
        current = self.data[region].astype(np.float32)           
        mixed = current * (1 - alpha) + np.array(target, np.float32) * alpha  
        self.data[region] = np.rint(mixed).astype(np.uint8)     

    def paint(self, region, color, opacity):
        self._blend(region, (*color, 255), opacity)

    def erase(self, region, opacity):
        self._blend(region, (0, 0, 0, 0), opacity)

    def copy(self):
        return Layer(self.data.copy(), self.name, self.visible)