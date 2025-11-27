# app.py
# 🎯 One Big Model - Final Debugged & Themed Version

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
if "custom_win_rate" not in st.session_state:
    st.session_state.custom_win_rate = 0.50
if "odds" not in st.session_state:
    st.session_state.odds = 1.48
if "recommended_stake" not in st.session_state:
    st.session_state.recommended_stake = 0.0
if "last_outcome" not in st.session_state:
    st.session_state.last_outcome = None
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"  # Default theme

# === THEME TOGGLE & CUSTOM STYLES ===
# Sidebar toggle for theme
theme_toggle = st.sidebar.checkbox("☀️/🌙 Toggle Light/Dark Theme", value=(st.session_state.theme == "Light"))
if theme_toggle:
    st.session_state.theme = "Light" if st.session_state.theme == "Dark" else "Dark"

# Define theme colors
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
    metric_text_color = "#111111"  # Ensures dark text in light mode

st.markdown(f"""
<style>
    /* Global Styles */
    .stApp {{ 
        background-color: {bg_color}; 
        color: {text_color}; 
    }}
    
    /* Radio buttons and general inputs */
    .stRadio > div {{ 
        background-color: {card_bg}; 
        padding: 8px; 
        border-radius: 8px; 
    }}
    .stTextInput > div > div > input, 
    .stNumberInput > div > div > input, 
    .stSelectbox > div > div > div {{ 
        color: {text_color} !important; 
        background-color: {input_bg} !important; 
    }}
    
    /* Primary button */
    .stButton button[kind="primary"] {{ 
        background-color: {primary_color}; 
        color: white; 
        border: none; 
    }}
    
    /* Metric Cards - This is the critical fix for light mode */
    .stMetric {{
        background-color: {metric_bg};
        padding: 16px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid {card_bg};
        color: {metric_text_color} !important;
    }}
    .stMetric .st-emotion-cache-1wmy9hl {{ /* Metric label */
        color: {metric_text_color} !important;
    }}
    .stMetric .st-emotion-cache-g3pm9b {{ /* Metric value */
        color: {primary_color} !important;
        font-weight: 600;
    }}
    .stMetric .st-emotion-cache-1a0t4q8 {{ /* Delta */
        color: {metric_text_color} !important;
    }}

    /* Expanders */
    .stExpander {{ 
        border: 1px solid #444; 
        border-radius: 8px; 
        background-color: {card_bg}; 
    }}
    .stExpander > div > div > div > p {{ 
        color: {text_color}; 
    }}
    
    /* Headings */
    .stMarkdown h2, .stMarkdown h3 {{ 
        color: {primary_color}; 
    }}

    /* Ensure all text is readable */
    .stMarkdown, .stRadio, .stSelectbox {{
        color: {text_color} !important;
    }}
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

# 🟢 Define win_rate and avg_odds BEFORE any function that uses them
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
    avg_odds = st.session_state.odds
    st.markdown(f"**Your Stats: Win Rate {win_rate:.1%} | Avg Odds {avg_odds:.2f}**")

# === RECOMMENDED STAKE ===
st.subheader("Recommended Stake")

# Core Risk Model Logic - Now receives 'win_rate' as a parameter
def calculate_stake(input_win_rate):
    remaining_target = st.session_state.target_profit - (st.session_state.current_bankroll - st.session_state.starting_bankroll)
    events_remaining = st.session_state.total_events - st.session_state.events_completed
    if events_remaining <= 0:
        return 0.0

    # Base risk per mode
    if st.session_state.betting_mode == "Steady Grind":
        base_risk = 0.02
    elif st.session_state.betting_mode == "Comeback":
        base_risk = 0.03
    else:  # Power Reset
        base_risk = 0.04

    # Kelly Criterion
    implied_prob = 1 / st.session_state.odds
    edge = input_win_rate - implied_prob  # Use the passed parameter
    if edge <= 0:
        return 0.0

    kelly_fraction = edge / ((st.session_state.odds - 1) / 1)
    fractional_kelly = kelly_fraction * 0.5

    stake_from_kelly = fractional_kelly * st.session_state.current_bankroll
    stake_from_risk_cap = base_risk * st.session_state.current_bankroll
    final_stake = min(stake_from_kelly, stake_from_risk_cap)

    return max(final_stake, 5.0)

# 🔄 Calculate stake with the explicitly passed win_rate
st.session_state.recommended_stake = calculate_stake(win_rate)

# Display
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
colR.metric("Remaining Target", f"${max(0, remaining_target):,.2f}")

if st.session_state.last_outcome == "win":
    st.success(f"✅ Win recorded! +${st.session_state.recommended_stake:,.2f}")
elif st.session_state.last_outcome == "loss":
    st.error(f"❌ Loss recorded. -${st.session_state.recommended_stake:,.2f}")
