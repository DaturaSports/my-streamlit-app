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
    st.session_state.opening_odds = 1.80
    st.session_state.mode = None
    st.session_state.auto_running = False
    st.session_state.speed = 1.0
    st.session_state.bet_phase = None
    st.session_state.sunk_fund = 0.0  # Cumulative lost stakes in current losing run
    st.session_state.in_losing_streak = False

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

st.set_page_config(page_title="Datura Companion v2.2", layout="wide")

# --- RACE DATA ---
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
        st.session_state.sunk_fund = 0.0

    win_rate_base = st.slider("Expected Win Rate (Favourite)", 0.01, 1.00, 0.60, format="%.2f")

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
st.title("🐕 Datura Companion v2.2")

# Metrics
pnl = st.session_state.bankroll - st.session_state.initial_bankroll
col1, col2, col3 = st.columns(3)
col1.metric("Bankroll", f"\${st.session_state.bankroll:,.2f}")
col2.metric("P&L", f"\${pnl:,.2f}", delta=f"{pnl:+,.2f}")
col3.metric("Sunk Fund", f"\${st.session_state.sunk_fund:,.2f}")

st.divider()

# --- MODE SELECTION ---
mode_col1, mode_col2 = st.columns(2)
if mode_col1.button("🎯 Start-of-Day Run", use_container_width=True):
    st.session_state.mode = 'race_day'
    st.session_state.bet_phase = 'start_day'
    st.session_state.current_race_index = 0
    st.session_state.consecutive_wins = 0
    st.session_state.sunk_fund = 0.0
    st.session_state.last_bet_amount = 0.0
    st.rerun()

if mode_col2.button("🔁 Perpetual Run", use_container_width=True):
    st.session_state.mode = 'perpetual'
    st.session_state.bet_phase = 'perpetual'
    st.session_state.current_race_index = 0
    st.session_state.consecutive_wins = 0
    st.session_state.sunk_fund = 0.0
    st.session_state.last_bet_amount = 0.0
    st.rerun()

# --- DISPLAY MODE ---
if st.session_state.mode == 'race_day':
    st.info("🏁 Start-of-Day Run: ×2/×3/×5 progression. Opening odds only.")
elif st.session_state.mode == 'perpetual':
    st.info("🌀 Perpetual Run: Stake = (Sunk Fund / (Live Odds - 1)) × 1.11. Reset on win.")
else:
    st.info("Select a mode to begin.")
    st.stop()

# --- AUTO RUN CONTROL ---
if st.session_state.auto_running:
    st.warning("▶️ Auto Run Active — Simulating...")
    col_a, col_b = st.columns([1, 1])
    if col_a.button("⏸️ Pause Auto Run"):
        st.session_state.auto_running = False
        st.rerun()
    if col_b.button("⏹️ Stop & Reset"):
        st.session_state.auto_running = False
        st.session_state.mode = None
        st.session_state.bet_phase = None
        st.rerun()
    st.divider()

# --- CURRENT RACE ---
if st.session_state.mode == 'race_day':
    if st.session_state.current_race_index >= len(race_day_races_with_odds):
        st.success("🎉 All races completed!")
        st.stop()
    race = race_day_races_with_odds[st.session_state.current_race_index]
    full_race_label = f"{race['track']} • {race['race']} [{race['time']}] - {race['horse']} (Barrier {race['barrier']})"
    st.session_state.current_odds = race['odds']
else:
    full_race_label = f"Race #{st.session_state.current_race_index + 1}"

st.subheader("Current Race")
st.markdown(f"**{full_race_label}**")

# --- OPENING ODDS INPUT (for thresholds) ---
st.subheader("Opening Day Odds")
opening_odds = st.number_input(
    "Enter Opening Odds of Favourite",
    min_value=1.01,
    value=st.session_state.opening_odds,
    step=0.01,
    format="%.2f"
)
st.session_state.opening_odds = opening_odds

# Show notification if below \$1.25
if opening_odds < 1.25:
    st.error("❌ No Bet – Odds below \$1.25")
    st.stop()

# --- LIVE ODDS (for stake calculation) ---
st.subheader("Live Odds (For Stake Calc)")
live_odds = st.number_input(
    "Enter Current Live Odds",
    min_value=1.01,
    value=st.session_state.current_odds,
    step=0.01,
    format="%.2f"
)
st.session_state.current_odds = live_odds

# --- PROBABILITY GAP REFERENCE (based on Opening Odds) ---
p1 = 1 / st.session_state.opening_odds
thresholds = [0.35, 0.40, 0.45, 0.50]
results = {}
for t in thresholds:
    p2_max = p1 - t
    if p2_max <= 0:
        results[t] = "Not feasible"
    else:
        min_odds_2nd = round(1 / p2_max, 2)
        results[t] = min_odds_2nd

st.info(f"""
🔍 **Probability Gap Thresholds (Opening Odds: \${st.session_state.opening_odds:.2f})**  
- **≥35% gap** → 2nd fav ≥ **{results[0.35]}**
- **≥40% gap** → 2nd fav ≥ **{results[0.40]}**
- **≥45% gap** → 2nd fav ≥ **{results[0.45]}**
- **≥50% gap** → 2nd fav ≥ **{results[0.50]}**
""", icon="📊")

