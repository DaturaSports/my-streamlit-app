import streamlit as st
import random
import time

# --- Session State Initialization ---
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 10000.0
if 'base_stake' not in st.session_state:
    st.session_state.base_stake = 100.0
if 'loss_streak' not in st.session_state:
    st.session_state.loss_streak = 0
if 'race_count' not in st.session_state:
    st.session_state.race_count = 0
if 'betting_active' not in st.session_state:
    st.session_state.betting_active = True
if 'last_result' not in st.session_state:
    st.session_state.last_result = None
if 'just_resumed' not in st.session_state:
    st.session_state.just_resumed = False

# --- App Title ---
st.title("🏁 Daily Racing & Betting Simulator")

# --- Configuration Panel ---
st.sidebar.header("🔧 Configuration")
st.session_state.bankroll = st.sidebar.number_input(
    "Bankroll (\$)", 100.0, 1_000_000.0, st.session_state.bankroll, 100.0
)
st.session_state.base_stake = st.sidebar.number_input(
    "Base Stake (\$)", 10.0, 1000.0, st.session_state.base_stake, 10.0
)

# Expected win rate and odds input
user_win_rate = st.sidebar.slider("Expected Win Rate (%)", 1, 99, 55) / 100.0
market_odds = st.sidebar.slider("Market Odds (Decimal)", 1.5, 10.0, 2.0, 0.1)

# Implied probability
implied_prob = 1 / market_odds

# Edge calculation
if st.session_state.loss_streak > 0:
    adjusted_edge = (user_win_rate * 1.1) - implied_prob  # Slight boost after losses
else:
    adjusted_edge = user_win_rate - implied_prob

edge_pct = adjusted_edge * 100

# --- Display Metrics ---
st.write("### 💰 Current Status")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Bankroll", f"\${st.session_state.bankroll:,.2f}")
col2.metric("Base Stake", f"\${st.session_state.base_stake:,.2f}")
col3.metric("Loss Streak", st.session_state.loss_streak)
col4.metric("Edge", f"{edge_pct:+.2f}%")

# --- Stake Calculation Logic ---
def calculate_stake():
    if st.session_state.just_resumed:
        stake = st.session_state.base_stake
        st.session_state.just_resumed = False
        return stake

    multiplier = 2 ** st.session_state.loss_streak
    return st.session_state.base_stake * multiplier

current_stake = calculate_stake()

# --- Race Simulation ---
st.write("### 🏁 Race Day")
st.write(f"Race #{st.session_state.race_count + 1}: Ready to run")

# Win probability with edge
win_prob = user_win_rate * 1.05  # Model edge
outcome = random.random() < win_prob

# --- Bet Action Buttons (Always Visible) ---
st.write("### 🎯 Result")
col1, col2 = st.columns([1, 1])

with col1:
    if st.button("✅ Win", key="win_btn", use_container_width=True):
        st.session_state.last_result = "win"
        st.session_state.loss_streak = 0
        profit = current_stake * (market_odds - 1)
        st.session_state.bankroll += profit
        st.session_state.race_count += 1
        st.session_state.betting_active = True
        st.rerun()

with col2:
    if st.button("❌ Loss", key="loss_btn", use_container_width=True):
        st.session_state.last_result = "loss"
        st.session_state.loss_streak += 1
        if current_stake <= st.session_state.bankroll:
            st.session_state.bankroll -= current_stake
        else:
            # Stake exceeds bankroll
            if st.session_state.bankroll > 0:
                # Allow user to choose
                st.warning(f"⚠️ Required stake (\${current_stake:.2f}) exceeds bankroll (\${st.session_state.bankroll:.2f}).")
                col_a, col_b = st.columns(2)
                if col_a.button("🔻 Stake Remaining", key="partial_stake"):
                    st.session_state.bankroll = 0
                    st.session_state.race_count += 1
                    st.session_state.betting_active = True
                    st.rerun()
                if col_b.button("🔄 Reset Stake", key="reset_stake"):
                    st.session_state.loss_streak = 0
                    st.session_state.race_count += 1
                    st.session_state.betting_active = True
                    st.session_state.just_resumed = True
                    st.rerun()
            else:
                st.error("Bankroll depleted. Reset manually.")
        else:
            st.session_state.race_count += 1
            st.session_state.betting_active = True
            st.rerun()

# --- Display Recommended Stake ---
st.write("### 📊 Bet Details")
st.write(f"- **Model Edge**: {edge_pct:+.2f}%")
st.write(f"- **Current Stake**: \${current_stake:,.2f}")
if current_stake > st.session_state.bankroll and st.session_state.bankroll > 0:
    st.warning(f"⚠️ Stake exceeds bankroll. Next action required: stake remaining or reset.")
elif st.session_state.bankroll == 0:
    st.info("Bankroll exhausted. Use 'Reset Stake' to continue with base stake.")

# --- Reset Controls ---
st.write("### 🔁 Manual Controls")
if st.button("🔁 Reset Loss Streak"):
    st.session_state.loss_streak = 0
    st.session_state.just_resumed = True
    st.success("Loss streak reset. Next stake = base")
    st.rerun()

if st.button("🔄 Reset All"):
    for key in ['bankroll', 'base_stake', 'loss_streak', 'race_count', 'last_result', 'betting_active', 'just_resumed']:
        if key == 'bankroll':
            st.session_state[key] = 10000.0
        elif key == 'base_stake':
            st.session_state[key] = 100.0
        else:
            st.session_state[key] = 0
    st.success("All settings reset to default")
    st.rerun()
