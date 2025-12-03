import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(page_title="Australian Dog Racing Trial", layout="centered")
st.title("🐕 Australian Dog Racing Trial")
st.markdown("Track your betting strategy with dynamic stake recommendations and bankroll management.")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    initial_bankroll = st.number_input(
        "Initial Bankroll ($)", min_value=1.0, value=1000.0, step=50.0, format="%.2f"
    )
    default_stake_pct = st.slider(
        "Default Stake (% of bankroll)", min_value=0.1, max_value=10.0, value=1.0, step=0.1
    )
    st.markdown("---")
    if st.button("Reset All Data"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

# Initialize session state
if 'bankroll' not in st.session_state:
    st.session_state.bankroll = initial_bankroll
    st.session_state.initial_bankroll = initial_bankroll
    st.session_state.last_bet_amount = 0.0
    st.session_state.last_odds = 0.0
    st.session_state.consecutive_wins = 0
    st.session_state.consecutive_losses = 0
    st.session_state.betting_active = True  # Start betting immediately
    st.session_state.race_history = []
    st.session_state.waiting_for_loss = False

# Display current bankroll and stats
col1, col2 = st.columns(2)
col1.metric("Current Bankroll", f"${st.session_state.bankroll:,.2f}")
col2.metric("Profit & Loss", f"${st.session_state.bankroll - st.session_state.initial_bankroll:,.2f}")

st.markdown(f"**Win Streak:** {st.session_state.consecutive_wins} | **Loss Streak:** {st.session_state.consecutive_losses}")
st.markdown("---")

# Live race input form
st.subheader("Enter Race Result")
with st.form("race_form"):
    race_name = st.text_input("Race Name (e.g., Rosehill Race 5 - Lyles)", placeholder="Enter race details")
    odds = st.number_input("Odds (Decimal)", min_value=1.01, value=2.00, step=0.01, format="%.2f")
    
    # Calculate recommended stake
    if not st.session_state.betting_active:
        recommended_stake = 0.0
    else:
        if st.session_state.consecutive_losses == 0:
            # First bet or after a win
            recommended_stake = st.session_state.bankroll * (default_stake_pct / 100)
        else:
            # After a loss: apply multiplier based on last odds
            last_odds = st.session_state.last_odds
            if last_odds > 2.00:
                multiplier = 2
            elif 1.50 < last_odds <= 2.00:
                multiplier = 3
            elif 1.25 < last_odds <= 1.50:
                multiplier = 5
            else:
                multiplier = 1  # Fallback
            recommended_stake = st.session_state.last_bet_amount * multiplier

    st.info(f"**Recommended Stake:** ${recommended_stake:,.2f}")

    result = st.radio("Race Result", options=["Win", "Loss", "No Bet"], horizontal=True)
    actual_stake = st.number_input(
        "Actual Stake Used ($)", min_value=0.0, value=recommended_stake, step=0.01, format="%.2f"
    )
    submitted = st.form_submit_button("Process Race")

if submitted:
    if not race_name.strip():
        st.error("Please enter a race name.")
    else:
        # Calculate payout and P/L
        if result == "Win":
            payout = actual_stake * odds
            profit_loss = payout - actual_stake
            st.session_state.consecutive_wins += 1
            st.session_state.consecutive_losses = 0
            st.session_state.betting_active = True  # Continue until 2 wins
        elif result == "Loss":
            payout = 0.0
            profit_loss = -actual_stake
            st.session_state.consecutive_losses += 1
            st.session_state.consecutive_wins = 0
            st.session_state.betting_active = True  # Always bet after a loss
        else:  # No Bet
            payout = 0.0
            profit_loss = 0.0
            # Do not update win/loss streak
            st.session_state.betting_active = False  # Maintain "No Bet" state

        # Update bankroll
        st.session_state.bankroll += profit_loss

        # Check exit condition: 2 consecutive wins
        if st.session_state.consecutive_wins >= 2:
            st.session_state.betting_active = False

        # Record race in history
        new_entry = {
            "Race": race_name,
            "Odds": odds,
            "Stake": actual_stake,
            "Result": result,
            "Payout": payout,
            "P/L": profit_loss,
            "Cumulative P/L": st.session_state.bankroll - st.session_state.initial_bankroll,
            "Bankroll After": st.session_state.bankroll,
            "Consecutive Wins": st.session_state.consecutive_wins,
            "Consecutive Losses": st.session_state.consecutive_losses,
            "Betting Active": "Yes" if st.session_state.betting_active else "No",
        }
        st.session_state.race_history.append(new_entry)

        # Update last bet and odds for next calculation
        if result in ["Win", "Loss"]:
            st.session_state.last_bet_amount = actual_stake
            st.session_state.last_odds = odds

        st.success(f"Race processed! Bankroll updated to ${st.session_state.bankroll:,.2f}")
        st.rerun()

# Display race history
if st.session_state.race_history:
    st.markdown("---")
    st.subheader("Race History")
    history_df = pd.DataFrame(st.session_state.race_history)
    st.dataframe(history_df.style.format({
        "Odds": "{:.2f}",
        "Stake": "${:,.2f}",
        "Payout": "${:,.2f}",
        "P/L": "${:,.2f}",
        "Cumulative P/L": "${:,.2f}",
        "Bankroll After": "${:,.2f}",
    }), use_container_width=True)

# Footer
st.markdown("---")
st.caption("© 2025 Rei Labs | Australian Dog Racing Trial | Strategy based on 60% win rate with progressive staking.")
