"""
Service de matching : algorithme de scoring sur 100 points.

Critères :
  - Compatibilité matière/compétence (40 pts)
  - Compatibilité horaires / disponibilités communes (30 pts)
  - Proximité de filière (15 pts)
  - Proximité de niveau (15 pts)

Seuil minimum : 30/100 pour être affiché.
"""
import json
from datetime import time
from typing import List, Dict, Any


SCORE_THRESHOLD = 30  # Score minimum pour afficher un matching

# Correspondance filières (distance)
FILIERE_DISTANCE = {
    ("IA", "IM"): 10, ("IA", "GL"): 15, ("IA", "SE&IoT"): 20, ("IA", "SI"): 25,
    ("IM", "GL"): 10, ("IM", "SE&IoT"): 15, ("IM", "SI"): 20,
    ("GL", "SE&IoT"): 10, ("GL", "SI"): 15,
    ("SE&IoT", "SI"): 10,
}

# Ordre des niveaux
NIVEAU_ORDER = {"L1": 1, "L2": 2, "L3": 3, "M1": 4, "M2": 5}


def _matiere_score(mentor_competences: List[str], mentoree_lacunes: List[str],
                   offer_matiere: str, demand_matiere: str) -> tuple[float, List[str]]:
    """
    Score de compatibilité matière (0-40).
    Retourne (score, liste_matieres_communes).
    """
    # Normalise en minuscules pour la comparaison
    comp_set = {c.lower() for c in mentor_competences}
    lacune_set = {l.lower() for l in mentoree_lacunes}

    # Matière principale de l'offre/demande
    if offer_matiere.lower() == demand_matiere.lower():
        base = 40.0
    else:
        base = 0.0

    # Bonus si la matière est dans les compétences du mentor et lacunes du mentoré
    communes = comp_set & lacune_set
    bonus = min(len(communes) * 5, 20)

    matieres_communes = list(communes | ({offer_matiere.lower()} if offer_matiere.lower() == demand_matiere.lower() else set()))
    return min(base + bonus, 40), matieres_communes


def _horaires_score(mentor_dispos: List[Dict], mentoree_dispos: List[Dict]) -> tuple[float, List[Dict]]:
    """
    Score de compatibilité horaires (0-30).
    Retourne (score, créneaux_communs).
    """
    communes = []

    for md in mentor_dispos:
        for ed in mentoree_dispos:
            if md["jour"].lower() != ed["jour"].lower():
                continue
            # Intersection des créneaux
            try:
                debut_m = time.fromisoformat(md["heure_debut"])
                fin_m = time.fromisoformat(md["heure_fin"])
                debut_e = time.fromisoformat(ed["heure_debut"])
                fin_e = time.fromisoformat(ed["heure_fin"])
            except (ValueError, TypeError):
                continue

            debut_c = max(debut_m, debut_e)
            fin_c = min(fin_m, fin_e)
            if debut_c < fin_c:
                communes.append({
                    "jour": md["jour"],
                    "heure_debut": debut_c.strftime("%H:%M"),
                    "heure_fin": fin_c.strftime("%H:%M"),
                })

    score = min(len(communes) * 10, 30)
    return score, communes


def _filiere_score(filiere_mentor: str, filiere_mentoree: str) -> float:
    """Score de proximité filière (0-15)."""
    if not filiere_mentor or not filiere_mentoree:
        return 7.5  # Neutre si info manquante
    if filiere_mentor == filiere_mentoree:
        return 15.0
    dist = FILIERE_DISTANCE.get(
        (filiere_mentor, filiere_mentoree),
        FILIERE_DISTANCE.get((filiere_mentoree, filiere_mentor), 30)
    )
    return max(0, 15 - dist * 0.5)


def _niveau_score(niveau_mentor: str, niveau_mentoree: str) -> float:
    """
    Score de proximité niveau (0-15).
    Idéal : mentor 1 ou 2 niveaux au-dessus du mentoré.
    """
    if not niveau_mentor or not niveau_mentoree:
        return 7.5
    nm = NIVEAU_ORDER.get(niveau_mentor, 0)
    ne = NIVEAU_ORDER.get(niveau_mentoree, 0)
    diff = nm - ne
    if diff <= 0:
        return 0   # Le mentor doit être plus avancé
    if diff == 1:
        return 15
    if diff == 2:
        return 12
    return max(0, 15 - diff * 3)


def compute_score(offer, demand) -> Dict[str, Any]:
    """
    Calcule le score de matching entre une offre et une demande.

    Args:
        offer: objet Offer avec ses relations user/profile
        demand: objet Demand avec ses relations user/profile

    Returns:
        dict avec score, matieres_communes, dispos_communes, détail
    """
    mentor_profile = offer.user.profile if offer.user else None
    mentoree_profile = demand.user.profile if demand.user else None

    mentor_competences = [c.matiere for c in mentor_profile.competences] if mentor_profile else []
    mentoree_lacunes = [l.matiere for l in mentoree_profile.lacunes] if mentoree_profile else []
    mentor_dispos = [d.to_dict() for d in mentor_profile.disponibilites] if mentor_profile else []
    mentoree_dispos = [d.to_dict() for d in mentoree_profile.disponibilites] if mentoree_profile else []

    s_matiere, matieres_communes = _matiere_score(
        mentor_competences, mentoree_lacunes, offer.matiere, demand.matiere
    )
    s_horaires, dispos_communes = _horaires_score(mentor_dispos, mentoree_dispos)
    s_filiere = _filiere_score(
        mentor_profile.filiere if mentor_profile else None,
        mentoree_profile.filiere if mentoree_profile else None,
    )
    s_niveau = _niveau_score(
        mentor_profile.niveau if mentor_profile else None,
        mentoree_profile.niveau if mentoree_profile else None,
    )

    total = s_matiere + s_horaires + s_filiere + s_niveau

    return {
        "score": round(total, 2),
        "matieres_communes": ", ".join(matieres_communes) if matieres_communes else "",
        "dispos_communes": json.dumps(dispos_communes),
        "detail": {
            "matiere": s_matiere,
            "horaires": s_horaires,
            "filiere": s_filiere,
            "niveau": s_niveau,
        }
    }


def run_matching_for_demand(demand, offers):
    """
    Lance l'algorithme sur une demande contre une liste d'offres.
    Retourne les résultats triés par score décroissant, au-dessus du seuil.
    """
    results = []
    for offer in offers:
        # Pas d'auto-matching
        if offer.user_id == demand.user_id:
            continue
        result = compute_score(offer, demand)
        if result["score"] >= SCORE_THRESHOLD:
            results.append({"offer": offer, **result})
    return sorted(results, key=lambda x: x["score"], reverse=True)
