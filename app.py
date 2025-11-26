# app.py
# 🎯 One Big Model - Full UI Reconstruction with Internal Risk Framework

import streamlit as st
from datetime import datetime

# === CUSTOM STYLES ===
st.markdown("""
<style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
        font-family: 'Segoe UI', sans-serif;
        background-color: #121212; /* Dark theme background */
        color: #e0e0e0;
    }
    .stRadio > div {
        flex-direction: row;
        gap: 10px;
        background-color: #1e1e1e;
        padding: 8px;
        border-radius: 8px;
    }
    .stButton button {
        height: 3em;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
    }
    .stButton button[kind="primary"] {
        background-color: #00cc00;
        color: white;
    }
    .stMetric {
        background-color: #1e1e1e;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    .stMetric > div > div:first-child {
        color: #b0b0b0;
        font-size: 0.9em;
    }
    .stMetric > div > div:last-child {
        color: #e0e0e0;
        font-size: 1.3em;
        font-weight: 600;
    }
    .stExpander {
        border: 1px solid #333;
        border-radius: 8px;
    }
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        color: #e0e0e0;
        background-color: #2d2d2d;
    }
</style>
""", unsafe_allow_html=True)

# === SESSION STATE INITIALIZATION ===
if "starting_bankroll" not in st.session_state:
    st.session_state.starting_bankroll = 1000.0
if "current_bankroll" not in st.session_state:
    st.session_state.current_bankroll = 1000.0
if "target_profit" not in st.session_state:
    st.session_state.target_profit = 500.0
if "total_events" not in st.session_state:
    st.session_state.total_events = 50
if "events_completed" not in st.session_state:
    st.session_state.events_completed = 0
if "betting_mode" not in st.session_state:
    st.session_state.betting_mode = "Steady Grind"
if "pattern_source" not in st.session_state:
    st.session_state.pattern_source = "Use Proven League Strategy"
if "selected_league" not in st.session_state:
    st.session_state.selected_league = "NRL Favourite"
if "odds" not in st.session_state:
    st.session_state.odds = 1.48
if "recommended_stake" not in st.session_state:
    st.session_state.recommended_stake = 0.0
if "last_outcome" not in st.session_state:
    st.session_state.last_outcome = None

# === STRATEGY & GOALS ===
st.title("🎯 One Big Model")

with st.expander("How It Works"):
    st.write("""
    This system uses your historical performance and internal risk models to determine optimal stake sizes.
    - **Steady Grind:** Low-risk, consistent growth. Stake is a fixed percentage of bankroll.
    - **Comeback:** Medium-risk. Increases stake after a loss to recover, but with a cap.
    - **Power Reset:** High-risk. Resets after a win to base stake, but uses higher base risk.
    """)

col1, col2 = st.columns(2)
with col1:
    st.session_state.betting_mode = st.radio(
        "Betting Mode",
        ["Steady Grind", "Comeback", "Power Reset"],
        index=0 if st.session_state.betting_mode == "Steady Grind" else 1 if st.session_state.betting_mode == "Comeback" else 2
    )

with col2:
    st.session_state.target_profit = st.number_input("Target Profit ($)", min_value=0.0, value=st.session_state.target_profit, step=10.0)
    st.session_state.total_events = st.number_input("Total Events", min_value=1, value=st.session_state.total_events, step=1)

# === PATTERN SOURCE ===
st.subheader("Pattern Source")
st.session_state.pattern_source = st.radio(
    "Select Pattern Source",
    ["Use Proven League Strategy", "Create Custom Pattern"],
    index=0 if st.session_state.pattern_source == "Use Proven League Strategy" else 1
)

if st.session_state.pattern_source == "Use Proven League Strategy":
    st.session_state.selected_league = st.selectbox(
        "Choose League",
        ["NRL Favourite", "Soccer League A", "Basketball League X"],
        index=0 if st.session_state.selected_league == "NRL Favourite" else 1 if st.session_state.selected_league == "Soccer League A" else 2
    )
    # Hardcoded stats for "NRL Favourite" as per your image
    win_rate = 0.666
    avg_odds = 1.48
    st.markdown(f"**Stats: Win Rate {win_rate:.1%} | Avg Odds {avg_odds:.2f}**")

