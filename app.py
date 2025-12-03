# app.py
# 🎯 One Big Model - Final Fix: Stake Now Updates Correctly

import streamlit as st

# === SESSION STATE INITIALIZATION ===
if "starting_bankroll" not in st.session_state:
    st.session_state.starting_bankroll = 1000.0
if "current_bankroll" not in st.session_state:
    st.session_state.current_bankroll = 1000.0
if "target_profit" not in st.session_state:
    st.session_state.target_profit = 500.0
if "total_events" not in st.session_state:
    st.session_state.total_events = 50
if "events_completed" not in st.session_state:
    st.session_state.events_completed = 0
if "betting_mode" not in st.session_state:
    st.session_state.betting_mode = "Steady Grind"
if "pattern_source" not in st.session_state:
    st.session_state.pattern_source = "Use Proven League Strategy"
if "selected_league" not in st.session_state:
    st.session_state.selected_league = "NRL Favourite"
if "custom_win_rate" not in st.session_state:
    st.session_state.custom_win_rate = 0.50
if "odds" not in st.session_state:
    st.session_state.odds = 1.48  # 🔴 CRITICAL: Was missing
if "recommended_stake" not in st.session_state:
    st.session_state.recommended_stake = 0.0
if "last_outcome" not in st.session_state:
    st.session_state.last_outcome = None
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"
if "current_stake_multiplier" not in st.session_state:
    st.session_state.current_stake_multiplier = 1.0

# === THEME TOGGLE & STYLES ===
theme_toggle = st.sidebar.checkbox("☀️/🌙 Toggle Light/Dark Theme", value=(st.session_state.theme == "Light"))
if theme_toggle:
    st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"

primary_color = "#00cc00" if st.session_state.theme == "Dark" else "#009900"
bg_color = "#121212" if st.session_state.theme == "Dark" else "#f8f9fa"
text_color = "#e0e0e0" if st.session_state.theme == "Dark" else "#111111"
metric_bg = "#2a2a2a" if st.session_state.theme == "Dark" else "#f1f3f5"
metric_text_color = "#ffffff" if st.session_state.theme == "Dark" else "#111111"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .stMetric {{ background-color: {metric_bg}; color: {metric_text_color} !important; padding: 16px; border-radius: 8px; }}
    .stMetric .st-emotion-cache-1wmy9hl, .stMetric .st-emotion-cache-g3pm9b, .stMetric .st-emotion-cache-1a0t4q8 {{ color: {metric_text_color} !important; }}
    .stButton button[kind="primary"] {{ background-color: {primary_color}; color: white; }}
