#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from ..mcp.client import MCPClient
from ..utils.voice import speech_to_text
from config.constants import ConstantConfig
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware


logger = logging.getLogger(__name__)
app = FastAPI()
origins = [
  "http://localhost:3000",
]
app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,  # or ["*"] to allow all (dev only)
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)


@app.post("/api/v1/chat")
async def chat(request: Request):
  body = await request.json()
  logger.info(f"HTTP Request body: {body}")
  prompt = body.get("prompt", "").strip()
  if not prompt:
    return {"error": "Prompt is required."}
  logger.info(f"HTTP Request body prompt: {prompt}")
  mcp_client = MCPClient()
  try:
    await mcp_client.connect_to_server(
      str(ConstantConfig.MCP_SERVER_PATH)
    )
    response = await mcp_client.query(prompt)
    return {"response": response[-1]['content']}
  except TypeError as e:
    if str(e) == "string indices must be integers, not 'str'":
      return {"error": "Invalid response format from chat API."}
    else:
      return (f"Error chat API: {e}")
  except Exception as e:
    return {"response": e}
  finally:
    await mcp_client.cleanup()


@app.post("/api/v1/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
  audio_bytes = await file.read()
  result = speech_to_text(audio_bytes)
  return result


if __name__ == "__main__":
  raise Exception("This script should not be run as main.")
