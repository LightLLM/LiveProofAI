"""
LiveProof AI – optional GPU worker (embedding service).
Logs GPU utilization when run with nvidia.com/gpu. Without sentence-transformers this is a stub.
"""
import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

try:
    import torch
    HAS_TORCH = True
    HAS_CUDA = torch.cuda.is_available()
except Exception:
    HAS_TORCH = False
    HAS_CUDA = False


@app.route("/health", methods=["GET"])
def health():
    gpu_info = {}
    if HAS_TORCH and HAS_CUDA:
        gpu_info = {
            "cuda_available": True,
            "device_count": torch.cuda.device_count(),
            "device_name": torch.cuda.get_device_name(0) if torch.cuda.device_count() else None,
        }
    else:
        gpu_info = {"cuda_available": HAS_CUDA, "message": "No GPU or torch not installed"}
    return jsonify({"status": "ok", "gpu": gpu_info})


@app.route("/embed", methods=["POST"])
def embed():
    """Stub: return fake embeddings. Replace with sentence-transformers + CUDA for real usage."""
    body = request.get_json() or {}
    texts = body.get("texts", [])
    if not texts:
        return jsonify({"error": "texts required"}), 400
    # Stub: 384-dim zero vector per text (sentence-transformers all-MiniLM-L6-v2 dimension)
    dim = 384
    embeddings = [[0.0] * dim for _ in texts]
    return jsonify({"embeddings": embeddings, "dim": dim, "gpu_used": HAS_CUDA})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
