import streamlit as st
import pandas as pd

# Page configuration
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'  # default

# Toggle function
def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Apply theme via CSS (custom styling for dark mode and robust light mode)
if st.session_state.theme == 'dark':
    st.markdown("""
    <style>
        .stApp { background-color: #0E1117; color: #FAFAFA; }
        h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, .stCaption, label, .st-emotion-cache-10trblm { color: #FAFAFA !important; }
        .stRadio > label, .stNumberInput > label { color: #FAFAFA !important; }
        .st-bb { background-color: #0E1117 !important; } /* Main background */
        .st-at { background-color: #1F1F1F !important; border: 1px solid #333 !important; } /* Input/Select background */
        .st-bc { color: #FAFAFA !important; } /* Text within widgets */
        .st-emotion-cache-16idsys p { color: #FAFAFA !important; } /* Paragraph text */
        .st-emotion-cache-1kyxreq { border: 1px solid #333 !important; } /* Border for some elements */
        .st-emotion-cache-12w0qpk { background-color: #1F1F1F !important; border: 1px solid #333 !important; } /* Button background */
        .st-emotion-cache-1v3fvav { color: #FAFAFA !important; } /* Metric values */
        .st-emotion-cache-1g6x8q { color: #FAFAFA !important; } /* Metric labels */
        .st-emotion-cache-13k62yr { color: #FAFAFA !important; } /* Table text */
        .st-emotion-cache-f1g0i0 { background-color: #1F1F1F !important; } /* Table header/background */
    </style>
    """, unsafe_allow_html=True)
else: # Light mode
    st.markdown("""
    <style>
        .stApp { background-color: #FFFFFF; color: #000000; }
        h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, .stCaption, label, .st-emotion-cache-10trblm { color: #000000 !important; }
        .stRadio > label, .stNumberInput > label { color: #000000 !important; }
        .st-at { background-color: white !important; border: 1px solid #CCCCCC !important; } /* Input/Select background */
        .st-bc { color: #000000 !important; } /* Text within widgets */
        .st-emotion-cache-16idsys p { color: #000000 !important; } /* Paragraph text */
        .st-emotion-cache-12w0qpk { background-color: white !important; border: 1px solid #CCCCCC !important; } /* Button background */
        .st-emotion-cache-1v3fvav { color: #000000 !important; } /* Metric values */
        .st-emotion-cache-1g6x8q { color: #000000 !important; } /* Metric labels */
        .st-emotion-cache-13k62yr { color: #000000 !important; } /* Table text */
        .st-emotion-cache-f1g0i0 { background-color: #F0F2F6 !important; } /* Table header/background */
    </style>
    """, unsafe_allow_html=True)

st.set_page_config(page_title="Australian Dog Racing Trial", layout="centered")
st.title("🐕 Australian Dog Racing Trial")
st.markdown("Track your strategy with auto-pause, reset stakes, and theme control.")

# Initialize session state at the very top
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0
    st.session_state.initial_bankroll = 1000.0
    st.session_state.last_bet_amount = 0.0
    st.session_state.last_odds = 0.0
    st.session_state.consecutive_wins = 0
    st.session_state.consecutive_losses = 0
    st.session_state.race_index = 0
    st.session_state.race_history = []
    st.session_state.just_resumed = False  # Flag: if we just resumed after 2-win pause

    # Pre-loaded races
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

# Sidebar configuration
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
    st.button("🔁 Reset All Data", on_click=lambda: [st.session_state.update({key: None for key in st.session_state}) or st.session_state.clear()])
    st.markdown("---")
    st.button("🌓 Toggle Dark/Light Mode", on_click=toggle_theme)
    st.markdown(f"<small>Current Theme: **{st.session_state.theme.title()}**</small>", unsafe_allow_html=True)

