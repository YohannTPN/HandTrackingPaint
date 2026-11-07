import math
import time

WRIST, THUMB_TIP, INDEX_TIP, MIDDLE_MCP = 0, 4, 8, 9

FINGERS = {
    "index": (6, 8),
    "middle": (10, 12),
    "ring": (14, 16),
    "pinky": (18, 20),
}

OK_PINCH_RATIO = 0.25  
POSES_BY_COUNT = ("fist", "one", "two", "three", "four")


def pinch_ratio(points):
    """Distance thumb-index finger divided by hand size (same calculation as HandPaint)."""
    hand_size = math.dist(points[WRIST], points[MIDDLE_MCP])
    if hand_size == 0:
        return 1.0
    return math.dist(points[THUMB_TIP], points[INDEX_TIP]) / hand_size


def extended_fingers(points):
    """Returns {finger: True/False}.

    A finger is tense if its tip is further from the wrist than its PIP joint.
    We only compare distances: it works regardless of the hand’s orientation.
    """
    wrist = points[WRIST]
    return {name: math.dist(wrist, points[tip]) > math.dist(wrist, points[pip])
            for name, (pip, tip) in FINGERS.items()}


def classify_pose(points):
    """Name of the pose : "ok", "fist", "one", "two", "three" ou "four" (number of extended fingers)."""
    fingers = extended_fingers(points)
    count = sum(fingers.values())
    others_up = sum(fingers[name] for name in ("middle", "ring", "pinky"))

    # Le signe "OK" : pouce et index qui se touchent, et au moins 2 autres doigts levés.
    # Cette condition évite de confondre un poing (pouce contre l'index) avec un "OK".
    if pinch_ratio(points) < OK_PINCH_RATIO and others_up >= 2:
        return "ok"
    return POSES_BY_COUNT[count]


def assign_hands(wrist_xs, draw_side="right"):
    """Decide which hand draws and which commands, from the horizontal position.

    `wrist_xs` : the abscissa of each hand detected.
    The image is mirrored: the user’s right hand is on the right side of the image.
    Returns (drawing hand index, control hand index), None if absent.
    Only one hand detected: it is the hand that draws.
    """
    n = len(wrist_xs)
    if n == 0:
        return None, None
    if n == 1:
        return 0, None
    order = sorted(range(n), key=lambda i: wrist_xs[i])
    left, right = order[0], order[-1]
    return (right, left) if draw_side == "right" else (left, right)


class CommandGesture:
    """Triggers a command when a pose is held for long enough.

    Rules:
    - you must first show a fist to "arm" (the hand at rest does not trigger anything);
    - a pose must be held `hold_seconds` without interruption;
    - Once triggered, the command is not repeated: you have to make a fist again;
    - If the hand disappears more than `absent_seconds`, or if you call disarm(), you need to redo a fist.
    """

    def __init__(self, hold_seconds=0.4, absent_seconds=0.5, clock=time.monotonic):
        self.hold_seconds = hold_seconds
        self.absent_seconds = absent_seconds
        self.clock = clock
        self.armed = False
        self.pose = None
        self._since = None
        self._last_seen = None

    @property
    def progress(self):
        """Maintenance progress, from 0 to 1 (for display)."""
        if not self.armed or self.pose in (None, "fist"):
            return 0.0
        return min(1.0, (self.clock() - self._since) / self.hold_seconds)

    def disarm(self):
        """Forget everything: the next order will require a fist."""
        self.armed = False
        self.pose = None
        self._since = None

    def update(self, points):
        """To be called on each image with the control hand points (or None).

        Returns the name of the pose that was just triggered, otherwise None.
        """
        now = self.clock()
        pose = classify_pose(points) if points is not None else None

        if pose is not None:
            self._last_seen = now
        elif self._last_seen is None or now - self._last_seen > self.absent_seconds:
            self.armed = False              

        if pose != self.pose:               
            self.pose = pose
            self._since = now

        if pose == "fist":
            self.armed = True
            return None
        if pose is None or not self.armed:
            return None

        if now - self._since >= self.hold_seconds:
            self.armed = False             
            return pose
        return None