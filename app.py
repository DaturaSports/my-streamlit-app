# datura_companion.py - Datura Companion v3.0 (Final: Fixed Odds for Start-of-Day)
import streamlit as st
import pandas as pd
from datetime import datetime

# --- SESSION STATE INIT ---
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0
    st.session_state.initial_bankroll = 1000.0
    st.session_state.consecutive_wins = 0
    st.session_state.last_bet_amount = 0.0
    st.session_state.last_bet_odds = 1.80
    st.session_state.race_history = []
    st.session_state.current_race_index = 0
    st.session_state.current_odds = 1.80
    st.session_state.mode = None  # 'race_day', 'perpetual', 'sports'
    st.session_state.auto_running = False
    st.session_state.speed = 1.0
    st.session_state.bet_phase = None
    st.session_state.sunk_fund = 0.0
    st.session_state.sports_selection = None
    st.session_state.t20_current_index = 0
    st.session_state.fixture_list = []

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

st.set_page_config(page_title="Datura Companion v3.0", layout="wide")

# --- RACE DATA (Start-of-Day) - Fixed Odds as Provided ---
race_day_races_with_odds = [
    {"track": "Caulfield", "race": "Race 1", "time": "11:15am/1:15pm", "horse": "Ambassadorial (6)", "barrier": "6", "odds": 1.90},
    {"track": "Randwick", "race": "Race 2", "time": "12:05pm/1:05pm", "horse": "Autumn Break (5)", "barrier": "5", "odds": 1.85},
    {"track": "Caulfield", "race": "Race 3", "time": "12:20pm/1:20pm", "horse": "Guest House (6)", "barrier": "6", "odds": 2.00},
    {"track": "Doomben", "race": "Race 2", "time": "12:48pm/1:48pm", "horse": "Dominant Darcy (2)", "barrier": "2", "odds": 1.75},
    {"track": "Morphettville", "race": "Race 4", "time": "1:07pm/2:07pm", "horse": "World's My Oyster (4)", "barrier": "4", "odds": 1.85},
    {"track": "Ascot", "race": "Race 2", "time": "3:04pm/4:04pm", "horse": "Boy Crush (7)", "barrier": "7", "odds": 1.70},
    {"track": "Doomben", "race": "Race 9", "time": "5:10pm/6:10pm", "horse": "Hell (2)", "barrier": "2", "odds": 1.70},
    {"track": "Ascot", "race": "Race 7", "time": "6:12pm/7:12pm", "horse": "Fancy Red (4)", "barrier": "4", "odds": 1.85}
]

