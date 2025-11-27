# app.py
# 🎯 One Big Model - Debugged & Enhanced

import streamlit as st
from datetime import datetime

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
if "custom_win_rate" not in st.session_state:  # New state for custom pattern
    st.session_state.custom_win_rate = 0.50
if "odds" not in st.session_state:
    st.session_state.odds = 1.48
if "recommended_stake" not in st.session_state:
    st.session_state.recommended_stake = 0.0
if "last_outcome" not in st.session_state:
    st.session_state.last_outcome = None
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"  # Default theme

# === CUSTOM STYLES & THEME TOGGLE ===
# This injects CSS and a button to toggle between light and dark modes.
# The theme is stored in session_state and persists across reruns.
theme_toggle = st.sidebar.checkbox("☀️/🌙 Toggle Light/Dark Theme", value=(st.session_state.theme == "Light"))
if theme_toggle:
    st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"

if st.session_state.theme == "Dark":
    primary_color = "#00cc00"
    bg_color = "#121212"
    card_bg = "#1e1e1e"
    text_color = "#e0e0e0"
    input_bg = "#2d2d2d"
else:
    primary_color = "#009900"
    bg_color = "#f0f0f0"
    card_bg = "#ffffff"
    text_color = "#111111"
    input_bg = "#ffffff"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .stRadio > div {{ background-color: {card_bg}; padding: 8px; border-radius: 8px; }}
    .stButton button[kind="primary"] {{ background-color: {primary_color}; color: white; }}
    .stMetric {{ background-color: {card_bg}; padding: 12px; border-radius: 8px; }}
    .stExpander {{ border: 1px solid #444; border-radius: 8px; }}
    .stTextInput > div > div > input, .stNumberInput > div > div > input {{ 
        color: {text_color}; background-color: {input_bg}; 
    }}
    .stMarkdown h2 {{ color: {primary_color}; }}
</style>
""", unsafe_allow_html=True)

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
        index=["Steady Grind", "Comeback", "Power Reset"].index(st.session_state.betting_mode)
    )

with col2:
    st.session_state.target_profit = st.number_input("Target Profit ($)", min_value=0.0, value=float(st.session_state.target_profit), step=10.0)
    st.session_state.total_events = st.number_input("Total Events", min_value=1, value=int(st.session_state.total_events), step=1)

# === PATTERN SOURCE ===
st.subheader("Pattern Source")
st.session_state.pattern_source = st.radio(
    "Select Pattern Source",
    ["Use Proven League Strategy", "Create Custom Pattern"],
    index=0 if st.session_state.pattern_source == "Use Proven League Strategy" else 1
)

# 🟢 Define win_rate and avg_odds at the top level so calculate_stake() can always access them
win_rate = 0.0
avg_odds = 1.0

if st.session_state.pattern_source == "Use Proven League Strategy":
    st.session_state.selected_league = st.selectbox(
        "Choose League",
        ["NRL Favourite", "Soccer League A", "Basketball League X"],
        index=["NRL Favourite", "Soccer League A", "Basketball League X"].index(st.session_state.selected_league)
    )
    # Set the values based on the selected league
    if st.session_state.selected_league == "NRL Favourite":
        win_rate = 0.666
        avg_odds = 1.48
    elif st.session_state.selected_league == "Soccer League A":
        win_rate = 0.60
        avg_odds = 1.67
    else:  # Basketball League X
        win_rate = 0.55
        avg_odds = 1.82
    st.markdown(f"**Stats: Win Rate {win_rate:.1%} | Avg Odds {avg_odds:.2f}**")

else:  # Create Custom Pattern
    st.session_state.custom_win_rate = st.slider(
        "Your Estimated Win Rate",
        min_value=0.01,
        max_value=0.99,
        value=st.session_state.custom_win_rate,
        step=0.01,
        format="%.2f"
    )
    win_rate = st.session_state.custom_win_rate
    avg_odds = st.session_state.odds  # Or let user input this
    st.markdown(f"**Your Stats: Win Rate {win_rate:.1%} | Avg Odds {avg_odds:.2f}**")

# === BANKROLL & NEXT EVENT ===
st.subheader("Bankroll & Next Event")
st.session_state.starting_bankroll = st.number_input("Starting Bankroll ($)", min_value=0.0, value=float(st.session_state.starting_bankroll), step=100.0)
st.session_state.odds = st.number_input("Odds for Upcoming Event", min_value=1.01, value=float(st.session_state.odds), step=0.01)

# === RECOMMENDED STAKE ===
st.subheader("Recommended Stake")

# Core Risk Model Logic - Now robust and always has access to 'win_rate'
def calculate_stake():
    remaining_target = st.session_state.target_profit - (st.session_state.current_bankroll - st.session_state.starting_bankroll)
    events_remaining = st.session_state.total_events - st.session_state.events_completed
    if events_remaining <= 0:
        return 0.0

    # Base risk per mode (aligned with internal framework)
    if st.session_state.betting_mode == "Steady Grind":
        base_risk = 0.02  # 2% of bankroll
    elif st.session_state.betting_mode == "Comeback":
        base_risk = 0.03  # 3%, with dynamic adjustment after loss
    else:  # Power Reset
        base_risk = 0.04  # 4%, resets to base after win

    # Conservative Kelly Fraction using the win_rate (from proven or custom)
    implied_prob = 1 / st.session_state.odds
    edge = win_rate - implied_prob
    if edge <= 0:
        return 0.0

    kelly_fraction = edge / ((st.session_state.odds - 1) / 1)
    fractional_kelly = kelly_fraction * 0.5  # 50% Kelly for risk control

    # Final stake is the minimum of: Kelly recommendation, mode-specific risk cap
    stake_from_kelly = fractional_kelly * st.session_state.current_bankroll
    stake_from_risk_cap = base_risk * st.session_state.current_bankroll
    final_stake = min(stake_from_kelly, stake_from_risk_cap)

    return max(final_stake, 5.0)  # Minimum $5 stake

# 🔄 Calculate stake EVERY TIME the app reruns (after input changes, win/loss, etc.)
st.session_state.recommended_stake = calculate_stake()

# Display
colA, colB = st.columns([2, 1])
with colA:
    st.markdown(f"<h2>${st.session_state.recommended_stake:,.2f}</h2>", unsafe_allow_html=True)
    if events_remaining > 0:
        profit_per_event = remaining_target / events_remaining
        st.markdown(f"Need ${profit_per_event:,.2f} profit/event over {events_remaining} events")
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
        # 🔄 Rerun to recalculate stake with updated bankroll
        st.rerun()

with colY:
    if st.button("🔴 Mark as Loss"):
        st.session_state.current_bankroll -= st.session_state.recommended_stake
        st.session_state.events_completed += 1
        st.session_state.last_outcome = "loss"
        # 🔄 Rerun to recalculate stake with updated bankroll
        st.rerun()

with colZ:
    if st.button("🔄 Reset All"):
        for key in st.session_state.keys():
            del st.session_state[key]
        # This will force a fresh start
        st.rerun()

# === DISPLAY FINAL METRICS ===
st.divider()
colP, colQ, colR = st.columns(3)
colP.metric("Current Bankroll", f"${st.session_state.current_bankroll:,.2f}")
colQ.metric("Events Completed", st.session_state.events_completed)
colR.metric("Remaining Target", f"${max(0, remaining_target):,.2f}")

if st.session_state.last_outcome == "win":
    st.success(f"✅ Win recorded! +${st.session_state.recommended_stake:,.2f}")
elif st.session_state.last_outcome == "loss":
    st.error(f"❌ Loss recorded. -${st.session_state.recommended_stake:,.2f}")
