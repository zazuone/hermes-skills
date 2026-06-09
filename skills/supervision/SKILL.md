---
name: supervision
description: Use when working with object detection, segmentation, classification, or tracking results from any CV model (YOLO, Transformers, MMDetection). Roboflow Supervision provides model-agnostic tools — unified Detections format, 30+ annotators, zone counting, line crossing, ByteTrack tracking, dataset IO, and video processing. pip install supervision.
triggers:
  - supervision
  - object detection
  - 目标检测
  - YOLO
  - computer vision
  - cv annotation
  - detection visualization
  - zone counting
  - tracking
---

# Roboflow Supervision

**Model-agnostic computer vision toolbox.** Takes detection/segmentation/classification outputs from any model and provides unified tools for annotation, counting, tracking, dataset management, and video processing.

`pip install supervision`

## One-Liner Philosophy

```python
import supervision as sv
```

Then: convert model output → `sv.Detections` → use any tool in the library.

## Core: `sv.Detections`

The universal detection format. Convert from any model:

```python
# Ultralytics YOLO
result = model(image)[0]
detections = sv.Detections.from_ultralytics(result)

# HuggingFace Transformers
detections = sv.Detections.from_transformers(result)

# MMDetection
detections = sv.Detections.from_mmdetection(result)

# SAHI sliced inference
detections = sv.Detections.from_sahi(result)

# Manual construction
import numpy as np
detections = sv.Detections(
    xyxy=np.array([[100, 100, 200, 200], [300, 300, 400, 400]]),  # N×4
    confidence=np.array([0.95, 0.80]),
    class_id=np.array([0, 1])
)
```

**Key fields:**
- `xyxy` — bounding boxes (N×4, [x1,y1,x2,y2])
- `mask` — segmentation masks (N×H×W, optional)
- `confidence` — confidence scores (N, optional)
- `class_id` — class IDs (N, optional)
- `tracker_id` — tracking IDs (N, used after tracking)
- `data` — extra metadata dict

**Filtering:**
```python
# By confidence
detections = detections[detections.confidence > 0.5]

# By class
detections = detections[detections.class_id == 0]
detections = detections[np.isin(detections.class_id, [0, 2, 3])]
```

## Annotators (30+)

All follow the same pattern: create annotator → call `.annotate(scene, detections)`.

```python
# Setup
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()
mask_annotator = sv.MaskAnnotator()

# Apply in sequence
annotated = box_annotator.annotate(scene=image, detections=detections)
annotated = label_annotator.annotate(scene=annotated, detections=detections)
```

**Most useful annotators:**

| Annotator | What it does |
|-----------|-------------|
| `BoxAnnotator` | Draw bounding boxes |
| `MaskAnnotator` | Draw segmentation masks |
| `LabelAnnotator` | Add class name + confidence labels |
| `RichLabelAnnotator` | Labels with custom text/color/position |
| `RoundBoxAnnotator` | Rounded corner boxes |
| `DotAnnotator` | Mark center points |
| `CircleAnnotator` | Draw circles around objects |
| `EllipseAnnotator` | Ellipses (good for people) |
| `TriangleAnnotator` | Triangle markers |
| `PolygonAnnotator` | Draw polygon outlines |
| `EdgeAnnotator` | Edge outlines |
| `HaloAnnotator` | Glow effect behind boxes |
| `HeatMapAnnotator` | Heatmap overlay |
| `ColorAnnotator` | Color-coded boxes by class |
| `PercentageBarAnnotator` | Confidence bar under box |
| `PixelateAnnotator` | Pixelate detected regions (privacy) |
| `BlurAnnotator` | Blur detected regions (privacy) |
| `CropAnnotator` | Crop out detections |
| `IconAnnotator` | Emoji/icon overlay |
| `TraceAnnotator` | Draw trails/lines for tracked objects |
| `VertexAnnotator` | Mark polygon vertices |
| `VertexLabelAnnotator` | Label polygon vertices |
| `ComparisonAnnotator` | Side-by-side comparison |
| `BackgroundOverlayAnnotator` | Dim/color overlay outside detections |
| `OrientedBoxAnnotator` | Oriented (rotated) bounding boxes |
| `LineZoneAnnotator` | Count lines + crossing visualization |

**Custom colors:**
```python
from supervision.draw.color import Color, ColorPalette

box_annotator = sv.BoxAnnotator(
    color=Color.RED,                # single color for all
    color_lookup=sv.ColorLookup.INDEX  # per-class color from palette
)

# Custom palette
custom_palette = ColorPalette([Color.RED, Color.GREEN, Color.BLUE])
```

## Zone Counting

Count objects inside a polygon zone:

```python
# Define a polygon (e.g. a store shelf area)
polygon = np.array([[100, 100], [500, 100], [500, 400], [100, 400]])
zone = sv.PolygonZone(polygon=polygon)

# Count detections inside the zone
count = zone.trigger(detections=detections)
print(f"Objects in zone: {count}")

# Visualize the zone
zone_annotator = sv.PolygonZoneAnnotator(zone=zone)
annotated = zone_annotator.annotate(scene=image)
```

## Line Crossing