# --- T20 WORLD CUP 2026 FIXTURES ---
t20_fixtures = [
    {"date": "2026-02-07", "match": "Pakistan vs Netherlands", "stage": "Group Stage", "venue": "Mumbai"},
    {"date": "2026-02-07", "match": "India vs USA", "stage": "Group Stage", "venue": "Mumbai"},
    {"date": "2026-02-08", "match": "Australia vs Oman", "stage": "Group Stage", "venue": "Kolkata"},
    {"date": "2026-02-08", "match": "Sri Lanka vs Ireland", "stage": "Group Stage", "venue": "Kolkata"},
    {"date": "2026-02-09", "match": "England vs Italy", "stage": "Group Stage", "venue": "Colombo"},
    {"date": "2026-02-09", "match": "West Indies vs Scotland", "stage": "Group Stage", "venue": "Colombo"},
    {"date": "2026-02-10", "match": "New Zealand vs UAE", "stage": "Group Stage", "venue": "Chennai"},
    {"date": "2026-02-10", "match": "South Africa vs Canada", "stage": "Group Stage", "venue": "Chennai"},
    {"date": "2026-02-11", "match": "India vs Namibia", "stage": "Group Stage", "venue": "Delhi"},
    {"date": "2026-02-12", "match": "Pakistan vs USA", "stage": "Group Stage", "venue": "Delhi"},
    {"date": "2026-02-13", "match": "Australia vs Zimbabwe", "stage": "Group Stage", "venue": "Bangalore"},
    {"date": "2026-02-13", "match": "Sri Lanka vs Oman", "stage": "Group Stage", "venue": "Bangalore"},
    {"date": "2026-02-14", "match": "England vs Nepal", "stage": "Group Stage", "venue": "Ahmedabad"},
    {"date": "2026-02-14", "match": "West Indies vs Italy", "stage": "Group Stage", "venue": "Ahmedabad"},
    {"date": "2026-02-15", "match": "India vs Pakistan", "stage": "Group Stage", "venue": "Mumbai"},
    {"date": "2026-02-16", "match": "New Zealand vs Canada", "stage": "Group Stage", "venue": "Pune"},
    {"date": "2026-02-16", "match": "South Africa vs UAE", "stage": "Group Stage", "venue": "Pune"},
    {"date": "2026-02-17", "match": "Afghanistan vs Canada", "stage": "Group Stage", "venue": "Nagpur"},
    {"date": "2026-02-17", "match": "New Zealand vs Afghanistan", "stage": "Group Stage", "venue": "Nagpur"},
    {"date": "2026-02-18", "match": "Namibia vs Netherlands", "stage": "Group Stage", "venue": "Hyderabad"},
    {"date": "2026-02-18", "match": "India vs Netherlands", "stage": "Group Stage", "venue": "Hyderabad"},
    {"date": "2026-02-19", "match": "USA vs Namibia", "stage": "Group Stage", "venue": "Visakhapatnam"},
    {"date": "2026-02-19", "match": "Pakistan vs Namibia", "stage": "Group Stage", "venue": "Visakhapatnam"},
    {"date": "2026-02-20", "match": "Ireland vs Zimbabwe", "stage": "Group Stage", "venue": "Colombo"},
    {"date": "2026-02-20", "match": "Australia vs Ireland", "stage": "Group Stage", "venue": "Colombo"},
    {"date": "2026-02-21", "match": "Super 8 Match 1", "stage": "Super 8", "venue": "Mumbai"},
    {"date": "2026-02-21", "match": "Super 8 Match 2", "stage": "Super 8", "venue": "Kolkata"},
    {"date": "2026-02-22", "match": "Super 8 Match 3", "stage": "Super 8", "venue": "Chennai"},
    {"date": "2026-02-22", "match": "Super 8 Match 4", "stage": "Super 8", "venue": "Colombo"},
    {"date": "2026-02-23", "match": "Super 8 Match 5", "stage": "Super 8", "venue": "Ahmedabad"},
    {"date": "2026-02-23", "match": "Super 8 Match 6", "stage": "Super 8", "venue": "Pune"},
    {"date": "2026-02-24", "match": "Super 8 Match 7", "stage": "Super 8", "venue": "Delhi"},
    {"date": "2026-02-24", "match": "Super 8 Match 8", "stage": "Super 8", "venue": "Bangalore"},
    {"date": "2026-02-25", "match": "Super 8 Match 9", "stage": "Super 8", "venue": "Mumbai"},
    {"date": "2026-02-25", "match": "Super 8 Match 10", "stage": "Super 8", "venue": "Kolkata"},
    {"date": "2026-02-26", "match": "Super 8 Match 11", "stage": "Super 8", "venue": "Chennai"},
    {"date": "2026-02-26", "match": "Super 8 Match 12", "stage": "Super 8", "venue": "Colombo"},
    {"date": "2026-03-04", "match": "Semi-Final 1", "stage": "Semi-Final", "venue": "Mumbai"},
    {"date": "2026-03-05", "match": "Semi-Final 2", "stage": "Semi-Final", "venue": "Kolkata"},
    {"date": "2026-03-08", "match": "Final", "stage": "Final", "venue": "Chennai"},
]

