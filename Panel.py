import cv2

class Panel:

    BG = (35, 40, 49)
    BORDER = (78, 88, 103)
    TEXT = (235, 239, 245)
    MUTED = (160, 170, 184)
    ACCENT = (190, 115, 75)

    def __init__(self, pos, size, sliders, color_wheel, preview_pos,
                 preview_size, get_color, swatch_rects, get_history):
        self.pos = tuple(pos)
        self.size = tuple(size)
        self.sliders = sliders
        self.color_wheel = color_wheel
        self.preview_pos = tuple(preview_pos)
        self.preview_size = preview_size
        self.get_color = get_color
        self.swatch_rects = swatch_rects
        self.get_history = get_history

    def draw(self, view):
        x, y = self.pos
        w, h = self.size
        cv2.rectangle(view, (x, y), (x + w, y + h), self.BG, -1, cv2.LINE_AA)
        cv2.rectangle(view, (x, y), (x + w, y + h), self.BORDER, 2, cv2.LINE_AA)
        cv2.putText(view, "COLOR & BRUSH SETTINGS", (x + 18, y + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, self.TEXT, 1, cv2.LINE_AA)

        wx, wy = self.color_wheel.pos
        ww, wh = self.color_wheel.size
        x1, y1 = max(0, wx), max(0, wy)
        x2, y2 = min(view.shape[1], wx + ww), min(view.shape[0], wy + wh)
        if x1 < x2 and y1 < y2:
            wheel_crop = self.color_wheel.wheel_image[y1-wy:y2-wy, x1-wx:x2-wx]
            mask_crop = self.color_wheel.mask[y1-wy:y2-wy, x1-wx:x2-wx]
            target = view[y1:y2, x1:x2]
            target[mask_crop > 0] = wheel_crop[mask_crop > 0]

        cv2.putText(view, "CURRENT COLOR", (self.preview_pos[0], self.preview_pos[1] - 9),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, self.MUTED, 1, cv2.LINE_AA)
        px, py = self.preview_pos
        ps = self.preview_size
        cv2.rectangle(view, (px, py), (px + ps, py + ps), self.get_color(), -1)
        cv2.rectangle(view, (px, py), (px + ps, py + ps), (225, 230, 238), 2)

        cv2.putText(view, "RECENT COLORS", (px, py + ps + 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, self.MUTED, 1, cv2.LINE_AA)
        self.draw_history(view)

        for slider in self.sliders:
            slider.draw(view)

        cv2.putText(view, "Thumb + Index finger to select / adjust",
                    (x + 18, y + h - 14), cv2.FONT_HERSHEY_SIMPLEX,
                    0.34, self.MUTED, 1, cv2.LINE_AA)

    def contains(self, point):
        x, y = point
        px, py = self.pos
        w, h = self.size
        return px <= x < px + w and py <= y < py + h

    def slider_at(self, point):
        for slider in self.sliders:
            if slider.contains(point):
                return slider
        return None

    def draw_history(self, view):
        history = self.get_history()
        for i, (rx, ry, rw, rh) in enumerate(self.swatch_rects):
            if i < len(history):
                cv2.rectangle(view, (rx, ry), (rx + rw, ry + rh), history[i], -1)
            else:
                cv2.rectangle(view, (rx, ry), (rx + rw, ry + rh), (54, 61, 73), -1)
            cv2.rectangle(view, (rx, ry), (rx + rw, ry + rh), self.BORDER, 1)

    def history_color_at(self, point):
        x, y = point
        history = self.get_history()
        for i, (rx, ry, rw, rh) in enumerate(self.swatch_rects):
            if i < len(history) and rx <= x < rx + rw and ry <= y < ry + rh:
                return history[i]
        return None
