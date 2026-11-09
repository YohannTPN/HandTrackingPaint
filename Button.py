import cv2

class Button:

    def __init__(self, pos, size, label, action, active=False, enabled=True,
                 accent=(190, 115, 75)):
        self.pos = tuple(pos)
        self.size = tuple(size)
        self.label = str(label)
        self.action = action
        self.active = active
        self.enabled = enabled
        self.accent = accent

    def contains(self, point):
        x, y = point
        px, py = self.pos
        w, h = self.size
        return px <= x < px + w and py <= y < py + h

    def draw(self, image, font_scale=0.48):
        x, y = self.pos
        w, h = self.size
        if not self.enabled:
            fill = (55, 55, 55)
            text = (125, 125, 125)
            border = (70, 70, 70)
        elif self.active:
            fill = self.accent
            text = (255, 255, 255)
            border = (225, 175, 135)
        else:
            fill = (74, 61, 53)
            text = (225, 230, 238)
            border = (100, 81, 70)

        cv2.rectangle(image, (x, y), (x + w, y + h), fill, -1, cv2.LINE_AA)
        cv2.rectangle(image, (x, y), (x + w, y + h), border, 1, cv2.LINE_AA)
        font = cv2.FONT_HERSHEY_SIMPLEX
        (tw, th), _ = cv2.getTextSize(self.label, font, font_scale, 1)
        tx = x + max(5, (w - tw) // 2)
        ty = y + (h + th) // 2
        cv2.putText(image, self.label, (tx, ty), font, font_scale, text, 1, cv2.LINE_AA)
