/**
 * matieres-loader.js — Données des matières par filière IFRI
 * Expose window.MATIERES et window.getAllMatieres()
 */

const MATIERES = {
  IA: [
    "Machine Learning", "Deep Learning", "Computer Vision",
    "Traitement du Langage Naturel", "Algorithmes d'optimisation",
    "Réseaux de neurones", "Python pour IA", "Statistiques avancées",
    "Data Mining", "Robotique intelligente",
  ],
  IM: [
    "Développement Web", "Développement Mobile", "React / Vue.js",
    "Flutter / React Native", "UX/UI Design", "Node.js", "REST API",
    "Bases de données", "DevOps", "Cloud Computing",
  ],
  GL: [
    "Génie logiciel", "Conception orientée objet", "Patterns de conception",
    "Tests logiciels", "Méthodes Agile / Scrum", "Architecture logicielle",
    "Java / Spring", "Python / Django", "Intégration continue",
    "Gestion de projet IT",
  ],
  "SE&IoT": [
    "Systèmes embarqués", "Arduino / Raspberry Pi", "Protocoles IoT",
    "MQTT / CoAP", "Électronique numérique", "Systèmes temps réel",
    "Réseaux de capteurs", "C / C++", "Linux embarqué", "Sécurité IoT",
  ],
  SI: [
    "Systèmes d'information", "ERP / SAP", "Analyse métier",
    "Modélisation UML", "Base de données relationnelles", "SQL avancé",
    "Business Intelligence", "Audit informatique", "Gestion de projet",
    "Gouvernance IT",
  ],
  // Communs toutes filières
  Commun: [
    "Algorithmique", "Structures de données", "Mathématiques discrètes",
    "Probabilités et statistiques", "Réseaux informatiques", "Sécurité informatique",
    "Systèmes d'exploitation", "Base de données", "Programmation C",
  ],
};

/**
 * Retourne toutes les matières (dédupliquées).
 */
function getAllMatieres() {
  const all = new Set();
  Object.values(MATIERES).forEach(list => list.forEach(m => all.add(m)));
  return [...all].sort();
}

/**
 * Retourne les matières d'une filière + les communes.
 */
function getMatieresByFiliere(filiere) {
  return [...(MATIERES[filiere] || []), ...(MATIERES.Commun || [])];
}

window.MATIERES = MATIERES;
window.getAllMatieres = getAllMatieres;
window.getMatieresByFiliere = getMatieresByFiliere;