df_fixtures = pd.DataFrame(t20_fixtures)
df_fixtures['date'] = pd.to_datetime(df_fixtures['date'])
df_fixtures = df_fixtures.sort_values('date').reset_index(drop=True)

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Settings")
    new_bankroll = st.number_input(
        "Starting Bankroll (\\$)",
        min_value=10.0,
        value=st.session_state.initial_bankroll,
        step=10.0
    )
    if new_bankroll != st.session_state.initial_bankroll:
        st.session_state.initial_bankroll = new_bankroll
        st.session_state.bankroll = new_bankroll
        st.session_state.sunk_fund = 0.0

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
st.title("🐕 Datura Companion v3.0")

# Metrics
pnl = st.session_state.bankroll - st.session_state.initial_bankroll
col1, col2, col3 = st.columns(3)
col1.metric("Bankroll", f"\\${st.session_state.bankroll:,.2f}")
col2.metric("P&L", f"\\${pnl:,.2f}", delta=f"{pnl:+,.2f}")
col3.metric("Mode", st.session_state.mode or "None")

st.divider()

# --- MODE NAVIGATION ---
st.subheader("🎯 Select Mode")

col_m1, col_m2, col_m3 = st.columns(3)
if col_m1.button("🏁 Start-of-Day Run", use_container_width=True):
    st.session_state.mode = 'race_day'
    st.session_state.bet_phase = 'start_day'
    st.session_state.current_race_index = 0
    st.session_state.consecutive_wins = 0
    st.session_state.sunk_fund = 0.0
    st.session_state.last_bet_amount = 0.0
    st.rerun()

if col_m2.button("🌀 Perpetual Run", use_container_width=True):
    st.session_state.mode = 'perpetual'
    st.session_state.bet_phase = 'perpetual'
    st.session_state.current_race_index = 0
    st.session_state.consecutive_wins = 0
    st.session_state.sunk_fund = 0.0
    st.session_state.last_bet_amount = 0.0
    st.rerun()

if col_m3.button("🏏 Sports", use_container_width=True):
    st.session_state.mode = 'sports'
    st.session_state.sports_selection = 't20'
    st.session_state.t20_current_index = 0
    st.session_state.selected_fixture = None
    st.rerun()

st.divider()

# === MODE: START-OF-DAY RUN ===
if st.session_state.mode == 'race_day':
    if st.session_state.current_race_index >= len(race_day_races_with_odds):
        st.success("🎉 All races completed!")
        st.stop()

    race = race_day_races_with_odds[st.session_state.current_race_index]
    full_race_label = f"{race['track']} • {race['race']} [{race['time']}] - {race['horse']} (Barrier {race['barrier']})"
    st.subheader("Current Race")
    st.markdown(f"**{full_race_label}**")

    # Fixed odds — no user input
    st.session_state.current_odds = race['odds']

    if st.session_state.current_odds < 1.25:
        st.error("❌ No Bet – Odds below \\$1.25")
        st.stop()

    st.info(f"**Fixed Odds: \\${st.session_state.current_odds:.2f}**", icon="🎯")

    # --- PROBABILITY GAPS using fixed odds as opening ===
    implied_prob = 1 / st.session_state.current_odds
    thresholds = [0.35, 0.40, 0.45, 0.50]
    results = {}
    for t in thresholds:
        p2_max = implied_prob - t
        results[t] = round(1 / p2_max, 2) if p2_max > 0 else "N/A"

    st.info(f"""
    🔍 **Odds Gap Targets (Fixed: \\${st.session_state.current_odds:.2f})**
    - ≥35% → ≥ {results[0.35]}
    - ≥40% → ≥ {results[0.40]}
    - ≥45% → ≥ {results[0.45]}
    - ≥50% → ≥ {results[0.50]}
    """, icon="📊")

    # --- STAKE CALC (×2/×3/×5) ---
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
        st.warning("⚠️ Stake exceeds bankroll. Capped.")
        recommended_stake = st.session_state.bankroll

    st.success(f"**Recommended Stake:** \\${recommended_stake:,.2f}")

    # --- WIN/LOSS ---
    col_win, col_loss = st.columns(2)
    def log_race(result, profit):
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.race_history.append({
            "Race": full_race_label, "Phase": "Start-of-Day", "Stake": recommended_stake,
            "Result": result, "Profit": profit, "Bankroll": st.session_state.bankroll, "Timestamp": timestamp
        })
        st.session_state.current_race_index += 1
        st.rerun()

    if col_win.button("✅ WIN", use_container_width=True):
        profit = (recommended_stake * st.session_state.current_odds) - recommended_stake
        st.session_state.bankroll += profit
        st.session_state.consecutive_wins += 1
        st.session_state.last_bet_amount = st.session_state.bankroll * 0.01
        st.session_state.last_bet_odds = st.session_state.current_odds
        log_race("WIN", round(profit, 2))

    if col_loss.button("❌ LOSS", use_container_width=True):
        st.session_state.bankroll -= recommended_stake
        st.session_state.consecutive_wins = 0
        st.session_state.last_bet_amount = recommended_stake
        st.session_state.last_bet_odds = st.session_state.current_odds
        log_race("LOSS", -recommended_stake)

