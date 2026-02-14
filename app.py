# datura_companion.py - Datura Companion v5.1 (Clean, Working, No Errors)
import streamlit as st
import pandas as pd
from datetime import datetime

# --- Initialize Session State ---
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0
    st.session_state.initial_bankroll = 1000.0
    st.session_state.consecutive_wins = 0
    st.session_state.consecutive_losses = 0
    st.session_state.last_bet_amount = 0.0
    st.session_state.last_bet_odds = 1.80
    st.session_state.race_history = []
    st.session_state.current_race_index = 0
    st.session_state.mode = None
    st.session_state.bet_active = True  # Enable betting unless paused

# --- RACE DATA (14 Feb 2026) ---
race_day_races = [
    {"track": "Eagle Farm", "race": "Race 2", "time": "12:03", "horse": "Larado (4)", "odds": 1.75},
    {"track": "Flemington", "race": "Race 4", "time": "12:45", "horse": "Immortal Star (1)", "odds": 2.25},
    {"track": "Morphettville", "race": "Race 3", "time": "12:57", "horse": "Bassett Babe (5)", "odds": 1.40},
    {"track": "Randwick", "race": "Race 4", "time": "13:05", "horse": "Sovereign Hill (7)", "odds": 2.05},
    {"track": "Randwick", "race": "Race 5", "time": "13:40", "horse": "Cross Tasman (10)", "odds": 1.90},
    {"track": "Flemington", "race": "Race 6", "time": "13:55", "horse": "Saint George (6)", "odds": 2.50},
    {"track": "Randwick", "race": "Race 8", "time": "15:30", "horse": "Autumn Glow (9)", "odds": 1.60},
    {"track": "Flemington", "race": "Race 9", "time": "15:50", "horse": "Sixties (10)", "odds": 1.80}
]

# --- T20 FIXTURES ---
t20_fixtures = [
    {"date": "2026-02-14", "match": "England vs Nepal", "stage": "Group Stage", "venue": "Ahmedabad"},
    {"date": "2026-02-14", "match": "West Indies vs Italy", "stage": "Group Stage", "venue": "Ahmedabad"},
    {"date": "2026-02-15", "match": "India vs Pakistan", "stage": "Group Stage", "venue": "Mumbai"},
    {"date": "2026-02-16", "match": "New Zealand vs Canada", "stage": "Group Stage", "venue": "Pune"},
    {"date": "2026-02-21", "match": "Super 8 Match 1", "stage": "Super 8", "venue": "Mumbai"},
    {"date": "2026-02-25", "match": "Semi-Final 1", "stage": "Semi-Final", "venue": "Mumbai"},
    {"date": "2026-03-08", "match": "Final", "stage": "Final", "venue": "Chennai"}
]

