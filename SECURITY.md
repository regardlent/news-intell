# Politique de sécurité

Le projet **news-intell** accorde une grande importance à la sécurité.
Cette page décrit comment signaler une vulnérabilité et quelles versions sont
prises en charge.

## 📧 Signaler une vulnérabilité

Merci de **ne pas** ouvrir une issue publique pour un problème de sécurité.
Préférez un signalement privé afin de protéger les utilisateurs :

- Ouvrez une conversation privée via
  **[GitHub Security Advisories](https://github.com/regardlent/news-intell/security/advisories/new)**
  (recommandé), **ou**
- Envoyez un email à l'adresse suivante : (à préciser — voir le contact des
  mainteneurs dans le dépôt).

**Lors de votre signalement, merci de fournir :**

1. Une description du problème ;
2. Les étapes pour le reproduire (code minimal de préférence) ;
3. La version affectée ;
4. L'impact potentiel (si vous le pouvez) ;
5. Toute suggestion de correction.

## 🗓️ Versions prises en charge

| Version | Statut                  |
|---------|-------------------------|
| `0.1.x` | ✅ Activement maintenue |
| < 0.1   | ❌ Non supportée        |

## 🔒 Bonnes pratiques

Ce projet s'appuie sur un serveur **LocalAI** local. Veillez à :

- Ne pas exposer votre serveur LocalAI sur le réseau public sans protection ;
- Conserver vos clés d'API dans le fichier `.env` (jamais versionné) ;
- Utiliser des sources de news de confiance.

Les dépendances sont suivies par **Dependabot** (voir
[`.github/dependabot.yml`](.github/dependabot.yml)).
