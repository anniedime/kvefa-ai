import os
import json
from datetime import datetime
from pathlib import Path
import streamlit as st
import anthropic

# ══════════════════════════════════════════════════════════════════════════════
# STORAGE — mémoire persistante (conversations + activité réelle)
# ══════════════════════════════════════════════════════════════════════════════
HISTORY_FILE = Path(__file__).parent / "conversations.json"
MAX_CONVS = 50          # limite stockage
MAX_RECENT = 5          # affichées dans "Activité récente"

def load_history() -> dict:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"conversations": []}

def save_history(data: dict) -> None:
    try:
        HISTORY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass  # silent fail (FS read-only possible sur certains hébergeurs)

def make_conv_id() -> str:
    return "conv_" + datetime.now().strftime("%Y%m%d%H%M%S%f")

def make_title(text: str, max_len: int = 64) -> str:
    title = text.strip().split("\n")[0]
    if len(title) > max_len:
        title = title[:max_len].rsplit(" ", 1)[0] + "…"
    return title or "Nouvelle conversation"

def relative_time(iso_ts: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_ts)
        delta = datetime.now() - dt
        s = int(delta.total_seconds())
        if s < 60:    return f"{s}s"
        if s < 3600:  return f"{s // 60} min"
        if s < 86400: return f"{s // 3600}h"
        d = s // 86400
        return f"{d}j" if d < 7 else dt.strftime("%d %b")
    except Exception:
        return "—"

def detect_category(text: str):
    """Devine icône + couleur en fonction du contenu (pour l'activité)."""
    t = text.lower()
    if any(k in t for k in ["dm linkedin", "prospect", "prospecter", "promoteur"]):
        return ("◈", "blue")
    if any(k in t for k in ["analys", "audit", "score", "marché", "tendance", "zone"]):
        return ("◎", "gold")
    if any(k in t for k in ["post linkedin", "contenu", "hook", "caption", "reel", "newsletter"]):
        return ("✎", "pink")
    if any(k in t for k in ["veille", "opportunité", "signal", "détect"]):
        return ("↗", "green")
    return ("✦", "violet")

def save_current_conversation() -> None:
    """Persiste la conversation courante (st.session_state.messages) sur disque."""
    if not st.session_state.get("messages"):
        return
    history = load_history()
    conv_id = st.session_state.get("current_conv_id")
    first_user = next((m["content"] for m in st.session_state.messages if m["role"] == "user"), "")
    now = datetime.now().isoformat()

    existing = next((c for c in history["conversations"] if c["id"] == conv_id), None)
    if existing:
        existing["messages"] = st.session_state.messages
        existing["updated_at"] = now
        if first_user:
            existing["title"] = make_title(first_user)
    else:
        new_id = conv_id or make_conv_id()
        st.session_state.current_conv_id = new_id
        history["conversations"].append({
            "id": new_id,
            "title": make_title(first_user) if first_user else "Nouvelle conversation",
            "started_at": now,
            "updated_at": now,
            "messages": st.session_state.messages,
        })

    # tri du plus récent au plus ancien, limite MAX_CONVS
    history["conversations"].sort(key=lambda c: c.get("updated_at", c.get("started_at", "")), reverse=True)
    history["conversations"] = history["conversations"][:MAX_CONVS]
    save_history(history)

