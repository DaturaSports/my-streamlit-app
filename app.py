# app.py
# 🎯 One Big Model - Live Betting Strategy Interface

import streamlit as st
import math

# === CUSTOM STYLES ===
st.markdown("""
<style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
        font-family: 'Segoe UI', sans-serif;
    }
    .stRadio > div {
        flex-direction: row;
        gap: 10px;
    }
    .stButton button {
        height: 3em;
        border-radius: 8px;
        font-weight: 600;
    }
    .stButton button[kind="primary"] {
        background-color: #00cc00;
        color: white;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# === APP TITLE ===
st.title("🎯 One Big Model")
st.markdown("A live betting strategy system with memory and dynamic staking.")

# === SESSION STATE INITIALIZATION ===
if "strategy" not in st.session_state:
    st.session_state.strategy = "A"
if "wins" not in st.session_state:
    st.session_state.wins = 0
if "losses" not in st.session_state:
    st.session_state.losses = 0
if "total_profit" not in st.session_state:
    st.session_state.total_profit = 0.0
if "current_stake" not in st.session_state:
    st.session_state.current_stake = 50.0
if "last_outcome" not in st.session_state:
    st.session_state.last_outcome = None
if "bankroll" not in st.session_state:
    st.session_state.bankroll = 1000.0  # Fixed bankroll assumption

# === STRATEGY SELECTION ===
strategy = st.radio(
    "Select Strategy",
    options=["A", "B", "C"],
    index=0,
    horizontal=True,
    help="Choose your betting approach. A: Conservative | B: Balanced | C: Aggressive"
)

st.session_state.strategy = strategy

st.write(f"**Active Strategy: {strategy}**")

# === WIN / LOSS BUTTONS ===
col1, col2, _ = st.columns([1, 1, 3])

with col1:
    if st.button("🟢 Win"):
        st.session_state.wins += 1
        st.session_state.total_profit += st.session_state.current_stake
        st.session_state.last_outcome = "win"

with col2:
    if st.button("🔴 Loss"):
        st.session_state.losses += 1
        st.session_state.total_profit -= st.session_state.current_stake
        st.session_state.last_outcome = "loss"

# === CALCULATE NEXT STAKE ===
if st.button("🔁 Calculate My Next Bet"):
    total_bets = st.session_state.wins + st.session_state.losses
    win_rate = st.session_state.wins / total_bets if total_bets > 0 else 0.0
    
    # Dynamic stake by strategy
    if strategy == "A":  # Conservative
        risk_factor = 0.02
    elif strategy == "B":  # Balanced
        risk_factor = 0.035
    else:  # Aggressive
        risk_factor = 0.05

    # Kelly-inspired sizing
    estimated_edge = max(win_rate - 0.5, 0.05)  # Assume minimum 5% edge
    kelly_fraction = estimated_edge * 2  # Full Kelly
    final_fraction = min(kelly_fraction, 0.1)  # Cap at 10%

    new_stake = max(
        st.session_state.bankroll * risk_factor * final_fraction * 10,
        50.0  # Minimum stake
    )
    new_stake = min(new_stake, 500.0)  # Max stake cap

    st.session_state.current_stake = round(new_stake, 2)

# === DISPLAY METRICS ===
st.divider()
st.subheader("📊 Performance Summary")

colA, colB, colC = st.columns(3)
colA.metric("Total Bets", st.session_state.wins + st.session_state.losses)
colB.metric("Win Rate", f"{st.session_state.wins / (st.session_state.wins + st.session_state.losses) * 100:.1f}%" if (st.session_state.wins + st.session_state.losses) > 0 else "0.0%")
colC.metric("Current Stake", f"${st.session_state.current_stake:,.2f}")
st.metric("Net Profit", f"${st.session_state.total_profit:+,.2f}")

# === LAST OUTCOME FEEDBACK ===
if st.session_state.last_outcome == "win":
    st.success("✅ Last bet: **Win** – Great job!")
elif st.session_state.last_outcome == "loss":
    st.warning("❌ Last bet: **Loss** – Stay disciplined.")

# === RESET BUTTON ===
with st.expander("🛠️ Admin Controls"):
    if st.button("Reset All Data"):
        for key in ["wins", "losses", "total_profit", "current_stake", "last_outcome"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()
