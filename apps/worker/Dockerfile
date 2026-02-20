# GPU worker: optional embedding service (sentence-transformers + CUDA).
# Build: docker build -f apps/worker/Dockerfile -t liveproof-worker .
# Run on LKE with NVIDIA device plugin and GPU node pool.
FROM nvidia/cuda:12.1-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3 python3-pip curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY apps/worker/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY apps/worker/ .

EXPOSE 8080
CMD ["python3", "server.py"]
