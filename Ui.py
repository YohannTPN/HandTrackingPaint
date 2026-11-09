import os
import time
from collections import deque

import cv2
import numpy as np

from Brush import Brush
from Button import Button
from ColorWheel import ColorWheel
from LayerStack import LayerStack
from Panel import Panel
from Slider import Slider
from ui.layout import Layout
from ui.theme import ACCENT, TEXT, MUTED, PANEL, BUTTON_BORDER
from ui.drawing import DrawingController
from ui.layers_view import LayersView
from ui.renderer import Renderer


class UI:
    def __init__(self, brush=None, buttons=None):
        self.brush = brush or Brush()
        self.eraser = Brush(color=(255,255,255), thickness=20)
        self.layers = None
        self.stroke_mask = None
        self.buttons = []
        self.layer_buttons = []
        self.is_panel_open = False
        self.panel = None
        self.color_wheel = None
        self.active_tool = "brush"
        self.active_slider = None
        self.actions_history = deque(maxlen=30)
        self.restore_history = deque(maxlen=30)
        self.color_history = deque([(0,0,0),(255,255,255),(0,0,255),(0,255,0),(255,0,0)],maxlen=5)
        self.layout = None
        self.frame_w = self.frame_h = 0
        self.canvas_rect = (0,0,0,0)
        self.layer_list_y = 0
        self.drawing = DrawingController(self)
        self.layers_view = LayersView(self)
        self.renderer = Renderer(self)
        self.show_tutorial = True

    # ---- Canvas and adaptive layout ----
    def ensure_canvas(self, width, height):
        width, height = int(width), int(height)
        if self.layers is None:
            self.layers = LayerStack(width,height)
            self.stroke_mask = np.zeros((height,width),np.uint8)
            self._build_layout(width,height)
        elif (width,height)!=(self.frame_w,self.frame_h):
            self._resize_canvas(width,height)

    def _resize_canvas(self,width,height):
        old_w,old_h=self.frame_w,self.frame_h
        for layer in self.layers.layers:
            layer.data=cv2.resize(layer.data,(width,height),interpolation=cv2.INTER_NEAREST)
        self.stroke_mask=cv2.resize(self.stroke_mask,(width,height),interpolation=cv2.INTER_NEAREST)
        self.layers.width,self.layers.height=width,height
        self._build_layout(width,height)
        self.clear_history()

    def _build_layout(self,width,height):
        self.frame_w,self.frame_h=width,height
        self.layout=Layout.calculate(width,height)
        self.canvas_rect=self.layout.canvas
        self.buttons=[]
        actions={
            "brush":self.use_brush,"fill":self.use_fill,"eraser":self.use_eraser,
            "undo":self.pop_last_action,"redo":self.restore_state,
            "colors":self.toggle_panel,"save":self.save,
        }
        labels={"brush":"Brush","fill":"Fill","eraser":"Eraser","undo":"Undo","redo":"Redo","colors":"Colors","save":"Save"}
        for key,pos,size in self.layout.toolbar_buttons():
            self.buttons.append(Button(pos,size,labels[key],actions[key]))
        self._build_layer_buttons()
        self._build_color_panel()

    def _build_layer_buttons(self):
        x=self.layout.width-self.layout.right_w+8
        width=self.layout.right_w-16
        y=self.layout.top_h+31
        bh=25; gap=5
        specs=[("+ New layer",self.add_layer),("- Delete layer",self.delete_layer),
               ("< Previous",self.select_previous_layer),("> Next",self.select_next_layer),
               ("Toggle eye",self.toggle_active_layer_visibility)]
        self.layer_buttons=[]
        for label,action in specs:
            self.layer_buttons.append(Button((x,y),(width,bh),label,action))
            y+=bh+gap
        self.layer_list_y=y+7

    def _build_color_panel(self):
        cw,ch=self.layout.canvas[2],self.layout.canvas[3]-self.layout.canvas[1]
        wheel=min(132,max(88,int(min(cw,ch)*.27)))
        panel_w=min(max(300,wheel+180),max(300,cw-16))
        panel_h=min(ch-16,wheel+190)
        px=self.layout.canvas[0]+max(8,(cw-panel_w)//2)
        py=self.layout.canvas[1]+max(8,(ch-panel_h)//2)
        wheel_pos=(px+14,py+40)
        self.color_wheel=ColorWheel(wheel_pos,(wheel,wheel),initial_color=self.brush.color)
        preview_size=42
        preview_pos=(wheel_pos[0]+wheel+20, wheel_pos[1]+4)
        sw=20; sy=preview_pos[1]+preview_size+24
        swatches=[(preview_pos[0]+i*(sw+5),sy,sw,sw) for i in range(5)]
        sx=px+14; slider_w=panel_w-28
        base_y=wheel_pos[1]+wheel+32
        sliders=[
            Slider((sx,base_y),(slider_w,15),1,50,self.get_brush_thickness,self.set_brush_thickness,"Size"),
            Slider((sx,base_y+43),(slider_w,15),0,255,self.get_brightness,self.set_brightness,"Brightness"),
            Slider((sx,base_y+86),(slider_w,15),1,255,self.get_opacity,self.set_opacity,"Opacity"),
        ]
        self.panel=Panel((px,py),(panel_w,panel_h),sliders,self.color_wheel,preview_pos,preview_size,self.preview_color,swatches,self.get_color_history)


    
    def handle_tutorial_key(self, key):
        """Handle key presses related to the tutorial display."""

        if key in (ord("h"), ord("H")):
            self.show_tutorial = not self.show_tutorial


    def draw_tutorial(self, frame):
        """Draw the tutorial overlay on the given frame."""

        import cv2

        h, w = frame.shape[:2]

        # Dimensions du panneau
        panel_w = min(650, w - 40)
        panel_h = min(490, h - 40)

        x = (w - panel_w) // 2
        y = (h - panel_h) // 2

        # Fond sombre
        overlay = frame.copy()
        cv2.rectangle(
            overlay,
            (x, y),
            (x + panel_w, y + panel_h),
            (45, 51, 62),
            -1
        )

        cv2.addWeighted(overlay, 0.94, frame, 0.06, 0, frame)

        cv2.rectangle(
            frame,
            (x, y),
            (x + panel_w, y + panel_h),
            (244, 133, 66),
            2
        )

        cv2.putText(
            frame,
            "HAND TRACKING PAINT",
            (x + 25, y + 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.85,
            (244, 133, 66),
            2,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            "GESTURE TUTORIAL",
            (x + 25, y + 78),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (220, 230, 240),
            1,
            cv2.LINE_AA
        )

        cv2.line(
            frame,
            (x + 25, y + 95),
            (x + panel_w - 25, y + 95),
            (70, 83, 102),
            1
        )

        instructions = [
            ("DRAWING HAND - RIGHT", [
                "Pinch thumb + index finger",
                "Move your hand to draw"
            ]),
            ("COMMAND HAND - LEFT", [
                "Make a fist to activate commands",
                "1 finger : Undo",
                "2 fingers : Redo",
                "3 fingers : Brush",
                "4 fingers : Eraser",
                "OK gesture : Toggle color panel"
            ])
        ]

        current_y = y + 135

        for section, lines in instructions:
            cv2.putText(
                frame,
                section,
                (x + 25, current_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.58,
                (244, 133, 66),
                2,
                cv2.LINE_AA
            )

            current_y += 30

            for line in lines:
                cv2.putText(
                    frame,
                    "- " + line,
                    (x + 40, current_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.48,
                    (232, 237, 245),
                    1,
                    cv2.LINE_AA
                )
                current_y += 27

            current_y += 12

        cv2.line(
            frame,
            (x + 25, y + panel_h - 65),
            (x + panel_w - 25, y + panel_h - 65),
            (70, 83, 102),
            1
        )

        
        cv2.putText(
            frame,
            "H : OPEN / CLOSE TUTORIAL",
            (x + 25, y + panel_h - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.43,
            (170, 182, 200),
            1,
            cv2.LINE_AA
        )

    # ---- Tools ----
    def current_brush(self):
        return self.eraser if self.active_tool=="eraser" else self.brush
    def current_color(self): return self.current_brush().color
    def change_color(self,color):
        self.active_tool="brush"; self.brush.color=tuple(int(v) for v in color)
        self.remember_color()
    def use_brush(self): self.active_tool="brush"
    def use_eraser(self): self.active_tool="eraser"
    def use_fill(self): self.active_tool="fill"
    def open_panel(self): self.is_panel_open=True
    def toggle_panel(self): self.is_panel_open=not self.is_panel_open

    # ---- Canvas operations ----
    def point_in_canvas(self,point):
        x,y=point; left,top,right,bottom=self.canvas_rect
        return left<=x<right and top<=y<bottom
    def draw_line(self,p1,p2): self.drawing.draw_segment(p1,p2)
    def fill_canvas(self,point): self.drawing.fill(point)
    def apply_stroke(self,layer): self.drawing.apply_stroke(layer)
    def blend_region(self,target,region,color,opacity):
        if np.any(region):
            a=opacity/255.0
            target[region]=np.rint(target[region].astype(np.float32)*(1-a)+np.asarray(color,np.float32)*a).astype(np.uint8)

    # ---- Undo / redo ----
    def register_state(self):
        if self.layers is None:return
        self.actions_history.append((self.layers.active_index,self.layers.active.data.copy()))
        self.restore_history.clear(); self.remember_color()
    def restore_state(self): self._restore(self.restore_history,self.actions_history)
    def pop_last_action(self): self._restore(self.actions_history,self.restore_history)
    def _restore(self,source,target):
        if self.layers is None or not source:return
        index,snapshot=source.pop()
        if index>=len(self.layers.layers):return
        layer=self.layers.layers[index]
        target.append((index,layer.data.copy()))
        layer.data[:]=snapshot
        self.layers.select(index)
    def clear_history(self):
        self.actions_history.clear(); self.restore_history.clear()

    # ---- Layer operations ----
    def add_layer(self):
        if self.layers and self.layers.add() is not None:self.clear_history()
    def delete_layer(self):
        if self.layers and self.layers.delete_active():self.clear_history()
    def select_next_layer(self):
        if self.layers:self.layers.select(min(len(self.layers.layers)-1,self.layers.active_index+1))
    def select_previous_layer(self):
        if self.layers:self.layers.select(max(0,self.layers.active_index-1))
    def toggle_active_layer_visibility(self):
        if self.layers:self.layers.active.toggle_visibility()
    def layer_label(self):
        if not self.layers:return "No layer"
        return f"{self.layers.active.name} {self.layers.active_index+1}/{len(self.layers.layers)}"

    # ---- Brush settings / palette ----
    def get_brush_thickness(self):return self.current_brush().thickness
    def set_brush_thickness(self,value):self.current_brush().thickness=int(value)
    def get_brightness(self):return self.color_wheel.brightness if self.color_wheel else 255
    def set_brightness(self,value):
        if self.color_wheel:
            self.color_wheel.brightness=int(value); self.color_wheel._update_wheel_image()
    def get_opacity(self):return self.current_brush().opacity
    def set_opacity(self,value):self.current_brush().opacity=int(value)
    def preview_color(self):
        b=self.current_brush(); a=b.opacity/255.0
        return tuple(int(c*a+255*(1-a)) for c in b.color)
    def remember_color(self):
        color=tuple(self.brush.color)
        if color in self.color_history:self.color_history.remove(color)
        self.color_history.appendleft(color)
    def get_color_history(self):return list(self.color_history)

    # ---- Pointer interaction ----
    def button_at(self,point):return next((b for b in self.buttons if b.contains(point)),None)
    def handle_click(self,point):
        if self.is_panel_open:
            color=self.color_wheel.select_color(point)
            if color is not None:self.change_color(color); return True
            swatch=self.panel.history_color_at(point)
            if swatch is not None:self.change_color(swatch); return True
            slider=self.panel.slider_at(point)
            if slider is not None:
                self.active_slider=slider; slider.set_value_from_point(point); return True
            if not self.panel.contains(point):self.is_panel_open=False
            return True
        button=self.button_at(point)
        if button:
            button.action(); return True
        for button in self.layer_buttons:
            if button.contains(point):button.action(); return True
        index=self.layers_view.index_at(point)
        if index is not None:self.layers.select(index); return True
        if not self.point_in_canvas(point):return True
        if self.active_tool=="fill":
            self.register_state(); self.fill_canvas(point); return True
        return False
    def on_drag(self,point):
        if self.active_slider:self.active_slider.set_value_from_point(point)
    def on_release(self):
        self.active_slider=None
        if self.stroke_mask is not None and self.stroke_mask.any():
            self.apply_stroke(self.layers.active); self.stroke_mask[:]=0

    # ---- Save / display ----
    def save(self):
        if self.layers is None:return None
        filename=os.path.join(os.getcwd(),f"paint_{int(time.time())}.png")
        cv2.imwrite(filename,self.layers.composite())
        print(f"Drawing saved : {filename}")
        return filename
    
    def show(self, camera_frame, cursor=None, drawing=False):
        cv2.imshow("Camera", camera_frame)

        paint_frame = self.renderer.compose(cursor, drawing)

        if self.show_tutorial:
            self.draw_tutorial(paint_frame)

        cv2.imshow("Paint", paint_frame)

