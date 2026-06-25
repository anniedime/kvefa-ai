import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path

import anthropic
import streamlit as st

# ══════════════════════════════════════════════════════════════════════════════
# STORAGE — prospects + paramètres, persistés localement
# ══════════════════════════════════════════════════════════════════════════════
DATA_FILE = Path(__file__).parent / "prospects.json"
DEFAULT_DATA = {
    "settings": {"offer_context": "", "sender_name": "", "sender_company": ""},
    "prospects": [],
}


def load_data() -> dict:
    if DATA_FILE.exists():
        try:
            data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            data.setdefault("settings", dict(DEFAULT_DATA["settings"]))
            data.setdefault("prospects", [])
            return data
        except Exception:
            pass
    return json.loads(json.dumps(DEFAULT_DATA))


def save_data(data: dict) -> None:
    try:
        DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


def now_iso() -> str:
    return datetime.now().isoformat()


STATUTS = ["À contacter", "Message généré", "Contacté", "Relance envoyée", "Répondu", "Qualifié", "Perdu"]
CANAUX = ["LinkedIn", "Email"]
POSTES = [
    "Dirigeant / Gérant",
    "Directeur général",
    "Directeur travaux",
    "Conducteur de travaux",
    "Directeur technique",
    "Responsable achats",
    "Directeur administratif et financier",
    "Peu importe",
]
SPECIALITES = [
    "Peu importe",
    "Gros œuvre",
    "Second œuvre",
    "Travaux publics",
    "Génie civil / VRD",
    "Rénovation énergétique",
    "Construction bois",
]
TAILLES = ["Peu importe", "TPE / PME (< 50 salariés)", "ETI (50-500 salariés)", "Grand groupe (500+)"]

# ══════════════════════════════════════════════════════════════════════════════
# CLAUDE
# ══════════════════════════════════════════════════════════════════════════════
MODEL = "claude-opus-4-7"
SEARCH_TOOLS = [{"type": "web_search_20260209", "name": "web_search"}]

SEARCH_SYSTEM_PROMPT = """Tu es un assistant de prospection B2B spécialisé dans le secteur du BTP \
(bâtiment et travaux publics) en France.

Ta mission : à partir des critères donnés par l'utilisateur, utilise la recherche web pour identifier \
des entreprises BTP réelles et leurs dirigeants ou responsables, pertinents comme cibles de prospection.

RÈGLES STRICTES :
- N'invente JAMAIS un email ou un lien LinkedIn : si tu ne le trouves pas via la recherche, laisse le \
champ vide ("").
- Base-toi uniquement sur des informations trouvées via la recherche web (sites d'entreprise, presse, \
LinkedIn public, annuaires professionnels).
- Si tu n'es pas certain qu'une entreprise ou une personne existe réellement, ne l'inclus pas.
- Réponds UNIQUEMENT avec un tableau JSON valide, sans texte avant ni après, sans bloc de code markdown.

Format attendu :
[
  {
    "company": "Nom de l'entreprise",
    "contact_name": "Nom du contact, ou \\"\\" si non identifié",
    "role": "Poste du contact",
    "region": "Région / ville",
    "specialty": "Spécialité BTP",
    "size_hint": "Taille estimée de l'entreprise",
    "score": 0,
    "score_reason": "Pourquoi cette cible est pertinente (1-2 phrases)",
    "suggested_channel": "LinkedIn ou Email",
    "linkedin_url": "URL LinkedIn trouvée, ou \\"\\"",
    "email": "Email trouvé, ou \\"\\"",
    "source_summary": "Ce que tu as trouvé et où (1 phrase)"
  }
]"""

MESSAGE_SYSTEM_PROMPT = """Tu es un copilote de prospection B2B pour le secteur du BTP. Tu écris des \
messages de prospection courts, directs, crédibles, sans ton commercial lourd ni clichés. Tu écris \
comme un humain qui connaît le métier du BTP, pas comme une IA générique. Tu t'adresses à des dirigeants \
et responsables BTP qui ont peu de temps à perdre."""

SEQUENCE_SYSTEM_PROMPT = MESSAGE_SYSTEM_PROMPT + """

Tu rédiges une séquence de relance progressive : chaque message apporte un angle différent du \
précédent, ce n'est jamais une simple répétition. Le dernier message est une relance finale sobre, qui \
laisse la porte ouverte sans insister.

Réponds UNIQUEMENT avec un tableau JSON valide, sans texte avant ni après, sans bloc de code markdown.
Format :
[
  {"step": "Premier contact", "delay": "J0", "content": "..."},
  {"step": "Relance 1", "delay": "J+4", "content": "..."},
  {"step": "Relance 2", "delay": "J+9", "content": "..."}
]
Pour un email, inclus "Objet : ..." en première ligne de chaque "content"."""


