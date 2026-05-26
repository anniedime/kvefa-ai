import os
import streamlit as st
import anthropic

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="K—VEFA Intelligence",
    page_icon="⬡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Design system — extrait de k-vefa.netlify.app ────────────────────────────
CSS = """
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
/* ── TOKENS ─────────────────────────────────────────────────────────────── */
:root {
  --bg:         #0A0E1A;
  --bg-2:       #0F1424;
  --bg-3:       #1A1F33;
  --gold:       #B8975E;
  --gold-lt:    #D4B574;
  --gold-dim:   rgba(184,151,94,0.10);
  --gold-border:rgba(184,151,94,0.22);
  --cream:      #F8F4ED;
  --txt:        #E8E2D5;
  --txt-muted:  rgba(232,226,213,0.55);
  --border:     rgba(232,226,213,0.09);
  --serif:      'Fraunces', Georgia, serif;
  --sans:       'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --ease:       cubic-bezier(.4,0,.2,1);
}

/* ── BASE ───────────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
  background: var(--bg) !important;
  font-family: var(--sans);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--txt);
}

/* Masquer tout le chrome Streamlit */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stDeployButton { display: none !important; }

/* Scrollbar premium */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
  background: rgba(184,151,94,0.25);
  border-radius: 2px;
}

/* Sélection texte */
::selection { background: var(--gold); color: var(--bg); }

/* ── CONTAINER ──────────────────────────────────────────────────────────── */
.block-container {
  max-width: 760px !important;
  padding: 0 24px 80px !important;
}

/* ── HEADER ─────────────────────────────────────────────────────────────── */
.kv-header {
  text-align: center;
  padding: 52px 0 36px;
}

.kv-logo {
  font-family: var(--serif);
  font-size: 1.9rem;
  font-weight: 500;
  color: var(--txt);
  letter-spacing: -0.025em;
  line-height: 1;
  margin-bottom: 10px;
}
.kv-logo em {
  color: var(--gold);
  font-style: normal;
}

.kv-tagline {
  font-family: var(--sans);
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--txt-muted);
}

.kv-rule {
  width: 36px;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
  margin: 18px auto 0;
}

/* ── MODES ──────────────────────────────────────────────────────────────── */
.kv-modes {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  justify-content: center;
  margin-bottom: 36px;
}
.kv-mode {
  font-family: var(--sans);
  font-size: 0.67rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gold);
  background: var(--gold-dim);
  border: 1px solid var(--gold-border);
  border-radius: 2px;
  padding: 5px 11px;
  white-space: nowrap;
}

/* ── SUGGESTIONS ────────────────────────────────────────────────────────── */
.kv-intro {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--txt-muted);
  text-align: center;
  margin-bottom: 16px;
}

.kv-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 9px;
  margin-bottom: 36px;
}

.kv-card {
  background: var(--bg-2);
  border: 1px solid var(--border);
  border-radius: 5px;
  padding: 15px 17px;
  cursor: pointer;
  transition: all .2s var(--ease);
  text-align: left;
  width: 100%;
}
.kv-card:hover {
  border-color: var(--gold-border);
  background: var(--bg-3);
  transform: translateY(-1px);
  box-shadow: 0 8px 32px -8px rgba(10,14,26,0.5);
}
.kv-card-tag {
  font-size: 0.64rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 5px;
}
.kv-card-text {
  font-size: 0.875rem;
  color: var(--txt);
  line-height: 1.45;
  font-weight: 400;
}

/* ── CHAT MESSAGES ──────────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
  background: transparent !important;
  padding: 0 !important;
  margin-bottom: 4px !important;
  gap: 12px !important;
}

/* Avatar user */
[data-testid="stChatMessageAvatarUser"] {
  background: rgba(248,244,237,0.12) !important;
  border-radius: 4px !important;
  width: 30px !important;
  min-width: 30px !important;
  height: 30px !important;
  font-size: 0.8rem !important;
  color: var(--cream) !important;
}

/* Avatar assistant */
[data-testid="stChatMessageAvatarAssistant"] {
  background: var(--gold) !important;
  border-radius: 4px !important;
  width: 30px !important;
  min-width: 30px !important;
  height: 30px !important;
  font-size: 0.8rem !important;
  color: var(--bg) !important;
}

/* Contenu user */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
[data-testid="stChatMessageContent"] {
  background: var(--cream) !important;
  color: #0A0E1A !important;
  border-radius: 2px 8px 8px 8px !important;
  padding: 13px 17px !important;
  font-size: 0.925rem !important;
  line-height: 1.65 !important;
  box-shadow: 0 2px 12px -4px rgba(10,14,26,0.18) !important;
  border: none !important;
  max-width: 88% !important;
}

/* Contenu assistant */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"])
[data-testid="stChatMessageContent"] {
  background: var(--bg-2) !important;
  color: var(--txt) !important;
  border-radius: 8px 2px 8px 8px !important;
  border: 1px solid var(--border) !important;
  padding: 18px 22px !important;
  font-size: 0.925rem !important;
  line-height: 1.75 !important;
  max-width: 92% !important;
}

/* Typographie dans les messages */
[data-testid="stChatMessageContent"] p {
  margin-bottom: 0.65em;
  color: inherit;
}
[data-testid="stChatMessageContent"] p:last-child { margin-bottom: 0; }

[data-testid="stChatMessageContent"] h1,
[data-testid="stChatMessageContent"] h2,
[data-testid="stChatMessageContent"] h3 {
  font-family: var(--serif) !important;
  font-weight: 500 !important;
  color: var(--txt) !important;
  letter-spacing: -0.02em !important;
  margin: 1em 0 0.4em !important;
  line-height: 1.2 !important;
}
[data-testid="stChatMessageContent"] h2 { font-size: 1.1rem !important; }
[data-testid="stChatMessageContent"] h3 { font-size: 1rem !important; }

[data-testid="stChatMessageContent"] strong {
  color: var(--txt) !important;
  font-weight: 600 !important;
}

[data-testid="stChatMessageContent"] ul,
[data-testid="stChatMessageContent"] ol {
  padding-left: 1.2em !important;
  margin: 0.4em 0 0.6em !important;
}
[data-testid="stChatMessageContent"] li {
  margin-bottom: 0.3em !important;
  line-height: 1.6 !important;
}

[data-testid="stChatMessageContent"] code {
  background: rgba(184,151,94,0.1) !important;
  color: var(--gold-lt) !important;
  border-radius: 3px !important;
  padding: 1px 5px !important;
  font-size: 0.85em !important;
}

[data-testid="stChatMessageContent"] hr {
  border-color: var(--border) !important;
  margin: 1em 0 !important;
}

/* User message text color overrides */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
[data-testid="stChatMessageContent"] strong,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
[data-testid="stChatMessageContent"] h1,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
[data-testid="stChatMessageContent"] h2,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
[data-testid="stChatMessageContent"] h3 {
  color: #0A0E1A !important;
}

/* ── INPUT ──────────────────────────────────────────────────────────────── */
.stChatInputContainer {
  background: var(--bg) !important;
  border-top: 1px solid var(--border) !important;
  padding: 14px 0 12px !important;
}

.stChatInput > div {
  background: var(--bg-2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 6px !important;
  transition: border-color .2s var(--ease), box-shadow .2s var(--ease) !important;
}

.stChatInput > div:focus-within {
  border-color: rgba(184,151,94,0.4) !important;
  box-shadow: 0 0 0 3px rgba(184,151,94,0.07) !important;
}

.stChatInput textarea {
  background: transparent !important;
  color: var(--txt) !important;
  font-family: var(--sans) !important;
  font-size: 0.935rem !important;
  line-height: 1.55 !important;
  padding: 13px 16px !important;
  caret-color: var(--gold) !important;
  border: none !important;
  box-shadow: none !important;
}

.stChatInput textarea::placeholder {
  color: var(--txt-muted) !important;
  font-size: 0.9rem !important;
}

/* Bouton envoi */
[data-testid="stChatInputSubmitButton"] button,
.stChatInputContainer button[kind="primaryFormSubmit"] {
  background: var(--gold) !important;
  border-radius: 4px !important;
  border: none !important;
  color: var(--bg) !important;
  transition: all .2s var(--ease) !important;
}
[data-testid="stChatInputSubmitButton"] button:hover,
.stChatInputContainer button[kind="primaryFormSubmit"]:hover {
  background: #A07F47 !important;
  transform: translateY(-1px) !important;
}

/* ── BOUTON RESET ───────────────────────────────────────────────────────── */
div[data-testid="stButton"] > button {
  background: transparent !important;
  color: var(--txt-muted) !important;
  border: 1px solid var(--border) !important;
  border-radius: 3px !important;
  font-family: var(--sans) !important;
  font-size: 0.7rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  padding: 7px 18px !important;
  transition: all .2s var(--ease) !important;
  display: block !important;
  margin: 0 auto !important;
}
div[data-testid="stButton"] > button:hover {
  background: rgba(232,226,213,0.05) !important;
  border-color: rgba(232,226,213,0.22) !important;
  color: var(--txt) !important;
}

/* ── API KEY ────────────────────────────────────────────────────────────── */
[data-testid="stExpander"] {
  background: var(--bg-2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 6px !important;
}
[data-testid="stExpander"] summary {
  color: var(--txt-muted) !important;
  font-size: 0.85rem !important;
  font-family: var(--sans) !important;
}
[data-testid="stTextInput"] input {
  background: var(--bg-3) !important;
  color: var(--txt) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
  font-family: var(--sans) !important;
  font-size: 0.9rem !important;
  caret-color: var(--gold) !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--gold-border) !important;
  box-shadow: 0 0 0 2px rgba(184,151,94,0.07) !important;
}
[data-testid="stTextInput"] label {
  color: var(--txt-muted) !important;
  font-size: 0.8rem !important;
}

/* ── ALERTS ─────────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
  background: rgba(184,151,94,0.06) !important;
  border: 1px solid var(--gold-border) !important;
  border-radius: 5px !important;
  color: var(--txt) !important;
}

/* ── CURSOR ANIMATION ───────────────────────────────────────────────────── */
@keyframes kv-blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0; }
}
.kv-cursor {
  display: inline-block;
  width: 2px;
  height: 0.9em;
  background: var(--gold);
  margin-left: 2px;
  border-radius: 1px;
  animation: kv-blink 1.1s var(--ease) infinite;
  vertical-align: text-bottom;
}

/* ── FOOTER DISCRET ─────────────────────────────────────────────────────── */
.kv-footer {
  text-align: center;
  padding: 20px 0 0;
  font-size: 0.67rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(232,226,213,0.2);
}

/* ── DIVIDER CONVERSATION ───────────────────────────────────────────────── */
.kv-conv-label {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 28px;
  font-size: 0.67rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(232,226,213,0.22);
}
.kv-conv-label::before,
.kv-conv-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}
</style>
"""

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """Tu es K-VEFA AI, un copilote IA spécialisé dans :
- la commercialisation VEFA,
- le marketing immobilier neuf,
- la création de contenu multi-réseaux,
- la prospection B2B immobilière,
- l'analyse rapide de promoteurs immobiliers,
- la veille commerciale et marketing.

Tu travailles pour une entreprise qui aide les promoteurs immobiliers et équipes commerciales à :
- accélérer leurs lancements VEFA,
- améliorer leur visibilité,
- générer plus de leads,
- créer du contenu plus rapidement,
- détecter des opportunités commerciales,
- optimiser leur communication digitale.

Ton rôle principal n'est PAS d'être un assistant généraliste.

Tu es :
- un accélérateur de contenu,
- un assistant de prospection,
- un analyseur marketing immobilier,
- un générateur d'angles commerciaux,
- un copilote commercial VEFA.

Tu écris comme :
- un directeur marketing immobilier,
- un consultant VEFA senior,
- un expert LinkedIn B2B,
- un copywriter business moderne.

--------------------------------------------------
# OBJECTIFS PRINCIPAUX
--------------------------------------------------

Tes priorités sont :

1. Générer rapidement du contenu à forte valeur
2. Transformer une idée en contenus multi-plateformes
3. Générer des opportunités commerciales
4. Identifier des prospects intéressants
5. Produire des hooks performants
6. Automatiser la génération d'idées marketing
7. Aider les équipes commerciales à gagner du temps
8. Créer des messages de prospection naturels
9. Détecter les faiblesses marketing des promoteurs
10. Générer des conversations business.

--------------------------------------------------
# CONNAISSANCE METIER
--------------------------------------------------

Tu comprends parfaitement :
- les lancements VEFA,
- les promoteurs immobiliers,
- les commercialisateurs,
- les sites programmes,
- les sélecteurs de lots,
- les problématiques marketing immobilières,
- les workflows commerciaux VEFA,
- les enjeux de visibilité,
- les problématiques de génération de leads,
- les dépendances entre prestataires,
- les retards de lancement,
- les problématiques de coordination marketing/commercial.

Tu connais :
- le vocabulaire métier,
- les objections des promoteurs,
- les KPIs commerciaux,
- les enjeux ROI,
- les problématiques de branding immobilier,
- les tendances du marché immobilier neuf.

--------------------------------------------------
# ROLE DU SCRAPING
--------------------------------------------------

Le scraping est utilisé comme un système d'enrichissement intelligent.

Quand l'utilisateur fournit :
- une URL,
- un profil LinkedIn,
- un nom d'entreprise,
- un site web,
- un promoteur,
- un programme immobilier,

tu dois automatiquement utiliser l'outil web_fetch pour récupérer les informations, puis :

1. Extraire les informations utiles
2. Identifier les signaux business
3. Détecter les opportunités marketing
4. Détecter les faiblesses de communication
5. Identifier des angles de prospection
6. Générer des insights exploitables.

Le scraping doit toujours servir :
- la prospection,
- le contenu,
- l'analyse commerciale,
- la génération d'idées.

--------------------------------------------------
# MODES OPERATIONNELS
--------------------------------------------------

Tu peux fonctionner dans plusieurs modes et les détecter automatiquement.

## MODE CONTENT → Création de contenu multi-réseaux.
## MODE REPURPOSING → Transformation d'un contenu en plusieurs formats.
## MODE PROSPECTION → Création de messages commerciaux personnalisés.
## MODE ANALYSE → Audit rapide d'un promoteur ou d'une présence digitale.
## MODE VEILLE → Analyse de tendances et détection d'opportunités.
## MODE IDEATION → Génération d'idées, hooks et angles marketing.

--------------------------------------------------
# CREATION DE CONTENU
--------------------------------------------------

Quand tu crées du contenu :

Tu dois :
- écrire de façon conversationnelle,
- optimiser pour lecture mobile,
- éviter le ton corporate,
- éviter le jargon IA,
- privilégier les phrases courtes,
- favoriser l'engagement,
- utiliser des hooks forts,
- utiliser des insights métier,
- rester crédible et concret.

Le contenu doit être : expert, simple, moderne, humain, orienté business, utile, non générique.

--------------------------------------------------
# REGLES LINKEDIN
--------------------------------------------------

Quand tu écris un post LinkedIn :

Tu dois :
- générer 5 hooks,
- générer 3 CTA,
- optimiser le temps de lecture,
- créer de la curiosité,
- utiliser des lignes courtes,
- éviter les blocs longs,
- favoriser les commentaires,
- éviter le ton vendeur.

Le post doit contenir : un hook, un développement, un insight, une conclusion, un CTA subtil.

--------------------------------------------------
# GENERATION D'ANGLES
--------------------------------------------------

Quand on te donne un sujet, génère :
- angles business, émotionnels, ROI, différenciants, éducatifs, "pain points", controversés crédibles.

Evite : les banalités, les angles génériques, les formulations vues partout.

--------------------------------------------------
# MODE ANALYSE PROMOTEUR
--------------------------------------------------

Quand tu analyses un promoteur, fournis :

## SCORE GLOBAL /100
## FORCES
## FAIBLESSES
## OPPORTUNITES
## QUICK WINS
## ANGLE DE PROSPECTION
## ACTIONS PRIORITAIRES

--------------------------------------------------
# MODE PROSPECTION
--------------------------------------------------

Quand tu génères un message commercial :

Tu dois : personnaliser l'approche, mentionner un élément spécifique, rester naturel, être crédible, être court, créer de la curiosité, éviter les formulations génériques.

Tu peux générer : DM LinkedIn, emails, relances, séquences de suivi.

--------------------------------------------------
# STRUCTURE DE SORTIE
--------------------------------------------------

Quand pertinent, structure les réponses ainsi :

## CONTEXTE
## INSIGHTS
## OPPORTUNITES
## CONTENU GENERE
## ANGLE COMMERCIAL
## ACTIONS RECOMMANDEES

--------------------------------------------------
# STYLE D'ECRITURE
--------------------------------------------------

Tu écris toujours : comme un humain, comme un expert métier, de façon concise, crédible, moderne, business.
Tu évites : les clichés IA, le ton corporate vide, les formulations génériques, les réponses vagues.
Tu dois agir comme : un copilote commercial, un accélérateur de contenu, un assistant marketing VEFA ultra réactif."""

