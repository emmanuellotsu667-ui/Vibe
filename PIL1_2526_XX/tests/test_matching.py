"""
Tests pytest — Service de matching (unitaires)
"""
import pytest
from unittest.mock import MagicMock
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def make_profile(filiere, niveau, competences, lacunes, dispos):
    p = MagicMock()
    p.filiere = filiere
    p.niveau = niveau
    p.competences = [MagicMock(matiere=c) for c in competences]
    p.lacunes = [MagicMock(matiere=l) for l in lacunes]
    p.disponibilites = [
        MagicMock(**{"to_dict.return_value": d}) for d in dispos
    ]
    return p


def make_offer(user_id, matiere, filiere, niveau, competences, dispos):
    o = MagicMock()
    o.user_id = user_id
    o.matiere = matiere
    o.user = MagicMock()
    o.user.profile = make_profile(filiere, niveau, competences, [], dispos)
    return o


def make_demand(user_id, matiere, filiere, niveau, lacunes, dispos):
    d = MagicMock()
    d.user_id = user_id
    d.matiere = matiere
    d.user = MagicMock()
    d.user.profile = make_profile(filiere, niveau, [], lacunes, dispos)
    return d


def test_perfect_match():
    """Score max attendu quand tout correspond."""
    from app.services.matching import compute_score
    dispos = [{"jour": "Lundi", "heure_debut": "08:00", "heure_fin": "10:00"}]
    offer  = make_offer(1, "Machine Learning", "IA", "M1", ["Machine Learning"], dispos)
    demand = make_demand(2, "Machine Learning", "IA", "L3", ["Machine Learning"], dispos)
    result = compute_score(offer, demand)
    assert result["score"] >= 70


def test_no_matiere_match():
    """Score faible si matières incompatibles."""
    from app.services.matching import compute_score
    offer  = make_offer(1, "Réseaux", "GL", "L3", ["Réseaux"], [])
    demand = make_demand(2, "Deep Learning", "IA", "L2", ["Deep Learning"], [])
    result = compute_score(offer, demand)
    # Matière principale différente => score matière = 0
    assert result["detail"]["matiere"] == 0


def test_horaires_communs():
    """Vérifie le calcul de créneaux communs."""
    from app.services.matching import _horaires_score
    mentor_dispos  = [{"jour": "Mardi", "heure_debut": "08:00", "heure_fin": "12:00"}]
    mentoree_dispos = [{"jour": "Mardi", "heure_debut": "09:00", "heure_fin": "11:00"}]
    score, communes = _horaires_score(mentor_dispos, mentoree_dispos)
    assert score > 0
    assert len(communes) == 1
    assert communes[0]["heure_debut"] == "09:00"


def test_horaires_aucun_commun():
    from app.services.matching import _horaires_score
    d1 = [{"jour": "Lundi", "heure_debut": "08:00", "heure_fin": "10:00"}]
    d2 = [{"jour": "Vendredi", "heure_debut": "14:00", "heure_fin": "16:00"}]
    score, communes = _horaires_score(d1, d2)
    assert score == 0
    assert communes == []


def test_niveau_score_mentor_plus_avance():
    from app.services.matching import _niveau_score
    assert _niveau_score("M1", "L3") == 15
    assert _niveau_score("L3", "M1") == 0  # Mentor moins avancé → 0
    assert _niveau_score("L2", "L1") == 15


def test_matching_suggest_endpoint(client, auth_headers):
    resp = client.get("/api/matching/suggest", headers=auth_headers)
    assert resp.status_code == 200
    assert "matchings" in resp.get_json()
