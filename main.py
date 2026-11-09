
import os
import sys

from HandPaint import HandPaint


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    model_path = resource_path("hand_landmarker.task")
    app = HandPaint(model_path)
    app.run()
