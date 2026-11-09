import cv2


class Slider:
    def __init__(self, pos, size, min_val, max_val, getter, setter,
                 label="", step=1):
        self.label = label
        self.pos = tuple(pos)
        self.size = tuple(size)
        self.min_val = min_val
        self.max_val = max_val
        self.get_brush_value = getter
        self.set_brush_value = setter
        self.step = max(1, step)

    def contains(self, point):
        x, y = point
        px, py = self.pos
        w, h = self.size
        return px <= x < px + w and py <= y < py + h

    def set_value_from_point(self, point):
        px, _ = self.pos
        w, _ = self.size
        if w <= 0:
            return
        relative_x = max(0, min(w, point[0] - px))
        value = self.min_val + (relative_x / w) * (self.max_val - self.min_val)
        value = round(value / self.step) * self.step
        self.set_brush_value(max(self.min_val, min(self.max_val, value)))

    def selected_value(self):
        px, py = self.pos
        w, h = self.size
        span = self.max_val - self.min_val
        ratio = 0 if span == 0 else (self.get_brush_value() - self.min_val) / span
        ratio = max(0.0, min(1.0, ratio))
        return int(px + ratio * w), int(py + h // 2)

    def draw(self, image):
        x, y = self.pos
        w, h = self.size
        value = self.get_brush_value()
        ratio = 0 if self.max_val == self.min_val else (
            (value - self.min_val) / (self.max_val - self.min_val)
        )
        ratio = max(0.0, min(1.0, ratio))
        cy = y + h // 2
        cv2.putText(image, f"{self.label.upper()}  {value}",
                    (x, y - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.43,
                    (220, 225, 235), 1, cv2.LINE_AA)
        cv2.line(image, (x, cy), (x + w, cy), (75, 84, 98), 5, cv2.LINE_AA)
        cv2.line(image, (x, cy), (x + int(w * ratio), cy),
                 (190, 115, 75), 5, cv2.LINE_AA)
        hx = x + int(w * ratio)
        cv2.circle(image, (hx, cy), 7, (245, 245, 245), -1, cv2.LINE_AA)
        cv2.circle(image, (hx, cy), 7, (190, 115, 75), 2, cv2.LINE_AA)