# Re-initialize bankroll if changed in sidebar
if st.session_state.initial_bankroll != initial_bankroll:
    st.session_state.initial_bankroll = initial_bankroll
    st.session_state.bankroll = initial_bankroll
    st.session_state.last_bet_amount = 0.0
    st.session_state.last_odds = 0.0
    st.session_state.consecutive_wins = 0
    st.session_state.consecutive_losses = 0
    st.session_state.race_index = 0
    st.session_state.race_history = []
    st.session_state.just_resumed = False

# Determine betting status
current_wins = st.session_state.consecutive_wins
current_losses = st.session_state.consecutive_losses

# Rule: After 2 wins → pause until a loss
if current_wins >= 2:
    st.session_state.betting_active = False
    betting_status = "⏸️ No bet – wait for a loss"
elif wait_after_two_losses and current_losses < 2:
    st.session_state.betting_active = False
    betting_status = "⏸️ No bet – waiting for 2 losses"
else:
    st.session_state.betting_active = True
    betting_status = "🟢 Betting active"

# Display status
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

# Show betting status
st.info(betting_status)

# Calculate recommended stake
if st.session_state.betting_active:
    if st.session_state.just_resumed:
        # Reset to 1% of current bankroll after loss breaks 2-win pause
        recommended_stake = st.session_state.bankroll * (default_stake_pct / 100)
        st.session_state.just_resumed = False  # Reset flag
    elif current_losses == 0:
        recommended_stake = st.session_state.bankroll * (default_stake_pct / 100)
    else:
        last_odds = st.session_state.last_odds
        if last_odds > 2.00:
            multiplier = 2
        elif 1.50 < last_odds <= 2.00:
            multiplier = 3
        elif 1.25 < last_odds <= 1.50:
            multiplier = 5
        else:
            multiplier = 1
        recommended_stake = st.session_state.last_bet_amount * multiplier

    if recommended_stake > st.session_state.bankroll:
        recommended_stake = st.session_state.bankroll
        st.warning("📉 Stake reduced to available bankroll.")

    st.info(f"💡 **Recommended Stake:** ${recommended_stake:,.2f}")
else:
    recommended_stake = 0.0

# Win/Loss input — always enabled
st.markdown("### Result")
result = st.radio(
    "Record result",
    ["Win", "Loss"],
    key=f"result_{current_idx}",
    help="You can record the outcome even if betting is paused"
)

# Action button
if st.button("✅ Record Result"):
    # Only place a bet if betting is active
    if st.session_state.betting_active:
        actual_stake = recommended_stake
    else:
        actual_stake = 0.0

    # Process result
    if result == "Win":
        payout = actual_stake * current_race['odds']
        profit_loss = payout - actual_stake
        st.session_state.consecutive_wins += 1
        st.session_state.consecutive_losses = 0
        if st.session_state.betting_active:
            st.session_state.last_bet_amount = actual_stake
            st.session_state.last_odds = current_race['odds']
    else:  # Loss
        payout = 0.0
        profit_loss = -actual_stake
        st.session_state.consecutive_losses += 1
        st.session_state.consecutive_wins = 0

        # If currently paused due to 2 wins, and this is a loss → resume with 1% reset
        if current_wins >= 2:
            st.session_state.betting_active = True
            st.session_state.just_resumed = True  # Trigger 1% reset on next race
            st.session_state.last_odds = current_race['odds']  # Still log it for logic
        # Else: update last bet/odds only if it was a real bet
        elif st.session_state.betting_active:
            st.session_state.last_bet_amount = actual_stake
            st.session_state.last_odds = current_race['odds']

    # Update bankroll
    st.session_state.bankroll += profit_loss

    # Record in history
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

    # Move to next race
    st.session_state.race_index += 1
    st.rerun()

# Progress indicator
st.markdown(f"<center>Progress: {current_idx + 1} / {total_races}</center>", unsafe_allow_html=True)

# Race History
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
st.caption("© 2025 Rei Labs | Dog Racing Strategy Trial | Features: 2-win pause, 1% reset on resumption, dark/light mode.")
