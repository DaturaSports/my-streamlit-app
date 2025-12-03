# app.py
# 🎯 One Big Model - Dynamic Strategy Fix

import streamlit as st

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
if "custom_win_rate" not in st.session_state:
    st.session_state.custom_win_rate = 0.50
if "odds" not in st.session_state:
    st.session_state.odds = 1.48
if "recommended_stake" not in st.session_state:
    st.session_state.recommended_stake = 0.0
if "last_outcome" not in st.session_state:
    st.session_state.last_outcome = None
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"
# NEW: Track the current multiplier for Comeback and Power Reset
if "current_stake_multiplier" not in st.session_state:
    st.session_state.current_stake_multiplier = 1.0  # Start at 1x base risk

# === THEME TOGGLE & CUSTOM STYLES ===
theme_toggle = st.sidebar.checkbox("☀️/🌙 Toggle Light/Dark Theme", value=(st.session_state.theme == "Light"))
if theme_toggle:
    st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"

if st.session_state.theme == "Dark":
    primary_color = "#00cc00"
    bg_color = "#121212"
    card_bg = "#1e1e1e"
    text_color = "#e0e0e0"
    input_bg = "#2d2d2d"
    metric_bg = "#2a2a2a"
    metric_text_color = "#ffffff"
else:
    primary_color = "#009900"
    bg_color = "#f8f9fa"
    card_bg = "#ffffff"
    text_color = "#111111"
    input_bg = "#ffffff"
    metric_bg = "#f1f3f5"
    metric_text_color = "#111111"

st.markdown(f"""
<style>
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .stRadio > div {{ background-color: {card_bg}; padding: 8px; border-radius: 8px; }}
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input, 
    .stSelectbox > div > div > div {{ 
        color: {text_color} !important; 
        background-color: {input_bg} !important; 
    }}
    .stButton button[kind="primary"] {{ background-color: {primary_color}; color: white; }}
    .stMetric {{
        background-color: {metric_bg}; 
        padding: 16px; 
        border-radius: 8px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); 
        border: 1px solid {card_bg};
        color: {metric_text_color} !important;
    }}
    .stMetric .st-emotion-cache-1wmy9hl, .stMetric .st-emotion-cache-g3pm9b, .stMetric .st-emotion-cache-1a0t4q8 {{
        color: {metric_text_color} !important;
    }}
    .stExpander {{ border: 1px solid #444; border-radius: 8px; background-color: {card_bg}; }}
    .stMarkdown h2, .stMarkdown h3 {{ color: {primary_color}; }}
</style>
""", unsafe_allow_html=True)

# === STRATEGY & GOALS ===
st.title("🎯 One Big Model")