</style>
""", unsafe_allow_html=True)

# === STRATEGY & GOALS ===
st.title("🎯 One Big Model")

col1, col2 = st.columns(2)
with col1:
    st.session_state.betting_mode = st.radio("Betting Mode", ["Steady Grind", "Comeback", "Power Reset"], index=["Steady Grind", "Comeback", "Power Reset"].index(st.session_state.betting_mode))
with col2:
    st.session_state.target_profit = st.number_input("Target Profit ($)", min_value=0.0, value=float(st.session_state.target_profit), step=10.0)
    st.session_state.total_events = st.number_input("Total Events", min_value=1, value=int(st.session_state.total_events), step=1)

# === PATTERN SOURCE & WIN_RATE ===
st.subheader("Pattern Source")
st.session_state.pattern_source = st.radio("Select Pattern Source", ["Use Proven League Strategy", "Create Custom Pattern"], index=0 if st.session_state.pattern_source == "Use Proven League Strategy" else 1)

# 🟢 MOVE WIN_RATE LOGIC HERE — BEFORE ANY FUNCTION USES IT
win_rate = 0.50
avg_odds = 1.48

if st.session_state.pattern_source == "Use Proven League Strategy":
    st.session_state.selected_league = st.selectbox("Choose League", ["NRL Favourite", "Soccer League A", "Basketball League X"], index=["NRL Favourite", "Soccer League A", "Basketball League X"].index(st.session_state.selected_league))
    league_data = {
        "NRL Favourite": (0.666, 1.48),
        "Soccer League A": (0.60, 1.67),
        "Basketball League X": (0.55, 1.82)
    }
    win_rate, avg_odds = league_data[st.session_state.selected_league]
else:
    st.session_state.custom_win_rate = st.slider("Your Estimated Win Rate", min_value=0.01, max_value=0.99, value=st.session_state.custom_win_rate, step=0.01)
    win_rate = st.session_state.custom_win_rate
    avg_odds = st.session_state.odds

st.session_state.odds = avg_odds  # Ensure odds are updated

# === DYNAMIC STAKE MULTIPLIER ===
def update_stake_multiplier():
    mode = st.session_state.betting_mode
    outcome = st.session_state.last_outcome

    if mode == "Steady Grind":
        st.session_state.current_stake_multiplier = 1.0
    elif mode == "Comeback":
        if outcome == "loss":
            st.session_state.current_stake_multiplier = min(st.session_state.current_stake_multiplier + 0.5, 3.0)
        elif outcome == "win":
            st.session_state.current_stake_multiplier = 1.0
    elif mode == "Power Reset":
        if outcome == "win":
            st.session_state.current_stake_multiplier = min(st.session_state.current_stake_multiplier + 0.5, 3.0)
        elif outcome == "loss":
            st.session_state.current_stake_multiplier = 1.0

update_stake_multiplier()  # Run after win_rate and last_outcome are set

# === CALCULATE STAKE ===
def calculate_stake(p):
    if st.session_state.current_bankroll <= 0:
        return 0.0

    b = st.session_state.odds - 1  # Net odds
    q = 1 - p
    kelly = (b * p - q) / b if b > 0 else 0.0
    fractional_kelly = max(kelly * 0.5, 0.0)  # 50% Kelly, no negative

    base_risk = {
        "Steady Grind": 0.02,
        "Comeback": 0.03,
        "Power Reset": 0.04
    }[st.session_state.betting_mode]

    risk_amount = st.session_state.current_bankroll * (base_risk * st.session_state.current_stake_multiplier)
    kelly_amount = st.session_state.current_bankroll * fractional_kelly

    stake = min(risk_amount, kelly_amount)
    return max(stake, 5.0)

st.session_state.recommended_stake = calculate_stake(win_rate)

# === DISPLAY STAKE ===
st.subheader("Recommended Stake")
colA, colB = st.columns([2, 1])
with colA:
    st.markdown(f"<h2 style='color: {primary_color};'>${st.session_state.recommended_stake:,.2f}</h2>", unsafe_allow_html=True)
with colB:
    st.metric("Win Rate", f"{win_rate:.1%}")
    st.metric("Odds", f"{st.session_state.odds:.2f}")
    st.metric("Mult", f"{st.session_state.current_stake_multiplier:.1f}x")

# === RECORD OUTCOME ===
st.subheader("Record Outcome")
colX, colY, colZ = st.columns(3)
with colX:
    if st.button("🟢 Mark as Win"):
        st.session_state.current_bankroll += st.session_state.recommended_stake
        st.session_state.events_completed += 1
        st.session_state.last_outcome = "win"
        st.rerun()
with colY:
    if st.button("🔴 Mark as Loss"):
        st.session_state.current_bankroll -= st.session_state.recommended_stake
        st.session_state.events_completed += 1
        st.session_state.last_outcome = "loss"
        st.rerun()
with colZ:
    if st.button("🔄 Reset All"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# === FINAL METRICS ===
st.divider()
colP, colQ, colR = st.columns(3)
colP.metric("Bankroll", f"${st.session_state.current_bankroll:,.2f}")
colQ.metric("Completed", st.session_state.events_completed)
colR.metric("Remaining", f"${max(0, st.session_state.target_profit - (st.session_state.current_bankroll - st.session_state.starting_bankroll)):,.2f}")
