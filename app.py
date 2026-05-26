import os
import streamlit as st
import anthropic

st.set_page_config(
    page_title="K—VEFA Intelligence",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — v3 premium
# ══════════════════════════════════════════════════════════════════════════════
CSS = """
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;1,9..144,300;1,9..144,400&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>

/* ── TOKENS ──────────────────────────────────────────────────────────────── */
:root {
  --bg:     #070B17;
  --bg-2:   #0B0F1E;
  --bg-3:   #0F1426;
  --bg-4:   #141930;
  --bg-5:   #1A2040;
  --gold:   #C4A46B;
  --gold-lt:#D4B98A;
  --gold-dk:#A07A42;
  --g8:  rgba(196,164,107,0.08);
  --g12: rgba(196,164,107,0.12);
  --g20: rgba(196,164,107,0.20);
  --g28: rgba(196,164,107,0.28);
  --gbr: rgba(196,164,107,0.18);
  --cream: #EDE7D4;
  --txt:   #D8D0BC;
  --txt2:  rgba(216,208,188,0.60);
  --txt3:  rgba(216,208,188,0.34);
  --bd:    rgba(216,208,188,0.07);
  --bd2:   rgba(216,208,188,0.04);
  --serif: 'Fraunces', Georgia, serif;
  --sans:  'Inter', -apple-system, sans-serif;
  --ease:  cubic-bezier(.4,0,.2,1);
  --eout:  cubic-bezier(0,.55,.45,1);
  --sh:    0 8px 48px -16px rgba(0,0,0,0.75);
  --shg:   0 0 60px -20px rgba(196,164,107,0.14);
}

/* ── RESET ───────────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body { background: var(--bg) !important; font-family: var(--sans); -webkit-font-smoothing: antialiased; font-feature-settings: "ss01","cv11"; }
.stApp { background: var(--bg) !important; color: var(--txt); }

/* ── BACKGROUND — architectural depth (no cheap grid) ───────────────────── */
.stApp::before {
  content: '';
  position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background:
    radial-gradient(ellipse 130% 55% at 50% -10%, rgba(196,164,107,0.055) 0%, transparent 55%),
    radial-gradient(ellipse 55% 90% at -5% 60%,  rgba(196,164,107,0.022) 0%, transparent 50%),
    radial-gradient(ellipse 55% 90% at 105% 60%, rgba(100,130,220,0.025) 0%, transparent 50%);
}
.stApp::after {
  content: '';
  position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image:
    repeating-linear-gradient(0deg,   transparent, transparent 95px, rgba(196,164,107,0.016) 95px, rgba(196,164,107,0.016) 96px),
    repeating-linear-gradient(90deg,  transparent, transparent 191px,rgba(196,164,107,0.010) 191px,rgba(196,164,107,0.010) 192px);
}

/* ── CHROME HIDE ─────────────────────────────────────────────────────────── */
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], .stDeployButton { display: none !important; }

/* ── SCROLLBAR ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(196,164,107,0.2); border-radius: 2px; }
::selection { background: rgba(196,164,107,0.22); color: var(--cream); }

/* ── LAYOUT ──────────────────────────────────────────────────────────────── */
section[data-testid="stMain"], .main {
  display: flex !important; flex-direction: column !important;
  min-height: 100vh !important; overflow-y: auto !important;
}
.block-container, [data-testid="stAppViewBlockContainer"] {
  flex: 1 1 auto !important; padding: 0 44px 24px !important;
  max-width: 100% !important; position: relative; z-index: 1;
}
[data-testid="stChatInputContainer"] { flex-shrink: 0 !important; margin-top: auto !important; }

/* ── SIDEBAR ─────────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--bg-2) !important;
  border-right: 1px solid var(--bd) !important;
  min-width: 256px !important; max-width: 272px !important;
}
[data-testid="stSidebarContent"] { padding: 0 !important; background: transparent !important; }

.kv-logo-wrap { padding: 22px 20px 16px; border-bottom: 1px solid var(--bd); margin-bottom: 2px; }
.kv-logotype {
  font-family: var(--serif); font-size: 1.28rem; font-weight: 400;
  color: var(--txt); letter-spacing: -0.03em; line-height: 1;
  display: flex; align-items: center; margin-bottom: 6px;
}
.kv-logotype em { color: var(--gold); font-style: normal; }
.kv-logotype-badge {
  display: inline-flex; align-items: center;
  font-size: 0.5rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
  color: var(--bg); background: var(--gold); border-radius: 2px;
  padding: 2px 5px; margin-left: 7px; position: relative; top: -1px;
}
.kv-ai-status { display: flex; align-items: center; gap: 6px; }
.kv-status-ring {
  width: 7px; height: 7px; border-radius: 50%; background: #4ADE80;
  box-shadow: 0 0 8px rgba(74,222,128,0.5);
  animation: kv-pulse-green 2.4s ease-in-out infinite;
}
.kv-status-label { font-size: 0.58rem; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: rgba(74,222,128,0.65); }

.kv-nav-label { padding: 14px 20px 5px; font-size: 0.57rem; font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase; color: var(--txt3); }

[data-testid="stSidebar"] [data-testid="stButton"] button {
  background: transparent !important; border: none !important;
  color: var(--txt2) !important; text-align: left !important;
  font-family: var(--sans) !important; font-size: 0.84rem !important; font-weight: 400 !important;
  padding: 7px 20px !important; border-radius: 0 !important; width: 100% !important;
  border-left: 2px solid transparent !important; letter-spacing: 0 !important;
  text-transform: none !important; transition: all .15s var(--ease) !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
  background: var(--g8) !important; color: var(--txt) !important; border-left-color: var(--gbr) !important;
}

.kv-div { height: 1px; background: var(--bd); margin: 10px 20px; }

/* Activity feed */
.kv-activity {
  margin: 4px 10px 8px; padding: 14px 15px;
  background: linear-gradient(145deg, var(--bg-3) 0%, var(--bg-4) 100%);
  border: 1px solid var(--bd); border-radius: 7px;
}
.kv-widget-head { font-size: 0.57rem; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; color: var(--txt3); margin-bottom: 10px; }
.kv-act-row { display: flex; align-items: flex-start; gap: 9px; margin-bottom: 9px; padding-bottom: 9px; border-bottom: 1px solid var(--bd2); }
.kv-act-row:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }
.kv-act-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--gold); opacity: 0.55; margin-top: 5px; flex-shrink: 0; }
.kv-act-main { font-size: 0.72rem; color: var(--txt2); line-height: 1.4; }
.kv-act-time { font-size: 0.62rem; color: var(--txt3); display: block; margin-top: 2px; }

/* Market insight */
.kv-insight {
  margin: 0 10px 8px; padding: 11px 14px;
  background: var(--g8); border: 1px solid var(--gbr); border-radius: 6px;
}
.kv-insight-head { font-size: 0.57rem; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; color: var(--gold); opacity: 0.7; margin-bottom: 5px; }
.kv-insight-val { font-family: var(--serif); font-size: 1.2rem; font-weight: 300; color: var(--txt); line-height: 1; }
.kv-insight-delta { font-size: 0.68rem; color: #4ADE80; margin-top: 3px; display: flex; align-items: center; gap: 3px; }

/* Model tag */
.kv-model-strip {
  margin: 0 10px 10px; padding: 8px 12px;
  background: var(--bg-3); border: 1px solid var(--bd); border-radius: 5px;
  display: flex; align-items: center; gap: 7px;
}
.kv-model-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--gold); animation: kv-pulse-gold 2.5s ease-in-out infinite; flex-shrink: 0; }
.kv-model-name { font-size: 0.63rem; font-weight: 600; color: var(--txt3); letter-spacing: 0.07em; }

/* Session status */
.kv-session {
  margin: 0 10px 10px; padding: 12px 14px;
  background: var(--g8); border: 1px solid var(--gbr); border-radius: 6px;
}
.kv-session-row { display: flex; align-items: center; gap: 7px; }
.kv-session-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--gold); animation: kv-pulse-gold 2s ease-in-out infinite; }
.kv-session-label { font-size: 0.7rem; font-weight: 600; color: var(--gold); letter-spacing: 0.07em; }
.kv-session-sub { font-size: 0.63rem; color: var(--txt3); margin-top: 4px; padding-left: 13px; }

/* ── HERO ────────────────────────────────────────────────────────────────── */
.kv-hero {
  position: relative; padding: 44px 0 36px; overflow: hidden;
}
.kv-hero-deco {
  position: absolute; right: -40px; top: 10px;
  width: 280px; height: 280px;
  border: 1px solid rgba(196,164,107,0.07);
  transform: rotate(15deg); pointer-events: none;
}
.kv-hero-deco-2 {
  position: absolute; right: 40px; top: 50px;
  width: 160px; height: 160px;
  border: 1px solid rgba(196,164,107,0.04);
  transform: rotate(15deg); pointer-events: none;
}
.kv-hero-label {
  font-size: 0.6rem; font-weight: 700; letter-spacing: 0.24em; text-transform: uppercase;
  color: var(--gold); margin-bottom: 14px;
  display: flex; align-items: center; gap: 10px;
  animation: kv-fade-up 0.45s var(--eout) both;
}
.kv-hero-label::before { content: ''; width: 22px; height: 1px; background: var(--gold); opacity: 0.45; }
.kv-hero-title {
  font-family: var(--serif); font-size: clamp(1.9rem, 3.2vw, 2.85rem);
  font-weight: 300; color: var(--txt); letter-spacing: -0.035em;
  line-height: 1.08; margin-bottom: 15px;
  animation: kv-fade-up 0.5s var(--eout) 0.05s both;
}
.kv-hero-title em { color: var(--gold); font-style: italic; font-weight: 300; }
.kv-hero-title strong { font-weight: 400; color: var(--txt); }
.kv-hero-sub {
  font-size: 0.88rem; color: var(--txt2); line-height: 1.65;
  max-width: 500px; margin-bottom: 28px;
  animation: kv-fade-up 0.55s var(--eout) 0.1s both;
}
.kv-metrics {
  display: flex; gap: 0; margin-bottom: 0;
  animation: kv-fade-up 0.6s var(--eout) 0.15s both;
}
.kv-metric { padding: 11px 20px; border: 1px solid var(--bd); border-right: none; background: var(--bg-2); }
.kv-metric:first-child { border-radius: 6px 0 0 6px; }
.kv-metric:last-child  { border-right: 1px solid var(--bd); border-radius: 0 6px 6px 0; }
.kv-metric-val { font-family: var(--serif); font-size: 1.25rem; font-weight: 300; color: var(--gold); letter-spacing: -0.03em; line-height: 1; margin-bottom: 3px; }
.kv-metric-lbl { font-size: 0.6rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--txt3); }

/* ── SECTION LABEL ───────────────────────────────────────────────────────── */
.kv-section-label {
  font-size: 0.59rem; font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase;
  color: var(--txt3); margin: 26px 0 14px;
  display: flex; align-items: center; gap: 12px;
}
.kv-section-label::after { content: ''; flex: 1; height: 1px; background: var(--bd); }

/* ── MODULE CARDS v3 ─────────────────────────────────────────────────────── */
.kv-module {
  background: linear-gradient(155deg, var(--bg-2) 0%, var(--bg-3) 100%);
  border: 1px solid var(--bd); border-radius: 8px;
  overflow: hidden; cursor: pointer; position: relative;
  transition: transform .28s var(--ease), border-color .28s var(--ease), box-shadow .28s var(--ease);
  animation: kv-fade-up 0.5s var(--eout) both;
}
.kv-module::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent 0%, var(--gold) 50%, transparent 100%);
  opacity: 0; transition: opacity .3s var(--ease);
}
.kv-module:hover { border-color: var(--gbr); transform: translateY(-3px); box-shadow: var(--sh), var(--shg); }
.kv-module:hover::before { opacity: 1; }

.kv-module-img-wrap { position: relative; height: 120px; overflow: hidden; }
.kv-module-img { width: 100%; height: 100%; object-fit: cover; display: block; filter: grayscale(25%) saturate(0.75) brightness(0.85); transition: filter .4s var(--ease), transform .4s var(--ease); }
.kv-module:hover .kv-module-img { filter: grayscale(0%) saturate(1) brightness(0.95); transform: scale(1.04); }
.kv-module-img-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to bottom, rgba(7,11,23,0.15) 0%, rgba(7,11,23,0.78) 100%);
}
.kv-module-img-cat {
  position: absolute; bottom: 10px; left: 14px;
  font-size: 0.58rem; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--gold); background: rgba(7,11,23,0.6); padding: 3px 8px; border-radius: 2px;
  backdrop-filter: blur(4px);
}
.kv-module-body { padding: 16px 18px 18px; }
.kv-module-title { font-family: var(--serif); font-size: 1.02rem; font-weight: 400; color: var(--txt); letter-spacing: -0.025em; margin-bottom: 6px; line-height: 1.2; }
.kv-module-desc { font-size: 0.77rem; color: var(--txt2); line-height: 1.5; margin-bottom: 12px; }

/* AI Preview snippet */
.kv-preview {
  background: var(--bg); border: 1px solid var(--bd); border-radius: 5px;
  padding: 8px 11px; margin-bottom: 13px; position: relative; overflow: hidden;
}
.kv-preview-tag {
  font-size: 0.5rem; font-weight: 700; letter-spacing: 0.1em; color: var(--gold);
  opacity: 0.45; text-transform: uppercase;
  position: absolute; top: 6px; right: 8px;
}
.kv-preview-text {
  font-size: 0.71rem; color: var(--txt2); line-height: 1.45; font-style: italic;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.kv-module-foot { display: flex; align-items: center; justify-content: space-between; }
.kv-module-arrow { font-size: 0.7rem; font-weight: 600; color: var(--gold); letter-spacing: 0.06em; transition: letter-spacing .2s var(--ease), gap .2s var(--ease); display: flex; align-items: center; gap: 4px; }
.kv-module:hover .kv-module-arrow { letter-spacing: 0.12em; }
.kv-module-usage { font-size: 0.6rem; color: var(--txt3); letter-spacing: 0.04em; }

/* ── CHIP PROMPTS ────────────────────────────────────────────────────────── */
.kv-chips { display: flex; flex-wrap: wrap; gap: 7px; margin: 20px 0 12px; animation: kv-fade-up 0.55s var(--eout) 0.2s both; }
.kv-chip {
  display: inline-flex; align-items: center; gap: 5px;
  padding: 6px 13px; background: var(--bg-2);
  border: 1px solid var(--bd); border-radius: 100px;
  font-size: 0.76rem; color: var(--txt2);
  cursor: pointer; white-space: nowrap;
  transition: all .18s var(--ease);
}
.kv-chip:hover { background: var(--g8); border-color: var(--gbr); color: var(--gold-lt); transform: translateY(-1px); }

/* ── COMMAND CENTER AREA ─────────────────────────────────────────────────── */
.kv-command-bar {
  padding: 14px 44px 6px;
  animation: kv-fade-up 0.6s var(--eout) 0.25s both;
}
.kv-command-label {
  font-size: 0.59rem; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--txt3); margin-bottom: 8px;
  display: flex; align-items: center; gap: 8px;
}
.kv-command-label::before {
  content: '';
  width: 4px; height: 4px; border-radius: 50%; background: var(--gold);
  animation: kv-pulse-gold 2s ease-in-out infinite; display: inline-block;
}

/* Input */
[data-testid="stChatInputContainer"], .stChatInputContainer {
  background: transparent !important; border-top: none !important;
  padding: 0 44px 26px !important;
}
[data-testid="stChatInput"] > div, .stChatInput > div {
  background: var(--bg-2) !important;
  border: 1px solid var(--gbr) !important;
  border-radius: 10px !important;
  box-shadow: 0 0 0 4px rgba(196,164,107,0.04), 0 0 70px -24px rgba(196,164,107,0.14), var(--sh) !important;
  transition: border-color .25s var(--ease), box-shadow .25s var(--ease) !important;
}
[data-testid="stChatInput"] > div:focus-within, .stChatInput > div:focus-within {
  border-color: rgba(196,164,107,0.48) !important;
  box-shadow: 0 0 0 5px rgba(196,164,107,0.07), 0 0 90px -20px rgba(196,164,107,0.22), var(--sh) !important;
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
  border: none !important; border-radius: 6px !important; color: var(--bg) !important;
  width: 36px !important; height: 36px !important; margin: 8px 10px !important;
  box-shadow: 0 4px 12px rgba(196,164,107,0.25) !important;
  transition: all .2s var(--ease) !important;
}
[data-testid="stChatInputSubmitButton"] button:hover {
  background: linear-gradient(135deg, var(--gold-lt) 0%, var(--gold) 100%) !important;
  transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(196,164,107,0.35) !important;
}

/* ── CONVERSATION ────────────────────────────────────────────────────────── */
.kv-conv-head {
  padding: 20px 0 15px; border-bottom: 1px solid var(--bd); margin-bottom: 18px;
  display: flex; align-items: center; justify-content: space-between;
}
.kv-conv-title { font-family: var(--serif); font-size: 0.88rem; font-weight: 300; color: var(--txt2); }
.kv-conv-meta { display: flex; align-items: center; gap: 7px; }
.kv-conv-badge { font-size: 0.6rem; color: var(--gold); background: var(--g8); border: 1px solid var(--gbr); border-radius: 2px; padding: 2px 7px; font-weight: 600; letter-spacing: 0.07em; }
.kv-model-tag { font-size: 0.58rem; color: var(--txt3); border: 1px solid var(--bd); border-radius: 2px; padding: 2px 6px; letter-spacing: 0.04em; }

[data-testid="stChatMessage"] {
  background: transparent !important; padding: 0 !important;
  gap: 12px !important; margin-bottom: 4px !important;
  max-width: 820px; margin-left: auto; margin-right: auto;
}
[data-testid="stChatMessageAvatarUser"] {
  background: rgba(237,231,212,0.07) !important; border: 1px solid rgba(237,231,212,0.11) !important;
  border-radius: 4px !important; width: 26px !important; min-width: 26px !important; height: 26px !important;
  color: var(--cream) !important; font-size: 0.64rem !important;
}
[data-testid="stChatMessageAvatarAssistant"] {
  background: linear-gradient(135deg, var(--gold-lt) 0%, var(--gold-dk) 100%) !important;
  border-radius: 4px !important; width: 26px !important; min-width: 26px !important; height: 26px !important;
  color: var(--bg) !important; font-size: 0.64rem !important;
  box-shadow: 0 4px 12px rgba(196,164,107,0.3) !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
  background: var(--cream) !important; color: #070B17 !important;
  border-radius: 2px 8px 8px 8px !important; padding: 11px 15px !important;
  font-size: 0.9rem !important; line-height: 1.65 !important;
  max-width: 74% !important; box-shadow: 0 2px 20px -4px rgba(0,0,0,0.4) !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
  background: var(--bg-2) !important; color: var(--txt) !important;
  border-radius: 8px 2px 8px 8px !important; border: 1px solid var(--bd) !important;
  padding: 16px 20px !important; font-size: 0.9rem !important; line-height: 1.78 !important;
  max-width: 88% !important; box-shadow: var(--sh) !important;
}
[data-testid="stChatMessageContent"] p { margin-bottom: 0.5em !important; color: inherit !important; }
[data-testid="stChatMessageContent"] p:last-child { margin-bottom: 0 !important; }
[data-testid="stChatMessageContent"] h2 { font-family: var(--serif) !important; font-size: 1.02rem !important; font-weight: 400 !important; color: var(--txt) !important; letter-spacing: -0.02em !important; margin: 1em 0 0.3em !important; }
[data-testid="stChatMessageContent"] h3 { font-family: var(--serif) !important; font-size: 0.92rem !important; font-weight: 400 !important; color: var(--gold-lt) !important; margin: 0.8em 0 0.25em !important; }
[data-testid="stChatMessageContent"] strong { color: var(--txt) !important; font-weight: 600 !important; }
[data-testid="stChatMessageContent"] em { color: var(--gold-lt) !important; }
[data-testid="stChatMessageContent"] ul, [data-testid="stChatMessageContent"] ol { padding-left: 1.1em !important; margin: 0.3em 0 0.45em !important; }
[data-testid="stChatMessageContent"] li { margin-bottom: 0.25em !important; line-height: 1.6 !important; }
[data-testid="stChatMessageContent"] code { background: var(--g8) !important; color: var(--gold-lt) !important; border: 1px solid var(--gbr) !important; border-radius: 3px !important; padding: 1px 5px !important; font-size: 0.82em !important; }
[data-testid="stChatMessageContent"] blockquote { border-left: 2px solid var(--gbr) !important; padding-left: 12px !important; color: var(--txt2) !important; margin: 0.5em 0 !important; }
[data-testid="stChatMessageContent"] hr { border: none !important; border-top: 1px solid var(--bd) !important; margin: 0.8em 0 !important; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] p,
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] strong { color: #070B17 !important; }

/* ── MAIN BUTTONS ────────────────────────────────────────────────────────── */
[data-testid="stMain"] [data-testid="stButton"] button, .main [data-testid="stButton"] button {
  background: transparent !important; color: var(--txt2) !important;
  border: 1px solid var(--bd) !important; border-radius: 4px !important;
  font-family: var(--sans) !important; font-size: 0.69rem !important;
  font-weight: 600 !important; letter-spacing: 0.1em !important;
  text-transform: uppercase !important; padding: 8px 20px !important;
  transition: all .18s var(--ease) !important;
}
[data-testid="stMain"] [data-testid="stButton"] button:hover, .main [data-testid="stButton"] button:hover {
  background: var(--g8) !important; border-color: var(--gbr) !important; color: var(--gold) !important;
}
/* Pill buttons - second columns row */
[data-testid="stColumns"] + [data-testid="stColumns"] [data-testid="stButton"] button {
  background: var(--bg-2) !important; color: var(--txt2) !important;
  border: 1px solid var(--bd) !important; border-radius: 6px !important;
  font-size: 0.8rem !important; font-weight: 400 !important;
  letter-spacing: 0.01em !important; text-transform: none !important;
  padding: 9px 14px !important;
}
[data-testid="stColumns"] + [data-testid="stColumns"] [data-testid="stButton"] button:hover {
  background: var(--g8) !important; border-color: var(--gbr) !important; color: var(--gold-lt) !important;
}

/* ── API KEY ─────────────────────────────────────────────────────────────── */
[data-testid="stExpander"] { background: var(--bg-2) !important; border: 1px solid var(--bd) !important; border-radius: 6px !important; }
[data-testid="stExpander"] summary { color: var(--txt2) !important; font-size: 0.82rem !important; }
[data-testid="stTextInput"] input { background: var(--bg-3) !important; color: var(--txt) !important; border: 1px solid var(--bd) !important; border-radius: 4px !important; font-size: 0.9rem !important; caret-color: var(--gold) !important; }
[data-testid="stTextInput"] input:focus { border-color: var(--gbr) !important; box-shadow: 0 0 0 2px rgba(196,164,107,0.06) !important; outline: none !important; }
[data-testid="stTextInput"] label { color: var(--txt2) !important; font-size: 0.78rem !important; }
[data-testid="stAlert"] { background: var(--g8) !important; border: 1px solid var(--gbr) !important; border-radius: 5px !important; color: var(--txt) !important; font-size: 0.85rem !important; }

/* ── COLUMNS ─────────────────────────────────────────────────────────────── */
[data-testid="stColumns"] { gap: 12px !important; align-items: stretch !important; }

/* ── ANIMATIONS ──────────────────────────────────────────────────────────── */
@keyframes kv-fade-up { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
@keyframes kv-fade-in { from { opacity:0; } to { opacity:1; } }
@keyframes kv-pulse-gold { 0%,100%{opacity:1;box-shadow:0 0 8px rgba(196,164,107,0.4);} 50%{opacity:0.45;box-shadow:0 0 2px rgba(196,164,107,0.1);} }
@keyframes kv-pulse-green { 0%,100%{opacity:1;box-shadow:0 0 8px rgba(74,222,128,0.55);} 50%{opacity:0.55;box-shadow:0 0 3px rgba(74,222,128,0.15);} }
@keyframes kv-blink { 0%,100%{opacity:1;} 50%{opacity:0.1;} }
.kv-cursor {
  display: inline-block; width: 2px; height: 0.84em; background: var(--gold);
  margin-left: 1px; border-radius: 1px; animation: kv-blink 1s var(--ease) infinite;
  vertical-align: text-bottom;
}

/* Stagger for cards */
.kv-module:nth-child(1){animation-delay:.0s;}
.kv-module:nth-child(2){animation-delay:.08s;}
.kv-module:nth-child(3){animation-delay:.16s;}

/* ── RESPONSIVE ──────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .block-container,[data-testid="stAppViewBlockContainer"] { padding: 0 18px 20px !important; }
  [data-testid="stChatInputContainer"],.stChatInputContainer { padding: 0 18px 18px !important; }
  .kv-hero { padding: 28px 0 24px; }
  .kv-hero-title { font-size: 1.7rem !important; }
  .kv-metrics { flex-wrap: wrap; }
  .kv-metric { flex: 1 0 45%; }
  .kv-chips { gap: 6px; }
  .kv-command-bar { padding: 10px 18px 4px; }
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

MODULES = [
    {
        "icon": "✦",
        "cat": "CONTENU",
        "title": "Création de contenu",
        "desc": "Posts LinkedIn, captions Instagram, scripts Reels, newsletters",
        "preview": "« 5 raisons pour lesquelles les délais VEFA sont une opportunité… »",
        "usage": "Format professionnel · Multi-réseaux",
        "img": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=600&q=72&auto=format&fit=crop&crop=top",
        "prompt": "Crée un post LinkedIn premium sur les délais de livraison VEFA et la communication des promoteurs",
    },
    {
        "icon": "◈",
        "cat": "PROSPECTION",
        "title": "Prospection B2B",
        "desc": "DM LinkedIn, emails froids, séquences de relance personnalisées",
        "preview": "« Bonjour [Prénom], j'ai analysé votre lancement du programme… »",
        "usage": "Ciblage précis · Ton naturel",
        "img": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=600&q=72&auto=format&fit=crop",
        "prompt": "Génère un DM LinkedIn percutant pour prospecter un directeur marketing de promoteur immobilier",
    },
    {
        "icon": "◎",
        "cat": "ANALYSE",
        "title": "Audit promoteur",
        "desc": "Score digital /100, forces, faiblesses, angles d'approche précis",
        "preview": "« Score global : 61/100 · Point faible majeur : réseaux sociaux… »",
        "usage": "Score /100 · Quick wins",
        "img": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&q=72&auto=format&fit=crop&crop=top",
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
        "prompt": "Analyse les tendances du marché immobilier neuf en France et identifie les opportunités commerciales",
    },
]

NAV_ITEMS = [
    ("✦", "Contenu"), ("◈", "Prospection"), ("◎", "Analyse"),
    ("⊞", "Repurposing"), ("◇", "Idéation"), ("◉", "Veille"),
]

CHIPS = [
    ("✍", "Post LinkedIn sur les délais VEFA"),
    ("🏢", "Audit digital d'un promoteur"),
    ("◈", "DM de prospection Nexity"),
    ("⚡", "10 hooks réservation VEFA"),
    ("↔", "Décliner un sujet en 6 formats"),
]

ACTIVITY = [
    ("Post LinkedIn — Délais VEFA", "Il y a 2h"),
    ("Audit Bouygues Immo — Score 74/100", "Il y a 5h"),
    ("DM LinkedIn — Directeur marketing", "Hier"),
    ("10 hooks — leads immobilier neuf", "Il y a 2j"),
]

# ══════════════════════════════════════════════════════════════════════════════
# INIT
# ══════════════════════════════════════════════════════════════════════════════
api_key = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""
if not api_key:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.html(CSS)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # Logo + AI status
    st.markdown("""
    <div class="kv-logo-wrap">
      <div class="kv-logotype">K<em>—</em>VEFA<span class="kv-logotype-badge">AI</span></div>
      <div class="kv-ai-status">
        <span class="kv-status-ring"></span>
        <span class="kv-status-label">Opus 4.7 · Actif</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    st.markdown('<div class="kv-nav-label">Modules</div>', unsafe_allow_html=True)

    for icon, label in NAV_ITEMS:
        if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
            mod = next((m for m in MODULES if m["cat"].upper() == label.upper() or m["title"].upper() == label.upper()), None)
            if mod:
                st.session_state.messages.append({"role": "user", "content": mod["prompt"]})
                st.rerun()

    st.markdown('<div class="kv-div"></div>', unsafe_allow_html=True)

    # Activity feed
    act_rows = "".join([
        f"""<div class="kv-act-row">
          <div class="kv-act-dot"></div>
          <div><div class="kv-act-main">{text}</div><span class="kv-act-time">{time}</span></div>
        </div>"""
        for text, time in ACTIVITY
    ])
    st.markdown(f"""
    <div class="kv-activity">
      <div class="kv-widget-head">Activité récente</div>
      {act_rows}
    </div>
    """, unsafe_allow_html=True)

    # Market insight
    st.markdown("""
    <div class="kv-insight">
      <div class="kv-insight-head">Marché VEFA · France</div>
      <div class="kv-insight-val">+12 % leads Q1</div>
      <div class="kv-insight-delta">↑ vs. trimestre précédent</div>
    </div>
    """, unsafe_allow_html=True)

    # Model badge
    st.markdown("""
    <div class="kv-model-strip">
      <div class="kv-model-dot"></div>
      <div class="kv-model-name">claude-opus-4-7 · Cache actif · &lt;2s</div>
    </div>
    """, unsafe_allow_html=True)

    # Session / reset
    if st.session_state.messages:
        n = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.markdown(f"""
        <div class="kv-session">
          <div class="kv-session-row">
            <span class="kv-session-dot"></span>
            <span class="kv-session-label">Session active</span>
          </div>
          <div class="kv-session-sub">{n} échange{"s" if n > 1 else ""} · En cours</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("↺  Nouvelle conversation", key="reset", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # API key (if missing)
    if not api_key:
        st.markdown('<div class="kv-div"></div>', unsafe_allow_html=True)
        with st.expander("🔑 Clé API", expanded=True):
            api_key = st.text_input("Clé Anthropic", type="password", placeholder="sk-ant-...")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if not api_key:
    st.markdown("""
    <div style="text-align:center;padding:100px 0;color:rgba(216,208,188,0.3);font-size:0.85rem;">
      Configurez votre clé API dans la barre latérale pour accéder à K—VEFA Intelligence.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Welcome ─────────────────────────────────────────────────────────────────
if not st.session_state.messages:

    # Hero
    st.markdown("""
    <div class="kv-hero">
      <div class="kv-hero-deco"></div>
      <div class="kv-hero-deco-2"></div>
      <div class="kv-hero-label">Intelligence VEFA</div>
      <div class="kv-hero-title">
        Votre centre de commande<br><em>immobilier premium</em>
      </div>
      <div class="kv-hero-sub">
        L'IA spécialisée VEFA qui prospecte, analyse et crée du contenu<br>
        en quelques secondes — sans formation, sans friction.
      </div>
      <div class="kv-metrics">
        <div class="kv-metric"><div class="kv-metric-val">3–5h</div><div class="kv-metric-lbl">Gagnées / semaine</div></div>
        <div class="kv-metric"><div class="kv-metric-val">+38%</div><div class="kv-metric-lbl">Taux de réponse</div></div>
        <div class="kv-metric"><div class="kv-metric-val">&lt;60s</div><div class="kv-metric-lbl">Génération moy.</div></div>
        <div class="kv-metric"><div class="kv-metric-val">Opus 4.7</div><div class="kv-metric-lbl">Modèle IA</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Module cards (top 3)
    st.markdown('<div class="kv-section-label">Modules principaux</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="small")
    for col, mod in zip([c1, c2, c3], MODULES[:3]):
        with col:
            st.markdown(f"""
            <div class="kv-module">
              <div class="kv-module-img-wrap">
                <img class="kv-module-img" src="{mod['img']}" alt="{mod['title']}" loading="lazy">
                <div class="kv-module-img-overlay"></div>
                <div class="kv-module-img-cat">{mod['cat']}</div>
              </div>
              <div class="kv-module-body">
                <div class="kv-module-title">{mod['title']}</div>
                <div class="kv-module-desc">{mod['desc']}</div>
                <div class="kv-preview">
                  <span class="kv-preview-tag">Aperçu IA</span>
                  <div class="kv-preview-text">{mod['preview']}</div>
                </div>
                <div class="kv-module-foot">
                  <div class="kv-module-arrow">Démarrer →</div>
                  <div class="kv-module-usage">{mod['usage']}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Ouvrir", key=f"mod_{mod['cat']}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": mod["prompt"]})
                st.rerun()

    # Secondary modules as pills
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3, gap="small")
    for col, mod in zip([p1, p2, p3], MODULES[3:]):
        with col:
            if st.button(f"{mod['icon']}  {mod['title']}", key=f"pill_{mod['cat']}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": mod["prompt"]})
                st.rerun()

    # Chip prompts label
    st.markdown('<div class="kv-section-label" style="margin-top:22px">Suggestions rapides</div>', unsafe_allow_html=True)

# ── Conversation ─────────────────────────────────────────────────────────────
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

# ── AI Command Center label ──────────────────────────────────────────────────
if not st.session_state.messages:
    # Chip buttons (5 suggestions)
    kc1, kc2, kc3, kc4, kc5 = st.columns(5, gap="small")
    for col, (icon, label) in zip([kc1, kc2, kc3, kc4, kc5], CHIPS):
        with col:
            if st.button(f"{icon}  {label[:26]}{'…' if len(label)>26 else ''}", key=f"chip_{label[:8]}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": label})
                st.rerun()
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

st.html("""
<div class="kv-command-bar">
  <div class="kv-command-label">Commande IA</div>
</div>
""")

# ── Input ────────────────────────────────────────────────────────────────────
prompt = st.chat_input("Décrivez votre besoin VEFA — contenu, prospection, analyse, hooks…")

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
                system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
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

        except Exception as e:
            err = str(e)
            if "credit" in err.lower() or "balance" in err.lower():
                placeholder.error("Solde Anthropic insuffisant. Rechargez votre compte sur console.anthropic.com")
            elif "api_key" in err.lower() or "auth" in err.lower():
                placeholder.error("Clé API invalide. Vérifiez la configuration dans la sidebar.")
            else:
                placeholder.error(f"Erreur : {err}")
    st.rerun()