with st.expander("How It Works"):
    st.write("""
    This system uses your historical performance and internal risk models to determine optimal stake sizes.
    - **Steady Grind:** Low-risk, consistent growth. Stake is a fixed percentage of bankroll.
    - **Comeback:** Medium-risk. Increases stake after a loss to recover, but with a cap. Resets to base after a win.
    - **Power Reset:** High-risk. Increases stake after a win to "power" growth. Resets to base after a loss.
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

# Define win_rate and avg_odds
win_rate = 0.0
avg_odds = 1.0

if st.session_state.pattern_source == "Use Proven League Strategy":
    st.session_state.selected_league = st.selectbox(
        "Choose League",
        ["NRL Favourite", "Soccer League A", "Basketball League X"],
        index=["NRL Favourite", "Soccer League A", "Basketball League X"].index(st.session_state.selected_league)
    )
    if st.session_state.selected_league == "NRL Favourite":
        win_rate = 0.666
        avg_odds = 1.48
    elif st.session_state.selected_league == "Soccer League A":
        win_rate = 0.60
        avg_odds = 1.67
    else:
        win_rate = 0.55
        avg_odds = 1.82
    st.markdown(f"**Stats: Win Rate {win_rate:.1%} | Avg Odds {avg_odds:.2f}**")

else:
    st.session_state.custom_win_rate = st.slider(
        "Your Estimated Win Rate",
        min_value=0.01,
        max_value=0.99,
        value=st.session_state.custom_winroll,
        step=0.01,
        format="%.2f"
    )
    win_rate = st.session_state.custom_win_rate
    avg_odds = st.session_state.odds
    st.markdown(f"**Your Stats: Win Rate {win_rate:.1%} | Avg Odds {avg_odds:.2f}**")

# === CORE DYNAMIC STAKE LOGIC ===
# This function now updates the multiplier based on the last outcome and the selected mode.
def update_stake_multiplier():
    mode = st.session_state.betting_mode
    outcome = st.session_state.last_outcome

    if mode == "Steady Grind":
        # Always reset to 1.0
        st.session_state.current_stake_multiplier = 1.0
    elif mode == "Comeback":
        if outcome == "loss":
            # Increase multiplier after a loss
            st.session_state.current_stake_multiplier += 0.5
            # Cap it at 3.0x to prevent overbetting
            st.session_state.current_stake_multiplier = min(st.session_state.current_stake_multiplier, 3.0)
        elif outcome == "win":
            # Reset to base after a win
            st.session_state.current_stake_multiplier = 1.0
    elif mode == "Power Reset":
        if outcome == "win":
            # Increase multiplier after a win
            st.session_state.current_stake_multiplier += 0.5
            st.session_state.current_stake_multiplier = min(st.session_state.current_stake_multiplier, 3.0)
        elif outcome == "loss":
            # Reset to base after a loss
            st.session_state.current_stake_multiplier = 1.0

# Call this function at the start of every run to ensure the multiplier is up-to-date
update_stake_multiplier()

# Now calculate the stake using the updated multiplier
def calculate_stake(input_win_rate):
    events_remaining = st.session_state.total_events - st.session_state.events_completed
    if events_remaining <= 0 or st.session_state.current_bankroll <= 0:
        return 0.0

    # Base risk percentage
    base_risk_pct = {
        "Steady Grind": 0.02,
        "Comeback": 0.03,
        "Power Reset": 0.04
    }[st.session_state.betting_mode]

    # Apply the current multiplier
    risk_pct = base_risk_pct * st.session_state.current_stake_multiplier

    # Kelly Criterion
    implied_prob = 1 / st.session_state.odds
    edge = input_win_rate - implied_prob
    if edge <= 0:
        return 0.0

    kelly_fraction = edge / ((st.session_state.odds - 1) / 1)
    fractional_kelly = kelly_fraction * 0.5  # 50% Kelly

    stake_from_kelly = fractional_kelly * st.session_state.current_bankroll
    stake_from_risk_cap = risk_pct * st.session_state.current_bankroll
    final_stake = min(stake_from_kelly, stake_from_risk_cap)

    return max(final_stake, 5.0)  # $5 minimum

# Calculate the recommended stake
st.session_state.recommended_stake = calculate_stake(win_rate)

# === DISPLAY RECOMMENDED STAKE ===
st.subheader("Recommended Stake")
colA, colB = st.columns([2, 1])
with colA:
    st.markdown(f"<h2 style='font-size: 28px; color: {primary_color};'>${st.session_state.recommended_stake:,.2f}</h2>", unsafe_allow_html=True)
    remaining_target = st.session_state.target_profit - (st.session_state.current_bankroll - st.session_state.starting_bankroll)
    events_remaining = st.session_state.total_events - st.session_state.events_completed
    if events_remaining > 0:
        profit_per_event = remaining_target / events_remaining
        st.markdown(f"Need **${profit_per_event:,.2f}** profit/event over **{events_remaining}** events")
    else:
        st.markdown("Target achieved or no events remaining.")
with colB:
    st.metric("Win Rate", f"{win_rate:.1%}")
    st.metric("Avg Odds", f"{avg_odds:.2f}")
    st.metric("Stake Multiplier", f"{st.session_state.current_stake_multiplier:.1f}x")

# === RECORD OUTCOME ===
st.subheader("Record Outcome")
colX, colY, colZ = st.columns(3)

with colX:
    if st.button("🟢 Mark as Win", key="win_btn"):
        st.session_state.current_bankroll += st.session_state.recommended_stake
        st.session_state.events_completed += 1
        st.session_state.last_outcome = "win"
        st.rerun()

with colY:
    if st.button("🔴 Mark as Loss", key="loss_btn"):
        st.session_state.current_bankroll -= st.session_state.recommended_stake
        st.session_state.events_completed += 1
        st.session_state.last_outcome = "loss"
        st.rerun()

with colZ:
    if st.button("🔄 Reset All", key="reset_btn"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# === DISPLAY FINAL METRICS ===
st.divider()
colP, colQ, colR = st.columns(3)
colP.metric("Current Bankroll", f"${st.session_state.current_bankroll:,.2f}")
colQ.metric("Events Completed", st.session_state.events_completed)
colR.metric("Remaining Target", f"${max(0, remaining_target):,.2f}")

# Show outcome and multiplier state
if st.session_state.last_outcome == "win":
    st.success(f"✅ Win recorded! +${st.session_state.recommended_stake:,.2f}")
elif st.session_state.last_outcome == "loss":
    st.error(f"❌ Loss recorded. -${st.session_state.recommended_stake:,.2f}")

# Debug info (can be removed later)
# st.caption(f"Debug: Stake Multiplier = {st.session_state.current_stake_multiplier}x")
