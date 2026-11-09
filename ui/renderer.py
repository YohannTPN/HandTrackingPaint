import cv2
from ui.theme import HEADER, TEXT, MUTED, GREEN, ACCENT

class Renderer:
    def __init__(self,ui): self.ui=ui

    def compose(self,cursor=None,drawing=False):
        u=self.ui
        if u.stroke_mask is not None and u.stroke_mask.any():
            preview=u.layers.active.copy(); u.drawing.apply_stroke(preview)
            image=u.layers.composite(active_override=preview)
        else: image=u.layers.composite()
        self.draw_toolbar(image)
        u.layers_view.draw(image)
        if u.is_panel_open and u.panel: u.panel.draw(image)
        self.draw_footer(image,drawing)
        if cursor is not None: self.draw_cursor(image,cursor,drawing)
        return image

    def draw_toolbar(self,image):
        u=self.ui
        cv2.rectangle(image,(0,0),(u.layout.width,u.layout.top_h),HEADER,-1)
        for button in u.buttons:
            button.active = button.label.lower()==u.active_tool
            button.draw(image,.39)

    def draw_footer(self,image,drawing):
        u=self.ui; y=u.layout.height-u.layout.footer_h
        cv2.rectangle(image,(0,y),(u.layout.width,u.layout.height),HEADER,-1)
        status="DRAWING" if drawing else "READY"
        cv2.putText(image,status,(10,u.layout.height-7),cv2.FONT_HERSHEY_SIMPLEX,.36,GREEN if drawing else MUTED,1,cv2.LINE_AA)
        cv2.putText(image,"S: SAVE   |   Q: QUIT",(max(125,u.layout.width-u.layout.right_w-145),u.layout.height-7),cv2.FONT_HERSHEY_SIMPLEX,.32,MUTED,1,cv2.LINE_AA)

    def draw_cursor(self,image,cursor,drawing):
        u=self.ui; radius=max(3,u.current_brush().thickness//2)
        if u.active_tool=="eraser": color=(185,190,198); thickness=2
        else: color=u.current_brush().color; thickness=-1 if drawing else 2
        cv2.circle(image,tuple(map(int,cursor)),radius,color,thickness,cv2.LINE_AA)
