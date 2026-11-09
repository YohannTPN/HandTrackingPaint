# HandTracking Paint

**Draw in the air.** HandTracking Paint is a Paint-style drawing application controlled entirely by hand gestures. It uses your webcam and [MediaPipe Hand Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker) to track your hands: pinch your thumb and index finger together to draw, click buttons, and interact with the interface without a mouse.

The application uses two hands:
- **Drawing hand:** controls the cursor and draws using a pinch gesture.
- **Command hand:** triggers tools and interface actions using predefined gestures.

## Download

Download the latest Windows version from
[GitHub Releases](../../releases/latest).

Extract the ZIP archive and launch `HandTrackingPaint.exe`.

## Features

- **Pinch to draw:** pinch your thumb and index finger together and move your hand to draw.
- **Pinch to click:** interact with toolbar buttons, layer controls, and sliders without a mouse.
- **Two-hand control:** use one hand for drawing and the other for commands.
- **Gesture commands:** undo, redo, switch tools, and toggle the colour panel.
- **Tools:** brush, eraser, and flood fill.
- **Layers:** create, delete, select, and toggle the visibility of layers.
- **Undo / Redo:** restore previous drawing states, with up to 30 history entries.
- **Colour panel:**
  - HSV colour wheel with adjustable brightness.
  - Brush size slider.
  - Brush opacity slider.
  - Live preview of the current colour.
  - History of the last five colours used.
- **Responsive interface:** the layout adapts to the camera resolution.
- **Startup tutorial:** an on-screen guide explains the gestures when the application starts. Press `H` to reopen it.
- **Save:** export your drawing as a PNG image.

## Requirements

- Python 3.11 (the version used during development).
- A webcam.
- The MediaPipe `hand_landmarker.task` model file.
- The dependencies listed in `requirements.txt`.

## Installation

### 1. Clone or download the project

Open a terminal in the project folder.

Create an isolated Python environment.

**Using Conda:**

```bash
conda create -n handtracking python=3.11
conda activate handtracking
```

**Or using venv:**

```bash
python -m venv .venv
```

On Windows:

```bash
.venv\Scripts\activate
```

On macOS / Linux:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Download the MediaPipe model

The `hand_landmarker.task` model should already be included in the project folder.

If it is missing, download it with:

```bash
curl -L -o hand_landmarker.task https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task
```

On Windows PowerShell, use `curl.exe` instead of `curl`, or download the file directly through your browser.

## Usage

Run the application from the project folder:

```bash
python main.py
```

Two windows will open:

- **Camera:** displays the webcam feed and detected hand landmarks.
- **Paint:** displays the drawing canvas and the application interface.

The gesture tutorial appears automatically when the application starts.

## Controls

### Drawing hand

By default, the **right hand** is used for drawing.

| Action | Gesture |
|---|---|
| Move the cursor | Move your hand |
| Draw | Pinch your thumb and index finger together, then move |
| Click a button | Pinch while the cursor is over the button |
| Drag a slider | Pinch on the slider and move your hand |

The cursor is positioned between the tip of your thumb and the tip of your index finger.

### Command hand

By default, the **left hand** is used for commands.

Make a fist to arm the command hand, then perform one of the following gestures:

| Gesture | Action |
|---|---|
| One finger | Undo |
| Two fingers | Redo |
| Three fingers | Select brush |
| Four fingers | Select eraser |
| OK gesture | Toggle colour panel |

The command hand is temporarily ignored while the drawing hand is drawing a stroke.

### Keyboard shortcuts

| Key | Action |
|---|---|
| `H` | Open or close the tutorial |
| `SPACE` | Close the tutorial |
| `ENTER` | Close the tutorial |
| `ESC` | Close the tutorial |
| `S` | Save the drawing as a PNG |
| `Q` | Quit the application |

Saved drawings are named `paint_<timestamp>.png` and written to the current working directory.

## Interface

### Toolbar

The toolbar provides access to the main tools and actions.

| Button | Effect |
|---|---|
| Brush | Selects the brush |
| Fill | Selects the flood-fill tool |
| Eraser | Selects the eraser |
| Undo | Reverts the last action |
| Redo | Restores the last reverted action |
| Colors | Opens the colour panel |
| Save | Saves the current drawing |

### Layers

The layer panel allows you to manage your drawing in separate layers.

Available actions:

- **New layer:** creates a new layer.
- **Delete layer:** deletes the active layer.
- **Previous / Next:** switches between layers.
- **Toggle eye:** shows or hides the active layer.
- **Layer selection:** select a layer from the layer list.

The layer system supports up to five layers.

### Colour panel

The colour panel contains:

- An HSV colour wheel.
- A brightness slider.
- A brush size slider.
- An opacity slider.
- A preview of the current colour.
- A history of the five most recently used colours.

Pinch a colour on the wheel or in the colour history to select it.

Pinching outside the panel closes it. While the panel is open, drawing on the canvas is disabled.

## How It Works

### Hand tracking

MediaPipe detects hand landmarks from the webcam feed. The application uses these landmarks to identify the drawing hand and the command hand.

