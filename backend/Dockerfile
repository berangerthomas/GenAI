FROM ollama/ollama:latest

# Installation des dépendances si nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Exposer le port par défaut d'Ollama
EXPOSE 11434

# Script de démarrage pour télécharger le modèle et lancer Ollama
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Définir le point d'entrée
ENTRYPOINT ["/start.sh"]