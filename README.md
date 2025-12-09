# SpatialLM3D

**Proyecto para Kotlin Multiplatform Contest 2026**

Aplicacion multiplataforma (Android/iOS/Desktop) que utiliza IA para analizar escenas 3D en tiempo real mediante AR/VR, detectando elementos arquitectonicos (muros, puertas, ventanas) y objetos con bounding boxes 3D.

## Estado del Proyecto

Backend FastAPI completado y testeado localmente. Listo para deployment en Render.com y desarrollo de aplicacion KMP.

## Arquitectura

```
┌─────────────────────────────────────────┐
│   KMP App (Android/iOS/Desktop)         │
│   - Compose Multiplatform UI            │
│   - Ktor Client                         │
│   - SQLDelight (cache)                  │
│   - Koin (DI)                           │
│   - Voyager (navigation)                │
└──────────────┬──────────────────────────┘
               │ HTTP/REST
               │
┌──────────────▼──────────────────────────┐
│   Backend FastAPI (Render.com)          │
│   - FastAPI framework                   │
│   - Mock responses (MVP)                │
│   - Auto-documentation (/docs)          │
└──────────────┬──────────────────────────┘
               │ Inference API (Future)
               │
┌──────────────▼──────────────────────────┐
│   HuggingFace SpatialLM Model           │
│   - SpatialLM1.1-Qwen-0.5B              │
│   - Post-concurso                       │
└─────────────────────────────────────────┘
```

## Estructura del Proyecto

```
spatiallm3d/
├── backend-api/                 # Backend FastAPI
│   ├── main.py                  # Servidor FastAPI
│   ├── requirements.txt         # Dependencias Python
│   ├── Dockerfile              # Para deploy
│   ├── test_api.py             # Tests
│   └── README.md               # Documentacion del backend
└── kmp-app/                    # Proyecto KMP (en desarrollo)
    ├── shared/                 # Codigo compartido
    ├── androidApp/             # App Android
    ├── iosApp/                 # App iOS
    └── desktopApp/             # App Desktop
```

## Quick Start

### 1. Probar Backend Localmente

```powershell
cd backend-api

# Crear y activar venv
python -m venv .venv
.\.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Correr servidor
python main.py
```

En otra terminal:
```powershell
cd backend-api
.\.venv\Scripts\activate
python test_api.py
```

### 2. Deploy Backend a Render

1. Crear Web Service en Render.com
2. Conectar repositorio GitHub
3. Configuracion:
   - Root Directory: `backend-api`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy y verificar en URL asignada

### 3. Inicializar Proyecto KMP

Utilizar Kotlin Multiplatform Wizard (https://kmp.jetbrains.com/) con las siguientes configuraciones:
- Platforms: Android, iOS, Desktop
- UI Framework: Compose Multiplatform
- Dependencies: Ktor Client, SQLDelight, Koin, Voyager Navigation

## Recursos HuggingFace

El proyecto utiliza recursos del modelo SpatialLM:

- **Modelo:** [SpatialLM1.1-Qwen-0.5B](https://huggingface.co/manycore-research/SpatialLM1.1-Qwen-0.5B)
- **Dataset:** [SpatialLM-Dataset](https://huggingface.co/datasets/manycore-research/SpatialLM-Dataset) (12,328 escenas)
- **Testset:** [SpatialLM-Testset](https://huggingface.co/datasets/manycore-research/SpatialLM-Testset) (107 casos)

**Nota:** El MVP del concurso utiliza respuestas mock para demostrar la arquitectura multiplataforma. La integracion del modelo real se implementara posteriormente.

## Tecnologias

### Backend
- FastAPI
- Uvicorn
- Python 3.11+
- HuggingFace (futuro)

### KMP App
- Kotlin Multiplatform
- Compose Multiplatform
- Ktor Client
- SQLDelight
- Koin
- Voyager Navigation
- ARCore (Android)
- ARKit (iOS)

### Deploy
- Render.com (backend)
- GitHub (CI/CD)

## Endpoints API

**Base URL:** `https://spatiallm3d-backend.onrender.com` (cuando este deployado)

| Endpoint | Metodo | Descripcion |
|----------|--------|-------------|
| `/` | GET | Info del API |
| `/health` | GET | Health check |
| `/api/v1/analyze` | POST | Analizar point cloud |
| `/api/v1/analyze/file` | POST | Analizar archivo .ply |
| `/docs` | GET | Documentacion Swagger |

Consultar `backend-api/README.md` para ejemplos detallados de uso.

## Licencia

MIT License - Compatible con Kotlin Multiplatform Contest 2026