Count objects crossing a line (e.g. people entering/exiting):

```python
# Define a line
line = sv.LineZone(start=(100, 300), end=(700, 300))

# Process each frame
for detections in detections_stream:
    crossed_in, crossed_out = line.trigger(detections=detections)
    # line.in_count, line.out_count auto-updated

# Visualize
line_annotator = sv.LineZoneAnnotator()
annotated = line_annotator.annotate(scene=frame, line_counter=line)
```

## Object Tracking (ByteTrack)

Built-in ByteTrack for tracking across frames:

```python
tracker = sv.ByteTrack()

# For each frame:
detections = sv.Detections.from_ultralytics(result)
detections = tracker.update_with_detections(detections)
# Now detections.tracker_id is populated (None for new objects)
```

**Smoother** — remove jitter:
```python
smoother = sv.DetectionsSmoother()
detections = smoother.update_with_detections(detections)
```

**TraceAnnotator** — draw movement trails:
```python
trace_annotator = sv.TraceAnnotator()
annotated = trace_annotator.annotate(scene=frame, detections=detections)
```

## Dataset IO

Load/save datasets in standard formats:

```python
# COCO format
dataset = sv.DetectionDataset.from_coco(
    images_directory_path="./images/",
    annotations_path="./annotations.json"
)

# YOLO format
dataset = sv.DetectionDataset.from_yolo(
    images_directory_path="./images/",
    annotations_directory_path="./labels/"
)

# Save as COCO
dataset.as_coco(annotations_path="./export/annotations.json")

# Iterate
for image_path, image, annotations in dataset:
    print(f"{image_path}: {len(annotations)} objects")
```

Classification datasets too:
```python
dataset = sv.ClassificationDataset.from_folder(
    root_path="./dataset/"  # each subfolder = class
)
```

## Video Processing

Process video frame by frame with automatic progress display:

```python
# Read
video_info = sv.VideoInfo.from_video_path("input.mp4")
print(f"{video_info.width}x{video_info.height}, {video_info.fps} fps")

# Write with generator pattern
with sv.VideoSink("output.mp4", video_info=video_info) as sink:
    for frame in sv.get_video_frames_generator("input.mp4"):
        # Process frame...
        result = model(frame)[0]
        detections = sv.Detections.from_ultralytics(result)
        annotated = box_annotator.annotate(scene=frame, detections=detections)
        sink.write_frame(annotated)
```

**Frame slicing** — sample frames:
```python
# Every 30th frame
generator = sv.get_video_frames_generator("input.mp4", stride=30)
for frame in generator:
    process(frame)
```

**Image/video sinks:**
```python
# Save individual frames
sink = sv.ImageSink(target_dir="./output/")
sink.save(frame, filename="frame_001.jpg")

# CSV export of detections
csv_sink = sv.CSVSink()
csv_sink.append(detections, {"frame": frame_id})
csv_sink.flush()  # write to disk
```

## Full Pipeline Example

```python
import cv2
import supervision as sv
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
tracker = sv.ByteTrack()
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()
video_info = sv.VideoInfo.from_video_path("input.mp4")

with sv.VideoSink("output_tracked.mp4", video_info=video_info) as sink:
    for frame in sv.get_video_frames_generator("input.mp4"):
        result = model(frame)[0]
        detections = sv.Detections.from_ultralytics(result)
        detections = detections[detections.confidence > 0.3]
        detections = tracker.update_with_detections(detections)

        annotated = box_annotator.annotate(scene=frame, detections=detections)
        annotated = label_annotator.annotate(
            scene=annotated,
            detections=detections,
            labels=[f"#{tracker_id}" for tracker_id in detections.tracker_id]
        )
        sink.write_frame(annotated)
```

## Tips

- **Model-agnostic**: Works with ANY model that outputs boxes/masks. Use `from_*` methods or construct `Detections` manually.
- **Stack annotators**: Call multiple annotators in sequence on the same frame.
- **Tracker + zone**: Combine ByteTrack + PolygonZone to track how long objects stay in an area.
- **Performance**: For real-time video, pre-filter detections (by confidence, by class) before annotating.
- **Accent colors**: `sv.ColorPalette.DEFAULT` has 10 colors. Use `ColorLookup.CLASS` for per-class, `ColorLookup.TRACK` for per-track.

## Pitfalls

- **OpenCV BGR vs RGB**: Supervision uses BGR (OpenCV default). If you load images with `cv2.imread()`, colors are correct. If using `matplotlib.imread()`, convert: `cv2.cvtColor(img, cv2.COLOR_RGB2BGR)`.
- **Large videos**: Loading entire video into memory will OOM. Always use the generator pattern with `sv.get_video_frames_generator()`.
- **BYTETracker IDs reset**: Tracker IDs are not persistent across different `ByteTrack` instances. Don't compare IDs from different sessions.
- **PolygonZone with complex shapes**: Self-intersecting polygons may give incorrect counts. Keep polygons simple and convex when possible.

## Reference

- Docs: https://supervision.roboflow.com
- GitHub: https://github.com/roboflow/supervision
- Notebooks: https://github.com/roboflow/notebooks
