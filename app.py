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

# --- RACE DATA WITH ODDS ---
race_day_races_with_odds = [
    {"track": "Morphetville", "race": "Race 2", "horse": "Light The Night", "barrier": "1", "odds": 2.40},
    {"track": "Rosehill", "race": "Race 1", "horse": "Regal Problem", "barrier": "1", "odds": 2.35},
    {"track": "Rosehill", "race": "Race 3", "horse": "Incognito", "barrier": "1", "odds": 1.55},
    {"track": "Rosehill", "race": "Race 4", "horse": "Miss Scandal", "barrier": "1", "odds": 2.40},
    {"track": "Caulfield", "race": "Race 6", "horse": "Big Sky", "barrier": "1", "odds": 1.65},
    {"track": "Rosehill", "race": "Race 6", "horse": "Cross Tavern", "barrier": "1", "odds": 1.55},
    {"track": "Eagle Farm", "race": "Race 5", "horse": "Earn To Burn", "barrier": "1", "odds": 1.95},
    {"track": "Ascot", "race": "Race 3", "horse": "Daryte", "barrier": "1", "odds": 1.70},
    {"track": "Morphetville", "race": "Race 10", "horse": "Mic Drop", "barrier": "1", "odds": 2.35},
    {"track": "Rosehill", "race": "Race 9", "horse": "Willie Oppa", "barrier": "1", "odds": 2.40},
    {"track": "Caulfield", "race": "Race 10", "horse": "Stealth of the Night", "barrier": "1", "odds": 2.30},
    {"track": "Eagle Farm", "race": "Race 10", "horse": "True Amor", "barrier": "1", "odds": 1.80},
    {"track": "Ascot", "race": "Race 7", "horse": "Famous Dain", "barrier": "1", "odds": 2.20},
    {"track": "Ascot", "race": "Race 9", "horse": "Too Darn Stormy", "barrier": "1", "odds": 2.25}
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
st.title("🐕 Datura Companion v1.5")

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
    st.info("🏁 Race Day Mode: 14 races. Pause after 2 wins.")
elif st.session_state.mode == 'perpetual':
    st.info("🌀 Perpetual Mode: Reset stake after win. No pause.")
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
    full_race_label = f"{race['track']} • {race['race']} - {race['horse']} (Barrier {race['barrier']})"
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

# --- IMPLIED PROBABILITY DIFFERENTIAL GUIDE (Perpetual Mode Only) ---
if st.session_state.mode == 'perpetual':
    imp_prob_fav = 1 / st.session_state.current_odds
    imp_prob_40 = imp_prob_fav * (1 - 0.40)
    imp_prob_45 = imp_prob_fav * (1 - 0.45)
    imp_prob_50 = imp_prob_fav * (1 - 0.50)
    odds_40 = round(1 / imp_prob_40, 2) if imp_prob_40 > 0 else 0
    odds_45 = round(1 / imp_prob_45, 2) if imp_prob_45 > 0 else 0
    odds_50 = round(1 / imp_prob_50, 2) if imp_prob_50 > 0 else 0

    st.info(f"""
    🔍 **Implied Probability Differential Guide**  
    Based on favourite odds: **{st.session_state.current_odds:.2f}** → Implied Prob: **{imp_prob_fav:.1%}**

    For a **clear market favourite**, the second favourite should have:
    - **40% lower probability** → Odds ≥ **{odds_40}**
    - **45% lower probability** → Odds ≥ **{odds_45}**
    - **50% lower probability** → Odds ≥ **{odds_50}**

    🎯 Stronger signal when second favourite's odds meet or exceed these values.  
    ✅ Minimum threshold: **40% differential** recommended.
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
    # Advance to next race
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
    if random.random() < win_prob:
        st.session_state.bankroll += (recommended_stake * st.session_state.current_odds) - recommended_stake
        st.session_state.consecutive_wins += 1
        st.session_state.last_bet_amount = st.session_state.bankroll * base_stake_pct
        log_and_advance("AUTO WIN", (recommended_stake * st.session_state.current_odds) - recommended_stake)
    else:
        st.session_state.bankroll -= recommended_stake
        st.session_state.consecutive_wins = 0
        st.session_state.last_bet_amount = recommended_stake
        log_and_advance("AUTO LOSS", -recommended_stake)

# --- RACE HISTORY ---
if st.session_state.race_history:
    st.divider()
    st.subheader("📋 Race History")
    history_df = pd.DataFrame(st.session_state.race_history)
    st.dataframe(history_df, use_container_width=True, hide_index=True)

    # --- PROFIT CHART ---
    st.subheader("📈 Profit Chart")
    chart_data = history_df[["Timestamp", "Bankroll"]].set_index("Timestamp")
    st.line_chart(chart_data["Bankroll"])

# --- EXPLAINER ---
with st.expander("ℹ️ Logic & Rules"):
    st.markdown("""
    ### **Datura Companion v1.5**
    - **Only bet on favourites** — no underdogs, no overlays
    - **Expected Win Rates**:
      - **NRL/AFL Favourites**: 65%
      - **Horses/Dogs (Start-of-Day Favourite)**: 60%
    - **Edge = (Expected Win Rate × Odds) - 1**
    - **Implied Probability Differential**:  
      Second favourite should be **40%–50% less likely** than favourite → strong market signal
    - **Staking**: Dynamic, based on loss streak and odds — **no 5% cap**
    - **Auto Run**: Simulate with speed control
    - **Profit Chart**: Track bankroll evolution

    **No form analysis. No insider knowledge. Just market structure.**
    """)
