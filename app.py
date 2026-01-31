import streamlit as st
import pandas as pd
from datetime import datetime
import time
import random

# --- SESSION STATE INIT ---
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0
    st.session_state.initial_bankroll = 1000.0
    st.session_state.consecutive_wins = 0
    st.session_state.last_bet_amount = 0.0
    st.session_state.race_history = []
    st.session_state.current_race_index = 0
    st.session_state.current_odds = 1.80
    st.session_state.mode = None
    st.session_state.auto_running = False
    st.session_state.speed = 1.0

# --- THEME TOGGLE ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Set theme
if st.session_state.theme == 'dark':
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #0e1117;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

st.set_page_config(page_title="Datura Companion", layout="wide")

# --- RACE DATA WITH ODDS AND TIME (AEDT) ---
race_day_races_with_odds = [
    {"track": "Morphetville", "race": "Race 2", "time": "12:29pm (AEDT)", "horse": "Light The Night", "barrier": "1", "odds": 2.40},
    {"track": "Rosehill", "race": "Race 1", "time": "12:35pm (AEDT)", "horse": "Regal Problem", "barrier": "1", "odds": 2.35},
    {"track": "Rosehill", "race": "Race 3", "time": "1:45pm (AEDT)", "horse": "Incognito", "barrier": "1", "odds": 1.55},
    {"track": "Rosehill", "race": "Race 4", "time": "2:20pm (AEDT)", "horse": "Miss Scandal", "barrier": "1", "odds": 2.40},
    {"track": "Caulfield", "race": "Race 6", "time": "3:10pm (AEDT)", "horse": "Big Sky", "barrier": "1", "odds": 1.65},
    {"track": "Rosehill", "race": "Race 6", "time": "3:30pm (AEDT)", "horse": "Cross Tavern", "barrier": "1", "odds": 1.55},
    {"track": "Eagle Farm", "race": "Race 5", "time": "3:38pm (AEDT)", "horse": "Earn To Burn", "barrier": "1", "odds": 1.95},
    {"track": "Ascot", "race": "Race 3", "time": "4:51pm (AEDT)", "horse": "Daryte", "barrier": "1", "odds": 1.70},
    {"track": "Morphetville", "race": "Race 10", "time": "5:12pm (AEDT)", "horse": "Mic Drop", "barrier": "1", "odds": 2.35},
    {"track": "Rosehill", "race": "Race 9", "time": "5:20pm (AEDT)", "horse": "Willie Oppa", "barrier": "1", "odds": 2.40},
    {"track": "Caulfield", "race": "Race 10", "time": "5:40pm (AEDT)", "horse": "Stealth of the Night", "barrier": "1", "odds": 2.30},
    {"track": "Eagle Farm", "race": "Race 10", "time": "6:48pm (AEDT)", "horse": "True Amor", "barrier": "1", "odds": 1.80},
    {"track": "Ascot", "race": "Race 7", "time": "7:17pm (AEDT)", "horse": "Famous Dain", "barrier": "1", "odds": 2.20},
    {"track": "Ascot", "race": "Race 9", "time": "8:30pm (AEDT)", "horse": "Too Darn Stormy", "barrier": "1", "odds": 2.25}
]

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Settings")
    new_bankroll = st.number_input(
        "Starting Bankroll (\$)",
        min_value=10.0,
        value=st.session_state.initial_bankroll,
        step=10.0
    )
    if new_bankroll != st.session_state.initial_bankroll:
        st.session_state.initial_bankroll = new_bankroll
        st.session_state.bankroll = new_bankroll
        st.session_state.last_bet_amount = 0.0

    base_stake_pct = st.slider(
        "Base Stake (% of Bankroll)",
        min_value=0.1,
        max_value=5.0,
        value=1.0,
        step=0.1,
        format="%.1f%%"
    ) / 100.0

    win_rate_base = st.slider("Expected Win Rate (Favourite)", 0.01, 1.00, 0.60, format="%.2f")

    # Auto Run Speed
    st.session_state.speed = st.select_slider(
        "Auto Run Speed",
        options=[0.5, 1.0, 2.0, 5.0],
        format_func=lambda x: "Slow" if x == 0.5 else "Normal" if x == 1.0 else "Fast" if x == 2.0 else "Max",
        value=1.0
    )

    if st.button("🌓 Toggle Theme"):
        toggle_theme()

    if st.button("🔁 Reset Session"):
        st.session_state.clear()
        st.rerun()