st.set_page_config(
    page_title="K—VEFA Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — v4 minimal premium
# ══════════════════════════════════════════════════════════════════════════════
CSS = """
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;1,9..144,300;1,9..144,400&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>

/* ── TOKENS ──────────────────────────────────────────────────────────────── */
:root {
  --bg:     #0A0E1A;
  --bg-2:   #0F1320;
  --bg-3:   #141828;
  --gold:   #C4A46B;
  --gold-lt:#D4B98A;
  --gold-dk:#A07A42;
  --g6:  rgba(196,164,107,0.06);
  --g10: rgba(196,164,107,0.10);
  --g18: rgba(196,164,107,0.18);
  --gbr: rgba(196,164,107,0.20);
  --cream: #EDE7D4;
  --txt:   #E4DDC8;
  --txt2:  rgba(228,221,200,0.62);
  --txt3:  rgba(228,221,200,0.36);
  --bd:    rgba(228,221,200,0.07);
  --bd2:   rgba(228,221,200,0.04);
  --serif: 'Fraunces', Georgia, serif;
  --sans:  'Inter', -apple-system, sans-serif;
  --ease:  cubic-bezier(.4,0,.2,1);
  --eout:  cubic-bezier(0,.55,.45,1);
}

/* ── RESET ───────────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body { background: var(--bg) !important; font-family: var(--sans); -webkit-font-smoothing: antialiased; }
.stApp { background: var(--bg) !important; color: var(--txt); }

/* ── BACKGROUND — discret ────────────────────────────────────────────────── */
.stApp::before {
  content: '';
  position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background:
    radial-gradient(ellipse 100% 50% at 50% 0%, rgba(196,164,107,0.035) 0%, transparent 60%),
    radial-gradient(ellipse 80% 60% at 100% 100%, rgba(196,164,107,0.018) 0%, transparent 50%);
}

/* ── CHROME HIDE ─────────────────────────────────────────────────────────── */
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], .stDeployButton, header[data-testid="stHeader"] { display: none !important; }

/* ── SCROLLBAR ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(196,164,107,0.18); border-radius: 2px; }
::selection { background: rgba(196,164,107,0.22); color: var(--cream); }

/* ── LAYOUT ──────────────────────────────────────────────────────────────── */
section[data-testid="stMain"], .main {
  display: flex !important; flex-direction: column !important;
  min-height: 100vh !important; overflow-y: auto !important;
}
.block-container, [data-testid="stAppViewBlockContainer"] {
  flex: 1 1 auto !important;
  padding: 48px 64px 32px !important;
  max-width: 1280px !important;
  margin: 0 auto !important;
  position: relative; z-index: 1;
}
[data-testid="stChatInputContainer"] { flex-shrink: 0 !important; margin-top: auto !important; }

/* ── SIDEBAR — épurée ────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--bg-2) !important;
  border-right: 1px solid var(--bd) !important;
  min-width: 240px !important; max-width: 260px !important;
}
[data-testid="stSidebar"] { height: 100vh !important; }
[data-testid="stSidebarContent"] {
  padding: 0 !important; background: transparent !important;
  display: flex !important; flex-direction: column !important;
  height: 100vh !important;
}

.kv-logo-wrap { padding: 30px 24px 22px; }
.kv-logotype {
  font-family: var(--serif); font-size: 1.5rem; font-weight: 400;
  color: var(--txt); letter-spacing: -0.025em; line-height: 1;
  display: flex; align-items: center; margin-bottom: 12px;
}
/* Tiret entre K et VEFA — petite barre CSS dessinée, contrôle pixel-perfect.
   Le caractère em-dash unicode reste trop dominant même réduit ; une barre
   CSS de 7px × 1.5px à mi-hauteur des capitales donne un rendu typographique
   plus serré et premium type Apple / Linear. */
.kv-logotype em {
  display: inline-block;
  width: 7px;
  height: 1.5px;
  background: var(--gold);
  opacity: 0.55;
  border-radius: 1px;
  margin: 0 6px;
  vertical-align: middle;
  position: relative;
  top: -3px;
  font-size: 0 !important;          /* masque le caractère original */
  color: transparent !important;
  text-indent: -9999px;              /* fallback masquage du glyphe */
  overflow: hidden;
}
.kv-logotype-badge {
  display: inline-flex; align-items: center;
  font-size: 0.5rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--bg); background: var(--gold); border-radius: 3px;
  padding: 2px 6px; margin-left: 10px; position: relative; top: -2px;
}
.kv-ai-status { display: flex; align-items: center; gap: 7px; }
.kv-status-ring {
  width: 6px; height: 6px; border-radius: 50%; background: #4ADE80;
  box-shadow: 0 0 8px rgba(74,222,128,0.5);
  animation: kv-pulse-green 2.4s ease-in-out infinite;
}
.kv-status-label {
  font-size: 0.58rem; font-weight: 600; letter-spacing: 0.14em;
  text-transform: uppercase; color: rgba(74,222,128,0.7);
}

/* Nav block — espacement vertical strict */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0 !important; }
[data-testid="stSidebar"] [data-testid="stElementContainer"] { margin: 0 !important; }
[data-testid="stSidebar"] .stButton { margin: 0 !important; padding: 0 !important; }

/* Nav buttons — flex strict, aligné gauche, icônes via ::before */
[data-testid="stSidebar"] [data-testid="stButton"] button {
  display: flex !important;
  align-items: center !important;
  justify-content: flex-start !important;
  text-align: left !important;
  background: transparent !important;
  border: none !important;
  color: var(--txt2) !important;
  font-family: var(--sans) !important;
  font-size: 0.88rem !important;
  font-weight: 400 !important;
  padding: 14px 24px !important;
  margin: 0 !important;
  border-radius: 0 !important;
  width: 100% !important;
  border-left: 2px solid transparent !important;
  letter-spacing: 0 !important;
  text-transform: none !important;
  transition: background .15s var(--ease), color .15s var(--ease), border-color .15s var(--ease) !important;
  line-height: 1.2 !important;
  min-height: 44px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button > div,
[data-testid="stSidebar"] [data-testid="stButton"] button p,
[data-testid="stSidebar"] [data-testid="stButton"] button [data-testid="stMarkdownContainer"] {
  margin: 0 !important;
  padding: 0 !important;
  text-align: left !important;
  width: auto !important;
  font-size: inherit !important;
  line-height: 1.2 !important;
  display: inline !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
  background: var(--g6) !important;
  color: var(--txt) !important;
  border-left-color: var(--gbr) !important;
}

/* Icon column — fixed width via ::before, alignée parfaitement */
[data-testid="stSidebar"] [class*="st-key-nav_"] button::before {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 22px !important;
  margin-right: 14px !important;
  color: var(--gold) !important;
  opacity: 0.7 !important;
  font-size: 0.95rem !important;
  flex-shrink: 0 !important;
  line-height: 1 !important;
}
[data-testid="stSidebar"] .st-key-nav_centre button::before      { content: "✦"; }
[data-testid="stSidebar"] .st-key-nav_prospection button::before { content: "◈"; }
[data-testid="stSidebar"] .st-key-nav_analyse button::before     { content: "◎"; }
[data-testid="stSidebar"] .st-key-nav_contenu button::before     { content: "✎"; }
[data-testid="stSidebar"] .st-key-nav_veille button::before      { content: "◉"; }
[data-testid="stSidebar"] [class*="st-key-nav_"] button:hover::before {
  opacity: 1 !important;
  color: var(--gold-lt) !important;
}

/* État actif — Centre de commande quand pas de conversation */
[data-testid="stSidebar"] .st-key-nav_centre.kv-active button {
  background: var(--g10) !important;
  color: var(--gold-lt) !important;
  border-left-color: var(--gold) !important;
}
[data-testid="stSidebar"] .st-key-nav_centre.kv-active button::before {
  opacity: 1 !important;
  color: var(--gold-lt) !important;
}

/* Espacement nav <-> profil */
.kv-nav-wrap { padding: 4px 0 0; }

/* Le stVerticalBlock interne doit aussi être flex column 100% — sinon le
   spacer ne sait pas sur quoi grandir. */
[data-testid="stSidebar"] section[data-testid="stSidebarContent"] > div:first-child,
[data-testid="stSidebar"] section[data-testid="stSidebarContent"] > [data-testid="stVerticalBlock"] {
  display: flex !important;
  flex-direction: column !important;
  flex: 1 1 auto !important;
  height: 100% !important;
  min-height: 100vh !important;
}

/* Spacer — pousse le profil en bas */
.kv-sidebar-spacer { flex: 1 1 auto; min-height: 220px; }
[data-testid="stSidebar"] [data-testid="stElementContainer"]:has(.kv-sidebar-spacer) {
  flex: 1 1 auto !important;
  min-height: 220px !important;
}

/* Séparateur subtil au-dessus du profil */
.kv-user-divider {
  height: 1px;
  background: var(--bd);
  margin: 0 22px 18px;
  opacity: 0.7;
}

/* User profile bottom — ancré naturellement en bas */
.kv-user {
  margin: 0 16px 22px;
  padding: 13px 14px;
  background: var(--bg-3);
  border: 1px solid var(--bd);
  border-radius: 10px;
  display: flex; align-items: center; gap: 12px;
  cursor: pointer; transition: border-color .2s var(--ease), background .2s var(--ease);
}
.kv-user:hover { background: rgba(196,164,107,0.04); }
.kv-user:hover { border-color: var(--gbr); }
.kv-user-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  background: linear-gradient(135deg, var(--gold-dk), var(--gold-lt));
  display: flex; align-items: center; justify-content: center;
  font-family: var(--serif); font-size: 0.85rem; font-weight: 500;
  color: var(--bg); flex-shrink: 0;
}
.kv-user-info { flex: 1; min-width: 0; }
.kv-user-name { font-size: 0.8rem; color: var(--txt); font-weight: 500; line-height: 1.2; }
.kv-user-plan { font-size: 0.65rem; color: var(--txt3); margin-top: 2px; }
.kv-user-chev { color: var(--txt3); font-size: 0.7rem; }

/* ── TOP-RIGHT BADGE ─────────────────────────────────────────────────────── */
.kv-top-badge {
  position: fixed; top: 22px; right: 36px; z-index: 100;
  display: flex; align-items: center; gap: 8px;
  padding: 8px 14px;
  background: var(--bg-2);
  border: 1px solid var(--bd);
  border-radius: 100px;
  font-size: 0.72rem; color: var(--txt2);
  font-weight: 500;
}
.kv-top-badge-icon {
  display: inline-flex; gap: 2px; align-items: center;
}
.kv-top-badge-icon span {
  display: inline-block; width: 2px; background: var(--gold);
  border-radius: 1px; animation: kv-wave 1.4s ease-in-out infinite;
}
.kv-top-badge-icon span:nth-child(1) { height: 6px;  animation-delay: 0s; }
.kv-top-badge-icon span:nth-child(2) { height: 10px; animation-delay: .15s; }
.kv-top-badge-icon span:nth-child(3) { height: 7px;  animation-delay: .3s; }
.kv-top-badge-icon span:nth-child(4) { height: 11px; animation-delay: .45s; }
@keyframes kv-wave { 0%,100% { transform: scaleY(1); opacity: .9; } 50% { transform: scaleY(.4); opacity: .5; } }

/* ── GREETING ────────────────────────────────────────────────────────────── */
.kv-greeting { margin-bottom: 30px; animation: kv-fade-up .5s var(--eout) both; }
.kv-greeting-title {
  font-family: var(--serif); font-weight: 400;
  font-size: clamp(2rem, 3.5vw, 2.8rem);
  color: var(--txt); letter-spacing: -0.025em;
  line-height: 1.1; margin: 0;
}
.kv-greeting-sub {
  font-family: var(--serif); font-weight: 300; font-style: italic;
  font-size: clamp(1.4rem, 2.4vw, 1.9rem);
  color: var(--gold); letter-spacing: -0.02em;
  line-height: 1.15; margin: 6px 0 0;
}

/* ── WELCOME INPUT (au-dessus, pas en bas) ───────────────────────────────── */
.kv-welcome-input-wrap {
  margin-bottom: 32px;
  animation: kv-fade-up .55s var(--eout) .08s both;
}
[data-testid="stForm"] {
  background: var(--bg-2) !important;
  border: 1px solid var(--bd) !important;
  border-radius: 12px !important;
  padding: 8px !important;
  transition: border-color .25s var(--ease), box-shadow .25s var(--ease) !important;
  box-shadow: 0 0 0 4px rgba(196,164,107,0.03), 0 8px 32px -12px rgba(0,0,0,0.5) !important;
}
[data-testid="stForm"]:focus-within {
  border-color: var(--gbr) !important;
  box-shadow: 0 0 0 5px rgba(196,164,107,0.05), 0 12px 40px -10px rgba(196,164,107,0.12) !important;
}
[data-testid="stForm"] [data-testid="stTextInput"] input {
  background: transparent !important;
  border: none !important;
  font-family: var(--sans) !important;
  font-size: 0.95rem !important;
  color: var(--txt) !important;
  padding: 14px 18px !important;
  caret-color: var(--gold) !important;
}
[data-testid="stForm"] [data-testid="stTextInput"] input::placeholder { color: var(--txt3) !important; }
[data-testid="stForm"] [data-testid="stTextInput"] > div { border: none !important; box-shadow: none !important; background: transparent !important; }
[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {
  background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dk) 100%) !important;
  border: none !important;
  color: var(--bg) !important;
  width: 44px !important; height: 44px !important;
  min-width: 44px !important;
  padding: 0 !important;
  border-radius: 8px !important;
  font-size: 1.1rem !important; font-weight: 600 !important;
  letter-spacing: 0 !important; text-transform: none !important;
  box-shadow: 0 4px 14px rgba(196,164,107,0.3) !important;
  transition: all .2s var(--ease) !important;
  display: flex !important; align-items: center !important; justify-content: center !important;
}
[data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover {
  background: linear-gradient(135deg, var(--gold-lt) 0%, var(--gold) 100%) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 18px rgba(196,164,107,0.4) !important;
}

/* ── SECTION LABELS ──────────────────────────────────────────────────────── */
.kv-section-tag {
  font-size: 0.62rem; font-weight: 700; letter-spacing: 0.22em;
  text-transform: uppercase; color: var(--txt3);
  margin: 28px 0 14px;
}

/* ── ACTION CARDS — 3 horizontales plates ────────────────────────────────── */
.kv-actions-grid {
  display: grid; grid-template-columns: 1fr 1fr 1fr;
  gap: 14px; margin-bottom: 10px;
  animation: kv-fade-up .6s var(--eout) .12s both;
}
.kv-action-card {
  display: block; text-decoration: none;
  background: var(--bg-2);
  border: 1px solid var(--bd);
  border-radius: 10px;
  padding: 22px 24px;
  cursor: pointer;
  transition: all .22s var(--ease);
  position: relative;
}
.kv-action-card:hover {
  background: var(--bg-3);
  border-color: var(--gbr);
  transform: translateY(-2px);
  box-shadow: 0 12px 32px -16px rgba(196,164,107,0.18);
}
.kv-action-icon {
  font-size: 1.35rem;
  color: var(--gold);
  margin-bottom: 14px;
  opacity: 0.92;
  line-height: 1;
}
.kv-action-title {
  font-family: var(--sans); font-size: 1rem; font-weight: 500;
  color: var(--txt); letter-spacing: -0.01em;
  margin-bottom: 3px;
}
.kv-action-desc {
  font-size: 0.8rem; color: var(--txt2);
  line-height: 1.4;
}

/* ── ACTIVITY LIST — épurée ──────────────────────────────────────────────── */
.kv-act-list {
  animation: kv-fade-up .65s var(--eout) .18s both;
}
.kv-act-item {
  display: flex; align-items: center; gap: 14px;
  padding: 14px 4px;
  border-bottom: 1px solid var(--bd2);
  transition: background .15s var(--ease);
}
.kv-act-item:hover { background: rgba(196,164,107,0.025); }
.kv-act-item:last-child { border-bottom: none; }
.kv-act-icon {
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.85rem;
  border-radius: 6px;
  flex-shrink: 0;
}
.kv-act-icon.gold { background: var(--g10); color: var(--gold); }
.kv-act-icon.blue { background: rgba(96,165,250,0.10); color: #93C5FD; }
.kv-act-icon.green { background: rgba(74,222,128,0.10); color: #6EE7B7; }
.kv-act-icon.pink { background: rgba(244,114,182,0.10); color: #F9A8D4; }
.kv-act-icon.violet { background: rgba(167,139,250,0.10); color: #C4B5FD; }
.kv-act-text {
  flex: 1; font-size: 0.86rem; color: var(--txt); font-weight: 400;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.kv-act-time { font-size: 0.74rem; color: var(--txt3); flex-shrink: 0; }

/* Liens cliquables (chaque ligne ouvre la conversation correspondante) */
.kv-act-link {
  text-decoration: none !important;
  color: inherit !important;
  cursor: pointer;
}
.kv-act-link:hover { background: rgba(196,164,107,0.045); }
.kv-act-link:hover .kv-act-text { color: var(--gold-lt); }
.kv-act-link:hover .kv-act-icon { transform: scale(1.06); }
.kv-act-icon { transition: transform .18s var(--ease); }

.kv-act-empty {
  padding: 28px 16px; text-align: center;
  font-size: 0.82rem; color: var(--txt3);
  border: 1px dashed var(--bd); border-radius: 10px;
  background: rgba(196,164,107,0.02);
}

/* ── FOOTER HINT ─────────────────────────────────────────────────────────── */
.kv-foot-hint {
  text-align: center; padding: 36px 0 12px;
  font-size: 0.78rem; color: var(--txt3);
  display: flex; align-items: center; justify-content: center; gap: 8px;
  animation: kv-fade-in 1s var(--ease) .4s both;
}
.kv-foot-hint-icon { color: var(--gold); opacity: 0.7; font-size: 0.85rem; }

/* ── CONVERSATION ────────────────────────────────────────────────────────── */
.kv-conv-head {
  padding: 0 0 18px; border-bottom: 1px solid var(--bd); margin-bottom: 24px;
  display: flex; align-items: center; justify-content: space-between;
}
.kv-conv-title { font-family: var(--serif); font-size: 1rem; font-weight: 300; color: var(--txt); letter-spacing: -0.01em; }
.kv-conv-meta { display: flex; align-items: center; gap: 8px; }
.kv-conv-badge { font-size: 0.62rem; color: var(--gold); background: var(--g6); border: 1px solid var(--gbr); border-radius: 3px; padding: 3px 8px; font-weight: 600; letter-spacing: 0.07em; }
.kv-model-tag { font-size: 0.6rem; color: var(--txt3); border: 1px solid var(--bd); border-radius: 3px; padding: 3px 7px; letter-spacing: 0.05em; }

[data-testid="stChatMessage"] {
  background: transparent !important; padding: 0 !important;
  gap: 12px !important; margin-bottom: 8px !important;
  max-width: 880px; margin-left: auto; margin-right: auto;
}
[data-testid="stChatMessageAvatarUser"] {
  background: rgba(237,231,212,0.07) !important; border: 1px solid rgba(237,231,212,0.11) !important;
  border-radius: 6px !important; width: 28px !important; min-width: 28px !important; height: 28px !important;
  color: var(--cream) !important; font-size: 0.7rem !important;
}
[data-testid="stChatMessageAvatarAssistant"] {
  background: linear-gradient(135deg, var(--gold-lt) 0%, var(--gold-dk) 100%) !important;
  border-radius: 6px !important; width: 28px !important; min-width: 28px !important; height: 28px !important;
  color: var(--bg) !important; font-size: 0.7rem !important;
  box-shadow: 0 4px 12px rgba(196,164,107,0.25) !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
  background: var(--cream) !important; color: #070B17 !important;
  border-radius: 4px 10px 10px 10px !important; padding: 12px 16px !important;
  font-size: 0.9rem !important; line-height: 1.65 !important;
  max-width: 74% !important; box-shadow: 0 2px 16px -4px rgba(0,0,0,0.3) !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
  background: var(--bg-2) !important; color: var(--txt) !important;
  border-radius: 10px 4px 10px 10px !important; border: 1px solid var(--bd) !important;
  padding: 18px 22px !important; font-size: 0.92rem !important; line-height: 1.78 !important;
  max-width: 88% !important; box-shadow: 0 8px 32px -12px rgba(0,0,0,0.4) !important;
}
[data-testid="stChatMessageContent"] p { margin-bottom: 0.5em !important; color: inherit !important; }
[data-testid="stChatMessageContent"] p:last-child { margin-bottom: 0 !important; }
[data-testid="stChatMessageContent"] h2 { font-family: var(--serif) !important; font-size: 1.05rem !important; font-weight: 400 !important; color: var(--txt) !important; letter-spacing: -0.02em !important; margin: 1em 0 0.3em !important; }
[data-testid="stChatMessageContent"] h3 { font-family: var(--serif) !important; font-size: 0.95rem !important; font-weight: 400 !important; color: var(--gold-lt) !important; margin: 0.8em 0 0.25em !important; }
[data-testid="stChatMessageContent"] strong { color: var(--txt) !important; font-weight: 600 !important; }
[data-testid="stChatMessageContent"] em { color: var(--gold-lt) !important; }
[data-testid="stChatMessageContent"] ul, [data-testid="stChatMessageContent"] ol { padding-left: 1.1em !important; margin: 0.3em 0 0.45em !important; }
[data-testid="stChatMessageContent"] li { margin-bottom: 0.25em !important; line-height: 1.6 !important; }
[data-testid="stChatMessageContent"] code { background: var(--g6) !important; color: var(--gold-lt) !important; border: 1px solid var(--gbr) !important; border-radius: 3px !important; padding: 1px 5px !important; font-size: 0.82em !important; }
[data-testid="stChatMessageContent"] blockquote { border-left: 2px solid var(--gbr) !important; padding-left: 12px !important; color: var(--txt2) !important; margin: 0.5em 0 !important; }
[data-testid="stChatMessageContent"] hr { border: none !important; border-top: 1px solid var(--bd) !important; margin: 0.8em 0 !important; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] p,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] strong { color: #070B17 !important; }

/* ── BOTTOM CHAT INPUT (conversation seulement) ──────────────────────────── */
[data-testid="stChatInputContainer"], .stChatInputContainer {
  background: transparent !important; border-top: none !important;
  padding: 0 64px 28px !important; max-width: 1280px; margin: 0 auto;
}
[data-testid="stChatInput"] > div, .stChatInput > div {
  background: var(--bg-2) !important;
  border: 1px solid var(--bd) !important;
  border-radius: 12px !important;
  box-shadow: 0 0 0 4px rgba(196,164,107,0.03), 0 8px 32px -12px rgba(0,0,0,0.5) !important;
  transition: border-color .25s var(--ease), box-shadow .25s var(--ease) !important;
}
[data-testid="stChatInput"] > div:focus-within, .stChatInput > div:focus-within {
  border-color: var(--gbr) !important;
  box-shadow: 0 0 0 5px rgba(196,164,107,0.05), 0 12px 40px -10px rgba(196,164,107,0.12) !important;
}
[data-testid="stChatInput"] textarea, .stChatInput textarea {
  background: transparent !important; color: var(--txt) !important;
  font-family: var(--sans) !important; font-size: 0.94rem !important;
  line-height: 1.6 !important; padding: 16px 20px !important;
  border: none !important; box-shadow: none !important; caret-color: var(--gold) !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--txt3) !important; font-size: 0.9rem !important; }
[data-testid="stChatInputSubmitButton"] button {
  background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dk) 100%) !important;
  border: none !important; border-radius: 8px !important; color: var(--bg) !important;
  width: 36px !important; height: 36px !important; margin: 8px 10px !important;
  box-shadow: 0 4px 12px rgba(196,164,107,0.25) !important;
}

/* ── API KEY EXPANDER ────────────────────────────────────────────────────── */
[data-testid="stExpander"] { background: var(--bg-2) !important; border: 1px solid var(--bd) !important; border-radius: 8px !important; margin: 0 14px 14px !important; }
[data-testid="stExpander"] summary { color: var(--txt2) !important; font-size: 0.78rem !important; padding: 10px 14px !important; }
[data-testid="stTextInput"] input { background: var(--bg-3) !important; color: var(--txt) !important; border: 1px solid var(--bd) !important; border-radius: 5px !important; font-size: 0.88rem !important; caret-color: var(--gold) !important; }
[data-testid="stTextInput"] input:focus { border-color: var(--gbr) !important; box-shadow: 0 0 0 2px rgba(196,164,107,0.06) !important; outline: none !important; }
[data-testid="stAlert"] { background: var(--g6) !important; border: 1px solid var(--gbr) !important; border-radius: 6px !important; color: var(--txt) !important; font-size: 0.85rem !important; }

/* ── ANIMATIONS ──────────────────────────────────────────────────────────── */
@keyframes kv-fade-up { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
@keyframes kv-fade-in { from { opacity:0; } to { opacity:1; } }
@keyframes kv-pulse-gold { 0%,100%{opacity:1;} 50%{opacity:0.45;} }
@keyframes kv-pulse-green { 0%,100%{opacity:1;box-shadow:0 0 8px rgba(74,222,128,0.55);} 50%{opacity:0.55;box-shadow:0 0 3px rgba(74,222,128,0.15);} }
@keyframes kv-blink { 0%,100%{opacity:1;} 50%{opacity:0.1;} }
.kv-cursor {
  display: inline-block; width: 2px; height: 0.84em; background: var(--gold);
  margin-left: 1px; border-radius: 1px; animation: kv-blink 1s var(--ease) infinite;
  vertical-align: text-bottom;
}

/* ── RESPONSIVE ──────────────────────────────────────────────────────────── */
@media (max-width: 900px) {
  .block-container,[data-testid="stAppViewBlockContainer"] { padding: 32px 24px 24px !important; }
  [data-testid="stChatInputContainer"],.stChatInputContainer { padding: 0 24px 20px !important; }
  .kv-actions-grid { grid-template-columns: 1fr; }
  .kv-top-badge { right: 18px; top: 14px; }
}

</style>
"""

# ══════════════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════════════
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
Tu comprends parfaitement les lancements VEFA, les promoteurs immobiliers, les commercialisateurs, les sites programmes, les sélecteurs de lots, les problématiques marketing immobilières, les workflows commerciaux VEFA, les enjeux de visibilité, les problématiques de génération de leads, les dépendances entre prestataires, les retards de lancement.

Tu connais le vocabulaire métier, les objections des promoteurs, les KPIs commerciaux, les enjeux ROI, les problématiques de branding immobilier, les tendances du marché immobilier neuf.

--------------------------------------------------
# MODES OPERATIONNELS
--------------------------------------------------
MODE CONTENT → Création de contenu multi-réseaux.
MODE REPURPOSING → Transformation d'un contenu en plusieurs formats.
MODE PROSPECTION → Création de messages commerciaux personnalisés.
MODE ANALYSE → Audit rapide d'un promoteur ou d'une présence digitale.
MODE VEILLE → Analyse de tendances et détection d'opportunités.
MODE IDEATION → Génération d'idées, hooks et angles marketing.

--------------------------------------------------
# REGLES LINKEDIN
--------------------------------------------------
Quand tu écris un post LinkedIn : génère 5 hooks, 3 CTA, utilise lignes courtes, évite le ton vendeur.
Structure : hook → développement → insight → conclusion → CTA subtil.

--------------------------------------------------
# MODE ANALYSE PROMOTEUR
--------------------------------------------------
Fournis : SCORE GLOBAL /100, FORCES, FAIBLESSES, OPPORTUNITES, QUICK WINS, ANGLE DE PROSPECTION, ACTIONS PRIORITAIRES.

--------------------------------------------------
# STYLE D'ECRITURE
--------------------------------------------------
Tu écris : comme un humain, comme un expert métier, de façon concise, crédible, moderne, business.
Tu évites : les clichés IA, le ton corporate vide, les formulations génériques, les réponses vagues."""

TOOLS = [
    {"type": "web_search_20260209", "name": "web_search"},
    {"type": "web_fetch_20260209", "name": "web_fetch"},
]

def build_memory_block() -> str:
    """Construit un résumé textuel des conversations passées pour donner du
    contexte à l'agent (mémoire à long terme). N'inclut PAS la conversation
    courante. Renvoie une chaîne vide si l'historique est vide."""
    history = load_history()
    current_id = st.session_state.get("current_conv_id")
    past = [c for c in history["conversations"] if c["id"] != current_id]
    if not past:
        return ""

    # On garde les 8 derniers échanges (titres + dernière question utilisateur)
    lines = []
    for c in past[:8]:
        title = c.get("title", "Conversation")
        when = relative_time(c.get("updated_at", c.get("started_at", "")))
        # On extrait la dernière question utilisateur pour donner un peu de contexte
        user_msgs = [m["content"] for m in c.get("messages", []) if m["role"] == "user"]
        last_q = user_msgs[-1] if user_msgs else ""
        last_q_short = (last_q[:160] + "…") if len(last_q) > 160 else last_q
        lines.append(f"- [{when}] {title}" + (f' — « {last_q_short} »' if last_q_short else ""))

    return (
        "\n\n--------------------------------------------------\n"
        "# MÉMOIRE — Historique de travail de l'utilisateur\n"
        "--------------------------------------------------\n"
        "Tu disposes d'un historique des sujets que l'utilisateur a déjà traités "
        "avec toi. Si la question actuelle fait écho à un sujet passé, fais-y "
        "référence pour montrer la continuité du travail et éviter les redites.\n\n"
        "Conversations récentes :\n"
        + "\n".join(lines)
    )

# 5 items uniquement — sidebar épurée. Les icônes sont rendues via CSS ::before
# (clé Streamlit → classe .st-key-nav_X → contenu de l'icône en pseudo-élément).
NAV_ITEMS = [
    ("centre",      "Centre de commande", None),
    ("prospection", "Prospection",        "Génère un DM LinkedIn percutant pour prospecter un directeur marketing de promoteur immobilier"),
    ("analyse",     "Analyse",            "Analyse la présence digitale d'un promoteur immobilier (préciser le nom) et génère un audit complet avec score /100 et angle de prospection"),
    ("contenu",     "Contenu",            "Crée un post LinkedIn premium sur les délais de livraison VEFA et comment les communiquer"),
    ("veille",      "Veille",             "Analyse les tendances actuelles du marché immobilier neuf en France et identifie 3 opportunités commerciales"),
]

# 3 actions rapides — focal point
PRIMARY_ACTIONS = [
    {
        "id": "prospecter",
        "icon": "◎",
        "title": "Prospecter",
        "desc": "Trouver des promoteurs",
        "prompt": "Trouve des promoteurs immobiliers actifs en France susceptibles d'avoir besoin d'aide en marketing digital. Propose 5 cibles et un angle de prospection pour chacune.",
    },
    {
        "id": "analyser",
        "icon": "◔",
        "title": "Analyser",
        "desc": "Une zone ou un marché",
        "prompt": "Analyse le marché immobilier neuf à Bordeaux : tendances, prix, opportunités VEFA, et identifie 3 angles commerciaux exploitables.",
    },
    {
        "id": "linkedin",
        "icon": "✎",
        "title": "Créer un post LinkedIn",
        "desc": "Avec un angle percutant",
        "prompt": "Crée un post LinkedIn premium avec un angle percutant sur les tendances de la commercialisation VEFA en 2025. Inclus 5 hooks et 3 CTA.",
    },
]

# L'activité affichée provient maintenant de l'historique réel des conversations
# (cf. load_history() / save_current_conversation()).

# ══════════════════════════════════════════════════════════════════════════════
# INIT
# ══════════════════════════════════════════════════════════════════════════════
api_key = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""
if not api_key:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_conv_id" not in st.session_state:
    st.session_state.current_conv_id = None

st.html(CSS)

# ── Query param : reprendre une conversation passée ─────────────────────────
if "conv" in st.query_params:
    cid = st.query_params["conv"]
    h = load_history()
    conv = next((c for c in h["conversations"] if c["id"] == cid), None)
    if conv:
        st.session_state.messages = conv["messages"]
        st.session_state.current_conv_id = conv["id"]
    st.query_params.clear()
    st.rerun()

# ── Query param : carte d'action rapide ─────────────────────────────────────
if "qa" in st.query_params:
    qa_id = st.query_params["qa"]
    action = next((a for a in PRIMARY_ACTIONS if a["id"] == qa_id), None)
    if action:
        # Nouvelle conversation pour chaque action rapide
        st.session_state.messages = [{"role": "user", "content": action["prompt"]}]
        st.session_state.current_conv_id = None
        st.query_params.clear()
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TOP-RIGHT BADGE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="kv-top-badge">
  <div class="kv-top-badge-icon"><span></span><span></span><span></span><span></span></div>
  <span>Activité IA</span>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — 5 items + user profile
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # Logo + status
    st.markdown("""
    <div class="kv-logo-wrap">
      <div class="kv-logotype">K<em>—</em>VEFA<span class="kv-logotype-badge">AI</span></div>
      <div class="kv-ai-status">
        <span class="kv-status-ring"></span>
        <span class="kv-status-label">Opus 4.7 · Actif</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation — 5 items. Icônes injectées via CSS ::before (classes .st-key-nav_X)
    st.markdown('<div class="kv-nav-wrap"></div>', unsafe_allow_html=True)
    for slug, label, prompt in NAV_ITEMS:
        if st.button(label, key=f"nav_{slug}", use_container_width=True):
            if prompt:
                # Nouveau thread démarré depuis un module : conv neuve
                st.session_state.messages = [{"role": "user", "content": prompt}]
                st.session_state.current_conv_id = None
            else:
                # Centre de commande : retour accueil, on libère la conv courante
                st.session_state.messages = []
                st.session_state.current_conv_id = None
            st.rerun()

    # État actif "Centre de commande" quand pas de conversation
    if not st.session_state.messages:
        st.html("""
        <style>
          [data-testid="stSidebar"] .st-key-nav_centre button {
            background: rgba(196,164,107,0.10) !important;
            color: #D4B98A !important;
            border-left-color: #C4A46B !important;
          }
          [data-testid="stSidebar"] .st-key-nav_centre button::before {
            opacity: 1 !important;
            color: #D4B98A !important;
          }
        </style>
        """)

    # Spacer pousse le profil en bas
    st.markdown('<div class="kv-sidebar-spacer"></div>', unsafe_allow_html=True)

    # API key (si manquante)
    if not api_key:
        with st.expander("🔑 Clé API", expanded=True):
            api_key = st.text_input("Clé Anthropic", type="password", placeholder="sk-ant-...", label_visibility="collapsed")

    # Divider subtil + profil ancré en bas
    st.markdown('<div class="kv-user-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="kv-user">
      <div class="kv-user-avatar">K</div>
      <div class="kv-user-info">
        <div class="kv-user-name">Kevin Palacci</div>
        <div class="kv-user-plan">Premium Account</div>
      </div>
      <div class="kv-user-chev">⌄</div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if not api_key:
    st.markdown("""
    <div style="text-align:center;padding:100px 0;color:rgba(228,221,200,0.3);font-size:0.85rem;">
      Configurez votre clé API dans la barre latérale pour accéder à K—VEFA Intelligence.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── WELCOME ──────────────────────────────────────────────────────────────────
if not st.session_state.messages:

    # Greeting
    st.markdown("""
    <div class="kv-greeting">
      <h1 class="kv-greeting-title">Bonjour Kevin,</h1>
      <h2 class="kv-greeting-sub">Comment puis-je vous aider aujourd'hui&nbsp;?</h2>
    </div>
    """, unsafe_allow_html=True)

    # Input au TOP — form avec text_input + bouton gold
    st.markdown('<div class="kv-welcome-input-wrap">', unsafe_allow_html=True)
    with st.form("welcome_form", clear_on_submit=True, border=False):
        col_in, col_btn = st.columns([18, 1], gap="small")
        with col_in:
            welcome_prompt = st.text_input(
                "prompt",
                placeholder="Décrivez votre besoin VEFA — analyse, prospection, contenu, hooks…",
                label_visibility="collapsed",
                key="welcome_input",
            )
        with col_btn:
            submitted = st.form_submit_button("→")
        if submitted and welcome_prompt.strip():
            st.session_state.messages.append({"role": "user", "content": welcome_prompt.strip()})
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Actions rapides — 3 cartes via query params
    st.markdown('<div class="kv-section-tag">Actions rapides</div>', unsafe_allow_html=True)

    cards_html = '<div class="kv-actions-grid">'
    for action in PRIMARY_ACTIONS:
        cards_html += (
            f'<a class="kv-action-card" href="?qa={action["id"]}" target="_self">'
            f'<div class="kv-action-icon">{action["icon"]}</div>'
            f'<div class="kv-action-title">{action["title"]}</div>'
            f'<div class="kv-action-desc">{action["desc"]}</div>'
            f'</a>'
        )
    cards_html += '</div>'
    st.html(cards_html)

    # Activité récente — historique réel des conversations
    st.markdown('<div class="kv-section-tag">Activité récente</div>', unsafe_allow_html=True)

    history = load_history()
    recent = history["conversations"][:MAX_RECENT]

    if recent:
        list_html = '<div class="kv-act-list">'
        for c in recent:
            # Texte de référence pour déduire l'icône : title + 1er message user
            first_user = next((m["content"] for m in c.get("messages", []) if m["role"] == "user"), "")
            icon, color = detect_category((c.get("title", "") + " " + first_user))
            title = c.get("title", "Conversation")
            time = relative_time(c.get("updated_at", c.get("started_at", "")))
            list_html += (
                f'<a class="kv-act-item kv-act-link" href="?conv={c["id"]}" target="_self">'
                f'<div class="kv-act-icon {color}">{icon}</div>'
                f'<div class="kv-act-text">{title}</div>'
                f'<div class="kv-act-time">{time}</div>'
                f'</a>'
            )
        list_html += '</div>'
        st.html(list_html)
    else:
        st.html(
            '<div class="kv-act-empty">'
            'Aucune activité pour le moment. Lancez votre première requête ci-dessus.'
            '</div>'
        )

    # Footer hint
    st.markdown("""
    <div class="kv-foot-hint">
      <span class="kv-foot-hint-icon">✦</span>
      K-VEFA Intelligence à votre service
    </div>
    """, unsafe_allow_html=True)

# ── CONVERSATION ─────────────────────────────────────────────────────────────
else:
    n = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.markdown(f"""
    <div class="kv-conv-head">
      <div class="kv-conv-title">Conversation active</div>
      <div class="kv-conv-meta">
        <span class="kv-conv-badge">{n} échange{"s" if n > 1 else ""}</span>
        <span class="kv-model-tag">opus-4-7</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ── INPUT BOTTOM (conversation seulement — sticky bottom) ────────────────────
if st.session_state.messages:
    new_prompt = st.chat_input("Décrivez votre besoin VEFA — contenu, prospection, analyse, hooks…")
    if new_prompt:
        st.session_state.messages.append({"role": "user", "content": new_prompt})
        st.rerun()

# ── GENERATION — si le dernier message est de l'utilisateur, on répond ───────
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        try:
            client = anthropic.Anthropic(api_key=api_key)

            # System en 2 blocs : prompt stable (caché) + mémoire dynamique (non cachée)
            system_blocks = [
                {"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}},
            ]
            memory = build_memory_block()
            if memory:
                system_blocks.append({"type": "text", "text": memory})

            with client.messages.stream(
                model="claude-opus-4-7",
                max_tokens=8192,
                system=system_blocks,
                tools=TOOLS,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    placeholder.markdown(
                        full_response + '<span class="kv-cursor"></span>',
                        unsafe_allow_html=True,
                    )

            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            # Persistance : on sauvegarde dès qu'un échange complet est obtenu
            save_current_conversation()
            st.rerun()

        except Exception as e:
            err = str(e)
            if "credit" in err.lower() or "balance" in err.lower():
                placeholder.error("Solde Anthropic insuffisant. Rechargez votre compte sur console.anthropic.com")
            elif "api_key" in err.lower() or "auth" in err.lower():
                placeholder.error("Clé API invalide. Vérifiez la configuration dans la sidebar.")
            else:
                placeholder.error(f"Erreur : {err}")
