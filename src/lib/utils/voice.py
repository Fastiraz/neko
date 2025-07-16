#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import tempfile
import whisper


def speech_to_text(audio_bytes: bytes) -> str:
  """
  Convert audio bytes into text using Whisper from OpenAI.

  :args:
  ------
    audio_bytes (bytes): Raw audio file content (e.g., from .webm or .wav)

  :return:
  --------
    str: Transcribed text.
  """
  model = whisper.load_model("tiny")
  with tempfile.NamedTemporaryFile(
    delete=False,
    suffix=".webm"
  ) as tmp:
    tmp.write(audio_bytes.read())
    tmp.flush()
    tmp_path = tmp.name
  result = model.transcribe(tmp_path)
  return result["text"]


def text_to_speech(text: str) -> None:
  """
  Generating audio from text using Dia-1.6B from Nari labs.

  :args:
  ------
    text (str): The text used to generate audio.

  :return:
  --------
    bytes: Audio stream.
  """
  raise NotImplementedError("Connect to nari-labs/Dia-1.6B TTS model here.")
