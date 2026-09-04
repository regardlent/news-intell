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

## Activer le modèle personnalisé

Le backend `personnalise` charge un GGUF en mémoire via `llama-cpp-python`.

```bash
pip install llama-cpp-python
```

> ⚠️ Sur certaines machines, la **compilation depuis les sources échoue**
> (bug de packaging `ChatAttachments...svelte`). Solutions :
> - utiliser une **roue précompilée** (`pip install llama-cpp-python --prefer-binary`
>   ou un index de roues communautaires) ;
> - installer les **outils de build MSVC + CMake** ;
> - ou exécuter l'installation sur une machine disposant d'un outillage de build.

Puis renseignez `modele_personnalise.chemin` (votre GGUF) et réglez `backend: "personnalise"`.

**Installation automatique** (télécharge un GGUF adapté + configure) :

```bash
python scripts/installer_modele_local.py --modele 3b   # ~2 Go, active « personnalise »
```

## Optimisation pour votre matériel

`scripts/diagnostiquer_materiel.py` détecte CPU / RAM / VRAM (GPU NVIDIA) et
**recommande** la taille/quantisation du modèle et les réglages
(`nb_threads`, `contexte`, `gpu_couches`) adaptés. Le fichier généré
`config/config.local.yaml` surcharge `config.yaml`.

```bash
python scripts/diagnostiquer_materiel.py            # rapport + recommandation
python scripts/diagnostiquer_materiel.py --ecrire   # écrit config/config.local.yaml
```