The default drawing hand is configured with `DRAW_SIDE = "right"` in `HandPaint.py`.

### Pinch detection

The distance between the thumb tip (landmark 4) and index tip (landmark 8) is divided by the distance between the wrist and the middle-finger base.

This normalisation makes pinch detection less dependent on the distance between your hand and the camera.

Two thresholds are used:
- `PINCH_ON`: starts a pinch.
- `PINCH_OFF`: ends a pinch.

This hysteresis prevents the pinch state from flickering.

### Cursor smoothing

The cursor is positioned at the midpoint between the thumb tip and index tip.

An exponential smoothing filter reduces cursor jitter.

### Click versus draw

The application decides whether a pinch is a click or a drawing action when the pinch starts.

- If the interface handles the interaction, the pinch is used for a button, slider, or colour selection.
- Otherwise, the pinch starts a drawing stroke.

### Command gestures

The command hand is managed by `CommandGesture`.

A fist is required to arm the command hand before a command can be triggered.

During a drawing stroke, the command hand is disarmed to prevent accidental actions.

### Undo and redo

The application stores snapshots of the active layer before drawing strokes and fill operations.

Two history stacks are used to support undo and redo, with a maximum of 30 entries each.

## Project Structure

| File / Folder | Role |
|---|---|
| `main.py` | Application entry point |
| `HandLandMarker.py` | Base class: webcam capture, MediaPipe detection, and application loop |
| `HandPaint.py` | Hand-controlled drawing, pinch detection, command gestures, and interaction logic |
| `Ui.py` | Main UI class: tools, canvas operations, history, and interface management |
| `Brush.py` | Brush settings, including colour, thickness, and opacity |
| `Button.py` | Interactive rectangular button |
| `Slider.py` | Reusable slider with getter and setter callbacks |
| `ColorWheel.py` | HSV colour wheel |
| `Panel.py` | Colour panel containing the wheel, sliders, preview, and colour history |
| `Layer.py` | Individual drawing layer |
| `LayerStack.py` | Layer management and compositing |
| `ui/layout.py` | Responsive interface layout calculations |
| `ui/theme.py` | Interface colours and theme constants |
| `ui/drawing.py` | Drawing and flood-fill operations |
| `ui/layers_view.py` | Layer panel rendering and interaction |
| `ui/renderer.py` | Canvas and interface rendering |
| `hand_landmarker.task` | MediaPipe hand landmark model |
| `requirements.txt` | Python dependencies |

## Configuration

Gesture behaviour can be adjusted in `HandPaint.py`.

| Constant | Meaning |
|---|---|
| `DRAW_SIDE` | Selects which hand is used for drawing (`"right"` or `"left"`) |
| `PINCH_ON` | Pinch ratio below which a pinch starts |
| `PINCH_OFF` | Pinch ratio above which a pinch ends |
| `SMOOTHING` | Cursor smoothing: `1` means no smoothing; lower values produce smoother but slower movement |

The interface layout is calculated dynamically according to the camera resolution.

## Building an Executable (Windows)

The project can be packaged into a standalone application using PyInstaller.

Install PyInstaller:

```bash
pip install pyinstaller
```

Build the application:

```bash
pyinstaller --noconfirm --clean --onedir --windowed --name "HandTrackingPaint" --add-data "hand_landmarker.task;." --collect-all mediapipe --collect-all cv2 --collect-all numpy main.py
```

The executable will be generated in:

```text
dist/HandTrackingPaint/
```

Keep the entire generated folder when distributing the application, including its internal dependencies and the model file.

## Known Limitations

- The eraser paints white, so it assumes a white canvas.
- Flood fill can spread through gaps in an outline. Shapes must be fully closed for predictable results.
- Strokes are drawn without anti-aliasing to avoid a pale halo between strokes and filled areas.
- OpenCV's built-in font has limited character support, so some accented characters may not display correctly.
- Hand tracking accuracy depends on lighting, camera quality, and hand visibility.
- The application is designed for two visible hands.

## Troubleshooting

**`A module that was compiled using NumPy 1.x cannot be run in NumPy 2.x`**

Your environment contains packages built against an older NumPy version. Create a fresh environment and reinstall the dependencies.

**MediaPipe prints `inference_feedback_manager.cc` warnings**

These warnings are generally harmless and can be ignored if hand tracking works correctly.

**Black camera window or no camera detected**

The application uses camera index `0` by default. Close other applications using the webcam or change `camera_index` in `HandLandMarker.py`.

**Cannot find `hand_landmarker.task`**

Make sure the model file is in the project folder and that you launch the application from the correct directory.

**The gestures are not detected correctly**

Try improving the lighting, keeping both hands visible, and avoiding hands overlapping in the camera view.

## Roadmap

- Zoom and canvas navigation.
- Improved text rendering and typography.
- More customisable gesture controls.
- Additional drawing tools.

## Credits

Hand tracking powered by [MediaPipe](https://ai.google.dev/edge/mediapipe).

Image processing powered by [OpenCV](https://opencv.org/).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
This application uses Google MediaPipe Hand Landmarker, which is licensed under the Apache License 2.0.

