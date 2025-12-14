"""
Utility script to convert SpatialLM raw output to structured JSON format.

This script parses the Python-style output from SpatialLM model and converts it
into clean JSON files that the FastAPI backend can serve instantly.

Usage:
    python utils/precompute_results.py --input results/scene0000_00.txt --output mock_data/scene0000_00_results.json

Input format (SpatialLM output):
    bbox_0=Bbox(sofa, 3.2, 5.7, 0.4, 1.57, 2.3, 0.9, 0.8)
    wall_0=Wall(1.2, 3.4, 0.0, 5.6, 3.4, 0.0, 2.7)
    door_0=Door(wall_0, 2.5, 0.0, 0.0, 0.9, 2.1)

Output format (JSON):
    {
        "walls": [...],
        "doors": [...],
        "windows": [...],
        "objects": [...]
    }
"""

import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class Point3D:
    x: float
    y: float
    z: float


@dataclass
class Wall:
    id: str
    start_x: float
    start_y: float
    start_z: float
    end_x: float
    end_y: float
    end_z: float
    height: float


@dataclass
class Door:
    id: str
    wall_id: str
    position_x: float
    position_y: float
    position_z: float
    width: float
    height: float


@dataclass
class Window:
    id: str
    wall_id: str
    position_x: float
    position_y: float
    position_z: float
    width: float
    height: float


@dataclass
class BoundingBox:
    id: str
    object_class: str
    position_x: float
    position_y: float
    position_z: float
    rotation_z: float
    scale_x: float
    scale_y: float
    scale_z: float
    confidence: float = 0.95


def parse_bbox_line(line: str, bbox_id: str) -> BoundingBox:
    """
    Parse a bbox line from SpatialLM output.

    Format: bbox_0=Bbox(sofa, 3.2, 5.7, 0.4, 1.57, 2.3, 0.9, 0.8)
    Args: (label, center_x, center_y, center_z, rotation_z, scale_x, scale_y, scale_z)
    """
    pattern = r'Bbox\(([^,]+),\s*([\d.-]+),\s*([\d.-]+),\s*([\d.-]+),\s*([\d.-]+),\s*([\d.-]+),\s*([\d.-]+),\s*([\d.-]+)\)'
    match = re.search(pattern, line)

    if not match:
        raise ValueError(f"Could not parse bbox line: {line}")

    label = match.group(1).strip()
    values = [float(match.group(i)) for i in range(2, 9)]

    return BoundingBox(
        id=bbox_id,
        object_class=label,
        position_x=values[0],
        position_y=values[1],
        position_z=values[2],
        rotation_z=values[3],
        scale_x=values[4],
        scale_y=values[5],
        scale_z=values[6],
        confidence=0.95  # Default confidence
    )


def parse_wall_line(line: str, wall_id: str) -> Wall:
    """
    Parse a wall line from SpatialLM output.

    Format: wall_0=Wall(start_x, start_y, start_z, end_x, end_y, end_z, height)
    """
    pattern = r'Wall\(([\d.-]+),\s*([\d.-]+),\s*([\d.-]+),\s*([\d.-]+),\s*([\d.-]+),\s*([\d.-]+),\s*([\d.-]+)\)'
    match = re.search(pattern, line)

    if not match:
        raise ValueError(f"Could not parse wall line: {line}")

    values = [float(match.group(i)) for i in range(1, 8)]

    return Wall(
        id=wall_id,
        start_x=values[0],
        start_y=values[1],
        start_z=values[2],
        end_x=values[3],
        end_y=values[4],
        end_z=values[5],
        height=values[6]
    )


def parse_door_line(line: str, door_id: str) -> Door:
    """
    Parse a door line from SpatialLM output.

    Format: door_0=Door(wall_id, pos_x, pos_y, pos_z, width, height)
    """
    pattern = r'Door\(([^,]+),\s*([\d.-]+),\s*([\d.-]+),\s*([\d.-]+),\s*([\d.-]+),\s*([\d.-]+)\)'
    match = re.search(pattern, line)

    if not match:
        raise ValueError(f"Could not parse door line: {line}")

    wall_id = match.group(1).strip()
    values = [float(match.group(i)) for i in range(2, 7)]

    return Door(
        id=door_id,
        wall_id=wall_id,
        position_x=values[0],
        position_y=values[1],
        position_z=values[2],
        width=values[3],
        height=values[4]
    )


def parse_window_line(line: str, window_id: str) -> Window:
    """
    Parse a window line from SpatialLM output.

    Format: window_0=Window(wall_id, pos_x, pos_y, pos_z, width, height)
    """
    pattern = r'Window\(([^,]+),\s*([\d.-]+),\s*([\d.-]+),\s*([\d.-]+),\s*([\d.-]+),\s*([\d.-]+)\)'
    match = re.search(pattern, line)

    if not match:
        raise ValueError(f"Could not parse window line: {line}")

    wall_id = match.group(1).strip()
    values = [float(match.group(i)) for i in range(2, 7)]

    return Window(
        id=window_id,
        wall_id=wall_id,
        position_x=values[0],
        position_y=values[1],
        position_z=values[2],
        width=values[3],
        height=values[4]
    )


def convert_to_json(input_file: Path) -> Dict[str, Any]:
    """
    Convert SpatialLM text output to structured JSON.

    Args:
        input_file: Path to the .txt file with SpatialLM output

    Returns:
        Dictionary with walls, doors, windows, and objects
    """
    walls = []
    doors = []
    windows = []
    objects = []

    with open(input_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Extract ID and type
            if '=' in line:
                var_name, _ = line.split('=', 1)
                var_name = var_name.strip()

                # Determine type and parse
                if var_name.startswith('bbox_'):
                    obj = parse_bbox_line(line, var_name)
                    objects.append(asdict(obj))

                elif var_name.startswith('wall_'):
                    wall = parse_wall_line(line, var_name)
                    walls.append(asdict(wall))

                elif var_name.startswith('door_'):
                    door = parse_door_line(line, var_name)
                    doors.append(asdict(door))

                elif var_name.startswith('window_'):
                    window = parse_window_line(line, var_name)
                    windows.append(asdict(window))

    return {
        "walls": walls,
        "doors": doors,
        "windows": windows,
        "objects": objects
    }


def main():
    parser = argparse.ArgumentParser(
        description='Convert SpatialLM output to JSON format'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Input .txt file with SpatialLM output'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output .json file path'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print JSON output'
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return 1

    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert and save
    print(f"Processing: {input_path}")
    result = convert_to_json(input_path)

    print(f"Found:")
    print(f"  - {len(result['walls'])} walls")
    print(f"  - {len(result['doors'])} doors")
    print(f"  - {len(result['windows'])} windows")
    print(f"  - {len(result['objects'])} objects")

    with open(output_path, 'w') as f:
        if args.pretty:
            json.dump(result, f, indent=2)
        else:
            json.dump(result, f)

    print(f"Saved to: {output_path}")
    return 0


if __name__ == "__main__":
    exit(main())
