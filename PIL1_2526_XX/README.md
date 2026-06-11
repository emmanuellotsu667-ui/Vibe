# IFRI MentorLink — PIL1_2526

> Application web de mentorat entre étudiants de l'IFRI (filières IA, IM, GL, SE&IoT, SI).

---

## 📋 Table des matières

1. [Présentation](#présentation)
2. [Stack technique](#stack-technique)
3. [Structure du projet](#structure-du-projet)
4. [Installation locale](#installation-locale)
5. [Variables d'environnement](#variables-denvironnement)
6. [Lancement](#lancement)
7. [API — Endpoints](#api--endpoints)
8. [Tests](#tests)
9. [Équipe](#équipe)

---

## Présentation

**IFRI MentorLink** met en relation des étudiants de l'IFRI souhaitant bénéficier ou offrir du mentorat académique. Un algorithme de matching scoré sur 100 points propose les meilleures combinaisons mentor–mentoré selon :

- La compatibilité des matières (compétences vs lacunes)
- La concordance des disponibilités horaires
- La proximité de filière et de niveau

Les échanges sont facilités par une messagerie instantanée (Socket.IO).

---

## Stack technique

| Composant       | Technologie                  |
|-----------------|------------------------------|
| Backend         | Python 3.11 + Flask 3.x      |
| Base de données | PostgreSQL 15 + SQLAlchemy   |
| Auth            | JWT (PyJWT) + bcrypt via Werkzeug |
| Temps réel      | Flask-SocketIO + eventlet    |
| Frontend        | HTML / CSS / JS + Tailwind CSS CDN |
| Tests           | pytest + pytest-flask        |

---

## Structure du projet

```
PIL1_2526_XX/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # create_app(), blueprints, CORS
│   │   ├── config/              # DevelopmentConfig, ProductionConfig
│   │   ├── database/            # init SQLAlchemy
│   │   ├── middleware/          # @token_required (JWT)
│   │   ├── models/              # User, Profile, Competence, Lacune,
│   │   │                        # Disponibilite, Offer, Demand,
│   │   │                        # Matching, Conversation, Message, Notification
│   │   ├── routes/              # auth, profile, offers, matching,
│   │   │                        # messages, notifications
│   │   ├── services/            # matching.py (algorithme de scoring)
│   │   ├── sockets/             # Socket.IO events
│   │   └── validators.py
│   ├── run.py
│   ├── requirements.txt
│   └── .env.example
├── Frontend/
│   ├── pages/                   # signin, signup (dans signin), dashboard,
│   │                            # requests, matching, messages, settings,
│   │                            # notifications, onboarding, reset-password
│   ├── js/
│   │   ├── api.js               # Client API global window.API
│   │   └── matieres-loader.js   # Données matières par filière
│   └── css/
│       └── styles.css
├── database/
│   └── schema.sql               # DDL PostgreSQL complet
├── docs/
│   └── rapport.html             # Trame rapport projet
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_profile.py
│   ├── test_offers.py
│   ├── test_matching.py
│   └── test_messages.py
├── README.md
├── LICENSE
└── .gitignore
```

---

## Installation locale

### Prérequis

- Python 3.11+
- PostgreSQL 15+
- Git

### Étapes

```bash
# 1. Cloner le dépôt
git clone <url-du-depot>
cd PIL1_2526_XX

# 2. Créer et activer l'environnement virtuel
cd backend
python -m venv venv
source venv/bin/activate      # Linux/Mac
# venv\Scripts\activate       # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'environnement
cp .env.example .env
# Éditer .env avec tes paramètres PostgreSQL
```

---

## Variables d'environnement

Fichier `backend/.env` (basé sur `.env.example`) :

```env
FLASK_ENV=development
SECRET_KEY=change-me-in-production
JWT_SECRET_KEY=change-me-jwt-secret

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/ifri_mentorlink

# Frontend (CORS)
FRONTEND_URL=http://localhost:3000
```

---

## Lancement

### Base de données

```bash
# Créer la base
createdb ifri_mentorlink

# Appliquer le schéma SQL
psql -d ifri_mentorlink -f database/schema.sql

# OU utiliser Flask-Migrate
cd backend
flask db init
flask db migrate -m "Initial"
flask db upgrade
```

### Backend

```bash
cd backend
source venv/bin/activate
python run.py
# → http://localhost:5000
```

### Frontend

Ouvrir `Frontend/pages/signin.html` directement dans un navigateur,  
**ou** lancer un serveur statique :

```bash
# Depuis la racine du projet
python -m http.server 3000
# → http://localhost:3000/Frontend/pages/signin.html
```

---

## API — Endpoints

### Auth
| Méthode | Route                          | Description            |
|---------|--------------------------------|------------------------|
| POST    | `/api/auth/register`           | Inscription            |
| POST    | `/api/auth/login`              | Connexion              |
| GET     | `/api/auth/me`                 | Profil courant (JWT)   |
| PUT     | `/api/auth/change-password`    | Changer mot de passe   |

### Profil
| Méthode | Route                              | Description              |
|---------|------------------------------------|--------------------------|
| GET     | `/api/profile/`                    | Mon profil               |
| PUT     | `/api/profile/`                    | Modifier profil          |
| POST    | `/api/profile/competences`         | Ajouter compétence       |
| DELETE  | `/api/profile/competences/<id>`    | Supprimer compétence     |
| POST    | `/api/profile/lacunes`             | Ajouter lacune           |
| DELETE  | `/api/profile/lacunes/<id>`        | Supprimer lacune         |
| POST    | `/api/profile/disponibilites`      | Ajouter dispo            |
| DELETE  | `/api/profile/disponibilites/<id>` | Supprimer dispo          |

### Offres & Demandes
| Méthode | Route                  | Description             |
|---------|------------------------|-------------------------|
| GET     | `/api/offers`          | Lister offres           |
| POST    | `/api/offers`          | Créer offre             |
| PUT     | `/api/offers/<id>`     | Modifier offre          |
| DELETE  | `/api/offers/<id>`     | Supprimer offre         |
| GET     | `/api/demands`         | Lister demandes         |
| POST    | `/api/demands`         | Créer demande           |
| PUT     | `/api/demands/<id>`    | Modifier demande        |
| DELETE  | `/api/demands/<id>`    | Supprimer demande       |

### Matching
| Méthode | Route                          | Description              |
|---------|--------------------------------|--------------------------|
| GET     | `/api/matching/suggest`        | Matchings suggérés       |
| POST    | `/api/matching/run`            | Lancer matching (sauvegarde) |
| PUT     | `/api/matching/<id>/status`    | Accepter/rejeter         |

### Messages
| Méthode | Route                                          | Description          |
|---------|------------------------------------------------|----------------------|
| GET     | `/api/messages/conversations`                  | Mes conversations    |
| POST    | `/api/messages/conversations`                  | Créer/obtenir conv   |
| GET     | `/api/messages/conversations/<id>`             | Messages d'une conv  |
| POST    | `/api/messages/conversations/<id>/send`        | Envoyer message      |

### Notifications
| Méthode | Route                              | Description       |
|---------|------------------------------------|-------------------|
| GET     | `/api/notifications/`              | Mes notifications |
| PUT     | `/api/notifications/read-all`      | Tout marquer lu   |
| PUT     | `/api/notifications/<id>/read`     | Marquer lu        |

---

## Tests

```bash
cd backend
source venv/bin/activate
pytest ../tests/ -v
```

Les tests utilisent SQLite en mémoire (pas besoin de PostgreSQL).

### Couverture
```bash
pip install pytest-cov
pytest ../tests/ --cov=app --cov-report=html
```

---

## Équipe

| Nom | Rôle |
|-----|------|
| _À compléter_ | Chef de projet |
| _À compléter_ | Backend |
| _À compléter_ | Frontend |
| _À compléter_ | Base de données |

---

## Licence

MIT — voir `LICENSE`
