import streamlit as st
import pandas as pd

# Theme toggle state
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Apply theme via universal CSS (no fragile class names)
if st.session_state.theme == 'dark':
    st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"], .stApp {
            background-color: #0E1117;
            color: #FFFFFF;
        }
        [data-testid="stHeader"], [data-testid="stSidebar"] {
            background-color: #0E1117;
        }
        .stRadio label, .stNumberInput label, .stMarkdown, .stText, .stCaption, label {
            color: #FFFFFF !important;
            font-weight: 500;
        }
        .st-emotion-cache-1v3fvav, /* Metric value */
        .st-emotion-cache-1g6x8q  /* Metric label */ {
            color: #FFFFFF !important;
        }
        .stTextInput input, .stNumberInput input {
            color: #FFFFFF !important;
            background-color: #1E1E1E !important;
            border: 1px solid #444 !important;
        }
        .stButton button {
            background-color: #262730;
            color: #FFFFFF;
            border: 1px solid #444;
        }
        .stButton button:hover {
            background-color: #333333;
            color: #FFFFFF;
        }
        .stDataFrame, .stTable {
            color: #FFFFFF;
        }
        .stDataFrame th, .stDataFrame td,
        .stTable th, .stTable td {
            color: #FFFFFF !important;
            background-color: #1E1E1E !important;
        }
        .stDataFrame th {
            background-color: #2D2D2D !important;
        }
        .stInfo {
            background-color: #1A1D21 !important;
            color: #FFFFFF;
        }
        .stWarning {
            background-color: #3C2A1F !important;
            color: #FFD700;
        }
    </style>
    """, unsafe_allow_html=True)
else:  # Light Mode – High Contrast Fix
    st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"], .stApp {
            background-color: #FFFFFF;
            color: #000000;
        }
        [data-testid="stHeader"], [data-testid="stSidebar"] {
            background-color: #FFFFFF;
        }
        .stRadio label, .stNumberInput label, .stMarkdown, .stText, .stCaption, label {
            color: #000000 !important;
            font-weight: 500;
        }
        .st-emotion-cache-1v3fvav, /* Metric value */
        .st-emotion-cache-1g6x8q  /* Metric label */ {
            color: #000000 !important;
        }
        .stTextInput input, .stNumberInput input {
            color: #000000 !important;
            background-color: #FFFFFF !important;
            border: 1px solid #AAAAAA !important;
        }
        .stButton button {
            background-color: #F0F0F0;
            color: #000000;
            border: 1px solid #CCCCCC;
        }
        .stButton button:hover {
            background-color: #DDDDDD;
            color: #000000;
        }
        .stDataFrame, .stTable {
            color: #000000;
        }
        .stDataFrame th, .stDataFrame td,
        .stTable th, .stTable td {
            color: #000000 !important;
            background-color: #FFFFFF !important;
        }
        .stDataFrame th {
            background-color: #F0F2F6 !important;
            color: #000000 !important;
        }
        .stInfo {
            background-color: #E6F3FF !important;
            color: #000000;
            border: 1px solid #B3D9FF;
        }
        .stWarning {
            background-color: #FFF3E0 !important;
            color: #CC5500;
            border: 1px solid #FFB74D;
        }
    </style>
    """, unsafe_allow_html=True)

# Page config
st.set_page_config(page_title="Australian Dog Racing Trial", layout="centered")
st.title("🐕 Australian Dog Racing Trial")
st.markdown("Track your strategy with auto-pause, reset stakes, and theme control.")

