"""
SpatialLM3D Backend API
FastAPI server que procesa point clouds usando HuggingFace Inference API
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import tempfile
import shutil
import os
import json
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SpatialLM3D API",
    description="Backend API para analisis de escenas 3D con SpatialLM",
    version="1.0.0"
)

# CORS para permitir requests desde app KMP
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En produccion, especificar origenes exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de datos (basados en paper SpatialLM + compatible con Kotlin models)
class Point3D(BaseModel):
    x: float
    y: float
    z: float

class Wall(BaseModel):
    id: str
    startPoint: Point3D
    endPoint: Point3D
    height: float

class Door(BaseModel):
    id: str
    wallId: str
    position: Point3D
    width: float
    height: float

class Window(BaseModel):
    id: str
    wallId: str
    position: Point3D
    width: float
    height: float

class BoundingBox(BaseModel):
    id: str
    objectClass: str
    position: Point3D
    rotation: float
    scale: Point3D
    confidence: float = 1.0

class SceneStructure(BaseModel):
    walls: List[Wall]
    doors: List[Door]
    windows: List[Window]
    objects: List[BoundingBox]

class AnalysisRequest(BaseModel):
    point_cloud_url: Optional[str] = None
    detect_walls: bool = True
    detect_doors: bool = True
    detect_windows: bool = True
    detect_objects: bool = True
    object_categories: Optional[List[str]] = None

class AnalysisResponse(BaseModel):
    scene: SceneStructure
    inference_time: float
    model_version: str
    point_count: int

# Health check
@app.get("/")
async def root():
    return {
        "name": "SpatialLM3D API",
        "version": "1.0.0",
        "status": "running",
        "model": "SpatialLM1.1-Qwen-0.5B",
        "endpoints": {
            "health": "/health",
            "analyze": "/api/v1/analyze (POST)",
            "analyze_file": "/api/v1/analyze/file (POST)",
            "precomputed": "/api/v1/precomputed/{scene_id} (GET)"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint para monitoring"""
    return {"status": "healthy"}

def list_available_scenes() -> List[str]:
    """List all available pre-computed scenes."""
    mock_data_dir = Path(__file__).parent / "mock_data"
    if not mock_data_dir.exists():
        return []
    json_files = mock_data_dir.glob("*_results.json")
    return [f.stem.replace("_results", "") for f in json_files]

@app.get("/api/v1/precomputed/{scene_id}")
async def get_precomputed_result(scene_id: str):
    """
    Get pre-computed analysis results by scene ID.

    This endpoint allows the KMP app to fetch results by filename
    without uploading the entire PLY file.

    Args:
        scene_id: Scene identifier without .ply extension (e.g., "scene0000_00")

    Returns:
        AnalysisResponse with pre-computed data

    Example:
        GET /api/v1/precomputed/scene0000_00
    """
    logger.info(f"Fetching pre-computed results for: {scene_id}")

    # Add .ply extension for lookup
    filename = f"{scene_id}.ply"
    scene = load_precomputed_results(filename)

    if scene is None:
        logger.warning(f"No pre-computed results found for: {scene_id}")
        available_scenes = list_available_scenes()
        raise HTTPException(
            status_code=404,
            detail=f"No pre-computed results available for scene: {scene_id}. "
                   f"Available scenes: {available_scenes}"
        )

    return AnalysisResponse(
        scene=scene,
        inference_time=0.05,
        model_version="SpatialLM1.1-Qwen-0.5B (pre-computed)",
        point_count=50000
    )

