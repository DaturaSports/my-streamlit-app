import streamlit as st
import pandas as pd
from datetime import datetime
import random
import time

# --- SESSION STATE INIT ---
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0
    st.session_state.initial_bankroll = 1000.0
    st.session_state.consecutive_wins = 0
    st.session_state.last_bet_amount = 0.0
    st.session_state.last_bet_odds = 1.70
    st.session_state.race_history = []
    st.session_state.current_race_index = 0
    st.session_state.current_odds = 1.80
    st.session_state.opening_odds = 1.80
    st.session_state.mode = None
    st.session_state.auto_running = False
    st.session_state.speed = 1.0
    st.session_state.bet_phase = None
    st.session_state.sunk_fund = 0.0
    st.session_state.sports_selection = None
    st.session_state.selected_fixture = None
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

st.set_page_config(page_title="Datura Companion v2.3 – Sports", layout="wide")

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

# Convert to DataFrame for sorting
df_fixtures = pd.DataFrame(t20_fixtures)
df_fixtures['date'] = pd.to_datetime(df_fixtures['date'])
df_fixtures = df_fixtures.sort_values('date').reset_index(drop=True)
df_fixtures['display'] = df_fixtures.apply(lambda x: f"{x['date'].strftime('%b %d')} | {x['match']} | {x['stage']} | {x['venue']}", axis=1)
fixture_options = df_fixtures['display'].tolist()

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
st.title("🏏 Sports Betting Module – T20 World Cup 2026")

# Metrics
pnl = st.session_state.bankroll - st.session_state.initial_bankroll
col1, col2, col3 = st.columns(3)
col1.metric("Bankroll", f"\${st.session_state.bankroll:,.2f}")
col2.metric("P&L", f"\${pnl:,.2f}", delta=f"{pnl:+,.2f}")
col3.metric("Win Streak", f"{st.session_state.consecutive_wins}W")

st.divider()

# --- SPORTS NAVIGATION ---
st.subheader("🌍 Sports")
col_s1, col_s2, col_s3 = st.columns(3)
if col_s1.button("🏏 T20", use_container_width=True):
    st.session_state.sports_selection = 't20'
    st.session_state.fixture_list = fixture_options
    st.rerun()
if col_s2.button("🏉 NRL", use_container_width=True):
    st.info("NRL coming soon.")
if col_s3.button("🇦🇺 AFL", use_container_width=True):
    st.info("AFL coming soon.")

# --- T20 SECTION ---
if st.session_state.sports_selection == 't20':
    st.success("✅ T20 World Cup 2026 – Select a fixture")
    selected_display = st.selectbox("📅 Select Fixture", options=fixture_options, index=0)
    st.session_state.selected_fixture = selected_display

    # Parse fixture
    selected_row = df_fixtures[df_fixtures['display'] == selected_display].iloc[0]
    match_info = f"**{selected_row['match']}** | {selected_row['stage']} | {selected_row['venue']} | {selected_row['date'].strftime('%B %d, %Y')}"

    st.markdown(f"### {match_info}")

    # --- ODDS INPUT ---
    opening_odds = st.number_input("🎯 Opening Odds of Favourite", min_value=1.01, value=1.80, step=0.01, format="%.2f")
    if opening_odds < 1.25:
        st.error("❌ No Bet – Odds below \$1.25")
        st.stop()

    live_odds = st.number_input("📡 Live Odds (For Stake)", min_value=1.01, value=opening_odds, step=0.01, format="%.2f")

    # --- PROBABILITY GAPS (Opening Odds) ---
    implied_prob = 1 / opening_odds
    thresholds = [0.35, 0.40, 0.45, 0.50]
    results = {}
    for t in thresholds:
        p2_max = implied_prob - t
        results[t] = round(1 / p2_max, 2) if p2_max > 0 else "N/A"

    st.info(f"""
    🔍 **Odds Gap Targets (Opening: \${opening_odds:.2f})**  
    - **≥35% gap** → ≥ **{results[0.35]}**
    - **≥40% gap** → ≥ **{results[0.40]}**
    - **≥45% gap** → ≥ **{results[0.45]}**
    - **≥50% gap** → ≥ **{results[0.50]}**
    """, icon="📊")

    # --- DATORA EDGE ---
    win_rate_base = 0.60
    datura_edge = (win_rate_base * opening_odds) - 1
    edge_color = "green" if datura_edge > 0 else "red"
    st.markdown(f"### **Edge:** :{edge_color}[{datura_edge * 100:+.2f}%]")

    # --- STAKE CALCULATION (Same as Start-of-Day) ---
    if st.session_state.consecutive_wins == 0 and st.session_state.last_bet_amount == 0:
        recommended_stake = st.session_state.bankroll * 0.01
    elif st.session_state.consecutive_wins > 0:
        recommended_stake = st.session_state.bankroll * 0.01
    else:
        if st.session_state.last_bet_odds > 2.00:
            recommended_stake = st.session_state.last_bet_amount * 2
        elif 1.50 < st.session_state.last_bet_odds <= 2.00:
            recommended_stake = st.session_state.last_bet_amount * 3
        elif 1.25 <= st.session_state.last_bet_odds <= 1.50:
            recommended_stake = st.session_state.last_bet_amount * 5
        else:
            recommended_stake = st.session_state.bankroll * 0.01

    if recommended_stake > st.session_state.bankroll:
        st.warning("⚠️ Stake exceeds bankroll. Capped.")
        recommended_stake = st.session_state.bankroll

    st.success(f"**Recommended Stake:** \${recommended_stake:,.2f}")

    # --- WIN/LOSS BUTTONS ---
    st.divider()
    col_win, col_loss = st.columns(2)

    def log_bet(result: str, profit: float):
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.session_state.race_history.append({
            "Fixture": selected_row['match'],
            "Stage": selected_row['stage'],
            "Opening Odds": opening_odds,
            "Live Odds": live_odds,
            "Stake": round(recommended_stake, 2),
            "Result": result,
            "Profit": round(profit, 2),
            "Bankroll": round(st.session_state.bankroll, 2),
            "Timestamp": timestamp
        })
        st.rerun()

    if col_win.button("✅ WIN", use_container_width=True):
        profit = (recommended_stake * live_odds) - recommended_stake
        st.session_state.bankroll += profit
        st.session_state.consecutive_wins += 1
        st.session_state.last_bet_amount = st.session_state.bankroll * 0.01
        st.session_state.last_bet_odds = opening_odds
        log_bet("WIN", profit)

    if col_loss.button("❌ LOSS", use_container_width=True):
        st.session_state.bankroll -= recommended_stake
        st.session_state.consecutive_wins = 0
        st.session_state.last_bet_amount = recommended_stake
        st.session_state.last_bet_odds = opening_odds
        log_bet("LOSS", -recommended_stake)

# --- BACK TO MAIN MODES ---
st.divider()
if st.button("⬅️ Back to Main Modes"):
    st.session_state.sports_selection = None
    st.session_state.selected_fixture = None
    st.rerun()
