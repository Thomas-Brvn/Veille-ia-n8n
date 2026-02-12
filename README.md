# Veille IA - Agregateur de news intelligent

Les avancees en intelligence artificielle vont tres vite. Chaque jour, des dizaines d'articles sortent sur le sujet, mais tous ne se valent pas. Certains sont du bruit, d'autres sont vraiment pertinents.

Cet outil filtre automatiquement les articles interessants autour de la data et de l'IA, aupres de sources connues, fiables et verifiables (ArXiv, TechCrunch, Google AI Blog, Hugging Face, Hacker News). Un LLM local (Llama 3.2 via Ollama) resume chaque article en francais et le classe par categorie.

Ce projet avait avant tout pour but de prendre en main n8n pour la premiere fois. C'est un premier projet simple, mais qui m'a permis de decouvrir les capacites de cet outil d'orchestration et de voir ce qu'on peut faire en combinant des workflows automatises avec un LLM local.

## Comment ca marche

```
Sources RSS (ArXiv, TechCrunch, Google AI, HuggingFace, HN)
        |
        v
   n8n (workflow automatise toutes les heures)
   -> Collecte les flux RSS
   -> Filtre les articles lies a l'IA/Data
   -> Deduplique
        |
        v
   Ollama (Llama 3.2, local)
   -> Resume en francais (2-3 phrases)
   -> Classe par tags (NLP, LLM, Business, Recherche...)
        |
        v
   summaries.json
        |
        v
   Frontend (Nginx, localhost:8080)
   -> Affichage des resumes avec filtres par source et par tag
```

## Stack

| Composant | Role |
|-----------|------|
| n8n | Orchestre la collecte RSS et le resume |
| Ollama + Llama 3.2 | Resume et classe chaque article en local |
| Nginx | Sert le dashboard web |
| Docker Compose | Fait tourner le tout en une commande |

## Installation

Prerequis : Docker et Docker Compose installes sur la machine (~4 Go de RAM pour Llama 3.2).

```bash
# 1. Cloner le repo
git clone https://github.com/Thomas-Brvn/veille-ia-n8n.git
cd veille-ia-n8n

# 2. Lancer les services
docker compose up -d

# 3. Telecharger le modele Llama 3.2
docker exec ollama ollama pull llama3.2

# 4. Importer le workflow dans n8n
#    - Ouvrir http://localhost:5678
#    - Se connecter (admin / changeme par defaut)
#    - Workflows > Import from File > selectionner workflows/01_rss_summarizer.json
#    - Activer le workflow (toggle en haut a droite)

# 5. Voir les resumes
#    Ouvrir http://localhost:8080
```

Le dashboard se met a jour automatiquement. Les articles arrivent apres la premiere execution du workflow.

## Ajouter des sources RSS

Dans n8n, il suffit d'ajouter un node RSS Feed Read avec l'URL du flux et de le connecter au node de filtrage. Quelques exemples de flux compatibles :

- `https://openai.com/blog/rss.xml`
- `https://www.theverge.com/rss/index.xml`
- `https://www.wired.com/feed/rss`

## Structure du projet

```
.
├── docker-compose.yml          # Configuration des 3 services
├── workflows/
│   └── 01_rss_summarizer.json  # Workflow n8n (collecte + resume + tags)
├── frontend/
│   ├── index.html              # Dashboard web
│   └── nginx.conf              # Config Nginx
├── data/                       # Resumes generes (non versionne)
└── README.md
```

## Licence

MIT
