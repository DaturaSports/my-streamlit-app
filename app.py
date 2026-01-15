import streamlit as st

# --- THEME & SESSION STATE INIT ---
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

st.set_page_config(page_title="Datura Dog Racing Model", layout="wide")

# Initialize session state
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 1000.0
    st.session_state.initial_bankroll = 1000.0
    st.session_state.streak = 1  # Positive = loss streak, Negative = win streak
    st.session_state.last_bet_amount = 0.0

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state.initial_bankroll = st.number_input("Starting Bankroll (\$)", value=1000.0)
    win_rate_base = st.slider("Overall Win Rate (%)", 1.0, 100.0, 60.0) / 100
    base_stake_pct = st.slider("Base Stake (%)", 0.1, 10.0, 1.0)
    if st.button("🌓 Toggle Theme"):
        toggle_theme()
    if st.button("🔁 Reset Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --- MAIN INTERFACE ---
st.title("🐕 Datura Dog Racing Model")

# Top Metrics
pnl = st.session_state.bankroll - st.session_state.initial_bankroll
col1, col2, col3 = st.columns(3)
col1.metric("Bankroll", f"\${st.session_state.bankroll:,.2f}")
col2.metric("P&L", f"\${pnl:,.2f}", delta=f"{pnl:,.2f}")
col3.metric("Current Streak", st.session_state.streak)

st.divider()

# --- INPUT & CALCULATIONS ---
col_input, col_output = st.columns([1, 1])

with col_input:
    st.subheader("Race Inputs")
    
    # Manual odds input (triggers instant recalc)
    bookie_odds = st.number_input(
        "Enter Bookmaker Odds", 
        min_value=1.01, 
        value=1.67, 
        step=0.01, 
        format="%.2f"
    )
    
    # 1. Implied Probability
    implied_prob = (1 / bookie_odds) * 100
    
    # 2. Over/Under Index = Streak × Win Rate %
    # Only use positive streak (losses) for index
    current_streak_for_index = abs(st.session_state.streak) if st.session_state.streak > 0 else 1
    ou_index = current_streak_for_index * (win_rate_base * 100)
    
    # 3. Datura Weighted Probability
    weighted_prob = (ou_index + implied_prob) / 2
    
    # 4. Datura Edge
    datura_edge = weighted_prob - implied_prob

with col_output:
    st.subheader("Model Output")
    
    st.markdown(f"**Implied Probability:** {implied_prob:.2f}%")
    st.markdown(f"**Over/Under Index:** {ou_index:.2f}%")
    st.markdown(f"**Weighted Probability:** {weighted_prob:.2f}%")
    
    edge_color = "green" if datura_edge > 0 else "red"
    st.markdown(f"### **Datura Edge:** :{edge_color}[{datura_edge:.2f}%]")
    
    # --- STAKE CALCULATION (Fully Dynamic) ---
    base_stake = st.session_state.bankroll * (base_stake_pct / 100)
    
    # Determine multiplier based on odds bracket
    if bookie_odds <= 1.50:
        odds_multiplier = 5
    elif bookie_odds <= 2.00:
        odds_multiplier = 3
    else:
        odds_multiplier = 2
    
    # Apply streak multiplier only during loss streaks
    if st.session_state.streak > 0:
        total_multiplier = odds_multiplier * st.session_state.streak
        recommended_stake = base_stake * total_multiplier
    else:
        # After a win, reset to base stake or conservative recovery
        recommended_stake = base_stake  # or use a smaller multiplier

    # Format stake to avoid scientific notation
    recommended_stake = max(recommended_stake, 0.01)  # prevent near-zero display

    st.success(f"**Recommended Stake:** \${recommended_stake:,.2f}")
    st.caption(f"Base: \${base_stake:,.2f} | Multiplier: ×{odds_multiplier} (odds) ×{st.session_state.streak if st.session_state.streak > 0 else 1} (streak)")

# --- ACTION BUTTONS ---
st.divider()
btn_win, btn_loss = st.columns(2)

if btn_win.button("✅ RACE WIN", use_container_width=True):
    profit = (recommended_stake * bookie_odds) - recommended_stake
    st.session_state.bankroll += profit
    # Reset streak to negative (winning streak)
    if st.session_state.streak < 0:
        st.session_state.streak -= 1  # Extend winning streak
    else:
        st.session_state.streak = -1  # Start new winning streak
    st.session_state.last_bet_amount = recommended_stake
    st.rerun()

if btn_loss.button("❌ RACE LOSS", use_container_width=True):
    st.session_state.bankroll -= recommended_stake
    # Reset or extend loss streak
    if st.session_state.streak > 0:
        st.session_state.streak += 1  # Extend losing streak
    else:
        st.session_state.streak = 1  # Start new losing streak
    st.session_state.last_bet_amount = recommended_stake
    st.rerun()

# --- EXPLAINER ---
with st.expander("ℹ️ How Edge & Stake Are Calculated"):
    st.markdown("""
    ### **Edge Logic**
    1. **Implied Prob**: \$1 / \\text{Odds}\$
    2. **Over/Under Index**: \$\\text{Current Loss Streak} \\times \\text{Win Rate (e.g., 60\\%)}\$
    3. **Weighted Prob**: \$(\\text{Index} + \\text{Implied}) / 2\$
    4. **Datura Edge**: \$\\text{Weighted Prob} - \\text{Implied Prob}\$

    ### **Stake Logic**
    - **Base Stake**: `Bankroll × Base %`
    - **Odds Multiplier**:
        - `≤ 1.50` → ×5
        - `1.51–2.00` → ×3
        - `≥ 2.01` → ×2
    - **Streak Multiplier**: Applied only during losing streaks
    - **Final Stake**: `Base × Odds Mult × Streak`

    > All values update instantly as you change odds or results.
    """)
