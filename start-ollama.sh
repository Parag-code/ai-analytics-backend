#!/bin/sh

echo "Starting Ollama..."
ollama serve &

echo "Waiting for Ollama to start..."
sleep 5

echo "Pulling model: $MODEL_NAME"
ollama pull $MODEL_NAME

echo "Ollama Ready"
wait