TOOLS = [
    {"type": "web_search_20260209", "name": "web_search"},
    {"type": "web_fetch_20260209", "name": "web_fetch"},
]

SUGGESTIONS = [
    ("CONTENU",      "Crée un post LinkedIn sur les délais VEFA"),
    ("ANALYSE",      "Analyse le site d'un promoteur"),
    ("PROSPECTION",  "Génère un DM pour prospecter Nexity"),
    ("REPURPOSING",  "Décline un sujet en 5 formats"),
    ("IDÉATION",     "Génère 10 hooks sur la réservation VEFA"),
    ("AUDIT",        "Audit marketing d'un programme neuf"),
]

MODES = ["Contenu", "Repurposing", "Prospection", "Analyse", "Veille", "Idéation"]

# ── API key ───────────────────────────────────────────────────────────────────
api_key = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""
if not api_key:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

# ── Inject design system ──────────────────────────────────────────────────────
st.markdown(CSS, unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="kv-header">
  <div class="kv-logo">K<em>—</em>VEFA</div>
  <div class="kv-tagline">Intelligence · Prospection · Contenu · Analyse</div>
  <div class="kv-rule"></div>
</div>
""", unsafe_allow_html=True)

# ── Modes bar ─────────────────────────────────────────────────────────────────
modes_html = '<div class="kv-modes">' + "".join(
    f'<span class="kv-mode">{m}</span>' for m in MODES
) + "</div>"
st.markdown(modes_html, unsafe_allow_html=True)

# ── API key saisie si absente ─────────────────────────────────────────────────
if not api_key:
    with st.expander("🔑 Configurer la clé API", expanded=True):
        api_key = st.text_input(
            "Clé API Anthropic",
            type="password",
            placeholder="sk-ant-...",
            help="console.anthropic.com → API Keys",
        )
    if not api_key:
        st.info("Entrez votre clé API pour accéder à K—VEFA Intelligence.")
        st.stop()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Reset ─────────────────────────────────────────────────────────────────────
if st.session_state.messages:
    if st.button("↺  Nouvelle conversation"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── Suggestions si conversation vide ─────────────────────────────────────────
if not st.session_state.messages:
    st.markdown('<div class="kv-intro">Par où souhaitez-vous commencer ?</div>', unsafe_allow_html=True)

    st.markdown('<div class="kv-grid">', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (tag, text) in enumerate(SUGGESTIONS):
        with cols[i % 2]:
            if st.button(
                f"**{tag}**\n{text}",
                key=f"sug_{i}",
                use_container_width=True,
            ):
                st.session_state.messages.append({"role": "user", "content": text})
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="kv-footer">
      K—VEFA Intelligence &nbsp;·&nbsp; Propulsé par Claude Opus
    </div>
    """, unsafe_allow_html=True)

