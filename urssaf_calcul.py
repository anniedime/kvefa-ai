"""Calcul des cotisations Urssaf d'un micro-entrepreneur.

Module sans dépendance à Streamlit : toutes les fonctions sont pures et
testables. Les taux sont regroupés dans TAUX / CFP / VERSEMENT_LIBERATOIRE
pour être mis à jour facilement quand l'Urssaf les change (en général au
1er janvier ou au 1er juillet).

⚠ Taux indicatifs 2026 — à vérifier sur autoentrepreneur.urssaf.fr.
"""
from dataclasses import dataclass, field
from datetime import date
import calendar

# ══════════════════════════════════════════════════════════════════════════════
# PARAMÈTRES 2026
# ══════════════════════════════════════════════════════════════════════════════
ACTIVITES = {
    "vente": {
        "label": "Vente de marchandises / hébergement (BIC)",
        "taux": 0.123,
        "cfp": 0.001,     # formation pro — commerçant
        "vl": 0.010,      # versement libératoire de l'impôt
        "plafond": 203_100,
    },
    "services_bic": {
        "label": "Prestations de services commerciales / artisanales (BIC)",
        "taux": 0.212,
        "cfp": 0.003,     # artisan (0,1 % si commerçant)
        "vl": 0.017,
        "plafond": 83_600,
    },
    "liberal_ssi": {
        "label": "Profession libérale non réglementée (BNC – SSI)",
        "taux": 0.261,
        "cfp": 0.002,
        "vl": 0.022,
        "plafond": 83_600,
    },
    "liberal_cipav": {
        "label": "Profession libérale réglementée (BNC – Cipav)",
        "taux": 0.232,
        "cfp": 0.002,
        "vl": 0.022,
        "plafond": 83_600,
    },
    "meuble_classe": {
        "label": "Location meublée de tourisme classée",
        "taux": 0.060,
        "cfp": 0.001,
        "vl": 0.010,
        "plafond": 83_600,
    },
}

# Réduction ACRE appliquée au taux de cotisations sociales (pas à la CFP ni au VL)
ACRE_REDUCTION_DEFAUT = 0.50

MOIS_FR = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
           "août", "septembre", "octobre", "novembre", "décembre"]


# ══════════════════════════════════════════════════════════════════════════════
# CALCUL
# ══════════════════════════════════════════════════════════════════════════════
@dataclass
class Ligne:
    activite: str
    ca: float
    taux_social: float
    cotisations: float
    cfp: float
    vl: float

    @property
    def total(self) -> float:
        return self.cotisations + self.cfp + self.vl


@dataclass
class Resultat:
    lignes: list = field(default_factory=list)

    @property
    def ca(self) -> float:
        return sum(l.ca for l in self.lignes)

    @property
    def cotisations(self) -> float:
        return sum(l.cotisations for l in self.lignes)

    @property
    def cfp(self) -> float:
        return sum(l.cfp for l in self.lignes)

    @property
    def vl(self) -> float:
        return sum(l.vl for l in self.lignes)

    @property
    def total(self) -> float:
        return round(self.cotisations + self.cfp + self.vl, 2)

    @property
    def net(self) -> float:
        """Ce qu'il reste après paiement de l'Urssaf."""
        return round(self.ca - self.total, 2)


def calculer(ca_par_activite: dict, acre: bool = False,
             acre_reduction: float = ACRE_REDUCTION_DEFAUT,
             versement_liberatoire: bool = False) -> Resultat:
    """Calcule ce qu'il faut verser pour une période.

    ca_par_activite : {"vente": 1200.0, "services_bic": 3000.0, ...}
    Le CA déclaré est arrondi à l'euro (comme sur le formulaire Urssaf).
    """
    res = Resultat()
    for code, ca in ca_par_activite.items():
        if code not in ACTIVITES:
            raise ValueError(f"Activité inconnue : {code}")
        ca = round(max(float(ca or 0), 0.0))
        p = ACTIVITES[code]
        taux = p["taux"] * (1 - acre_reduction) if acre else p["taux"]
        res.lignes.append(Ligne(
            activite=code,
            ca=ca,
            taux_social=taux,
            cotisations=round(ca * taux, 2),
            cfp=round(ca * p["cfp"], 2),
            vl=round(ca * p["vl"], 2) if versement_liberatoire else 0.0,
        ))
    return res


# ══════════════════════════════════════════════════════════════════════════════
# CALENDRIER
# ══════════════════════════════════════════════════════════════════════════════
def _fin_de_mois(annee: int, mois: int) -> date:
    return date(annee, mois, calendar.monthrange(annee, mois)[1])


def echeance(annee: int, mois: int, periodicite: str = "mensuelle") -> date:
    """Date limite de déclaration + paiement pour le CA encaissé en `mois`.

    Mensuelle : dernier jour du mois suivant.
    Trimestrielle : dernier jour du mois suivant la fin du trimestre.
    """
    if periodicite == "trimestrielle":
        mois = ((mois - 1) // 3 + 1) * 3   # dernier mois du trimestre
    mois_suivant = mois % 12 + 1
    annee_suivante = annee + (1 if mois == 12 else 0)
    return _fin_de_mois(annee_suivante, mois_suivant)


def fin_acre(debut_activite: date) -> date:
    """L'ACRE court jusqu'à la fin du 3e trimestre civil suivant le début d'activité."""
    trimestre = (debut_activite.month - 1) // 3      # 0..3
    t = trimestre + 3                               # 3e trimestre suivant
    annee = debut_activite.year + t // 4
    mois_fin = (t % 4) * 3 + 3
    return _fin_de_mois(annee, mois_fin)


def acre_active(debut_activite: date, annee: int, mois: int) -> bool:
    return _fin_de_mois(annee, mois) <= fin_acre(debut_activite) and \
        (annee, mois) >= (debut_activite.year, debut_activite.month)


def libelle_periode(annee: int, mois: int) -> str:
    return f"{MOIS_FR[mois - 1].capitalize()} {annee}"


def euros(x: float) -> str:
    s = f"{x:,.2f}".replace(",", " ").replace(".", ",")
    return f"{s} €"
