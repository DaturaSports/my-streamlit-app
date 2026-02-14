# datura_companion.py - Datura Companion v3.2 (Full Verified - 14 Feb 2026)
import streamlit as st
import pandas as pd
from datetime import datetime

# --- SESSION STATE INIT ---
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0
    st.session_state.initial_bankroll = 1000.0
    st.session_state.consecutive_wins = 0
    st.session_state.consecutive_losses = 0
    st.session_state.last_bet_amount = 0.0
    st.session_state.last_bet_odds = 1.80
    st.session_state.race_history = []
    st.session_state.current_race_index = 0
    st.session_state.current_odds = 1.80
    st.session_state.mode = None
    st.session_state.bet_phase = None
    st.session_state.sunk_fund = 0.0
    st.session_state.auto_running = False
    st.session_state.speed = 1.0
    st.session_state.sports_selection = None
    st.session_state.t20_current_index = 0
    st.session_state.selected_fixture = None
    st.session_state.theme = 'light'

# --- THEME TOGGLE ---
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

st.set_page_config(page_title="Datura Companion v3.2", layout="wide")

# --- RACE DATA (Start-of-Day) - 8 Favourites for Sat, 14 Feb 2026 ---
race_day_races_with_odds = [
    {"track": "Eagle Farm", "race": "Race 2", "time": "12:03", "horse": "Larado (4)", "barrier": "4", "odds": 1.75},
    {"track": "Flemington", "race": "Race 4", "time": "12:45", "horse": "Immortal Star (1)", "barrier": "1", "odds": 2.25},
    {"track": "Morphettville", "race": "Race 3", "time": "12:57", "horse": "Bassett Babe (5)", "barrier": "5", "odds": 1.40},
    {"track": "Randwick", "race": "Race 4", "time": "13:05", "horse": "Sovereign Hill (7)", "barrier": "7", "odds": 2.05},
    {"track": "Randwick", "race": "Race 5", "time": "13:40", "horse": "Cross Tasman (10)", "barrier": "10", "odds": 1.90},
    {"track": "Flemington", "race": "Race 6", "time": "13:55", "horse": "Saint George (6)", "barrier": "6", "odds": 2.50},
    {"track": "Randwick", "race": "Race 8", "time": "15:30", "horse": "Autumn Glow (9)", "barrier": "9", "odds": 1.60},
    {"track": "Flemington", "race": "Race 9", "time": "15:50", "horse": "Sixties (10)", "barrier": "10", "odds": 1.80}
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
st.title("🐕 Datura Companion v3.2")

# Metrics
pnl = st.session_state.bankroll - st.session_state.initial_bankroll
col1, col2, col3 = st.columns(3)
col1.metric("Bankroll", f"\${st.session_state.bankroll:,.2f}")
col2.metric("P&L", f"\${pnl:,.2f}", delta=f"{pnl:+,.2f}")
col3.metric("Mode", st.session_state.mode or "None")

st.divider()

# --- MODE NAVIGATION ---
st.subheader("🎯 Select Mode")

col_m1, col_m2, col_m3 = st.columns(3)
if col_m1.button("🏁 Start-of-Day Favourites", use_container_width=True):
    st.session_state.mode = 'race_day'
    st.session_state.bet_phase = 'start_day'
    st.session_state.current_race_index = 0
    st.session_state.consecutive_wins = 0
    st.session_state.consecutive_losses = 0
    st.session_state.sunk_fund = 0.0
    st.session_state.last_bet_amount = 0.0
    st.session_state.last_bet_odds = 1.80
    st.session_state.race_history = []
    st.rerun()

if col_m2.button("🌀 Perpetual Run", use_container_width=True):
    st.session_state.mode = 'perpetual'
    st.session_state.bet_phase = 'perpetual'
    st.session_state.current_race_index = 0
    st.session_state.consecutive_wins = 0
    st.session_state.consecutive_losses = 0
    st.session_state.sunk_fund = 0.0
    st.session_state.last_bet_amount = 0.0
    st.session_state.last_bet_odds = 1.80
    st.session_state.race_history = []
    st.rerun()

if col_m3.button("🏏 Sports (T20 WC 2026)", use_container_width=True):
    st.session_state.mode = 'sports'
    st.session_state.sports_selection = 't20'
    st.session_state.t20_current_index = 0
    st.session_state.selected_fixture = None
    st.session_state.race_history = []
    st.rerun()

st.divider()

# === MODE: START-OF-DAY FAVOURITES ===
if st.session_state.mode == 'race_day':
    if st.session_state.current_race_index >= len(race_day_races_with_odds):
        st.success("🎉 All races completed!")
        st.stop()

    race = race_day_races_with_odds[st.session_state.current_race_index]
    full_race_label = f"{race['track']} • {race['race']} [{race['time']}] - {race['horse']} (Barrier {race['barrier']})"
    st.subheader("Current Race")
    st.markdown(f"**{full_race_label}**")

    st.session_state.current_odds = race['odds']

    if st.session_state.current_odds < 1.25:
        st.error("❌ No Bet – Odds below \$1.25")
        if st.button("⏭️ Skip to Next Race"):
            st.session_state.current_race_index += 1
            st.rerun()
        st.stop()

    st.info(f"**Start-of-Day Odds: \${st.session_state.current_odds:.2f}**", icon="🎯")

    # Auto-pause after 2 wins
    if st.session_state.consecutive_wins >= 2:
        st.warning("⚠️ Auto-pause: 2 wins in a row. Resume with next loss.")
        if st.button("🟢 Win (Confirm)"):
            st.session_state.consecutive_wins += 1
            st.session_state.consecutive_losses = 0
            st.session_state.race_history.append({
                "race": full_race_label,
                "odds": st.session_state.current_odds,
                "stake": st.session_state.last_bet_amount,
                "result": "Win",
                "timestamp": datetime.now().isoformat()
            })
            st.session_state.current_race_index += 1
            st.rerun()
        if st.button("🔴 Loss (Override)"):
            st.session_state.consecutive_wins = 0
            st.session_state.consecutive_losses = 1
            st.session_state.race_history.append({
                "race": full_race_label,
                "odds": st.session_state.current_odds,
                "stake": st.session_state.last_bet_amount,
                "result": "Loss",
                "timestamp": datetime.now().isoformat()
            })
            st.session_state.current