# --- DATORA EDGE (based on Opening Odds) ---
implied_prob = 1 / st.session_state.opening_odds
datura_edge_decimal = (win_rate_base * st.session_state.opening_odds) - 1
datura_edge_percent = datura_edge_decimal * 100
edge_color = "green" if datura_edge_decimal > 0 else "red"
st.markdown(f"**Implied Prob:** {implied_prob * 100:.2f}%")
st.markdown(f"**Win Rate:** {win_rate_base:.2%}")
st.markdown(f"### **Datura Edge:** :{edge_color}[{datura_edge_percent:+.2f}%]")

# --- STAKE CALCULATION (Perpetual Run Only) ---
recommended_stake = 0.0

if st.session_state.bet_phase == 'perpetual':
    if st.session_state.consecutive_wins == 0 and st.session_state.last_bet_amount == 0:
        # First bet in run
        recommended_stake = st.session_state.bankroll * 0.01
    elif st.session_state.consecutive_wins > 0:
        # After win — reset
        recommended_stake = st.session_state.bankroll * 0.01
    else:
        # After loss — apply formula: (Sunk Fund / (Live Odds - 1)) × 1.11
        if (live_odds - 1) <= 0:
            st.error("Invalid odds: must be > 1.00")
            st.stop()
        recommended_stake = (st.session_state.sunk_fund / (live_odds - 1)) * 1.11

    # Cap stake to bankroll
    if recommended_stake > st.session_state.bankroll:
        st.warning(f"⚠️ Stake (\${recommended_stake:,.2f}) exceeds bankroll. Capped.")
        recommended_stake = st.session_state.bankroll

elif st.session_state.bet_phase == 'start_day':
    # Start-of-Day Run — as before (×2/×3/×5)
    if st.session_state.consecutive_wins == 0 and st.session_state.last_bet_amount == 0:
        recommended_stake = st.session_state.bankroll * 0.01
    elif st.session_state.consecutive_wins > 0:
        recommended_stake = st.session_state.bankroll * 0.01
    else:
        last_odds = st.session_state.last_bet_odds
        if last_odds > 2.00:
            recommended_stake = st.session_state.last_bet_amount * 2
        elif 1.50 < last_odds <= 2.00:
            recommended_stake = st.session_state.last_bet_amount * 3
        elif 1.25 <= last_odds <= 1.50:
            recommended_stake = st.session_state.last_bet_amount * 5
        else:
            recommended_stake = st.session_state.bankroll * 0.01

    if recommended_stake > st.session_state.bankroll:
        recommended_stake = st.session_state.bankroll

st.success(f"**Recommended Stake:** \${recommended_stake:,.2f}")

# --- WIN/LOSS BUTTONS ---
st.divider()
col_win, col_loss = st.columns(2)

def log_and_advance(result: str, profit: float):
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.race_history.append({
        "Race": full_race_label,
        "Phase": st.session_state.bet_phase,
        "Opening Odds": st.session_state.opening_odds,
        "Live Odds": st.session_state.current_odds,
        "Stake": round(recommended_stake, 2),
        "Result": result,
        "Profit": round(profit, 2),
        "Bankroll": round(st.session_state.bankroll, 2),
        "Sunk Fund": st.session_state.sunk_fund,
        "Timestamp": timestamp
    })
    st.session_state.current_race_index += 1
    st.session_state.current_odds = 1.80
    st.session_state.opening_odds = 1.80
    st.rerun()

if col_win.button("✅ WIN", use_container_width=True):
    profit = (recommended_stake * st.session_state.current_odds) - recommended_stake
    st.session_state.bankroll += profit
    st.session_state.consecutive_wins += 1
    st.session_state.sunk_fund = 0.0  # Reset
    st.session_state.last_bet_amount = st.session_state.bankroll * 0.01
    log_and_advance("WIN", profit)

if col_loss.button("❌ LOSS", use_container_width=True):
    st.session_state.bankroll -= recommended_stake
    st.session_state.consecutive_wins = 0
    st.session_state.sunk_fund += recommended_stake  # Add to cumulative loss
    st.session_state.last_bet_amount = recommended_stake
    log_and_advance("LOSS", -recommended_stake)

# --- AUTO RUN LOOP ---
if st.session_state.auto_running:
    time.sleep(2.0 / st.session_state.speed)
    win_prob = 0.60
    result = "WIN" if random.random() < win_prob else "LOSS"
    profit = 0.0
    if result == "WIN":
        profit = (recommended_stake * st.session_state.current_odds) - recommended_stake
        st.session_state.bankroll += profit
        st.session_state.consecutive_wins += 1
        st.session_state.sunk_fund = 0.0
    else:
        st.session_state.bankroll -= recommended_stake
        st.session_state.consecutive_wins = 0
        st.session_state.sunk_fund += recommended_stake
    st.session_state.last_bet_amount = recommended_stake
    log_and_advance(result, profit if result == "WIN" else -recommended_stake)
