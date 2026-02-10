#!/bin/bash
# pull_ollama_models.sh
# Télécharge les modèles nécessaires dans le conteneur Ollama

set -e

echo "⏳ Téléchargement de Llama 3.2 (LLM principal)..."
docker exec ollama ollama pull llama3.2

echo "⏳ Téléchargement de nomic-embed-text (embeddings)..."
docker exec ollama ollama pull nomic-embed-text

echo "✅ Modèles prêts !"
docker exec ollama ollama list
