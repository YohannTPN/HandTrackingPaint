import numpy as np

from Layer import Layer


class LayerStack:

    def __init__(self, width, height, max_layers=5):
        self.width = width
        self.height = height
        self.max_layers = max_layers

        self._counter = 0                      
        self.layers = [self._new_layer()]
        self.active_index = 0

    def _new_layer(self):
        self._counter += 1
        data = np.zeros((self.height, self.width, 4), np.uint8)
        return Layer(data, f"Layer {self._counter}")

    @property
    def active(self):
        return self.layers[self.active_index]

    def select(self, index):
        if 0 <= index < len(self.layers):
            self.active_index = index
            return True
        return False


    def add(self):
        if len(self.layers) >= self.max_layers:
            return None
        layer = self._new_layer()
        self.layers.insert(self.active_index + 1, layer)
        self.active_index += 1
        return layer

    def delete_active(self):
        if len(self.layers) == 1:
            return False
        del self.layers[self.active_index]
        self.active_index = max(0, self.active_index - 1)   
        return True


    def composite(self, active_override=None):
        out = np.full((self.height, self.width, 3), 255, np.float32)   

        for i, layer in enumerate(self.layers):
            if not layer.visible:
                continue
            source = active_override if (i == self.active_index and active_override is not None) else layer
            color = source.data[..., :3].astype(np.float32)
            alpha = source.data[..., 3:4].astype(np.float32) / 255.0
            out = color + out * (1 - alpha)

        return np.rint(out).astype(np.uint8)