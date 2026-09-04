# Modèle de langage — news-intell

## Moteurs de modèle (backend)

Le moteur est résolu par `news_intell/llm.py` (`creer_llm`) selon `config.backend` :

| `backend` | Moteur | Description |
|-----------|--------|-------------|
| `localai` | `LocalAIClient` | Serveur LocalAI (API compatible OpenAI) sur `base_url`. |
| `personnalise` | `ModelePersonnalise` | **Modèle local personnalisé** chargé en mémoire (GGUF via `llama-cpp-python`), **sans API LocalAI**. |

Pour activer le modèle local personnalisé :

```yaml
backend: "personnalise"
modele_personnalise:
  nom: "news-intell-expert"
  chemin: "/chemin/vers/mon-modele.gguf"
```

Il faut installer le chargeur local et fournir un fichier de modèle GGUF :

```bash
pip install llama-cpp-python
```

## Entraîner un modèle personnalisé

Le projet fournit un pipeline d'entraînement (LoRA) :

```bash
# 1. Préparer le jeu d'instructions à partir de données analysées
python scripts/entrainer_modele.py preparer --source data/resultats.json

# 2. Adapter (fine-tune LoRA) un modèle de base (GPU requis)
python scripts/entrainer_modele.py entrainer --base Qwen/Qwen2.5-0.5B-Instruct --epoques 3

# 3. Exporter en GGUF (via le convertisseur llama.cpp) et renseigner config.
python scripts/entrainer_modele.py exporter
```

> **Nécessite** : `torch`, `transformers`, `datasets`, `peft` et idéalement un GPU.
> Le script pioche les exemples dans `data/resultats.json` (résumé, thème,
> sentiment, PNL) pour « cultiver » le modèle sur votre propre ligne éditoriale.

## Recommandations

- Rassembler suffisamment d'articles analysés (`data/resultats.json`) pour
  constituer un jeu variant et étoffé.
- Ajuster `modele_personnalise.nom` et `chemin` après l'export GGUF.
- Le repli `localai` reste utilisable ; le backend `personnalise` s'active
  lorsque vous avez votre modèle.