def get_api_key() -> str:
    key = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""
    return key or os.environ.get("ANTHROPIC_API_KEY", "")


def _extract_json(text: str):
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


def _text_of(response) -> str:
    return "".join(b.text for b in response.content if b.type == "text").strip()


def search_prospects(api_key: str, criteria: dict, n: int) -> list:
    client = anthropic.Anthropic(api_key=api_key)
    user_prompt = f"""Critères de recherche :
- Zone géographique : {criteria['zone']}
- Poste recherché : {criteria['poste']}
- Spécialité BTP : {criteria['specialite']}
- Taille d'entreprise : {criteria['taille']}
- Contexte additionnel : {criteria['contexte'] or '(aucun)'}

Trouve {n} cibles de prospection pertinentes."""
    resp = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SEARCH_SYSTEM_PROMPT,
        tools=SEARCH_TOOLS,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return _extract_json(_text_of(resp))


def generate_message(api_key: str, prospect: dict, settings: dict, message_type: str, channel: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    user_prompt = f"""Prospect :
- Entreprise : {prospect['company']}
- Contact : {prospect.get('contact_name') or "(nom non identifié, adapte la formule d'introduction)"}
- Poste : {prospect.get('role', '')}
- Région : {prospect.get('region', '')}
- Spécialité BTP : {prospect.get('specialty', '')}
- Pourquoi cette cible : {prospect.get('score_reason', '')}

Notre offre : {settings.get('offer_context') or '(non précisée — reste générique sur la valeur apportée)'}
Expéditeur : {settings.get('sender_name', '')} — {settings.get('sender_company', '')}

Canal : {channel}
Type de message : {message_type}

Rédige le message. Pour un email, inclus une ligne "Objet : ..." suivie du corps. Pour LinkedIn, pas \
d'objet, message court (moins de 700 caractères). Pas de formule de politesse ringarde. Réponds \
uniquement avec le message, sans commentaire."""
    resp = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=MESSAGE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return _text_of(resp)


def generate_sequence(api_key: str, prospect: dict, settings: dict, channel: str) -> list:
    client = anthropic.Anthropic(api_key=api_key)
    user_prompt = f"""Prospect :
- Entreprise : {prospect['company']}
- Contact : {prospect.get('contact_name') or "(nom non identifié, adapte la formule d'introduction)"}
- Poste : {prospect.get('role', '')}
- Région : {prospect.get('region', '')}
- Spécialité BTP : {prospect.get('specialty', '')}
- Pourquoi cette cible : {prospect.get('score_reason', '')}

Notre offre : {settings.get('offer_context') or '(non précisée — reste générique sur la valeur apportée)'}
Expéditeur : {settings.get('sender_name', '')} — {settings.get('sender_company', '')}

Canal : {channel}

Rédige une séquence de relance en 3 étapes."""
    resp = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=SEQUENCE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return _extract_json(_text_of(resp))


def add_prospect(data: dict, r: dict) -> None:
    data["prospects"].append({
        "id": str(uuid.uuid4())[:8],
        "company": r.get("company", ""),
        "contact_name": r.get("contact_name", ""),
        "role": r.get("role", ""),
        "region": r.get("region", ""),
        "specialty": r.get("specialty", ""),
        "size_hint": r.get("size_hint", ""),
        "score": r.get("score", 0),
        "score_reason": r.get("score_reason", ""),
        "channel": r.get("suggested_channel") if r.get("suggested_channel") in CANAUX else "LinkedIn",
        "linkedin_url": r.get("linkedin_url", ""),
        "email": r.get("email", ""),
        "source_summary": r.get("source_summary", ""),
        "status": "À contacter",
        "notes": "",
        "messages": [],
        "created_at": now_iso(),
        "updated_at": now_iso(),
    })


# ══════════════════════════════════════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════════════════════════════════════
def render_search_page(data: dict, api_key: str) -> None:
    st.title("Rechercher des prospects BTP")
    st.caption(
        "L'agent utilise la recherche web pour identifier des entreprises et contacts BTP réels "
        "correspondant à vos critères. Rien n'est envoyé automatiquement."
    )

    col1, col2 = st.columns(2)
    with col1:
        zone = st.text_input("Zone géographique", value="France")
        poste = st.selectbox("Poste recherché", POSTES)
        specialite = st.selectbox("Spécialité BTP", SPECIALITES)
    with col2:
        taille = st.selectbox("Taille d'entreprise", TAILLES)
        n = st.slider("Nombre de prospects à rechercher", 3, 15, 5)
        contexte = st.text_area(
            "Contexte additionnel (optionnel)",
            placeholder="Ex : entreprises qui recrutent actuellement, qui ont un chantier récent, etc.",
        )

    if st.button("Lancer la recherche", type="primary", disabled=not api_key):
        with st.spinner("Recherche en cours…"):
            try:
                criteria = {"zone": zone, "poste": poste, "specialite": specialite, "taille": taille, "contexte": contexte}
                st.session_state.search_results = search_prospects(api_key, criteria, n)
            except Exception as e:
                st.error(f"Erreur lors de la recherche : {e}")
                st.session_state.search_results = []

    results = st.session_state.get("search_results", [])
    if results:
        st.subheader(f"{len(results)} résultat(s)")
        existing = {p["company"].strip().lower() for p in data["prospects"]}
        selected = []
        for i, r in enumerate(results):
            already = r.get("company", "").strip().lower() in existing
            label = f"{r.get('company', '?')} — {r.get('contact_name') or 'contact non identifié'} ({r.get('score', '?')}/100)"
            if already:
                label += " — déjà dans le CRM"
            with st.expander(label):
                st.write(
                    f"**Poste :** {r.get('role', '')}  \n**Région :** {r.get('region', '')}  \n"
                    f"**Spécialité :** {r.get('specialty', '')}  \n**Taille :** {r.get('size_hint', '')}"
                )
                st.write(f"**Pourquoi cette cible :** {r.get('score_reason', '')}")
                st.write(f"**Source :** {r.get('source_summary', '')}")
                if r.get("linkedin_url"):
                    st.write(f"LinkedIn : {r['linkedin_url']}")
                if r.get("email"):
                    st.write(f"Email : {r['email']}")
                st.write(f"**Canal suggéré :** {r.get('suggested_channel', '')}")
                if not already and st.checkbox("Ajouter au CRM", key=f"sel_{i}"):
                    selected.append(r)

        if selected and st.button(f"Ajouter {len(selected)} prospect(s) sélectionné(s) au CRM"):
            for r in selected:
                add_prospect(data, r)
            save_data(data)
            st.session_state.search_results = []
            st.success("Prospect(s) ajouté(s) à votre CRM.")
            st.rerun()


def render_prospect_detail(data: dict, prospect: dict, api_key: str) -> None:
    st.subheader(prospect["company"])
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(f"**Contact :** {prospect['contact_name'] or 'non identifié'} — {prospect['role']}")
        st.write(
            f"**Région :** {prospect['region']}  |  **Spécialité :** {prospect['specialty']}  |  "
            f"**Taille :** {prospect['size_hint']}"
        )
        st.write(f"**Score :** {prospect['score']}/100 — {prospect['score_reason']}")
        if prospect.get("linkedin_url"):
            st.write(f"LinkedIn : {prospect['linkedin_url']}")
        if prospect.get("email"):
            st.write(f"Email : {prospect['email']}")
    with col2:
        new_status = st.selectbox(
            "Statut", STATUTS,
            index=STATUTS.index(prospect["status"]) if prospect["status"] in STATUTS else 0,
            key=f"status_{prospect['id']}",
        )
        new_channel = st.selectbox(
            "Canal", CANAUX,
            index=CANAUX.index(prospect["channel"]) if prospect["channel"] in CANAUX else 0,
            key=f"channel_{prospect['id']}",
        )
        if new_status != prospect["status"] or new_channel != prospect["channel"]:
            prospect["status"], prospect["channel"], prospect["updated_at"] = new_status, new_channel, now_iso()
            save_data(data)

    notes = st.text_area("Notes", value=prospect.get("notes", ""), key=f"notes_{prospect['id']}")
    if notes != prospect.get("notes", ""):
        prospect["notes"], prospect["updated_at"] = notes, now_iso()
        save_data(data)

    st.divider()
    st.markdown("**Générer un message**")
    gcol1, gcol2, gcol3 = st.columns(3)
    with gcol1:
        msg_channel = st.selectbox("Canal du message", CANAUX, key=f"mchan_{prospect['id']}")
    with gcol2:
        msg_type = st.selectbox("Type", ["Premier contact", "Relance"], key=f"mtype_{prospect['id']}")
    with gcol3:
        st.write("")
        if st.button("Générer", key=f"gen_{prospect['id']}", disabled=not api_key):
            with st.spinner("Génération…"):
                try:
                    content = generate_message(api_key, prospect, data["settings"], msg_type, msg_channel)
                    prospect["messages"].append({
                        "type": msg_type, "channel": msg_channel, "content": content,
                        "generated_at": now_iso(), "sent": False, "sent_at": None,
                    })
                    if prospect["status"] == "À contacter":
                        prospect["status"] = "Message généré"
                    prospect["updated_at"] = now_iso()
                    save_data(data)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")

    if st.button("Générer une séquence de relance (3 étapes)", key=f"seq_{prospect['id']}", disabled=not api_key):
        with st.spinner("Génération de la séquence…"):
            try:
                steps = generate_sequence(api_key, prospect, data["settings"], prospect["channel"])
                for s in steps:
                    prospect["messages"].append({
                        "type": f"{s.get('step', 'Relance')} ({s.get('delay', '')})",
                        "channel": prospect["channel"],
                        "content": s.get("content", ""),
                        "generated_at": now_iso(), "sent": False, "sent_at": None,
                    })
                prospect["updated_at"] = now_iso()
                save_data(data)
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

    if prospect["messages"]:
        st.divider()
        st.markdown("**Historique des messages**")
        for real_idx in range(len(prospect["messages"]) - 1, -1, -1):
            m = prospect["messages"][real_idx]
            title = f"{m['type']} — {m['channel']} ({'envoyé' if m['sent'] else 'brouillon'})"
            with st.expander(title):
                st.text_area("Contenu", value=m["content"], height=150, key=f"content_{prospect['id']}_{real_idx}", disabled=True)
                sent = st.checkbox("Marqué comme envoyé", value=m["sent"], key=f"sent_{prospect['id']}_{real_idx}")
                if sent != m["sent"]:
                    m["sent"] = sent
                    m["sent_at"] = now_iso() if sent else None
                    prospect["updated_at"] = now_iso()
                    save_data(data)


def render_crm_page(data: dict, api_key: str) -> None:
    st.title("Mes prospects")
    prospects = data["prospects"]
    if not prospects:
        st.info("Aucun prospect pour le moment. Lancez une recherche pour commencer.")
        return

    overview = [{
        "Entreprise": p["company"], "Contact": p["contact_name"] or "—", "Poste": p["role"],
        "Région": p["region"], "Score": p["score"], "Statut": p["status"], "Canal": p["channel"],
    } for p in prospects]
    st.dataframe(overview, use_container_width=True, hide_index=True)

    st.divider()
    labels = [f"{p['company']} — {p['contact_name'] or 'contact non identifié'}" for p in prospects]
    idx = st.selectbox("Sélectionner un prospect", range(len(prospects)), format_func=lambda i: labels[i])
    render_prospect_detail(data, prospects[idx], api_key)


def render_settings_page(data: dict) -> None:
    st.title("Paramètres")
    st.caption("Ces informations servent de contexte pour générer des messages de prospection personnalisés.")
    settings = data["settings"]
    offer = st.text_area(
        "Votre entreprise et votre offre", value=settings.get("offer_context", ""), height=150,
        placeholder="Ex : Nous aidons les entreprises BTP à digitaliser leur suivi de chantier...",
    )
    sender_name = st.text_input("Votre nom", value=settings.get("sender_name", ""))
    sender_company = st.text_input("Votre entreprise", value=settings.get("sender_company", ""))
    if st.button("Enregistrer"):
        settings["offer_context"] = offer
        settings["sender_name"] = sender_name
        settings["sender_company"] = sender_company
        save_data(data)
        st.success("Paramètres enregistrés.")

    st.divider()
    st.caption(f"Clé API détectée : {'oui' if get_api_key() else 'non — définissez ANTHROPIC_API_KEY'}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(page_title="Prospect BTP AI", page_icon="▣", layout="wide")

data = load_data()
api_key = get_api_key()

st.sidebar.markdown("## Prospect BTP AI")
page = st.sidebar.radio(
    "Navigation", ["Rechercher des prospects", "Mes prospects", "Paramètres"], label_visibility="collapsed"
)
if not api_key:
    st.sidebar.warning("Clé ANTHROPIC_API_KEY manquante (variable d'environnement ou st.secrets).")

if page == "Rechercher des prospects":
    render_search_page(data, api_key)
elif page == "Mes prospects":
    render_crm_page(data, api_key)
else:
    render_settings_page(data)
