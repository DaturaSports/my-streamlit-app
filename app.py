import streamlit as st
import pandas as pd
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Greyhound Betting Tracker", page_icon="🐶", layout="centered")

# --- INITIALIZE SESSION STATE ---
if 'race_index' not in st.session_state:
    st.session_state.race_index = 0
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 100.0
if 'initial_bankroll' not in st.session_state:
    st.session_state.initial_bankroll = 100.0
if 'last_bet_amount' not in st.session_state:
    st.session_state.last_bet_amount = 0.0
if 'last_odds' not in st.session_state:
    st.session_state.last_odds = 1.0
if 'consecutive_wins' not in st.session_state:
    st.session_state.consecutive_wins = 0
if 'consecutive_losses' not in st.session_state:
    st.session_state.consecutive_losses = 0
if 'betting_active' not in st.session_state:
    st.session_state.betting_active = True
if 'just_resumed' not in st.session_state:
    st.session_state.just_resumed = False
if 'race_history' not in st.session_state:
    st.session_state.race_history = []

# --- USER INPUTS ---
st.title("🐶 Greyhound Betting Tracker")
st.markdown("Track races, apply staking logic, and log results.")

default_stake_pct = 1.0  # 1% of bankroll
wait_after_two_losses = False  # Option to pause after 2 losses

# --- RACE DATA ---
race_data = [
    {"track": "Ballarat", "name": "Ballarat • Race 4 - 5. Rocky Rebel (5)", "odds": 1.5},
    {"track": "Ballarat", "name": "Ballarat • Race 5 - 3. Bolo (3)", "odds": 1.35},
    {"track": "Angle Park", "name": "Angle Park • Race 3 - 4. Wicket (4)", "odds": 1.35},
    {"track": "Casino", "name": "Casino • Race 5 - 2. Jet Black (2)", "odds": 1.9},
    {"track": "Wentworth Park", "name": "Wentworth Park • Race 4 - 1. Flashy Mersey (1)", "odds": 1.5},
    {"track": "Hobart", "name": "Hobart • Race 3 - 1. Rojo Jojo (1)", "odds": 1.65},
    {"track": "Lismore", "name": "Lismore • Race 4 - 6. Silver Lining (6)", "odds": 1.45},
    {"track": "The Meadows", "name": "The Meadows • Race 6 - 2. Sassy Bella (2)", "odds": 1.8},
    {"track": "Dubbo", "name": "Dubbo • Race 5 - 1. Bolt Action (1)", "odds": 1.55},
    {"track": "Bendigo", "name": "Bendigo • Race 3 - 4. Wild Thing (4)", "odds": 1.75},
]

# --- RESET BUTTON ---
if st.button("🗑️ Reset All Data"):
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# --- CURRENT RACE ---
if st.session_state.race_index >= len(race_data):
    st.success("✅ All races processed!")
    st.stop()

current_race = race_data[st.session_state.race_index]
current_wins = st.session_state.consecutive_wins
current_losses = st.session_state.consecutive_losses

# --- DETERMINE BETTING STATUS ---
if current_wins >= 2:
    st.session_state.betting_active = False
    betting_status = "⏸️ No bet – wait for a loss"
elif wait_after_two_losses and current_losses < 2:
    st.session_state.betting_active = False
    betting_status = "⏸️ No bet – waiting for 2 losses"
else:
    st.session_state.betting_active = True
    betting_status = "🟢 Betting active"

# --- CALCULATE RECOMMENDED STAKE ---
if st.session_state.just_resumed:
    recommended_stake = st.session_state.bankroll * (default_stake_pct / 100)
elif st.session_state.betting_active:
    if current_losses == 0:
        recommended_stake = st.session_state.bankroll * (default_stake_pct / 100)
    else:
        # Recovery logic: 5× last bet if odds ≤ 1.50
        if st.session_state.last_odds <= 1.50:
            recommended_stake = st.session_state.last_bet_amount * 5
        else:
            recommended_stake = st.session_state.bankroll * (default_stake_pct / 100)
else:
    recommended_stake = 0.0

# Cap stake to bankroll
if recommended_stake > st.session_state.bankroll:
    recommended_stake = st.session_state.bankroll

# --- DISPLAY CURRENT RACE ---
st.markdown("---")
st.subheader(f"🎯 Current Race: {current_race['name']}")
st.write(f"**Odds:** {current_race['odds']}")
st.write(f"**Bankroll:** ${st.session_state.bankroll:,.2f}")
st.write(f"**Recommended Stake:** ${recommended_stake:,.2f}")
st.write(f"**Status:** {betting_status}")

# --- RESULT INPUT ---
result = st.radio("Select result:", ["Win", "Loss"], key=f"result_{st.session_state.race_index}")
if st.button("✅ Record Result"):
    st.session_state.result_input = result
    st.rerun()

# --- PROCESS RESULT ---
if 'result_input' in st.session_state:
    result = st.session_state.result_input
    del st.session_state.result_input

    # Determine actual stake
    if st.session_state.just_resumed:
        actual_stake = st.session_state.bankroll * (default_stake_pct / 100)
        st.session_state.just_resumed = False
    elif st.session_state.betting_active:
        actual_stake = recommended_stake
    else:
        actual_stake = 0.0

    # Cap stake
    if actual_stake > st.session_state.bankroll:
        actual_stake = st.session_state.bankroll

    # Initialize
    profit_loss = 0.0
    payout = 0.0

    # Process result
    if result == "Win":
        if actual_stake > 0:
            payout = actual_stake * current_race['odds']
            profit_loss = payout - actual_stake
            st.session_state.consecutive_wins += 1
            st.session_state.consecutive_losses = 0
            st.session_state.last_bet_amount = actual_stake
            st.session_state.last_odds = current_race['odds']
        else:
            st.session_state.consecutive_wins += 1
            st.session_state.consecutive_losses = 0
        st.session_state.bankroll += profit_loss
    else:
        if actual_stake > 0:
            profit_loss = -actual_stake
            st.session_state.consecutive_losses += 1
            st.session_state.consecutive_wins = 0
            st.session_state.last_bet_amount = actual_stake
            st.session_state.last_odds = current_race['odds']
        else:
            st.session_state.consecutive_losses += 1
            st.session_state.consecutive_wins = 0
            if not st.session_state.betting_active and current_wins >= 2:
                st.session_state.just_resumed = True
            profit_loss = 0.0
        st.session_state.bankroll += profit_loss

    # Log race
    st.session_state.race_history.append({
        "Race": current_race['name'],
        "Odds": current_race['odds'],
        "Stake": round(actual_stake, 2),
        "Result": result,
        "Payout": round(payout, 2),
        "P/L": round(profit_loss, 2),
        "Cumulative P/L": round(st.session_state.bankroll - st.session_state.initial_bankroll, 2),
        "Bankroll After": round(st.session_state.bankroll, 2),
        "Wins Streak": st.session_state.consecutive_wins,
        "Losses Streak": st.session_state.consecutive_losses,
        "Status": betting_status,
    })

    st.session_state.race_index += 1
    st.rerun()

# --- RACE HISTORY ---
if st.session_state.race_history:
    st.markdown("---")
    st.subheader("📊 Race History")
    history_df = pd.DataFrame(st.session_state.race_history)
    st.dataframe(history_df, use_container_width=True)