# --- MAIN INTERFACE ---
st.title("🐕 Datura Companion v1.7")

# Metrics
pnl = st.session_state.bankroll - st.session_state.initial_bankroll
col1, col2, col3 = st.columns(3)
col1.metric("Bankroll", f"\${st.session_state.bankroll:,.2f}")
col2.metric("P&L", f"\${pnl:,.2f}", delta=f"{pnl:+,.2f}")
col3.metric("Win Streak", f"{st.session_state.consecutive_wins}W")

st.divider()

# --- MODE SELECTION ---
mode_col1, mode_col2, mode_col3 = st.columns(3)
if mode_col1.button("🎯 Start Race Day", use_container_width=True):
    st.session_state.mode = 'race_day'
    st.session_state.current_race_index = 0
    st.session_state.consecutive_wins = 0
    st.session_state.last_bet_amount = 0.0
    st.session_state.auto_running = False
    st.rerun()

if mode_col2.button("🔁 Start Perpetual Run", use_container_width=True):
    st.session_state.mode = 'perpetual'
    st.session_state.current_race_index = 0
    st.session_state.consecutive_wins = 0
    st.session_state.last_bet_amount = 0.0
    st.session_state.auto_running = False
    st.rerun()

if mode_col3.button("▶️ Auto Run Simulation", use_container_width=True):
    if not st.session_state.mode:
        st.warning("Please select a mode first.")
    else:
        st.session_state.auto_running = True
        st.rerun()

# --- DISPLAY MODE STATUS ---
if st.session_state.mode == 'race_day':
    st.info("🏁 Race Day Mode: 14 races with AEDT times. Pause after 2 wins.")
elif st.session_state.mode == 'perpetual':
    st.info("🌀 Perpetual Mode: Dynamic probability gap thresholds.")
else:
    st.info("Select a mode to begin.")
    st.stop()

# --- AUTO RUN CONTROL BAR ---
if st.session_state.auto_running:
    st.warning("▶️ Auto Run Active — Simulating...")
    col_a, col_b = st.columns([1, 1])
    if col_a.button("⏸️ Pause Auto Run"):
        st.session_state.auto_running = False
        st.rerun()
    if col_b.button("⏹️ Stop & Reset"):
        st.session_state.auto_running = False
        st.session_state.mode = None
        st.rerun()
    st.divider()

# --- CURRENT RACE ---
if st.session_state.mode == 'race_day':
    if st.session_state.current_race_index >= len(race_day_races_with_odds):
        st.success("🎉 All races completed!")
        st.session_state.auto_running = False
        st.stop()
    race = race_day_races_with_odds[st.session_state.current_race_index]
    full_race_label = f"{race['track']} • {race['race']} [{race['time']}] - {race['horse']} (Barrier {race['barrier']})"
    st.session_state.current_odds = race['odds']
else:
    full_race_label = f"Perpetual Race #{st.session_state.current_race_index + 1}"

st.subheader("Current Race")
st.markdown(f"**{full_race_label}**")

# --- ODDS INPUT ---
st.subheader("Favourite Odds")
if st.session_state.mode == 'perpetual':
    odds_input = st.number_input(
        "Enter Favourite Odds",
        min_value=1.01,
        value=st.session_state.current_odds,
        step=0.01,
        format="%.2f",
        key="odds_input_live"
    )
    st.session_state.current_odds = odds_input
else:
    st.info(f"Odds auto-set to: **\${st.session_state.current_odds:.2f}** (from race card)")

