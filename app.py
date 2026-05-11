import os
import streamlit as st
import anthropic

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="K-VEFA AI",
    page_icon="🏗️",
    layout="centered",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Fond général */
  .stApp { background-color: #0f1117; }

  /* Header */
  .kvefa-header {
    text-align: center;
    padding: 2rem 0 1rem;
  }
  .kvefa-header h1 {
    font-size: 2rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .kvefa-header p {
    color: #8b9cb6;
    font-size: 0.9rem;
    margin: 0.4rem 0 0;
  }

  /* Badges modes */
  .modes-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    justify-content: center;
    margin: 1rem 0 1.5rem;
  }
  .mode-badge {
    background: #1e2535;
    color: #7dd3fc;
    border: 1px solid #2d3a52;
    border-radius: 999px;
    padding: 0.25rem 0.75rem;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.3px;
  }

  /* Messages */
  .stChatMessage { background: transparent !important; }
  [data-testid="stChatMessageContent"] { font-size: 0.95rem; line-height: 1.65; }

  /* Input */
  .stChatInputContainer { border-top: 1px solid #1e2535 !important; }
  .stChatInput textarea { background-color: #1a1f2e !important; color: #fff !important; }

  /* Bouton reset */
  .reset-btn { display: flex; justify-content: center; margin: 0.5rem 0 1.5rem; }
  div[data-testid="stButton"] > button {
    background: #1e2535;
    color: #8b9cb6;
    border: 1px solid #2d3a52;
    border-radius: 8px;
    font-size: 0.8rem;
    padding: 0.3rem 1rem;
  }
  div[data-testid="stButton"] > button:hover {
    background: #2d3a52;
    color: #fff;
    border-color: #3d4f6e;
  }
</style>
""", unsafe_allow_html=True)

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
    "📝  Crée un post LinkedIn sur les délais VEFA",
    "🔍  Analyse le site d'un promoteur",
    "✉️  Génère un DM de prospection pour Nexity",
    "🔄  Décline un sujet en 5 formats",
    "💡  Génère 10 hooks sur la réservation VEFA",
    "📊  Audit marketing d'un programme neuf",
]

# ── API key ───────────────────────────────────────────────────────────────────
api_key = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""
if not api_key:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="kvefa-header">
  <h1>🏗️ K-VEFA AI</h1>
  <p>Copilote IA pour la commercialisation VEFA & le marketing immobilier</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="modes-bar">
  <span class="mode-badge">✍️ Contenu</span>
  <span class="mode-badge">🔄 Repurposing</span>
  <span class="mode-badge">📨 Prospection</span>
  <span class="mode-badge">🔍 Analyse</span>
  <span class="mode-badge">📡 Veille</span>
  <span class="mode-badge">💡 Idéation</span>
</div>
""", unsafe_allow_html=True)

# ── API key saisie si absente ─────────────────────────────────────────────────
if not api_key:
    with st.expander("🔑 Configuration — Clé API Anthropic", expanded=True):
        api_key = st.text_input(
            "Clé API",
            type="password",
            placeholder="sk-ant-...",
            help="Obtenez votre clé sur console.anthropic.com",
        )
    if not api_key:
        st.info("Entrez votre clé API pour démarrer.")
        st.stop()

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Bouton reset ──────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔄  Nouvelle conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Suggestions si conversation vide ─────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("##### Que voulez-vous faire ?")
    cols = st.columns(2)
    for i, suggestion in enumerate(SUGGESTIONS):
        if cols[i % 2].button(suggestion, key=f"sug_{i}", use_container_width=True):
            # Extraire le texte sans l'emoji
            text = suggestion.split("  ", 1)[-1] if "  " in suggestion else suggestion
            st.session_state.messages.append({"role": "user", "content": text})
            st.rerun()
    st.markdown("---")

# ── Affichage historique ──────────────────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🏗️"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── Input ─────────────────────────────────────────────────────────────────────
prompt = st.chat_input("Posez votre question ou décrivez votre besoin VEFA…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🏗️"):
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
                        placeholder.markdown(full_response + "▌")

                final = stream.get_final_message()

            # Récupérer le texte si vide (cas outils serveur)
            if not full_response:
                for block in final.content:
                    if block.type == "text":
                        full_response += block.text

            placeholder.markdown(full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

        except anthropic.AuthenticationError:
            placeholder.error("Clé API invalide. Vérifiez votre clé Anthropic.")
        except Exception as e:
            placeholder.error(f"Erreur : {e}")