# ── Historique conversation ───────────────────────────────────────────────────
if st.session_state.messages:
    st.markdown('<div class="kv-conv-label">Conversation</div>', unsafe_allow_html=True)

for msg in st.session_state.messages:
    avatar = "◇" if msg["role"] == "user" else "◆"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── Input ─────────────────────────────────────────────────────────────────────
prompt = st.chat_input("Décrivez votre besoin VEFA…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="◇"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="◆"):
        placeholder = st.empty()
        full_response = ""

        try:
            client = anthropic.Anthropic(api_key=api_key)

            with client.messages.stream(
                model="claude-opus-4-7",
                max_tokens=8192,
                system=[
                    {
                        "type": "text",
                        "text": SYSTEM_PROMPT,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                tools=TOOLS,
                messages=st.session_state.messages,
            ) as stream:
                for event in stream:
                    if (
                        event.type == "content_block_delta"
                        and event.delta.type == "text_delta"
                    ):
                        full_response += event.delta.text
                        placeholder.markdown(full_response + '<span class="kv-cursor"></span>', unsafe_allow_html=True)

                final = stream.get_final_message()

            if not full_response:
                for block in final.content:
                    if block.type == "text":
                        full_response += block.text

            placeholder.markdown(full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

        except anthropic.AuthenticationError:
            placeholder.error("Clé API invalide.")
        except Exception as e:
            placeholder.error(f"Erreur : {e}")
