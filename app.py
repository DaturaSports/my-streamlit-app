import streamlit as st

# Initialize session state variables if not already present
if 'base_stake_pct' not in st.session_state:
    st.session_state.base_stake_pct = 1.0 / 100.0  # Default 1%

if 'bankroll' not in st.session_state:
    st.session_state.bankroll = 10000.0  # Default \$10,000

# App title
st.title("🏈 Sports Betting Model Interface")

# Bankroll input
st.session_state.bankroll = st.number_input(
    "Bankroll (\$)",
    min_value=100.0,
    max_value=1_000_000.0,
    value=st.session_state.bankroll,
    step=100.0,
    format="%.2f"
)

# Base stake percentage slider - FIXED VERSION
st.session_state.base_stake_pct = st.slider(
    "Base Stake %",
    min_value=0.5,
    max_value=5.0,
    value=1.0,
    step=0.5,
    format="%.1f%%"
) / 100.0

# Display current settings
st.write("### 🔍 Current Settings")
st.write(f"- **Bankroll**: \${st.session_state.bankroll:,.2f}")
st.write(f"- **Base Stake**: {st.session_state.base_stake_pct * 100:.1f}% of bankroll")
st.write(f"- **Stake Amount**: \${st.session_state.bankroll * st.session_state.base_stake_pct:,.2f}")

# Example: Input for user probability and odds
st.write("### 📊 Bet Input")
col1, col2 = st.columns(2)
with col1:
    user_prob = st.number_input("Your Win Probability (%)", 1.0, 99.0, 60.0, 0.5) / 100.0
with col2:
    odds = st.number_input("Market Odds (Decimal)", 1.01, 100.0, 2.0, 0.01)

# Implied probability from decimal odds
implied_prob = 1 / odds

# Expected Value calculation
ev = user_prob - implied_prob

# Stake sizing (example: kelly fraction)
kelly_fraction = 0.5  # Half-Kelly
kelly_stake = max(0, (user_prob - (1 - user_prob) / (odds - 1))) * kelly_fraction
unit_stake = st.session_state.bankroll * st.session_state.base_stake_pct
final_stake = min(unit_stake * (kelly_stake / 0.1), st.session_state.bankroll * 0.1)  # Cap max risk

# Decision logic
if ev > 0.01:
    decision = "✅ BET"
    color = "green"
else:
    decision = "❌ NO BET"
    color = "red"

# Results output
st.write("### 📈 Evaluation")
st.markdown(f"<h3 style='color:{color};'>{decision}</h3>", unsafe_allow_html=True)
st.write(f"- **Your Edge**: {ev * 100:+.2f}%")
st.write(f"- **Implied Probability**: {implied_prob * 100:.1f}%")
st.write(f"- **Expected Profit**: {ev * final_stake * 100:.2f}% of stake")
st.write(f"- **Recommended Stake**: \${final_stake:,.2f}")

# Kelly info
st.write("### ℹ️ Notes")
st.write("- Uses half-Kelly staking with base unit scaling")
st.write("- Positive EV threshold: >1% edge")
