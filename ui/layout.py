from dataclasses import dataclass

@dataclass
class Layout:
    width: int
    height: int
    top_h: int
    footer_h: int
    right_w: int
    canvas: tuple

    @classmethod
    def calculate(cls, width, height):
        top = max(48, min(66, int(height * 0.085)))
        footer = 24
        right = max(126, min(190, int(width * 0.19)))
        if width < 650:
            right = 122
        right = min(right, max(110, width // 3))
        canvas = (0, top, max(1, width-right), max(top+1, height-footer))
        return cls(width, height, top, footer, right, canvas)

    def toolbar_buttons(self):
        from Button import Button
        labels = [
            ("Brush", "brush"), ("Fill", "fill"), ("Eraser", "eraser"),
            ("Undo", "undo"), ("Redo", "redo"), ("Colors", "colors"), ("Save", "save")
        ]
        margin, gap = 7, 5
        available = self.width - self.right_w - 2*margin - gap*(len(labels)-1)
        bw = max(42, min(82, available // len(labels)))
        bh = max(29, self.top_h - 16)
        y = (self.top_h-bh)//2
        actions = None
        x = margin
        result = []
        for label, key in labels:
            result.append((key, (x,y), (bw,bh)))
            x += bw+gap
        return result
