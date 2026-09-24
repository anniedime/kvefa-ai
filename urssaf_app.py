"""Calculateur Urssaf mensuel — micro-entrepreneur.

Lancer : streamlit run urssaf_app.py
"""
import json
from datetime import date
from pathlib import Path

import streamlit as st

from urssaf_calcul import (
    ACTIVITES, ACRE_REDUCTION_DEFAUT, MOIS_FR,
    calculer, echeance, fin_acre, acre_active, libelle_periode, euros,
)

DATA_FILE = Path(__file__).parent / "urssaf_historique.json"


# ══════════════════════════════════════════════════════════════════════════════
# STORAGE — profil + déclarations
# ══════════════════════════════════════════════════════════════════════════════
def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"profil": {}, "declarations": {}}


def save_data(data: dict) -> None:
    try:
        DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        st.warning("Impossible d'enregistrer l'historique sur le disque.")


st.set_page_config(page_title="Mon Urssaf mensuel", page_icon="€", layout="centered")

data = load_data()
profil = data.setdefault("profil", {})
declarations = data.setdefault("declarations", {})

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — profil
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.header("Mon profil")
    codes = list(ACTIVITES)
    activites = st.multiselect(
        "Mes activités",
        codes,
        default=[c for c in profil.get("activites", ["services_bic"]) if c in codes],
        format_func=lambda c: ACTIVITES[c]["label"],
    )
    periodicite = st.radio(
        "Déclaration", ["mensuelle", "trimestrielle"],
        index=0 if profil.get("periodicite", "mensuelle") == "mensuelle" else 1,
        horizontal=True,
    )
    vl = st.toggle("Versement libératoire de l'impôt", value=profil.get("vl", False),
                   help="Option qui fait payer l'impôt sur le revenu en même temps que les cotisations.")
    debut = st.date_input(
        "Date de début d'activité",
        value=date.fromisoformat(profil["debut"]) if profil.get("debut") else date(2024, 1, 1),
        format="DD/MM/YYYY",
    )
    acre = st.toggle("Je bénéficie de l'ACRE", value=profil.get("acre", False))
    acre_red = ACRE_REDUCTION_DEFAUT
    if acre:
        acre_red = st.slider("Réduction ACRE (%)", 0, 100,
                             int(profil.get("acre_reduction", ACRE_REDUCTION_DEFAUT) * 100), 5) / 100
        st.caption(f"ACRE applicable jusqu'au {fin_acre(debut):%d/%m/%Y}.")

    nouveau_profil = {"activites": activites, "periodicite": periodicite, "vl": vl,
                      "debut": debut.isoformat(), "acre": acre, "acre_reduction": acre_red}
    if nouveau_profil != profil:
        data["profil"] = nouveau_profil
        save_data(data)

    st.divider()
    st.caption("Taux indicatifs 2026. Vérifiez-les sur "
               "[autoentrepreneur.urssaf.fr](https://www.autoentrepreneur.urssaf.fr).")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.title("Combien je verse à l'Urssaf ?")

if not activites:
    st.info("Choisissez au moins une activité dans le panneau de gauche.")
    st.stop()

tab_calcul, tab_historique = st.tabs(["Ce mois-ci", "Historique"])

