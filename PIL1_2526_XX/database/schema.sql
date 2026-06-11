-- ============================================================
-- IFRI MentorLink — Schéma PostgreSQL complet
-- PIL1_2526
-- ============================================================

-- Extension uuid (optionnel, non utilisé mais utile)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── Utilisateurs ────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    id           SERIAL PRIMARY KEY,
    nom          VARCHAR(80)  NOT NULL,
    prenom       VARCHAR(80)  NOT NULL,
    email        VARCHAR(120) NOT NULL UNIQUE,
    telephone    VARCHAR(20)  UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    is_active    BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ─── Profils ─────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS profiles (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    filiere         VARCHAR(20),          -- IA | IM | GL | SE&IoT | SI
    niveau          VARCHAR(10),          -- L1..M2
    bio             TEXT,
    centres_interet TEXT,
    photo_url       VARCHAR(255),
    onboarding_done BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ─── Compétences ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS competences (
    id               SERIAL PRIMARY KEY,
    profile_id       INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    matiere          VARCHAR(100) NOT NULL,
    niveau_maitrise  INTEGER NOT NULL DEFAULT 3 CHECK (niveau_maitrise BETWEEN 1 AND 5)
);

-- ─── Lacunes ─────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS lacunes (
    id         SERIAL PRIMARY KEY,
    profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    matiere    VARCHAR(100) NOT NULL,
    priorite   INTEGER NOT NULL DEFAULT 1
);

-- ─── Disponibilités ──────────────────────────────────────────

CREATE TABLE IF NOT EXISTS disponibilites (
    id           SERIAL PRIMARY KEY,
    profile_id   INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    jour         VARCHAR(20) NOT NULL,
    heure_debut  TIME NOT NULL,
    heure_fin    TIME NOT NULL,
    CHECK (heure_fin > heure_debut)
);

-- ─── Offres de mentorat ───────────────────────────────────────

CREATE TABLE IF NOT EXISTS offers (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    matiere     VARCHAR(100) NOT NULL,
    description TEXT,
    format      VARCHAR(20) NOT NULL DEFAULT 'les deux',  -- présentiel|en ligne|les deux
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_offers_matiere ON offers(matiere);
CREATE INDEX IF NOT EXISTS idx_offers_active  ON offers(is_active);

-- ─── Demandes de mentorat ─────────────────────────────────────

CREATE TABLE IF NOT EXISTS demands (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    matiere     VARCHAR(100) NOT NULL,
    description TEXT,
    format      VARCHAR(20) NOT NULL DEFAULT 'les deux',
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_demands_matiere ON demands(matiere);

-- ─── Matchings ───────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS matchings (
    id                SERIAL PRIMARY KEY,
    offer_id          INTEGER NOT NULL REFERENCES offers(id)  ON DELETE CASCADE,
    demand_id         INTEGER NOT NULL REFERENCES demands(id) ON DELETE CASCADE,
    score             FLOAT   NOT NULL DEFAULT 0,
    matieres_communes TEXT,
    dispos_communes   TEXT,
    status            VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending|accepted|rejected
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (offer_id, demand_id)
);

-- ─── Conversations ───────────────────────────────────────────

CREATE TABLE IF NOT EXISTS conversations (
    id         SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS conversation_participants (
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id         INTEGER NOT NULL REFERENCES users(id)         ON DELETE CASCADE,
    PRIMARY KEY (conversation_id, user_id)
);

-- ─── Messages ────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS messages (
    id              SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    sender_id       INTEGER NOT NULL REFERENCES users(id)         ON DELETE CASCADE,
    content         TEXT    NOT NULL,
    is_read         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);

-- ─── Notifications ───────────────────────────────────────────

CREATE TABLE IF NOT EXISTS notifications (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type       VARCHAR(50)  NOT NULL,  -- new_message|new_match|system
    title      VARCHAR(200) NOT NULL,
    body       TEXT,
    is_read    BOOLEAN      NOT NULL DEFAULT FALSE,
    ref_id     INTEGER,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notifs_user ON notifications(user_id, is_read);