# --- PERPETUAL PROBABILITY GAP THRESHOLD GUIDE ---
if st.session_state.mode == 'perpetual':
    p1 = 1 / st.session_state.current_odds
    thresholds = [0.40, 0.45, 0.50]
    results = {}

    for t in thresholds:
        p2_max = p1 - t
        if p2_max <= 0:
            results[t] = "Not feasible"
        else:
            min_odds_2nd = round(1 / p2_max, 2)
            results[t] = min_odds_2nd

    st.info(f"""
    🔍 **Perpetual Probability Gap Thresholds**  
    Favourite Odds: **\${st.session_state.current_odds:.2f}** → Implied Prob: **{p1:.1%}**

    For a valid bet, second favourite must have:
    - **≥ 40% gap** → Odds ≥ **{results[0.40] if results[0.40] != 'Not feasible' else 'N/A'}**
    - **≥ 45% gap** → Odds ≥ **{results[0.45] if results[0.45] != 'Not feasible' else 'N/A'}**
    - **≥ 50% gap** → Odds ≥ **{results[0.50] if results[0.50] != 'Not feasible' else 'N/A'}**

    ✅ Example:  
    If favourite is \$1.50 (66.7%), and second favourite is \$4.80 (20.8%),  
    gap = 66.7% – 20.8% = **45.9%** → **Meets 45% threshold → Bet Y**

    🎯 Only proceed if second favourite's **odds ≥ threshold values above**.
    """, icon="📊")

# --- DATORA EDGE ---
implied_prob = 1 / st.session_state.current_odds
datura_edge_decimal = (win_rate_base * st.session_state.current_odds) - 1
datura_edge_percent = datura_edge_decimal * 100

# --- STAKE LOGIC ---
betting_allowed = True
if st.session_state.mode == 'race_day' and st.session_state.consecutive_wins >= 2:
    betting_allowed = False
    st.warning("⏸️ 2 wins in a row. Betting paused until a loss occurs.")

if not betting_allowed:
    recommended_stake = 0.0
    st.info("No bet recommended (awaiting loss after 2 wins).")
else:
    if st.session_state.consecutive_wins > 0:
        recommended_stake = st.session_state.bankroll * base_stake_pct
    elif st.session_state.last_bet_amount == 0:
        recommended_stake = st.session_state.bankroll * base_stake_pct
    else:
        if st.session_state.current_odds > 2.00:
            recommended_stake = st.session_state.last_bet_amount * 2
        elif 1.50 < st.session_state.current_odds <= 2.00:
            recommended_stake = st.session_state.last_bet_amount * 3
        elif 1.25 < st.session_state.current_odds <= 1.50:
            recommended_stake = st.session_state.last_bet_amount * 5
        else:
            recommended_stake = st.session_state.bankroll * base_stake_pct

    if recommended_stake > st.session_state.bankroll:
        st.warning(f"⚠️ Stake exceeds bankroll. Reduced to \${st.session_state.bankroll:,.2f}")
        recommended_stake = st.session_state.bankroll

    st.success(f"**Recommended Stake:** \${recommended_stake:,.2f}")

# --- DISPLAY EDGE ---
st.markdown(f"**Implied Prob:** {implied_prob * 100:.2f}%")
st.markdown(f"**Expected Win Rate:** {win_rate_base:.2%}")
edge_color = "green" if datura_edge_decimal > 0 else "red"
st.markdown(f"### **Datura Edge:** :{edge_color}[{datura_edge_percent:+.2f}%]")

# --- WIN/LOSS BUTTONS ---
st.divider()
col_win, col_loss = st.columns(2)

def log_and_advance(result: str, profit: float):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.race_history.append({
        "Race": full_race_label,
        "Odds": st.session_state.current_odds,
        "Stake": round(recommended_stake, 2),
        "Result": result,
        "Profit": round(profit, 2),
        "Bankroll": round(st.session_state.bankroll, 2),
        "Timestamp": timestamp
    })
    st.session_state.current_race_index += 1
    st.session_state.current_odds = 1.80
    st.rerun()

if col_win.button("✅ WIN", use_container_width=True):
    if not betting_allowed:
        st.warning("Cannot place bet — 2 wins already recorded.")
    else:
        profit = (recommended_stake * st.session_state.current_odds) - recommended_stake
        st.session_state.bankroll += profit
        st.session_state.consecutive_wins += 1
        st.session_state.last_bet_amount = st.session_state.bankroll * base_stake_pct
        log_and_advance("WIN", profit)

if col_loss.button("❌ LOSS", use_container_width=True):
    st.session_state.bankroll -= recommended_stake
    st.session_state.consecutive_wins = 0
    st.session_state.last_bet_amount = recommended_stake
    log_and_advance("LOSS", -recommended_stake)

# --- AUTO RUN LOOP ---
if st.session_state.auto_running:
    time.sleep(2.0 / st.session_state.speed)
    win_prob = 0.60
