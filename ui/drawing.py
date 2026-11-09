import cv2
import numpy as np

class DrawingController:
    """Opérations raster : traits, gomme et pot de peinture."""
    def __init__(self, ui): self.ui=ui

    def draw_segment(self,p1,p2):
        u=self.ui
        if u.stroke_mask is not None:
            cv2.line(u.stroke_mask,p1,p2,255,u.current_brush().thickness,cv2.LINE_AA)

    def apply_stroke(self,layer):
        u=self.ui; region=u.stroke_mask>0
        if not np.any(region): return
        brush=u.current_brush()
        if u.active_tool=="eraser": layer.erase(region,brush.opacity)
        else: layer.paint(region,brush.color,brush.opacity)

    def fill(self,point):
        u=self.ui; h,w=u.layers.height,u.layers.width
        x,y=map(int,point)
        if not (0<=x<w and 0<=y<h): return
        mask=np.zeros((h+2,w+2),np.uint8)
        flags=cv2.FLOODFILL_MASK_ONLY|cv2.FLOODFILL_FIXED_RANGE|(255<<8)
        composite=u.layers.composite()
        cv2.floodFill(composite,mask,(x,y),0,loDiff=(24,24,24),upDiff=(24,24,24),flags=flags)
        region=mask[1:-1,1:-1]>0
        brush=u.brush
        u.layers.active.paint(region,brush.color,brush.opacity)