# Initialize session state
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0
    st.session_state.initial_bankroll = 1000.0
    st.session_state.last_bet_amount = 0.0
    st.session_state.last_odds = 0.0
    st.session_state.consecutive_wins = 0
    st.session_state.consecutive_losses = 0
    st.session_state.race_index = 0
    st.session_state.race_history = []
    st.session_state.just_resumed = False

    st.session_state.races = [
        {"name": "Warragul • Race 5 - 8. Sweet Trilby (8)", "odds": 1.90},
        {"name": "Warragul • Race 9 - 1. Sweet Coin Babe (1)", "odds": 1.75},
        {"name": "Wentworth Park • Race 1 - 3. Sabini (3)", "odds": 1.60},
        {"name": "Ballarat • Race 3 - 2. Trust In Process (2)", "odds": 1.50},
        {"name": "Ballarat • Race 4 - 1. Maximos (1)", "odds": 1.35},
        {"name": "Ballarat • Race 5 - 1. Hard Style Leon (1)", "odds": 1.35},
        {"name": "Angle Park • Race 3 - 4. Wicket (4)", "odds": 1.35},
        {"name": "Casino • Race 5 - 6. Kicker Splash (6)", "odds": 1.90},
        {"name": "Wentworth Park • Race 4 - 2. Winsome Rambo (2)", "odds": 1.50},
        {"name": "Hobart • Race 3 - 1. Rojo Jojo (1)", "odds": 1.65},
        {"name": "Q1 Lakeside • Race 3 - 4. Neame (4)", "odds": 1.45},
        {"name": "Casino • Race 7 - 1. Bentley Harris (1)", "odds": 1.45},
        {"name": "Angle Park • Race 6 - 7. Mallee Beauty (7)", "odds": 1.35},
        {"name": "Wentworth Park • Race 7 - 8. Magpie Hector (8)", "odds": 1.40},
        {"name": "Ballarat • Race 9 - 1. Flying Maverick (1)", "odds": 1.30},
        {"name": "Hobart • Race 9 - 8. Push The Button (8)", "odds": 1.55},
        {"name": "Q1 Lakeside • Race 11 - 7. Teresita (7)", "odds": 1.55},
    ]

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    initial_bankroll = st.number_input(
        "Starting Bankroll ($)", min_value=1.0, value=st.session_state.initial_bankroll, step=50.0, format="%.2f"
    )
    default_stake_pct = st.slider(
        "Base Stake (% of bankroll)", min_value=0.1, max_value=10.0, value=1.0, step=0.1
    )
    wait_after_two_losses = st.checkbox("Wait to bet until 2 losses in a row occur", value=False)
    st.markdown("---")
    st.button("🔁 Reset All Data", on_click=lambda: st.session_state.clear())
    st.markdown("---")
    st.button("🌓 Toggle Dark/Light Mode", on_click=toggle_theme)
    st.markdown(f"<small>Current Theme: <strong>{st.session_state.theme.title()}</strong></small>", unsafe_allow_html=True)

# Re-init bankroll if changed
if st.session_state.initial_bankroll != initial_bankroll:
    st.session_state.update({
        'initial_bankroll': initial_bankroll,
        'bankroll': initial_bankroll,
        'last_bet_amount': 0.0,
        'last_odds': 0.0,
        'consecutive_wins': 0,
        'consecutive_losses': 0,
        'race_index': 0,
        'race_history': [],
        'just_resumed': False
    })

# Determine betting status
current_wins = st.session_state.consecutive_wins
current_losses = st.session_state.consecutive_losses

if current_wins >= 2:
    st.session_state.betting_active = False
    betting_status = "⏸️ No bet – wait for a loss"
elif wait_after_two_losses and current_losses < 2:
    st.session_state.betting_active = False
    betting_status = "⏸️ No bet – waiting for 2 losses"
else:
    st.session_state.betting_active = True
    betting_status = "🟢 Betting active"

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Bankroll", f"${st.session_state.bankroll:,.2f}")
col2.metric("P&L", f"${st.session_state.bankroll - st.session_state.initial_bankroll:,.2f}")
col3.markdown(f"**Streak:** {current_wins}W / {current_losses}L")

# Race Navigation
race_list = st.session_state.races
current_idx = st.session_state.race_index
total_races = len(race_list)

