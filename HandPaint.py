import math

import cv2

from HandLandMarker import HandLandMarker
from HandGestures import CommandGesture, assign_hands
from Ui import UI

THUMB_TIP, INDEX_TIP = 4, 8
WRIST, MIDDLE_MCP = 0, 9


class HandPaint(HandLandMarker):
    """Paint controlled by two hands: one draws (pinching), the other controls (laying)."""

    PINCH_ON = 0.20    # ratio en dessous duquel on commence à dessiner
    PINCH_OFF = 0.30   # ratio au dessus duquel on s'arrête
    SMOOTHING = 0.5    # 1 = aucun lissage, plus bas = plus lisse mais plus lent

    DRAW_SIDE = "right"   # "right" : ta main droite dessine, la gauche commande ("left" pour l'inverse)

    # Name displayed on the screen for each placement of the control hand
    COMMAND_NAMES = {"one": "Undo", "two": "Restore", "three": "Prev layer",
                     "four": "Next layer", "ok": "Panel"}

    def __init__(self, model_path, ui=None):
        super().__init__(model_path, num_hands=2)
        self.ui = ui or UI()
        self.pinching = False
        self.prev_point = None
        self.smooth_point = None
        self.cursor = None

        self.was_pinching = False
        self.is_clicking_button = False
        self.can_register_action = True

        # Control hand: which pose triggers which interface action
        self.command_gesture = CommandGesture()
        self.commands = {
            "one": self.ui.pop_last_action,
            "two": self.ui.restore_state,
            "three": self.ui.select_previous_layer,
            "four": self.ui.select_next_layer,
            "ok": self.ui.toggle_panel,
        }

    # ---------- Moveset (drawing hand) ----------

    @staticmethod
    def pinch_ratio(points):
        """Distance pouce-index divisée par la taille de la main.

        La division rend la mesure indépendante de la distance à la caméra.
        """
        hand_size = math.dist(points[WRIST], points[MIDDLE_MCP])
        if hand_size == 0:
            return 1.0
        return math.dist(points[THUMB_TIP], points[INDEX_TIP]) / hand_size

    def update_pinch_state(self, ratio):
        # Hystérésis : deux seuils différents évitent le clignotement
        if self.pinching:
            self.pinching = ratio < self.PINCH_OFF
        else:
            self.pinching = ratio < self.PINCH_ON

    # ---------- Drawing Point ----------

    def brush_position(self, points):
        """Middle of thumb and index finger: stable even when the fingers touch each other."""
        tx, ty = points[THUMB_TIP]
        ix, iy = points[INDEX_TIP]
        raw = ((tx + ix) / 2, (ty + iy) / 2)

        if self.smooth_point is None:
            self.smooth_point = raw
        else:
            a = self.SMOOTHING
            self.smooth_point = (a * raw[0] + (1 - a) * self.smooth_point[0],
                                 a * raw[1] + (1 - a) * self.smooth_point[1])
        return int(self.smooth_point[0]), int(self.smooth_point[1])

    def release(self):
        """Stop current line."""
        self.pinching = False
        self.prev_point = None
        self.smooth_point = None
        self.is_clicking_button = False
        self.can_register_action = True
        self.ui.on_release()

    # ---------- Control Hand ----------

    def update_commands(self, frame, command_points):
        # During a stroke, the control hand is ignored and disarmed:
        # An undo in the middle of a line would be absurd, and the hand must not trigger anything at the end of the stroke.
        if self.pinching:
            self.command_gesture.disarm()
            command_points = None

        pose = self.command_gesture.update(command_points)
        if pose is not None:
            action = self.commands.get(pose)
            if action is not None:
                action()

        self.draw_command_feedback(frame, command_points)

    def draw_command_feedback(self, frame, command_points):
        """Write near the wrist what the control hand is doing."""
        if command_points is None:
            return
        gesture = self.command_gesture
        if not gesture.armed:
            text = "make a fist"
        elif gesture.pose in self.COMMAND_NAMES:
            text = f"{self.COMMAND_NAMES[gesture.pose]} {int(gesture.progress * 100)}%"
        else:
            text = "ready"
        x, y = command_points[WRIST]
        cv2.putText(frame, text, (x - 20, y + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # ---------- Hooks ----------

    def on_frame(self, frame, result):
        h, w = frame.shape[:2]
        self.ui.ensure_canvas(w, h)
        self.cursor = None

        # What hand is drawing, what hand is controlling?
        hands = [self.to_pixels(hand, w, h) for hand in result.hand_landmarks]
        draw_idx, command_idx = assign_hands([points[WRIST][0] for points in hands], self.DRAW_SIDE)
        draw_points = hands[draw_idx] if draw_idx is not None else None
        command_points = hands[command_idx] if command_idx is not None else None

        if command_points is not None:
            self.draw_hand(frame, command_points, "commands")
        self.update_commands(frame, command_points)

        if draw_points is None:
            self.release()
            return

        points = draw_points
        self.draw_hand(frame, points, "draw")

        self.was_pinching = self.pinching

        self.update_pinch_state(self.pinch_ratio(points))

        start_pinching = self.pinching and not self.was_pinching

        self.cursor = self.brush_position(points)

        if start_pinching:
            self.is_clicking_button = self.ui.handle_click(self.cursor)

        if not self.pinching:
            self.is_clicking_button = False
            self.can_register_action = True
            self.ui.on_release()

        if self.pinching and not self.is_clicking_button:
            if self.can_register_action:
                self.ui.register_state()
                self.can_register_action = False  # Empêche d'enregistrer plusieurs fois pour le même trait
            if self.prev_point is not None:
                self.ui.draw_line(self.prev_point, self.cursor)
            self.prev_point = self.cursor

        elif self.pinching and self.is_clicking_button:
            self.ui.on_drag(self.cursor)

        else:
            self.prev_point = None

    def render(self, frame):
        self.ui.show(frame, self.cursor, self.pinching)

    def on_key(self, key):
        if key == ord('s'):
            self.ui.save()
        return super().on_key(key)