"""
Script de testing para el backend API
Ejecutar: python test_api.py
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_root():
    """Test endpoint root"""
    print("\n1. Testing GET /")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200

def test_health():
    """Test health check"""
    print("\n2. Testing GET /health")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200

def test_analyze():
    """Test analyze endpoint"""
    print("\n3. Testing POST /api/v1/analyze")
    payload = {
        "detect_walls": True,
        "detect_doors": True,
        "detect_windows": True,
        "detect_objects": True,
        "object_categories": ["furniture", "appliances"]
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/analyze",
        json=payload
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Walls detected: {len(result['scene']['walls'])}")
    print(f"Doors detected: {len(result['scene']['doors'])}")
    print(f"Windows detected: {len(result['scene']['windows'])}")
    print(f"Objects detected: {len(result['scene']['objects'])}")
    print(f"Inference time: {result['inference_time']}s")
    print(f"Model: {result['model_version']}")
    assert response.status_code == 200

if __name__ == "__main__":
    print("=" * 60)
    print("Testing SpatialLM3D Backend API")
    print("=" * 60)

    try:
        test_root()
        test_health()
        test_analyze()

        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\nError: No se puede conectar al servidor.")
        print("Asegurate de que el servidor este corriendo:")
        print("  python main.py")
    except AssertionError as e:
        print(f"\nTest failed: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
