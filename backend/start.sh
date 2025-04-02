#!/bin/bash
set -e

# Démarrer Ollama en arrière-plan
ollama serve &

# Attendre que le serveur Ollama soit prêt
until curl -s http://localhost:11434 > /dev/null; do
    echo "Waiting for Ollama server to be ready..."
    sleep 5
done

# Télécharger le modèle Mistral
ollama pull mistral

# Garder le conteneur en cours d'exécution
tail -f /dev/null