with tab_calcul:
    today = date.today()
    # Par défaut : le mois précédent (c'est celui qu'on déclare maintenant)
    defaut_mois = today.month - 1 or 12
    defaut_annee = today.year if today.month > 1 else today.year - 1

    c1, c2 = st.columns(2)
    mois = c1.selectbox("Mois d'encaissement", range(1, 13), index=defaut_mois - 1,
                        format_func=lambda m: MOIS_FR[m - 1].capitalize())
    annee = c2.number_input("Année", 2020, 2100, defaut_annee, step=1)
    cle = f"{annee}-{mois:02d}"
    deja = declarations.get(cle, {}).get("ca", {})

    st.markdown("**Chiffre d'affaires encaissé** (sommes réellement reçues ce mois-ci, hors frais)")
    ca = {}
    for code in activites:
        ca[code] = st.number_input(ACTIVITES[code]["label"], min_value=0.0, step=100.0,
                                   value=float(deja.get(code, 0.0)), key=f"ca_{cle}_{code}")

    acre_mois = acre and acre_active(debut, annee, mois)
    res = calculer(ca, acre=acre_mois, acre_reduction=acre_red, versement_liberatoire=vl)

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("À verser à l'Urssaf", euros(res.total))
    m2.metric("Il me reste", euros(res.net))
    m3.metric("Date limite", f"{echeance(annee, mois, periodicite):%d/%m/%Y}")

    with st.expander("Détail du calcul", expanded=res.ca > 0):
        for l in res.lignes:
            if not l.ca:
                continue
            st.markdown(f"**{ACTIVITES[l.activite]['label']}** — CA {euros(l.ca)}")
            st.markdown(
                f"- Cotisations sociales ({l.taux_social * 100:.2f} %) : {euros(l.cotisations)}\n"
                f"- Formation professionnelle ({ACTIVITES[l.activite]['cfp'] * 100:.1f} %) : {euros(l.cfp)}"
                + (f"\n- Impôt – versement libératoire ({ACTIVITES[l.activite]['vl'] * 100:.1f} %) : {euros(l.vl)}"
                   if vl else "")
            )
        if acre_mois:
            st.success(f"ACRE appliquée : cotisations sociales réduites de {acre_red:.0%}.")
        if periodicite == "trimestrielle":
            st.caption("En déclaration trimestrielle, additionnez les 3 mois du trimestre "
                       "(onglet Historique).")

    if st.button("Enregistrer ce mois", type="primary"):
        declarations[cle] = {"ca": {k: v for k, v in ca.items() if v}, "total": res.total,
                             "acre": acre_mois}
        save_data(data)
        st.success(f"{libelle_periode(annee, mois)} enregistré.")

    # Plafonds de CA annuels
    ca_annee = {}
    for k, d in declarations.items():
        if k.startswith(f"{annee}-") and k != cle:
            for code, v in d["ca"].items():
                ca_annee[code] = ca_annee.get(code, 0) + v
    for code, v in ca.items():
        ca_annee[code] = ca_annee.get(code, 0) + v
    total_annee = sum(ca_annee.values())
    services = total_annee - ca_annee.get("vente", 0)
    for montant, plafond, nom in [(total_annee, ACTIVITES["vente"]["plafond"], "global"),
                                  (services, ACTIVITES["services_bic"]["plafond"], "services")]:
        if montant > plafond * 0.9:
            st.warning(f"CA {nom} {annee} : {euros(montant)} — plafond micro-entreprise "
                       f"{euros(plafond)}. Pensez à en parler à un comptable.")

with tab_historique:
    if not declarations:
        st.info("Aucun mois enregistré pour l'instant.")
    else:
        annees = sorted({k[:4] for k in declarations}, reverse=True)
        a = st.selectbox("Année", annees)
        lignes = []
        for k in sorted(declarations):
            if not k.startswith(a):
                continue
            d = declarations[k]
            ca_mois = sum(d["ca"].values())
            lignes.append({
                "Mois": libelle_periode(int(k[:4]), int(k[5:])),
                "CA encaissé": ca_mois,
                "Urssaf": d["total"],
                "Reste": ca_mois - d["total"],
                "Date limite": echeance(int(k[:4]), int(k[5:]), periodicite).strftime("%d/%m/%Y"),
            })
        st.dataframe(lignes, hide_index=True, width="stretch",
                     column_config={c: st.column_config.NumberColumn(format="%.2f €")
                                    for c in ["CA encaissé", "Urssaf", "Reste"]})
        t1, t2, t3 = st.columns(3)
        t1.metric(f"CA {a}", euros(sum(l["CA encaissé"] for l in lignes)))
        t2.metric("Total Urssaf", euros(sum(l["Urssaf"] for l in lignes)))
        t3.metric("Reste", euros(sum(l["Reste"] for l in lignes)))
        st.bar_chart(lignes, x="Mois", y="Urssaf", y_label="€ versés", sort=False)

        a_suppr = st.selectbox("Supprimer un mois", [""] + [k for k in sorted(declarations) if k.startswith(a)],
                               format_func=lambda k: libelle_periode(int(k[:4]), int(k[5:])) if k else "—")
        if a_suppr and st.button("Supprimer"):
            declarations.pop(a_suppr, None)
            save_data(data)
            st.rerun()
