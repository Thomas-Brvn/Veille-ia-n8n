# RAG Chatbot - Avis Amazon

Chatbot intelligent utilisant la technique **RAG** (Retrieval-Augmented Generation) pour répondre aux questions sur des produits Amazon en s'appuyant sur les avis clients réels.

Entièrement orchestré par **n8n**, propulsé par **Llama 3.2** via Ollama, avec **Qdrant** comme base vectorielle.

## Architecture

```
   Question utilisateur
          │
          ▼
   ┌─────────────┐     ┌──────────────┐     ┌──────────────┐
   │  Webhook     │────▶│  Embedding   │────▶│  Recherche   │
   │  n8n /chat   │     │  (Ollama)    │     │  (Qdrant)    │
   └─────────────┘     └──────────────┘     └──────┬───────┘
                                                    │
                                                    ▼
                                            ┌──────────────┐
                                            │  Prompt RAG  │
                                            │  + Llama 3.2 │
                                            └──────┬───────┘
                                                    │
                                                    ▼
                                              Réponse JSON
```

## Stack technique

| Composant | Rôle |
|-----------|------|
| **n8n** | Orchestration des workflows (ingestion + chatbot) |
| **Ollama + Llama 3.2** | LLM local pour la génération de réponses |
| **Ollama + nomic-embed-text** | Modèle d'embedding pour la vectorisation |
| **Qdrant** | Base de données vectorielle |
| **Python** | Script de préparation des données |

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) et Docker Compose
- ~8 Go de RAM disponible (pour Llama 3.2)
- Un dataset d'avis Amazon (voir section Données)

## Installation

### 1. Cloner le repo

```bash
git clone https://github.com/<ton-username>/rag-amazon-reviews.git
cd rag-amazon-reviews
```

### 2. Configurer l'environnement

```bash
cp .env.example .env
# Modifier .env si besoin (ports, mots de passe)
```

### 3. Lancer les services

```bash
docker compose up -d
```

### 4. Télécharger les modèles Ollama

```bash
./scripts/pull_ollama_models.sh
```

### 5. Préparer les données

Télécharger un dataset d'avis Amazon (ex: depuis [Kaggle](https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews) ou [HuggingFace](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023)), puis :

```bash
python scripts/prepare_data.py --input data/raw_reviews.csv --output data/reviews_clean.json
```

### 6. Importer les workflows dans n8n

1. Ouvrir n8n : http://localhost:5678
2. Aller dans **Workflows > Import from File**
3. Importer dans l'ordre :
   - `workflows/00_create_collection.json` (exécuter une fois)
   - `workflows/01_ingestion.json` (exécuter pour indexer les avis)
   - `workflows/02_chatbot_rag.json` (activer le webhook)

### 7. Tester le chatbot

```bash
curl -X POST http://localhost:5678/webhook/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Est-ce que ce produit est de bonne qualité ?"}'
```

## Structure du projet

```
.
├── docker-compose.yml          # Services : n8n, Qdrant, Ollama
├── .env.example                # Variables d'environnement
├── workflows/
│   ├── 00_create_collection.json   # Créer la collection Qdrant
│   ├── 01_ingestion.json           # Ingestion des avis → embeddings → Qdrant
│   └── 02_chatbot_rag.json         # Webhook chatbot RAG
├── scripts/
│   ├── prepare_data.py             # Nettoyage et préparation du dataset
│   └── pull_ollama_models.sh       # Téléchargement des modèles
├── data/                           # Données (non versionné)
└── docs/                           # Documentation additionnelle
```

## Workflows n8n

### 00 - Créer la collection
Initialise la collection `amazon_reviews` dans Qdrant avec les bons paramètres vectoriels (768 dimensions, distance cosinus).

### 01 - Ingestion
Lit le fichier JSON nettoyé, génère un embedding pour chaque avis via Ollama (nomic-embed-text), et stocke le vecteur + les métadonnées dans Qdrant.

### 02 - Chatbot RAG
Expose un webhook POST `/chat`. Pour chaque question :
1. Génère l'embedding de la question
2. Recherche les 5 avis les plus similaires dans Qdrant
3. Construit un prompt avec le contexte des avis
4. Envoie le prompt à Llama 3.2 pour générer une réponse synthétisée

## Licence

MIT
