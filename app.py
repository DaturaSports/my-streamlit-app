import streamlit as st
import pandas as pd

# Theme state
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# Universal CSS (dark/light)
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
        .custom-metric {
            background-color: #1E1E1E;
            border: 1px solid #333;
            padding: 10px;
            border-radius: 8px;
            color: #FFFFFF;
            font-family: monospace;
            text-align: center;
        }
        .custom-metric-label {
            font-size: 0.9em;
            color: #BBBBBB;
            margin-bottom: 4px;
        }
        .custom-metric-value {
            font-size: 1.3em;
            font-weight: bold;
            color: #FFFFFF;
        }
        .result-button-container {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 10px 0;
        }
        .result-button-container button {
            background-color: #262730;
            color: #FFFFFF !important;
            border: 1px solid #444;
            padding: 10px 20px;
            border-radius: 4px;
            font-size: 1em;
            width: 100px;
        }
        .result-button-container button:hover {
            background-color: #333333;
            color: #FFFFFF !important;
        }
        .stInfo {
            background-color: #1A1D21 !important;
            color: #FFFFFF !important;
        }
        .stWarning {
            background-color: #3C2A1F !important;
            color: #FFD700 !important;
        }
        .stWarning > div > p {
            color: #FFD700 !important;
        }
        .stMarkdown, label, .stText, .stCaption {
            color: #FFFFFF !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        html, body, [data-testid="stAppViewContainer"], .stApp {
            background-color: #FFFFFF;
            color: #000000;
        }
        [data-testid="stHeader"], [data-testid="stSidebar"] {
            background-color: #FFFFFF;
        }
        .custom-metric {
            background-color: #FFFFFF;
            border: 1px solid #CCCCCC;
            padding: 10px;
            border-radius: 8px;
            color: #000000;
            font-family: monospace;
            text-align: center;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .custom-metric-label {
            font-size: 0.9em;
            color: #000000;
            margin-bottom: 4px;
            font-weight: 500;
        }
        .custom-metric-value {
            font-size: 1.3em;
            font-weight: bold;
            color: #000000;
        }
        .result-button-container {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 16px 0 8px 0;
        }
        .result-button-container button {
            background-color: #F0F0F0;
            color: #000000 !important;
            border: 1px solid #CCCCCC;
            padding: 10px 20px;
            border-radius: 4px;
            font-size: 1em;
            width: 100px;
            font-weight: 500;
        }
        .result-button-container button:hover {
            background-color: #DDDDDD;
            color: #000000 !important;
        }
        .stInfo {
            background-color: #E6F3FF !important;
            color: #000000 !important;
            border: 1px solid #B3D9FF;
        }
        .stWarning {
            background-color: #FFF3E0 !important;
            color: #000000 !important;
            border: 1px solid #FFB74D;
        }
        .stWarning > div > p {
            color: #000000 !important;
        }
        .stMarkdown, label, .stText, .stCaption {
            color: #000000 !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Page config
st.set_page_config(page_title="Australian Dog Racing Trial", layout="centered")
st.title("🐕 Australian Dog Racing Trial")
st.markdown("Track your strategy with auto-pause, reset stakes, and full visibility.")

# Initialize session state
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0
    st.session_state.initial_bankroll = 1000.0
    st.session_state.last_bet_amount = 0.0
    st.session_state.consecutive_wins = 0
    st.session_state.consecutive_losses = 0
    st.session_state.race_index = 0
    st.session_state.race_history = []
    st.session_state.just_resumed = False
    st.session_state.betting_active = True
    st.session_state.use_perpetual = False  # New: mode switch
    st.session_state.races = [
        {"name": "Geelong • Race 1 - 1. Darkbonee (8)", "odds": 1.55},
        {"name": "Randwick • Race 5 - 10. Alabama Fox (6)", "odds": 2.00},
        {"name": "Geelong • Race 6 - 5. Harry's Yacht (9)", "odds": 2.20},
        {"name": "Pinjarra • Race 1 - 7. A Summer Fling (8)", "odds": 1.75},
        {"name": "Eagle Farm • Race 7 - 2. Ninja (11)", "odds": 2.35},
        {"name": "Pinjarra • Race 4 - 3. Articole (2)", "odds": 1.70},
    ]

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    initial_bankroll = st.number_input(
        "Starting Bankroll (\$)", min_value=1.0, value=st.session_state.initial_bankroll, step=50.0, format="%.2f"
    )
    default_stake_pct = st.slider(
        "Base Stake (% of bankroll)", min_value=0.1, max_value=10.0, value=1.0, step=0.1
    )
    wait_after_two_losses = st.checkbox("Wait to bet until 2 losses in a row occur", value=False)
    
    # 🔁 New: Perpetual Mode Toggle
    st.markdown("---")
    st.session_state.use_perpetual = st.checkbox("🔁 Perpetual Race Run Mode", value=False)
    
    st.markdown("---")
    st.button("🔁 Reset All Data", on_click=lambda: st.session_state.clear())
    st.markdown("---")
    st.button("🌓 Toggle Dark/Light Mode", on_click=toggle_theme)
    st.markdown(f"<small>Current Theme: <strong>{st.session_state.theme.title()}</strong></small>", unsafe_allow_html=True)

# Re-init on bankroll change
if st.session_state.initial_bankroll != initial_bankroll:
    st.session_state.update({
        'initial_bankroll': initial_bankroll,
        'bankroll': initial_bankroll,
        'last_bet_amount': 0.0,
        'consecutive_wins': 0,
        'consecutive_losses': 0,
        'race_index': 0,
        'race_history': [],
        'just_resumed': False,
        'betting_active': True,
        'use_perpetual': st.session_state.use_perpetual
    })

# Update betting status
current_wins = st.session_state.consecutive_wins
current_losses = st.session_state.consecutive_losses

if st.session_state.just_resumed:
    st.session_state.betting_active = True
    betting_status = "🟢 Betting active (reset after pause)"
elif current_wins >= 2:
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
with col1:
    st.markdown(f"""
    <div class="custom-metric">
        <div class="custom-metric-label">Bankroll</div>
        <div class="custom-metric-value">\${st.session_state.bankroll:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    pnl = st.session_state.bankroll - st.session_state.initial_bankroll
    color = '#228B22' if pnl >= 0 else '#B22222'
    st.markdown(f"""
    <div class="custom-metric">
        <div class="custom-metric-label">P&L</div>
        <div class="custom-metric-value" style="color: {color};">
            {'+' if pnl >= 0 else ''}\${pnl:,.2f}
        </div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"**Streak:** {current_wins}W / {current_losses}L")

# --- PERPETUAL RUN LOGIC ---
if st.session_state.use_perpetual:
    st.markdown("---")
    st.subheader("🔁 Perpetual Race Run Mode")
    st.info("You're in continuous mode. Select odds bracket to get stake recommendation.")

    # Odds selection logic (your brackets)
    odds_bracket = st.selectbox(
        "Select Odds Bracket",
        [
            "1.25–1.50",
            "1.50–1.75",
            "1.75–2.00",
            "2.00–2.25",
            "2.25–2.50",
            "2.50–3.00",
            ">3.00"
        ],
        key="perp_odds_select"
    )

    # Map bracket to representative odds (midpoint or typical)
    bracket_to_odds = {
        "1.25–1.50": 1.37,
        "1.50–1.75": 1.62,
        "1.75–2.00": 1.87,
        "2.00–2.25": 2.12,
        "2.25–2.50": 2.37,
        "2.50–3.00": 2.75,
        ">3.00": 3.50
    }
    current_odds = bracket_to_odds[odds_bracket]

    st.markdown(f"### 🏁 Race {st.session_state.race_index + 1} (Perpetual)")
    st.markdown(f"**Selected Odds:** \${current_odds:.2f}")

    st.info(betting_status)

    # --- STAKE CALCULATION ---
    recommended_stake = 0.0

    if st.session_state.just_resumed:
        recommended_stake = st.session_state.bankroll * (default_stake_pct / 100)
    elif st.session_state.betting_active:
        if st.session_state.consecutive_losses == 0:
            recommended_stake = st.session_state.bankroll * (default_stake_pct / 100)
        else:
            base_stake = st.session_state.last_bet_amount
            if current_odds > 2.00:
                multiplier = 2
            elif 1.50 <= current_odds <= 2.00:
                multiplier = 3
            elif 1.25 <= current_odds < 1.50:
                multiplier = 5
            else:
                multiplier = 1
            recommended_stake = base_stake * multiplier
    else:
        recommended_stake = 0.0

    if recommended_stake > st.session_state.bankroll:
        recommended_stake = st.session_state.bankroll
        st.warning("📉 Stake reduced to available bankroll.")

    if st.session_state.just_resumed:
        st.info(f"💡 **Recommended Stake:** \${recommended_stake:,.2f} (Reset after pause)")
    elif st.session_state.betting_active:
        st.info(f"💡 **Recommended Stake:** \${recommended_stake:,.2f}")
    else:
        st.info(betting_status)

    # --- RESULT BUTTONS ---
    st.markdown("### Record Result")
    st.markdown('<div class="result-button-container">', unsafe_allow_html=True)
    col_win, col_loss = st.columns(2)
    with col_win:
        if st.button("✅ Win", key="btn_win_perp"):
            st.session_state.result_input = "Win"
            st.session_state.current_perp_odds = current_odds
            st.rerun()
    with col_loss:
        if st.button("❌ Loss", key="btn_loss_perp"):
            st.session_state.result_input = "Loss"
            st.session_state.current_perp_odds = current_odds
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- STANDARD RACE MODE ---
else:
    race_list = st.session_state.races
    current_idx = st.session_state.race_index
    total_races = len(race_list)

    if current_idx >= total_races:
        st.success("🏁 All races completed!")
        st.stop()

    current_race = race_list[current_idx]
    current_odds = current_race['odds']
    st.markdown("---")
    st.subheader(f"Race {current_idx + 1} of {total_races}")
    st.markdown(f"### {current_race['name']} @ **\${current_odds}**")

    st.info(betting_status)

    # --- STAKE CALCULATION ---
    recommended_stake = 0.0

    if st.session_state.just_resumed:
        recommended_stake = st.session_state.bankroll * (default_stake_pct / 100)
    elif st.session_state.betting_active:
        if st.session_state.consecutive_losses == 0:
            recommended_stake = st.session_state.bankroll * (default_stake_pct / 100)
        else:
            base_stake = st.session_state.last_bet_amount
            if current_odds > 2.00:
                multiplier = 2
            elif 1.50 <= current_odds <= 2.00:
                multiplier = 3
            elif 1.25 <= current_odds < 1.50:
                multiplier = 5
            else:
                multiplier = 1
            recommended_stake = base_stake * multiplier
    else:
        recommended_stake = 0.0

    if recommended_stake > st.session_state.bankroll:
        recommended_stake = st.session_state.bankroll
        st.warning("📉 Stake reduced to available bankroll.")

    if st.session_state.just_resumed:
        st.info(f"💡 **Recommended Stake:** \${recommended_stake:,.2f} (Reset after pause)")
    elif st.session_state.betting_active:
        st.info(f"💡 **Recommended Stake:** \${recommended_stake:,.2f}")
    else:
        st.info(betting_status)

    # --- RESULT BUTTONS ---
    st.markdown("### Record Result")
    st.markdown('<div class="result-button-container">', unsafe_allow_html=True)
    col_win, col_loss = st.columns(2)
    with col_win:
        if st.button("✅ Win", key="btn_win"):
            st.session_state.result_input = "Win"
            st.rerun()
    with col_loss:
        if st.button("❌ Loss", key="btn_loss"):
            st.session_state.result_input = "Loss"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Skip Race
    MIN_ODDS_THRESHOLD = 1.25
    if current_odds < MIN_ODDS_THRESHOLD:
        st.warning(f"⚠️ Odds (\${current_odds:.2f}) below minimum threshold ({MIN_ODDS_THRESHOLD}). Consider skipping.")

    if st.button("⏭️ Skip This Race"):
        st.session_state.race_history.append({
            "Race": current_race['name'],
            "Odds": current_odds,
            "Stake": 0.0,
            "Result": "Skipped",
            "Payout": 0.0,
            "P/L": 0.0,
            "Cumulative P/L": round(st.session_state.bankroll - st.session_state.initial_bankroll, 2),
            "Bankroll After": round(st.session_state.bankroll, 2),
            "Wins Streak": st.session_state.consecutive_wins,
            "Losses Streak": st.session_state.consecutive_losses,
            "Status": "Skipped – Odds too low",
        })
        st.session_state.race_index += 1
        st.rerun()

# --- PROCESS RESULT (COMMON) ---
if 'result_input' in st.session_state:
    result = st.session_state.result_input
    del st.session_state.result_input

    # Capture state
    prior_wins = st.session_state.consecutive_wins
    was_paused = prior_wins >= 2
    prior_betting_active = st.session_state.betting_active

    # Determine actual stake
    if st.session_state.just_resumed:
        actual_stake = st.session_state.bankroll * (default_stake_pct / 100)
        st.session_state.just_resumed = False
    elif prior_betting_active:
        actual_stake = recommended_stake
    else:
        actual_stake = 0.0

    if actual_stake > st.session_state.bankroll:
        actual_stake = st.session_state.bankroll

    # Initialize
    profit_loss = 0.0
    payout = 0.0

    # Use correct odds
    if st.session_state.use_perpetual:
        current_odds = st.session_state.current_perp_odds
    else:
        current_odds = current_race['odds'] if 'current_race' in locals() else 1.0

    # Process result
    if result == "Win":
        if actual_stake > 0:
            payout = actual_stake * current_odds
            profit_loss = payout - actual_stake
            st.session_state.consecutive_wins += 1
            st.session_state.consecutive_losses = 0
            st.session_state.last_bet游戏副本
