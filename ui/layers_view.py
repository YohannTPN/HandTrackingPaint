import cv2
from ui.theme import PANEL, PANEL_ALT, BUTTON_BORDER, TEXT, MUTED, ACCENT, GREEN

class LayersView:
    def __init__(self,ui): self.ui=ui

    def draw(self,image):
        u=self.ui; x=u.layout.width-u.layout.right_w; w=u.layout.right_w; h=u.layout.height
        cv2.rectangle(image,(x,0),(u.layout.width,h),PANEL,-1)
        cv2.putText(image,"LAYERS",(x+10,u.layout.top_h+21),cv2.FONT_HERSHEY_SIMPLEX,.47,TEXT,1,cv2.LINE_AA)
        for button in u.layer_buttons: button.draw(image,.36)
        y0=u.layer_list_y
        for row,layer_index in enumerate(range(len(u.layers.layers)-1,-1,-1)):
            yy=y0+row*29
            if yy+24>=h-u.layout.footer_h: break
            layer=u.layers.layers[layer_index]
            active=layer_index==u.layers.active_index
            fill=ACCENT if active else PANEL_ALT
            cv2.rectangle(image,(x+8,yy),(u.layout.width-8,yy+23),fill,-1,cv2.LINE_AA)
            cv2.putText(image,"ON" if layer.visible else "OFF",(x+13,yy+16),cv2.FONT_HERSHEY_SIMPLEX,.30,GREEN if layer.visible else MUTED,1,cv2.LINE_AA)
            cv2.putText(image,layer.name[:12],(x+48,yy+16),cv2.FONT_HERSHEY_SIMPLEX,.34,TEXT,1,cv2.LINE_AA)

    def index_at(self,point):
        u=self.ui; x,y=point; sidebar_x=u.layout.width-u.layout.right_w
        if x<sidebar_x or y<u.layer_list_y: return None
        row=(y-u.layer_list_y)//29
        index=len(u.layers.layers)-1-int(row)
        return index if 0<=index<len(u.layers.layers) else None