# === MODE: PERPETUAL RUN ===
elif st.session_state.mode == 'perpetual':
    st.subheader("🌀 Perpetual Run")
    full_race_label = f"Race #{st.session_state.current_race_index + 1}"

    opening_odds = st.number_input("Opening Odds of Favourite", min_value=1.01, value=st.session_state.opening_odds, step=0.01, format="%.2f")
    st.session_state.opening_odds = opening_odds

    if opening_odds < 1.25:
        st.error("❌ No Bet – Odds below \\$1.25")
        st.stop()

    live_odds = st.number_input("Live Odds (For Stake)", min_value=1.01, value=1.80, step=0.01, format="%.2f")

    # --- PROBABILITY GAPS ---
    implied_prob = 1 / opening_odds
    thresholds = [0.35, 0.40, 0.45, 0.50]
    results = {}
    for t in thresholds:
        p2_max = implied_prob - t
        results[t] = round(1 / p2_max, 2) if p2_max > 0 else "N/A"

    st.info(f"""
    🔍 **Odds Gap Targets (Opening: \\${opening_odds:.2f})**
    - ≥35% → ≥ {results[0.35]}
    - ≥40% → ≥ {results[0.40]}
    - ≥45% → ≥ {results[0.45]}
    - ≥50% → ≥ {results[0.50]}
    """, icon="📊")

    # --- STAKE: (Sunk Fund / (Live Odds - 1)) × 1.11 ---
    if st.session_state.consecutive_wins == 0 and st.session_state.last_bet_amount == 0:
        recommended_stake = st.session_state.bankroll * 0.01
    elif st.session_state.consecutive_wins > 0:
        recommended_stake = st.session_state.bankroll * 0.01
    else:
        if (live_odds - 1) <= 0:
            st.error("Invalid live odds")
            st.stop()
        recommended_stake = (st.session_state.sunk_fund / (live_odds - 1)) * 1.11

    if recommended_stake > st.session_state.bankroll:
        st.warning("⚠️ Stake exceeds bankroll. Capped.")
        recommended_stake = st.session_state.bankroll

    st.success(f"**Recommended Stake:** \\${recommended_stake:,.2f}")

    # --- WIN/LOSS ---
    col_win, col_loss = st.columns(2)
    def log_perp(result, profit):
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.race_history.append({
            "Race": full_race_label, "Phase": "Perpetual", "Stake": recommended_stake,
            "Result": result, "Profit": profit, "Bankroll": st.session_state.bankroll, "Timestamp": timestamp
        })
        st.session_state.current_race_index += 1
        st.rerun()

    if col_win.button("✅ WIN", use_container_width=True):
        profit = (recommended_stake * live_odds) - recommended_stake
        st.session_state.bankroll += profit
        st.session_state.consecutive_wins += 1
        st.session_state.sunk_fund = 0.0
        st.session_state.last_bet_amount = st.session_state.bankroll * 0.01
        log_perp("WIN", round(profit, 2))

    if col_loss.button("❌ LOSS", use_container_width=True):
        st.session_state.bankroll -= recommended_stake
        st.session_state.consecutive_wins = 0
        st.session_state.sunk_fund += recommended_stake
        st.session_state.last_bet_amount = recommended_stake
        log_perp("LOSS", -recommended_stake)

