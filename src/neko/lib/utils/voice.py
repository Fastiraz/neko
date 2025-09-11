#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import tempfile
import whisper
from typing import Union


def speech_to_text(audio_bytes: bytes) -> dict:
  """
  Convert audio bytes to text using Whisper Tiny model.

  Args:
    audio_bytes (bytes): Audio file content in bytes (e.g. mp3 or wav).

  Returns:
    dict: {
      'language': Detected language (e.g., 'en'),
      'transcription': Transcribed text
    } or error message.
  """
  try:
    with tempfile.NamedTemporaryFile(suffix=".mp3") as tmp:
      tmp.write(audio_bytes)
      tmp.flush()
      model = whisper.load_model("tiny")
      result = model.transcribe(tmp.name)
      return {
        "language": result.get("language"),
        "transcription": result.get("text", "").strip()
      }
  except Exception as e:
    return {
      "error": f"An error occurred during transcription: {str(e)}"
    }


def text_to_speech(text: str) -> Union[bytes, None]:
  """Convert text to speech and return audio bytes.

  Args:
    text (str): The input text to convert to speech.

  Returns:
    bytes: Audio file content in memory (e.g., .mp3 or .wav).
    None: If not implemented yet.
  """
  # TODO: Implement Text-to-Speech using Bark or DIA
  return None