if current_idx >= total_races:
    st.success("🏁 All races completed!")
    st.stop()

current_race = race_list[current_idx]
st.markdown("---")
st.subheader(f"Race {current_idx + 1} of {total_races}")
st.markdown(f"### {current_race['name']} @ **${current_race['odds']}**")

st.info(betting_status)

# Stake calculation
if st.session_state.betting_active:
    if st.session_state.just_resumed:
        recommended_stake = st.session_state.bankroll * (default_stake_pct / 100)
        st.session_state.just_resumed = False
    elif current_losses == 0:
        recommended_stake = st.session_state.bankroll * (default_stake_pct / 100)
    else:
        last_odds = st.session_state.last_odds
        multiplier = 2 if last_odds > 2.00 else 3 if 1.50 < last_odds <= 2.00 else 5 if 1.25 < last_odds <= 1.50 else 1
        recommended_stake = st.session_state.last_bet_amount * multiplier

    if recommended_stake > st.session_state.bankroll:
        recommended_stake = st.session_state.bankroll
        st.warning("📉 Stake reduced to available bankroll.")

    st.info(f"💡 **Recommended Stake:** ${recommended_stake:,.2f}")
else:
    recommended_stake = 0.0

# Result input
st.markdown("### Result")
result = st.radio("Record result", ["Win", "Loss"], key=f"result_{current_idx}")

# Record result
if st.button("✅ Record Result"):
    actual_stake = recommended_stake if st.session_state.betting_active else 0.0

    if result == "Win":
        payout = actual_stake * current_race['odds']
        profit_loss = payout - actual_stake
        st.session_state.consecutive_wins += 1
        st.session_state.consecutive_losses = 0
        if st.session_state.betting_active:
            st.session_state.last_bet_amount = actual_stake
            st.session_state.last_odds = current_race['odds']
    else:
        payout = 0.0
        profit_loss = -actual_stake
        st.session_state.consecutive_losses += 1
        st.session_state.consecutive_wins = 0

        if current_wins >= 2:
            st.session_state.betting_active = True
            st.session_state.just_resumed = True
            st.session_state.last_odds = current_race['odds']
        elif st.session_state.betting_active:
            st.session_state.last_bet_amount = actual_stake
            st.session_state.last_odds = current_race['odds']

    st.session_state.bankroll += profit_loss

    st.session_state.race_history.append({
        "Race": current_race['name'], "Odds": current_race['odds'], "Stake": round(actual_stake, 2),
        "Result": result, "Payout": round(payout, 2), "P/L": round(profit_loss, 2),
        "Cumulative P/L": round(st.session_state.bankroll - st.session_state.initial_bankroll, 2),
        "Bankroll After": round(st.session_state.bankroll, 2),
        "Wins Streak": st.session_state.consecutive_wins,
        "Losses Streak": st.session_state.consecutive_losses,
        "Status": betting_status,
    })

    st.session_state.race_index += 1
    st.rerun()

# Progress
st.markdown(f"<center>Progress: {current_idx + 1} / {total_races}</center>", unsafe_allow_html=True)

# History
if st.session_state.race_history:
    st.markdown("---")
    st.subheader("📊 Race History")
    history_df = pd.DataFrame(st.session_state.race_history)
    st.dataframe(
        history_df[[
            "Race", "Odds", "Stake", "Result", "P/L", "Cumulative P/L", "Bankroll After",
            "Wins Streak", "Losses Streak", "Status"
        ]].style.format({
            "Odds": "{:.2f}",
            "Stake": "${:,.2f}",
            "P/L": "${:,.2f}",
            "Cumulative P/L": "${:,.2f}",
            "Bankroll After": "${:,.2f}",
        }),
        use_container_width=True
    )

# Footer
st.markdown("---")
st.caption("© 2025 Rei Labs | Dog Racing Strategy Trial | Full visibility in both themes.")
