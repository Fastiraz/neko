FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  git \
  curl \
  ffmpeg \
  libgl1 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
  && pip install comfy-cli \
  && yes | comfy tracking disable

RUN yes | comfy install --cpu

RUN pip install \
  Pillow \
  torch \
  torchvision \
  torchaudio

ENV COMFYUI_ADDRESS=0.0.0.0
ENV COMFYUI_PORT=8188
ENV COMFYUI_EXTRA_ARGS=""

EXPOSE 8188

ENTRYPOINT ["python", \
  "-u", "/root/comfy/ComfyUI/main.py", \
  "--listen", "0.0.0.0", \
  "--port", "8188", \
  "--cpu"]