# === MODE: SPORTS (T20) ===
elif st.session_state.mode == 'sports':
    st.subheader("🏏 T20 World Cup 2026")

    if st.session_state.t20_current_index >= len(df_fixtures):
        st.success("🎉 All fixtures completed!")
        st.stop()

    current_fixture = df_fixtures.iloc[st.session_state.t20_current_index]
    match_info = f"**{current_fixture['match']}** | {current_fixture['stage']} | {current_fixture['venue']} | {current_fixture['date'].strftime('%B %d, %Y')}"
    st.markdown(f"### {match_info}")

    opening_odds = st.number_input("Opening Odds of Favourite", min_value=1.01, value=1.80, step=0.01, format="%.2f")
    if opening_odds < 1.25:
        st.error("❌ No Bet – Odds below \\$1.25")
        st.stop()

    live_odds = st.number_input("Live Odds (For Stake)", min_value=1.01, value=opening_odds, step=0.01, format="%.2f")

    # --- PROBABILITY GAPS ---
    implied_prob = 1 / opening_odds
    thresholds = [0.35, 0.40, 0.45, 0.50]
    results = {}
    for t in thresholds:
        p2_max = implied_prob - t
        results[t] = round(1 / p2_max, 2) if p2_max > 0 else "N/A"

    st.info(f"""
    🔍 **Odds Gap Targets (Opening: \\${opening_odds:.2f})**
    - ≥35% → ≥ {results[0.35]}
    - ≥40% → ≥ {results[0.40]}
    - ≥45% → ≥ {results[0.45]}
    - ≥50% → ≥ {results[0.50]}
    """, icon="📊")

    # --- STAKE LOGIC (Same as Start-of-Day) ---
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
        st.warning("⚠️ Stake exceeds bankroll. Capped.")
        recommended_stake = st.session_state.bankroll

    st.success(f"**Recommended Stake:** \\${recommended_stake:,.2f}")

    # --- WIN/LOSS ---
    col_win, col_loss = st.columns(2)
    def log_sport(result, profit):
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.race_history.append({
            "Fixture": current_fixture['match'], "Stage": current_fixture['stage'],
            "Opening Odds": opening_odds, "Live Odds": live_odds,
            "Stake": recommended_stake, "Result": result, "Profit": profit,
            "Bankroll": st.session_state.bankroll, "Timestamp": timestamp
        })
        st.session_state.t20_current_index += 1
        st.rerun()

    if col_win.button("✅ WIN", use_container_width=True):
        profit = (recommended_stake * live_odds) - recommended_stake
        st.session_state.bankroll += profit
        st.session_state.consecutive_wins += 1
        st.session_state.last_bet_amount = st.session_state.bankroll * 0.01
        st.session_state.last_bet_odds = opening_odds
        log_sport("WIN", round(profit, 2))

    if col_loss.button("❌ LOSS", use_container_width=True):
        st.session_state.bankroll -= recommended_stake
        st.session_state.consecutive_wins = 0
        st.session_state.last_bet_amount = recommended_stake
        st.session_state.last_bet_odds = opening_odds
        log_sport("LOSS", -recommended_stake)

# --- BACK BUTTON ---
st.divider()
if st.button("⬅️ Back to Modes"):
    st.session_state.mode = None
    st.session_state.selected_fixture = None
    st.rerun()