# === BANKROLL & NEXT EVENT ===
st.subheader("Bankroll & Next Event")
st.session_state.starting_bankroll = st.number_input("Starting Bankroll ($)", min_value=0.0, value=st.session_state.starting_bankroll, step=100.0)
st.session_state.odds = st.number_input("Odds for Upcoming Event", min_value=1.01, value=st.session_state.odds, step=0.01)

# === RECOMMENDED STAKE ===
st.subheader("Recommended Stake")

# 🟢 MOVE THESE CALCULATIONS OUTSIDE the function so they are available for display
remaining_target = st.session_state.target_profit - (st.session_state.current_bankroll - st.session_state.starting_bankroll)
events_remaining = st.session_state.total_events - st.session_state.events_completed

# Core Risk Model Logic
def calculate_stake():
    # We can reuse the variables defined above if needed, or recalculate for clarity
    # Using the same logic here ensures consistency
    local_remaining_target = st.session_state.target_profit - (st.session_state.current_bankroll - st.session_state.starting_bankroll)
    local_events_remaining = st.session_state.total_events - st.session_state.events_completed
    
    if local_events_remaining <= 0:
        return 0.0

    # Base risk per mode (aligned with internal framework)
    if st.session_state.betting_mode == "Steady Grind":
        base_risk = 0.02  # 2% of bankroll
    elif st.session_state.betting_mode == "Comeback":
        base_risk = 0.03  # 3%, with dynamic adjustment after loss
    else:  # Power Reset
        base_risk = 0.04  # 4%, resets to base after win

    # Conservative Kelly Fraction using proven league stats
    implied_prob = 1 / st.session_state.odds
    edge = win_rate - implied_prob
    if edge <= 0:
        return 0.0

    kelly_fraction = edge / ((st.session_state.odds - 1) / 1)  # Simplified for win/lose
    fractional_kelly = kelly_fraction * 0.5  # 50% Kelly for risk control

    # Final stake is the minimum of: Kelly recommendation, mode-specific risk cap
    stake_from_kelly = fractional_kelly * st.session_state.current_bankroll
    stake_from_risk_cap = base_risk * st.session_state.current_bankroll
    final_stake = min(stake_from_kelly, stake_from_risk_cap)

    return max(final_stake, 5.0)  # Minimum $5 stake

# Calculate and store stake
st.session_state.recommended_stake = calculate_stake()

# Display
colA, colB = st.columns([2, 1])
with colA:
    st.markdown(f"<h2 style='color:#00cc00;'>${st.session_state.recommended_stake:,.2f}</h2>", unsafe_allow_html=True)
    # ✅ Now safe to use because defined above
    if events_remaining > 0:
        st.markdown(f"Need ${remaining_target / events_remaining:,.2f} profit/event over {events_remaining} events")
    else:
        st.markdown("Target achieved or no events remaining.")
with colB:
    st.metric("Win Rate", f"{win_rate:.1%}")
    st.metric("Avg Odds", f"{avg_odds:.2f}")


# === RECORD OUTCOME ===
st.subheader("Record Outcome")
colX, colY, colZ = st.columns(3)

with colX:
    if st.button("🟢 Mark as Win"):
        st.session_state.current_bankroll += st.session_state.recommended_stake
        st.session_state.events_completed += 1
        st.session_state.last_outcome = "win"
        st.rerun()

with colY:
    if st.button("🔴 Mark as Loss"):
        st.session_state.current_bankroll -= st.session_state.recommended_stake
        st.session_state.events_completed += 1
        st.session_state.last_outcome = "loss"
        st.rerun()

with colZ:
    if st.button("🔄 Reset All"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

# === DISPLAY FINAL METRICS ===
st.divider()
colP, colQ, colR = st.columns(3)
colP.metric("Current Bankroll", f"${st.session_state.current_bankroll:,.2f}")
colQ.metric("Events Completed", st.session_state.events_completed)
colR.metric("Remaining Target", f"${max(0, st.session_state.target_profit - (st.session_state.current_bankroll - st.session_state.starting_bankroll)):,.2f}")

if st.session_state.last_outcome == "win":
    st.success(f"✅ Win recorded! +${st.session_state.recommended_stake:,.2f}")
elif st.session_state.last_outcome == "loss":
    st.error(f"❌ Loss recorded. -${st.session_state.recommended_stake:,.2f}")
