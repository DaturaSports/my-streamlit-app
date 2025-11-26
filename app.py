  # DEPLOY FIX: force rebuild - 2025-11-26
  
# app.py
# 🎯 One Big Model - Live Betting Strategy Interface

import streamlit as st
import json
import os

# === STATE MANAGEMENT ===
# Load session state from file (simulate persistence)
STATE_FILE = "onebigmodel_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "strategy": "A",
        "bankroll": 1000.0,
        "wins": 0,
        "losses": 0,
        "total_profit": 0.0,
        "current_stake": 50.0,
        "win_rate": 0.0,
        "last_outcome": None
    }

def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except:
        pass

# Load at start
state = load_state()

# === APP TITLE ===
st.title("🎯 One Big Model")
st.markdown("A live betting strategy system with memory and dynamic staking.")

# === STRATEGY SELECTION ===
strategy = st.radio(
    "Select Strategy",
    options=["A", "B", "C"],
    index=0,
    horizontal=True,
    help="Choose your betting approach. A: Conservative | B: Balanced | C: Aggressive"
)

# Update only if changed
if strategy != state["strategy"]:
    state["strategy"] = strategy
    save_state(state)
    st.rerun()

st.write(f"**Active Strategy: {strategy}**")

# === WIN / LOSS BUTTONS ===
col1, col2, _ = st.columns([1, 1, 3])

with col1:
    if st.button("🟢 Win"):
        state["wins"] += 1
        # Example: win adds current stake
        profit = state["current_stake"]
        state["total_profit"] += profit
        state["last_outcome"] = "win"
        save_state(state)
        st.rerun()

with col2:
    if st.button("🔴 Loss"):
        state["losses"] += 1
        # Loss deducts stake
        loss = -state["current_stake"]
        state["total_profit"] += loss
        state["last_outcome"] = "loss"
        save_state(state)
        st.rerun()

# === CALCULATE NEXT STAKE ===
if st.button("🔁 Calculate My Next Bet"):
    total_bets = state["wins"] + state["losses"]
    win_rate = state["wins"] / total_bets if total_bets > 0 else 0.0
    state["win_rate"] = round(win_rate, 3)

    # Dynamic stake by strategy
    base_stake = 50.0
    if strategy == "A":
        # Conservative: never exceed 5% of bankroll
        risk_factor = 0.02
    elif strategy == "B":
        # Balanced
        risk_factor = 0.035
    else:
        # Aggressive
        risk_factor = 0.05

    # Simple Kelly-inspired: fraction based on edge estimate
    estimated_edge = max(win_rate - 0.5, 0.05)  # Assume minimum 5% edge
    kelly_fraction = estimated_edge * 2  # Full Kelly cap at 10%
    final_fraction = min(kelly_fraction, 0.1)

    new_stake = max(state["bankroll"] * risk_factor * final_fraction * 10, base_stake)
    state["current_stake"] = round(new_stake, 2)

    save_state(state)
    st.rerun()

# === DISPLAY METRICS ===
st.divider()
st.subheader("📊 Performance Summary")

colA, colB, colC = st.columns(3)
colA.metric("Total Bets", state["wins"] + state["losses"])
colB.metric("Win Rate", f"{state['win_rate']:.1%}")
colC.metric("Current Stake", f"${state['current_stake']:,}")

st.metric("Net Profit", f"${state['total_profit']:+,}")

# === LAST OUTCOME FEEDBACK ===
if state["last_outcome"] == "win":
    st.success("✅ Last bet: **Win** – Great job!")
elif state["last_outcome"] == "loss":
    st.warning("❌ Last bet: **Loss** – Stay disciplined.")

# === RESET BUTTON (Optional) ===
with st.expander("🛠️ Admin Controls"):
    if st.button("Reset All Data"):
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        st.rerun()
