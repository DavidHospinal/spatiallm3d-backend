# Mock Data Directory

This directory contains pre-computed analysis results from SpatialLM model inference.

## Structure

Each JSON file corresponds to a PLY file from the test dataset:

```
scene0000_00_results.json  -> scene0000_00.ply (Dining room)
scene0001_00_results.json  -> scene0001_00.ply (Bedroom)
scene0002_00_results.json  -> scene0002_00.ply (Living room)
scene0003_00_results.json  -> scene0003_00.ply (Office)
```

## JSON Format

Each file contains:

```json
{
  "walls": [
    {
      "id": "wall_0",
      "start_x": 0.0,
      "start_y": 0.0,
      "start_z": 0.0,
      "end_x": 5.0,
      "end_y": 0.0,
      "end_z": 0.0,
      "height": 2.7
    }
  ],
  "doors": [
    {
      "id": "door_0",
      "wall_id": "wall_0",
      "position_x": 2.5,
      "position_y": 0.0,
      "position_z": 0.0,
      "width": 0.9,
      "height": 2.1
    }
  ],
  "windows": [...],
  "objects": [
    {
      "id": "bbox_0",
      "object_class": "sofa",
      "position_x": 1.5,
      "position_y": 2.0,
      "position_z": 0.4,
      "rotation_z": 0.0,
      "scale_x": 2.0,
      "scale_y": 0.9,
      "scale_z": 0.8,
      "confidence": 0.95
    }
  ]
}
```

## How to Generate New Files

Run SpatialLM inference in Google Colab (see notebook), then convert output:

```bash
python utils/precompute_results.py \
  --input results/scene0004_00.txt \
  --output mock_data/scene0004_00_results.json \
  --pretty
```

## Contest Strategy

For the Kotlin Multiplatform Contest 2026, we pre-compute results to avoid needing GPU inference in production. This ensures instant response times and reliable demos.
