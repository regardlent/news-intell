"""Pipeline d'entraînement d'un modèle local « personnalisé » pour news-intell.

Prépare un jeu de données d'instruction en français, adapte (fine-tune) un
modèle de base via LoRA, et peut l'exporter au format GGUF utilisable par le
backend `personnalise` de `news_intell/llm.py`.

Usage (sur une machine avec GPU) :
    python scripts/entrainer_modele.py preparer   --source data/resultats.json
    python scripts/entrainer_modele.py entrainer  --base Qwen/Qwen2.5-0.5B-Instruct
    python scripts/entrainer_modele.py exporter
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJET = Path(__file__).resolve().parent.parent
if str(PROJET) not in sys.path:
    sys.path.insert(0, str(PROJET))

CHEMIN_DONNEES = Path("data") / "entrainement.jsonl"
CHEMIN_MODELE = Path("modele")


def _instructions(article: dict) -> list[dict]:
    """Convertit une analyse en exemples d'instruction français."""
    contenu = article.get("resume") or article.get("contenu") or article.get("titre", "")
    exemples = [
        {
            "instruction": "Résume cet article.",
            "contenu": contenu,
            "reponse": article.get("resume_ia", ""),
        },
        {
            "instruction": "Classe cet article par thème.",
            "contenu": contenu,
            "reponse": article.get("thematique", ""),
        },
        {
            "instruction": "Analyse le sentiment de cet article.",
            "contenu": contenu,
            "reponse": article.get("sentiment", ""),
        },
        {
            "instruction": "Analyse comportementale (PNL) de cet article.",
            "contenu": contenu,
            "reponse": json.dumps(article.get("pnl") or {}, ensure_ascii=False),
        },
    ]
    return exemples


def preparer(source: Path) -> int:
    """Construit data/entrainement.jsonl à partir de data/resultats.json."""
    if not source.exists():
        print(f"✖ Source introuvable : {source}")
        return 1
    donnees = json.loads(source.read_text(encoding="utf-8"))
    with CHEMIN_DONNEES.open("w", encoding="utf-8") as flux:
        for article in donnees:
            for exemple in _instructions(article):
                flux.write(json.dumps(exemple, ensure_ascii=False) + "\n")
    print(f"✔ {CHEMIN_DONNEES} généré ({len(donnees)} article(s)).")
    return 0


def entrainer(base: str, epoques: int) -> int:
    """Fine-tune (LoRA) d'un modèle de base sur le jeu d'instructions."""
    try:
        import torch
        from datasets import load_dataset
        from peft import LoraConfig, get_peft_model
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            Trainer,
            TrainingArguments,
        )
    except ImportError as exc:
        print(f"✖ Dépendances manquantes : {exc}. Installez torch, transformers, datasets, peft.")
        return 1

    if not CHEMIN_DONNEES.exists():
        print("✖ Lancez d'abord la commande « preparer ».")
        return 1

    dataset = load_dataset("json", data_files=str(CHEMIN_DONNEES))
    tokenizer = AutoTokenizer.from_pretrained(base)
    tokenizer.pad_token = tokenizer.eos_token

    def formater(exemple):
        texte = (
            f"<|user|>\n{exemple['instruction']}\n{exemple['contenu']}\n"
            f"<|assistant|>\n{exemple['reponse']}<|end|>"
        )
        return tokenizer(texte, truncation=True, max_length=512)

    data = dataset.map(formater)
    modele = AutoModelForCausalLM.from_pretrained(base, torch_dtype=torch.float16)
    config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    modele = get_peft_model(modele, config)
    args = TrainingArguments(
        output_dir=str(CHEMIN_MODELE),
        num_train_epochs=epoques,
        per_device_train_batch_size=2,
        save_strategy="epoch",
    )
    Trainer(model=modele, args=args, train_dataset=data["train"]).train()
    modele.save_pretrained(CHEMIN_MODELE)
    tokenizer.save_pretrained(CHEMIN_MODELE)
    print(f"✔ Modèle adapté enregistré dans {CHEMIN_MODELE}/.")
    return 0


def exporter() -> int:
    """Indique l'export GGUF (pour llama.cpp)."""
    print("ℹ Export GGUF : utilisez le convertisseur de llama.cpp sur le dossier 'modele/'.")
    return 0


def construire_parseur() -> argparse.ArgumentParser:
    parseur = argparse.ArgumentParser(
        prog="entrainer_modele",
        description="Entraîne un modèle local personnalisé pour news-intell.",
    )
    sous = parseur.add_subparsers(dest="commande", required=True)

    p_preparer = sous.add_parser("preparer", help="Prépare le jeu d'instructions.")
    p_preparer.add_argument("--source", type=Path, default=Path("data") / "resultats.json")

    p_entrainer = sous.add_parser("entrainer", help="Fine-tune LoRA.")
    p_entrainer.add_argument("--base", default="Qwen/Qwen2.5-0.5B-Instruct")
    p_entrainer.add_argument("--epoques", type=int, default=3)

    sous.add_parser("exporter", help="Exporte en GGUF (indication).")
    return parseur


def main(argv: list[str] | None = None) -> int:
    args = construire_parseur().parse_args(argv)
    if args.commande == "preparer":
        return preparer(args.source)
    if args.commande == "entrainer":
        return entrainer(args.base, args.epoques)
    return exporter()


if __name__ == "__main__":
    raise SystemExit(main())