@app.post("/api/v1/analyze")
async def analyze_scene(request: AnalysisRequest):
    """
    Analiza point cloud desde URL y retorna estructura 3D

    NOTA: Por ahora retorna datos mock hasta que configuremos HuggingFace API
    """
    logger.info(f"Analyzing scene with options: {request}")

    # TODO: Implementar llamada real a HuggingFace API
    # Por ahora, retornamos datos de ejemplo (mock)

    mock_scene = SceneStructure(
        walls=[
            Wall(
                id="wall_0",
                startPoint=Point3D(x=0.0, y=0.0, z=0.0),
                endPoint=Point3D(x=5.0, y=0.0, z=0.0),
                height=2.5
            ),
            Wall(
                id="wall_1",
                startPoint=Point3D(x=5.0, y=0.0, z=0.0),
                endPoint=Point3D(x=5.0, y=4.0, z=0.0),
                height=2.5
            ),
            Wall(
                id="wall_2",
                startPoint=Point3D(x=5.0, y=4.0, z=0.0),
                endPoint=Point3D(x=0.0, y=4.0, z=0.0),
                height=2.5
            ),
            Wall(
                id="wall_3",
                startPoint=Point3D(x=0.0, y=4.0, z=0.0),
                endPoint=Point3D(x=0.0, y=0.0, z=0.0),
                height=2.5
            )
        ],
        doors=[
            Door(
                id="door_0",
                wallId="wall_0",
                position=Point3D(x=2.5, y=0.0, z=0.0),
                width=0.9,
                height=2.1
            )
        ],
        windows=[
            Window(
                id="window_0",
                wallId="wall_1",
                position=Point3D(x=5.0, y=2.0, z=1.0),
                width=1.2,
                height=1.5
            )
        ],
        objects=[
            BoundingBox(
                id="bbox_0",
                objectClass="sofa",
                position=Point3D(x=1.5, y=2.0, z=0.5),
                rotation=0.0,
                scale=Point3D(x=2.0, y=0.9, z=0.8),
                confidence=0.95
            ),
            BoundingBox(
                id="bbox_1",
                objectClass="coffee_table",
                position=Point3D(x=2.5, y=2.5, z=0.4),
                rotation=0.0,
                scale=Point3D(x=1.2, y=0.6, z=0.45),
                confidence=0.89
            )
        ]
    )

    return AnalysisResponse(
        scene=mock_scene,
        inference_time=2.5,
        model_version="SpatialLM1.1-Qwen-0.5B (mock)",
        point_count=50000
    )

def load_precomputed_results(filename: str) -> Optional[SceneStructure]:
    """
    Load pre-computed analysis results from JSON file.

    Args:
        filename: Name of the PLY file (e.g., "scene0000_00.ply")

    Returns:
        SceneStructure if pre-computed data exists, None otherwise
    """
    # Extract scene ID from filename (e.g., "scene0000_00" from "scene0000_00.ply")
    scene_id = filename.replace('.ply', '')
    json_path = Path(__file__).parent / "mock_data" / f"{scene_id}_results.json"

    logger.info(f"Looking for pre-computed results at: {json_path}")

    if not json_path.exists():
        logger.warning(f"No pre-computed results found for: {filename}")
        return None

    try:
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Convert JSON to SceneStructure
        walls = [Wall(**w) for w in data.get('walls', [])]
        doors = [Door(**d) for d in data.get('doors', [])]
        windows = [Window(**w) for w in data.get('windows', [])]
        objects = [BoundingBox(**obj) for obj in data.get('objects', [])]

        logger.info(f"Loaded pre-computed results: {len(walls)} walls, {len(doors)} doors, {len(windows)} windows, {len(objects)} objects")

        return SceneStructure(
            walls=walls,
            doors=doors,
            windows=windows,
            objects=objects
        )

    except Exception as e:
        logger.error(f"Error loading pre-computed results: {e}")
        return None


@app.post("/api/v1/analyze/file")
async def analyze_scene_file(file: UploadFile = File(...)):
    """
    Analiza point cloud desde archivo .ply subido.

    Strategy: Uses pre-computed results if available (contest demo mode),
    otherwise returns default mock data.
    """
    logger.info(f"Received file: {file.filename}")

    # Validar extension
    if not file.filename.endswith('.ply'):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .ply")

    # Guardar archivo temporalmente
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ply") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name

        logger.info(f"File saved temporarily at: {tmp_path}")

        # Load pre-computed results if available
        scene = load_precomputed_results(file.filename)

        if scene is None:
            # Fallback to default mock data
            logger.info("Using fallback mock data")
            scene = SceneStructure(
                walls=[
                    Wall(
                        id="wall_0",
                        startPoint=Point3D(x=0.0, y=0.0, z=0.0),
                        endPoint=Point3D(x=5.0, y=0.0, z=0.0),
                        height=2.5
                    )
                ],
                doors=[],
                windows=[],
                objects=[
                    BoundingBox(
                        id="bbox_0",
                        objectClass="unknown",
                        position=Point3D(x=2.5, y=2.0, z=0.5),
                        rotation=0.0,
                        scale=Point3D(x=1.0, y=1.0, z=1.0),
                        confidence=0.5
                    )
                ]
            )

        # Limpiar archivo temporal
        os.unlink(tmp_path)

        return AnalysisResponse(
            scene=scene,
            inference_time=0.05,  # Instant with pre-computed data
            model_version="SpatialLM1.1-Qwen-0.5B (pre-computed)",
            point_count=50000
        )

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
