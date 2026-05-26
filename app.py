import os
import streamlit as st
import anthropic

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="K—VEFA Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design system ─────────────────────────────────────────────────────────────
CSS = """
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>

/* ═══ TOKENS ══════════════════════════════════════════════════════════════ */
:root {
  --bg:          #0A0E1A;
  --bg-2:        #0F1424;
  --bg-3:        #151A2E;
  --bg-4:        #1A1F33;
  --gold:        #B8975E;
  --gold-lt:     #D4B574;
  --gold-dk:     #A07F47;
  --gold-8:      rgba(184,151,94,0.08);
  --gold-12:     rgba(184,151,94,0.12);
  --gold-18:     rgba(184,151,94,0.18);
  --gold-25:     rgba(184,151,94,0.25);
  --gold-border: rgba(184,151,94,0.22);
  --cream:       #F8F4ED;
  --cream-2:     #F3EFE6;
  --txt:         #E8E2D5;
  --txt-muted:   rgba(232,226,213,0.55);
  --txt-soft:    rgba(232,226,213,0.35);
  --border:      rgba(232,226,213,0.09);
  --border-2:    rgba(232,226,213,0.05);
  --serif:       'Fraunces', Georgia, serif;
  --sans:        'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --ease:        cubic-bezier(.4,0,.2,1);
  --shadow:      0 8px 40px -12px rgba(10,14,26,0.6);
  --shadow-lg:   0 25px 80px -20px rgba(10,14,26,0.8);
  --glow:        0 0 40px rgba(184,151,94,0.06);
}

/* ═══ BASE ════════════════════════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }

html, body {
  background: var(--bg) !important;
  font-family: var(--sans);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-feature-settings: "ss01","cv11";
}

.stApp {
  background: var(--bg) !important;
  color: var(--txt);
}

/* Subtle architectural grid pattern */
.stApp::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(184,151,94,0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(184,151,94,0.025) 1px, transparent 1px);
  background-size: 72px 72px;
  pointer-events: none;
  z-index: 0;
}

/* Gold radial glow from top */
.stApp::after {
  content: '';
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 400px;
  background: radial-gradient(ellipse 80% 100% at 50% -10%, rgba(184,151,94,0.07) 0%, transparent 100%);
  pointer-events: none;
  z-index: 0;
}

/* Streamlit chrome - hide */
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stDeployButton { display: none !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(184,151,94,0.2); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(184,151,94,0.4); }

/* Selection */
::selection { background: var(--gold); color: var(--bg); }

/* ═══ LAYOUT ══════════════════════════════════════════════════════════════ */
.block-container {
  padding: 0 40px 120px !important;
  max-width: 100% !important;
  min-height: calc(100vh - 80px) !important;
  position: relative;
  z-index: 1;
}

/* ═══ SIDEBAR ═════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: var(--bg-2) !important;
  border-right: 1px solid var(--border) !important;
  min-width: 240px !important;
  max-width: 260px !important;
}

[data-testid="stSidebarContent"] {
  padding: 0 !important;
  background: transparent !important;
}

/* ── Sidebar Logo ── */
.kv-sidebar-logo {
  padding: 28px 22px 20px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 8px;
}

.kv-logotype {
  font-family: var(--serif);
  font-size: 1.35rem;
  font-weight: 500;
  color: var(--txt);
  letter-spacing: -0.025em;
  line-height: 1;
  display: flex;
  align-items: center;
  gap: 0;
  margin-bottom: 4px;
}
.kv-logotype em { color: var(--gold); font-style: normal; }

.kv-sidebar-sub {
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--txt-soft);
}

.kv-badge {
  display: inline-flex;
  align-items: center;
  font-size: 0.58rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--bg);
  background: var(--gold);
  border-radius: 2px;
  padding: 2px 5px;
  margin-left: 8px;
  vertical-align: middle;
  position: relative;
  top: -1px;
}

/* ── Sidebar Nav Label ── */
.kv-nav-section {
  padding: 16px 22px 6px;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--txt-soft);
}

/* ── Sidebar Buttons (nav) ── */
[data-testid="stSidebar"] [data-testid="stButton"] button {
  background: transparent !important;
  border: none !important;
  color: var(--txt-muted) !important;
  text-align: left !important;
  font-family: var(--sans) !important;
  font-size: 0.875rem !important;
  font-weight: 400 !important;
  padding: 8px 22px !important;
  border-radius: 0 !important;
  width: 100% !important;
  transition: all .15s var(--ease) !important;
  border-left: 2px solid transparent !important;
  letter-spacing: 0 !important;
  text-transform: none !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
  background: var(--gold-8) !important;
  color: var(--txt) !important;
  border-left-color: var(--gold-border) !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:active,
[data-testid="stSidebar"] [data-testid="stButton"] button:focus {
  background: var(--gold-12) !important;
  color: var(--gold) !important;
  border-left-color: var(--gold) !important;
  box-shadow: none !important;
}

/* ── Sidebar Divider ── */
.kv-sidebar-divider {
  height: 1px;
  background: var(--border);
  margin: 12px 22px;
}

/* ── Sidebar Status ── */
.kv-sidebar-status {
  padding: 14px 22px;
  margin: 8px 12px;
  background: var(--gold-8);
  border: 1px solid var(--gold-border);
  border-radius: 5px;
}
.kv-status-dot {
  display: inline-block;
  width: 6px; height: 6px;
  background: var(--gold);
  border-radius: 50%;
  margin-right: 7px;
  animation: kv-pulse 2s ease-in-out infinite;
}
.kv-status-text {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--gold);
  letter-spacing: 0.06em;
}
.kv-status-sub {
  font-size: 0.65rem;
  color: var(--txt-muted);
  margin-top: 3px;
  padding-left: 13px;
}

/* ── Sidebar Footer ── */
.kv-sidebar-footer {
  position: absolute;
  bottom: 0;
  left: 0; right: 0;
  padding: 16px 22px;
  border-top: 1px solid var(--border);
  background: var(--bg-2);
}
.kv-sidebar-footer-text {
  font-size: 0.65rem;
  color: var(--txt-soft);
  letter-spacing: 0.06em;
}

/* ═══ MAIN HEADER BAR ════════════════════════════════════════════════════ */
.kv-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 0 0;
  margin-bottom: 32px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 18px;
}
.kv-topbar-left {
  display: flex;
  align-items: center;
  gap: 14px;
}
.kv-breadcrumb {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--txt-soft);
}
.kv-breadcrumb span {
  color: var(--gold);
  margin: 0 6px;
}
.kv-topbar-title {
  font-family: var(--serif);
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--txt);
  letter-spacing: -0.02em;
}

/* ═══ MODULE CARDS ═══════════════════════════════════════════════════════ */
.kv-module {
  background: var(--bg-2);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 22px 20px 18px;
  margin-bottom: -1px;
  transition: all .22s var(--ease);
  position: relative;
  overflow: hidden;
}
.kv-module::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold-25), transparent);
  opacity: 0;
  transition: opacity .22s var(--ease);
}
.kv-module:hover { border-color: var(--gold-border); background: var(--bg-3); }
.kv-module:hover::before { opacity: 1; }

.kv-module-icon {
  width: 36px; height: 36px;
  background: var(--gold-12);
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--gold);
  font-size: 0.95rem;
  margin-bottom: 14px;
}

.kv-module-cat {
  font-size: 0.63rem;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 6px;
}

.kv-module-title {
  font-family: var(--serif);
  font-size: 1rem;
  font-weight: 500;
  color: var(--txt);
  letter-spacing: -0.02em;
  margin-bottom: 6px;
  line-height: 1.2;
}

.kv-module-desc {
  font-size: 0.8rem;
  color: var(--txt-muted);
  line-height: 1.5;
  margin-bottom: 14px;
}

.kv-module-arrow {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--gold);
  letter-spacing: 0.06em;
  opacity: 0.7;
  transition: all .15s var(--ease);
}
.kv-module:hover .kv-module-arrow {
  opacity: 1;
  letter-spacing: 0.1em;
}

/* Module button overlay */
.stMarkdown:has(.kv-module) ~ [data-testid="stButton"] > button,
[data-testid="stVerticalBlock"] > [data-testid="stButton"]:last-child > button {
  background: var(--bg-2) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 6px 6px !important;
  color: var(--gold) !important;
  font-size: 0.75rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  padding: 10px 20px !important;
  transition: all .2s var(--ease) !important;
}

/* ═══ WELCOME SECTION ════════════════════════════════════════════════════ */
.kv-welcome {
  text-align: center;
  padding: 20px 0 36px;
}
.kv-welcome-label {
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--gold);
  margin-bottom: 10px;
}
.kv-welcome-title {
  font-family: var(--serif);
  font-size: clamp(1.6rem, 3vw, 2.4rem);
  font-weight: 500;
  color: var(--txt);
  letter-spacing: -0.025em;
  line-height: 1.15;
  margin-bottom: 10px;
}
.kv-welcome-title em { color: var(--gold); font-style: normal; }
.kv-welcome-sub {
  font-size: 0.9rem;
  color: var(--txt-muted);
  line-height: 1.6;
  max-width: 480px;
  margin: 0 auto;
}

/* ═══ SECTION LABELS ═════════════════════════════════════════════════════ */
.kv-section-label {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--txt-soft);
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.kv-section-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}

/* ═══ CHAT ═══════════════════════════════════════════════════════════════ */
.kv-conv-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border);
}
.kv-conv-title {
  font-family: var(--serif);
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--txt-muted);
  letter-spacing: -0.01em;
}
.kv-conv-count {
  font-size: 0.65rem;
  color: var(--gold);
  background: var(--gold-8);
  border: 1px solid var(--gold-border);
  border-radius: 2px;
  padding: 2px 7px;
  font-weight: 600;
  letter-spacing: 0.06em;
}

[data-testid="stChatMessage"] {
  background: transparent !important;
  padding: 0 !important;
  gap: 14px !important;
  margin-bottom: 6px !important;
  max-width: 860px;
  margin-left: auto;
  margin-right: auto;
}

/* User avatar */
[data-testid="stChatMessageAvatarUser"] {
  background: rgba(248,244,237,0.1) !important;
  border: 1px solid rgba(248,244,237,0.15) !important;
  border-radius: 4px !important;
  width: 28px !important;
  min-width: 28px !important;
  height: 28px !important;
  font-size: 0.7rem !important;
  color: var(--cream) !important;
}

/* Assistant avatar */
[data-testid="stChatMessageAvatarAssistant"] {
  background: linear-gradient(135deg, var(--gold-lt) 0%, var(--gold) 100%) !important;
  border-radius: 4px !important;
  width: 28px !important;
  min-width: 28px !important;
  height: 28px !important;
  font-size: 0.7rem !important;
  color: var(--bg) !important;
  box-shadow: 0 4px 12px rgba(184,151,94,0.25) !important;
}

/* User message */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
[data-testid="stChatMessageContent"] {
  background: var(--cream) !important;
  color: #0A0E1A !important;
  border-radius: 2px 8px 8px 8px !important;
  padding: 12px 17px !important;
  font-size: 0.92rem !important;
  line-height: 1.65 !important;
  border: none !important;
  box-shadow: 0 2px 16px -4px rgba(10,14,26,0.2) !important;
  max-width: 78% !important;
}

/* Assistant message */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"])
[data-testid="stChatMessageContent"] {
  background: var(--bg-2) !important;
  color: var(--txt) !important;
  border-radius: 8px 2px 8px 8px !important;
  border: 1px solid var(--border) !important;
  padding: 18px 22px !important;
  font-size: 0.92rem !important;
  line-height: 1.78 !important;
  max-width: 90% !important;
  box-shadow: var(--shadow) !important;
}

/* Message typography */
[data-testid="stChatMessageContent"] p {
  margin-bottom: 0.6em !important;
  color: inherit !important;
}
[data-testid="stChatMessageContent"] p:last-child { margin-bottom: 0 !important; }

[data-testid="stChatMessageContent"] h1,
[data-testid="stChatMessageContent"] h2,
[data-testid="stChatMessageContent"] h3 {
  font-family: var(--serif) !important;
  font-weight: 500 !important;
  letter-spacing: -0.02em !important;
  line-height: 1.2 !important;
  margin: 1.1em 0 0.4em !important;
}
[data-testid="stChatMessageContent"] h2 {
  font-size: 1.05rem !important;
  color: var(--txt) !important;
}
[data-testid="stChatMessageContent"] h3 {
  font-size: 0.95rem !important;
  color: var(--gold-lt) !important;
}

[data-testid="stChatMessageContent"] strong {
  color: var(--txt) !important;
  font-weight: 600 !important;
}

[data-testid="stChatMessageContent"] em {
  color: var(--gold-lt) !important;
}

[data-testid="stChatMessageContent"] ul,
[data-testid="stChatMessageContent"] ol {
  padding-left: 1.1em !important;
  margin: 0.35em 0 0.5em !important;
}
[data-testid="stChatMessageContent"] li {
  margin-bottom: 0.28em !important;
  line-height: 1.6 !important;
}

[data-testid="stChatMessageContent"] code {
  background: var(--gold-8) !important;
  color: var(--gold-lt) !important;
  border: 1px solid var(--gold-border) !important;
  border-radius: 3px !important;
  padding: 1px 5px !important;
  font-size: 0.83em !important;
}

[data-testid="stChatMessageContent"] hr {
  border: none !important;
  border-top: 1px solid var(--border) !important;
  margin: 1em 0 !important;
}

[data-testid="stChatMessageContent"] blockquote {
  border-left: 2px solid var(--gold-border) !important;
  padding-left: 14px !important;
  color: var(--txt-muted) !important;
  margin: 0.6em 0 !important;
}

/* User message text overrides */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
[data-testid="stChatMessageContent"] p,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
[data-testid="stChatMessageContent"] strong,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
[data-testid="stChatMessageContent"] h2,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"])
[data-testid="stChatMessageContent"] h3 {
  color: #1A1F33 !important;
}

/* ═══ INPUT AREA ══════════════════════════════════════════════════════════ */
[data-testid="stChatInputContainer"],
.stChatInputContainer {
  background: linear-gradient(to bottom, transparent, rgba(10,14,26,0.98) 38%) !important;
  border-top: none !important;
  padding: 20px 48px 28px !important;
}

/* Inner input wrapper */
[data-testid="stChatInput"] > div,
.stChatInput > div {
  background: var(--bg-3) !important;
  border: 1px solid var(--gold-border) !important;
  border-radius: 10px !important;
  box-shadow: 0 0 0 1px rgba(184,151,94,0.04), var(--shadow) !important;
  transition: border-color .2s var(--ease), box-shadow .2s var(--ease) !important;
}
[data-testid="stChatInput"] > div:focus-within,
.stChatInput > div:focus-within {
  border-color: rgba(184,151,94,0.42) !important;
  box-shadow: 0 0 0 3px rgba(184,151,94,0.07), var(--shadow) !important;
}

[data-testid="stChatInput"] textarea,
.stChatInput textarea {
  background: transparent !important;
  color: var(--txt) !important;
  font-family: var(--sans) !important;
  font-size: 0.935rem !important;
  line-height: 1.6 !important;
  padding: 16px 20px !important;
  border: none !important;
  box-shadow: none !important;
  caret-color: var(--gold) !important;
  resize: none !important;
}
[data-testid="stChatInput"] textarea::placeholder,
.stChatInput textarea::placeholder {
  color: var(--txt-soft) !important;
  font-size: 0.9rem !important;
}

/* Submit button */
[data-testid="stChatInputSubmitButton"] button {
  background: var(--gold) !important;
  border: none !important;
  border-radius: 6px !important;
  color: var(--bg) !important;
  width: 36px !important;
  height: 36px !important;
  margin: 8px 10px !important;
  transition: all .18s var(--ease) !important;
}
[data-testid="stChatInputSubmitButton"] button:hover {
  background: var(--gold-lt) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 14px rgba(184,151,94,0.3) !important;
}

/* ═══ BUTTONS (main area) ════════════════════════════════════════════════ */
/* Main content buttons (reset + card CTAs) */
[data-testid="stMain"] [data-testid="stButton"] button,
.main [data-testid="stButton"] button {
  background: transparent !important;
  color: var(--txt-muted) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
  font-family: var(--sans) !important;
  font-size: 0.72rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  padding: 8px 20px !important;
  transition: all .2s var(--ease) !important;
}
[data-testid="stMain"] [data-testid="stButton"] button:hover,
.main [data-testid="stButton"] button:hover {
  background: var(--gold-8) !important;
  border-color: var(--gold-border) !important;
  color: var(--gold) !important;
}

/* ═══ API KEY ═════════════════════════════════════════════════════════════ */
[data-testid="stExpander"] {
  background: var(--bg-2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 6px !important;
}
[data-testid="stExpander"] summary {
  color: var(--txt-muted) !important;
  font-size: 0.82rem !important;
  font-family: var(--sans) !important;
  padding: 12px 16px !important;
}
[data-testid="stTextInput"] input {
  background: var(--bg-3) !important;
  color: var(--txt) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
  font-family: var(--sans) !important;
  font-size: 0.9rem !important;
  caret-color: var(--gold) !important;
  padding: 10px 14px !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--gold-border) !important;
  box-shadow: 0 0 0 2px rgba(184,151,94,0.07) !important;
  outline: none !important;
}
[data-testid="stTextInput"] label {
  color: var(--txt-muted) !important;
  font-size: 0.78rem !important;
  font-weight: 500 !important;
}

/* Info/error */
[data-testid="stAlert"] {
  background: var(--gold-8) !important;
  border: 1px solid var(--gold-border) !important;
  border-radius: 5px !important;
  color: var(--txt) !important;
  font-size: 0.88rem !important;
}

/* ═══ COLUMNS ════════════════════════════════════════════════════════════ */
[data-testid="stColumns"] {
  gap: 12px !important;
}

/* ═══ ANIMATIONS ══════════════════════════════════════════════════════════ */
@keyframes kv-blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.15; }
}
@keyframes kv-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.6; transform: scale(0.85); }
}
@keyframes kv-fade-up {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.kv-cursor {
  display: inline-block;
  width: 2px;
  height: 0.88em;
  background: var(--gold);
  margin-left: 1px;
  border-radius: 1px;
  animation: kv-blink 1.1s var(--ease) infinite;
  vertical-align: text-bottom;
}

.kv-fade-up {
  animation: kv-fade-up .3s var(--ease) both;
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

# ── Module definitions ────────────────────────────────────────────────────────
MODULES = [
    {
        "icon": "✦", "cat": "CONTENU", "title": "Création de contenu",
        "desc": "Posts LinkedIn, captions Instagram, scripts Reels, emails",
        "prompt": "Crée un post LinkedIn premium sur les délais de livraison VEFA et la communication des promoteurs",
    },
    {
        "icon": "◈", "cat": "PROSPECTION", "title": "Prospection B2B",
        "desc": "DM LinkedIn, emails froids, séquences de relance personnalisées",
        "prompt": "Génère un DM LinkedIn percutant pour prospecter un directeur marketing de promoteur immobilier",
    },
    {
        "icon": "◎", "cat": "ANALYSE", "title": "Audit promoteur",
        "desc": "Score digital /100, forces, faiblesses, angles d'approche",
        "prompt": "Analyse la présence digitale de Nexity et génère un audit complet avec score et angle de prospection",
    },
    {
        "icon": "⊞", "cat": "REPURPOSING", "title": "Multi-formats",
        "desc": "1 idée → 6 formats : LinkedIn, Instagram, Reel, email, DM",
        "prompt": "Décline ce sujet en 6 formats : les erreurs de communication lors d'un lancement VEFA",
    },
    {
        "icon": "◇", "cat": "IDÉATION", "title": "Hooks & Angles",
        "desc": "10 hooks, 7 angles business, émotionnels, ROI, pain points",
        "prompt": "Génère 10 hooks LinkedIn ultra-percutants sur la génération de leads VEFA pour les promoteurs",
    },
    {
        "icon": "◉", "cat": "VEILLE", "title": "Veille & Opportunités",
        "desc": "Tendances marché, signaux faibles, opportunités commerciales",
        "prompt": "Analyse les tendances du marché immobilier neuf en France et identifie les opportunités commerciales pour une agence marketing VEFA",
    },
]

NAV_ITEMS = [
    ("✦", "Contenu"),
    ("◈", "Prospection"),
    ("◎", "Analyse"),
    ("⊞", "Repurposing"),
    ("◇", "Idéation"),
    ("◉", "Veille"),
]

QUICK_ACTIONS = [
    "Post LinkedIn sur les délais VEFA",
    "DM de prospection Nexity",
    "Audit d'un site promoteur",
    "10 hooks réservation VEFA",
]

# ── API key ───────────────────────────────────────────────────────────────────
api_key = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""
if not api_key:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Inject CSS ────────────────────────────────────────────────────────────────
st.html(CSS)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # Logo
    st.markdown("""
    <div class="kv-sidebar-logo">
      <div class="kv-logotype">K<em>—</em>VEFA<span class="kv-badge">AI</span></div>
      <div class="kv-sidebar-sub">Intelligence Immobilière</div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown('<div class="kv-nav-section">Modules</div>', unsafe_allow_html=True)

    for icon, label in NAV_ITEMS:
        if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
            mod = next((m for m in MODULES if m["cat"].upper() == label.upper() or m["title"].upper() == label.upper()), None)
            if mod:
                st.session_state.messages.append({"role": "user", "content": mod["prompt"]})
                st.rerun()

    st.markdown('<div class="kv-sidebar-divider"></div>', unsafe_allow_html=True)

    # Quick actions
    st.markdown('<div class="kv-nav-section">Accès rapide</div>', unsafe_allow_html=True)

    for qa in QUICK_ACTIONS:
        label_short = qa[:32] + ("…" if len(qa) > 32 else "")
        if st.button(f"→  {label_short}", key=f"qa_{qa[:8]}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": qa})
            st.rerun()

    st.markdown('<div class="kv-sidebar-divider"></div>', unsafe_allow_html=True)

    # Session info
    if st.session_state.messages:
        msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.markdown(f"""
        <div class="kv-sidebar-status">
          <div><span class="kv-status-dot"></span><span class="kv-status-text">Session active</span></div>
          <div class="kv-status-sub">{msg_count} échange{"s" if msg_count > 1 else ""}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("↺  Nouvelle conversation", key="sidebar_reset", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    else:
        st.markdown("""
        <div class="kv-sidebar-status">
          <div><span class="kv-status-dot"></span><span class="kv-status-text">Prêt</span></div>
          <div class="kv-status-sub">Sélectionnez un module</div>
        </div>
        """, unsafe_allow_html=True)

    # API key if needed
    if not api_key:
        st.markdown('<div class="kv-sidebar-divider"></div>', unsafe_allow_html=True)
        with st.expander("🔑 Clé API", expanded=True):
            api_key = st.text_input(
                "Clé Anthropic",
                type="password",
                placeholder="sk-ant-...",
            )

# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════

if not api_key:
    st.markdown("""
    <div style="text-align:center; padding: 80px 0; color: rgba(232,226,213,0.4); font-size: 0.85rem;">
      Configurez votre clé API dans la sidebar pour accéder à K—VEFA Intelligence.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── No messages: welcome + module grid ───────────────────────────────────────
if not st.session_state.messages:

    # Top bar
    st.markdown("""
    <div class="kv-topbar">
      <div class="kv-topbar-left">
        <div class="kv-breadcrumb">K—VEFA <span>›</span> Tableau de bord</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Welcome
    st.markdown("""
    <div class="kv-welcome kv-fade-up">
      <div class="kv-welcome-label">Intelligence VEFA</div>
      <div class="kv-welcome-title">Que souhaitez-vous<br>accomplir <em>aujourd'hui</em> ?</div>
      <div class="kv-welcome-sub">
        Sélectionnez un module ou décrivez directement votre besoin.<br>
        L'agent détecte automatiquement le mode adapté.
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Module grid — row 1
    st.markdown('<div class="kv-section-label">Modules disponibles</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="small")
    cols_row1 = [col1, col2, col3]

    for i, mod in enumerate(MODULES[:3]):
        with cols_row1[i]:
            st.markdown(f"""
            <div class="kv-module">
              <div class="kv-module-icon">{mod["icon"]}</div>
              <div class="kv-module-cat">{mod["cat"]}</div>
              <div class="kv-module-title">{mod["title"]}</div>
              <div class="kv-module-desc">{mod["desc"]}</div>
              <div class="kv-module-arrow">Démarrer →</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Ouvrir", key=f"mod_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": mod["prompt"]})
                st.rerun()

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # Module grid — row 2
    col4, col5, col6 = st.columns(3, gap="small")
    cols_row2 = [col4, col5, col6]

    for i, mod in enumerate(MODULES[3:]):
        with cols_row2[i]:
            st.markdown(f"""
            <div class="kv-module">
              <div class="kv-module-icon">{mod["icon"]}</div>
              <div class="kv-module-cat">{mod["cat"]}</div>
              <div class="kv-module-title">{mod["title"]}</div>
              <div class="kv-module-desc">{mod["desc"]}</div>
              <div class="kv-module-arrow">Démarrer →</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Ouvrir", key=f"mod_{i+3}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": mod["prompt"]})
                st.rerun()

# ── Conversation ──────────────────────────────────────────────────────────────
else:

    msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])

    # Top bar
    st.markdown(f"""
    <div class="kv-topbar">
      <div class="kv-topbar-left">
        <div class="kv-breadcrumb">K—VEFA <span>›</span> Conversation</div>
        <div class="kv-conv-count">{msg_count} échange{"s" if msg_count > 1 else ""}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# ── Input ─────────────────────────────────────────────────────────────────────
prompt = st.chat_input("Décrivez votre besoin VEFA — contenu, prospection, analyse…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
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
                        placeholder.markdown(
                            full_response + '<span class="kv-cursor"></span>',
                            unsafe_allow_html=True,
                        )
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
            placeholder.error("Clé API invalide. Vérifiez votre clé Anthropic.")
        except Exception as e:
            placeholder.error(f"Erreur : {e}")
