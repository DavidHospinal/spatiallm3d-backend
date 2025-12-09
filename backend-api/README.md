# SpatialLM3D Backend API

Backend FastAPI para el proyecto SpatialLM3D del Kotlin Multiplatform Contest 2026.

## Arquitectura

```
KMP App (Android/iOS/Desktop)
    ↓ HTTP Request (Ktor Client)
Backend FastAPI (este servidor)
    ↓ Inference API
HuggingFace (SpatialLM model)
```

## Instalacion Local

### Opcion 1: Usando venv (recomendado)

```bash
cd backend-api

# Crear virtual environment
python -m venv .venv

# Activar (Windows PowerShell)
.\.venv\Scripts\activate

# Activar (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar token de HuggingFace
cp .env.example .env
# Editar .env y agregar tu HF_TOKEN

# Correr servidor
python main.py
```

### Opcion 2: Usando Docker

```bash
# Build imagen
docker build -t spatiallm3d-backend .

# Correr contenedor
docker run -p 8000:8000 -e HF_TOKEN=your_token spatiallm3d-backend
```

## Endpoints

### GET /
Informacion del API

### GET /health
Health check

### POST /api/v1/analyze
Analizar point cloud desde URL

Request:
```json
{
  "point_cloud_url": "https://example.com/scene.ply",
  "detect_walls": true,
  "detect_doors": true,
  "detect_windows": true,
  "detect_objects": true,
  "object_categories": ["furniture", "appliances"]
}
```

Response:
```json
{
  "scene": {
    "walls": [...],
    "doors": [...],
    "windows": [...],
    "objects": [...]
  },
  "inference_time": 2.5,
  "model_version": "SpatialLM1.1-Qwen-0.5B",
  "point_count": 50000
}
```

### POST /api/v1/analyze/file
Analizar point cloud desde archivo subido

Request: Multipart form con archivo .ply

Response: Mismo formato que /analyze

## Testing

```bash
# Test con curl
curl http://localhost:8000/health

# Test analyze endpoint
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"detect_walls": true, "detect_objects": true}'

# Test file upload
curl -X POST http://localhost:8000/api/v1/analyze/file \
  -F "file=@test.ply"
```

## Deploy a Render.com

1. Crear cuenta en https://render.com

2. Crear nuevo Web Service:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. Configurar variables de entorno:
   - `HF_TOKEN`: Tu token de HuggingFace

4. Deploy automatico desde GitHub

URL del servidor: `https://spatiallm3d-backend.onrender.com`

## Siguiente Paso

Una vez desplegado el backend, usar la URL en el cliente Ktor del proyecto KMP:

```kotlin
// shared/commonMain/data/SpatialLMClient.kt
class SpatialLMClient(private val httpClient: HttpClient) {
    private val baseUrl = "https://spatiallm3d-backend.onrender.com"

    suspend fun analyzeScene(pointCloud: PointCloud): Result<SceneStructure> {
        return httpClient.post("$baseUrl/api/v1/analyze") {
            contentType(ContentType.Application.Json)
            setBody(AnalysisRequest(...))
        }
    }
}
```

## Mejoras Futuras

- Implementar llamada real a HuggingFace Inference API
- Agregar rate limiting
- Agregar authentication (API keys)
- Implementar caching de resultados
- Agregar metrics (Prometheus)
- Implementar processing de archivos .ply grandes
- Agregar support para otros formatos (PCD, XYZ)

## Licencia

MIT License - Compatible con el Kotlin Multiplatform Contest 2026