# --- SIDEBAR ---
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

    if st.button("🔁 Reset Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- MAIN ---
st.title("🐕 Datura Companion v5.1")

# Metrics
pnl = st.session_state.bankroll - st.session_state.initial_bankroll
col1, col2, col3 = st.columns(3)
col1.metric("Bankroll", f"\${st.session_state.bankroll:,.2f}")
col2.metric("P&L", f"\${pnl:,.2f}")
col3.metric("Status", st.session_state.mode or "Idle")

st.divider()

# --- MODE SELECTION ---
col_m1, col_m2, col_m3 = st.columns(3)
if col_m1.button("🏁 Start-of-Day", use_container_width=True):
    st.session_state.mode = "race_day"
    st.session_state.current_race_index = 0
    st.session_state.consecutive_wins = 0
    st.session_state.consecutive_losses = 0
    st.session_state.last_bet_amount = 0.0
    st.session_state.bet_active = True
    st.rerun()

if col_m2.button("🌀 Perpetual Run", use_container_width=True):
    st.session_state.mode = "perpetual"
    st.session_state.current_race_index = 0
    st.session_state.consecutive_wins = 0
    st.session_state.consecutive_losses = 0
    st.session_state.last_bet_amount = 0.0
    st.session_state.bet_active = True
    st.rerun()

if col_m3.button("🏏 T20 Sports", use_container_width=True):
    st.session_state.mode = "sports"
    st.session_state.current_race_index = 0
    st.session_state.bet_active = True
    st.rerun()

st.divider()

# --- LOGIC: GET CURRENT RACE ---
def get_current_race():
    races = race_day_races
    idx = st.session_state.current_race_index % len(races)
    race = races[idx]
    full_label = f"{race['track']} • {race['race']} [{race['time']}] - {race['horse']}"
    return full_label, race['odds'], idx

# --- MODE: START-OF-DAY / PERPETUAL ---
if st.session_state.mode in ["race_day", "perpetual"]:
    full_label, odds, idx = get_current_race()
    st.subheader("Current Race")
    st.markdown(f"**{full_label} @ \${odds:.2f}**")

    # Disable bet if odds ≤ 1.25
    if odds <= 1.25:
        st.error("❌ No Bet – Odds too low")
    else:
        # Check 2-win pause rule
        if st.session_state.consecutive_wins >= 2:
            st.warning("⏸️ Paused: 2 wins – waiting for loss")
            st.session_state.bet_active = False
        else:
            st.session_state.bet_active = True

        # Calculate stake
        if st.session_state.bet_active:
            if st.session_state.consecutive_wins == 0 and st.session_state.last_bet_amount == 0:
                stake = st.session_state.bankroll * 0.01
            elif st.session_state.consecutive_wins > 0:
                stake = st.session_state.bankroll * 0.01
            else:
                last_odds = st.session_state.last_bet_odds
                if last_odds > 2.00:
                    stake = st.session_state.last_bet_amount * 2
                elif 1.50 < last_odds <= 2.00:
                    stake = st.session_state.last_bet_amount * 3
                elif 1.25 < last_odds <= 1.50:
                    stake = st.session_state.last_bet_amount * 5
                else:
                    stake = st.session_state.bankroll * 0.01

            # Cap stake
            if stake > st.session_state.bankroll:
                stake = st.session_state.bankroll
            st.success(f"✅ Bet Active | Stake: \${stake:,.2f}")

    # Win/Loss Buttons
    col_win, col_loss = st.columns(2)
    with col_win:
        if st.button("✅ Win"):
            if st.session_state.bet_active and odds > 1.25:
                profit = stake * (odds - 1)
                st.session_state.bankroll += profit
                st.session_state.consecutive_wins += 1
                st.session_state.consecutive_losses = 0
                st.session_state.last_bet_amount = stake
                st.session_state.last_bet_odds = odds
            else:
                st.session_state.consecutive_wins = 0
            st.session_state.current_race_index += 1
            st.rerun()

    with col_loss:
        if st.button("❌ Loss"):
            if st.session_state.bet_active and odds > 1.25:
                st.session_state.bankroll -= stake
                st.session_state.consecutive_losses += 1
                st.session_state.consecutive_wins = 0
                st.session_state.last_bet_amount = stake
                st.session_state.last_bet_odds = odds
                st.session_state.bet_active = True  # Always reactivate after loss
            st.session_state.current_race_index += 1
            st.rerun()

# --- MODE: SPORTS (T20) ---
if st.session_state.mode == "sports":
    if st.session_state.current_race_index >= len(t20_fixtures):
        st.info("🔚 All fixtures completed.")
    else:
        fixture = t20_fixtures[st.session_state.current_race_index]
        st.subheader("T20 World Cup 2026")
        st.markdown(f"**{fixture['match']}** – {fixture['stage']} | {fixture['venue']} ({fixture['date']})")

        odds = st.number_input("Enter Odds", min_value=1.01, value=1.80, step=0.05)
        if odds <= 1.25:
            st.error("❌ No Bet – Odds too low")
        else:
            if st.session_state.consecutive_wins >= 2:
                st.warning("⏸️ Paused: 2 wins – waiting for loss")
                st.session_state.bet_active = False
            else:
                st.session_state.bet_active = True

            if st.session_state.bet_active:
                if st.session_state.consecutive_wins == 0 and st.session_state.last_bet_amount == 0:
                    stake = st.session_state.bankroll * 0.01
                elif st.session_state.consecutive_wins > 0:
                    stake = st.session_state.bankroll * 0.01
                else:
                    last_odds = st.session_state.last_bet_odds
                    if last_odds > 2.00:
                        stake = st.session_state.last_bet_amount * 2
                    elif 1.50 < last_odds <= 2.00:
                        stake = st.session_state.last_bet_amount * 3
                    elif 1.25 < last_odds <= 1.50:
                        stake = st.session_state.last_bet_amount * 5
                    else:
                        stake = st.session_state.bankroll * 0.01

                if stake > st.session_state.bankroll:
                    stake = st.session_state.bankroll
                st.success(f"✅ Bet Active | Stake: \${stake:,.2f}")

        col_win, col_loss = st.columns(2)
        with col_win:
            if st.button("✅ Win (Sports)"):
                if st.session_state.bet_active and odds > 1.25:
                    profit = stake * (odds - 1)
                    st.session_state.bankroll += profit
                    st.session_state.consecutive_wins += 1
                    st.session_state.consecutive_losses = 0
                    st.session_state.last_bet_amount = stake
                    st.session_state.last_bet_odds = odds
                else:
                    st.session_state.consecutive_wins = 0
                st.session_state.current_race_index += 1
                st.rerun()

        with col_loss:
            if st.button("❌ Loss (Sports)"):
                if st.session_state.bet_active and odds > 1.25:
                    st.session_state.bankroll -= stake
                    st.session_state.consecutive_losses += 1
                    st.session_state.consecutive_wins = 0
                    st.session_state.last_bet_amount = stake
                    st.session_state.last_bet_odds = odds
                    st.session_state.bet_active = True
                st.session_state.current_race_index += 1
                st.rerun()

# --- HISTORY ---
if st.session_state.race_history:
    st.divider()
    st.subheader("📋 Bet History")
    for record in st.session_state.race_history:
        st.text(f"{record['time']} | {record['event']} | {record['result']} | \${record['profit']:+.2f}")
