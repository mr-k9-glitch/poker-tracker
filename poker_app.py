import streamlit as st

# Rotate dealer to next index
def rotate_dealer(dealer_index, num_players):
    return (dealer_index + 1) % num_players

# Main Streamlit App
def main():
    st.title("♠️ Poker Game Profit/Loss Tracker")

    if "participants" not in st.session_state:
        st.session_state.participants = []
        st.session_state.total_balances = []
        st.session_state.dealer_index = 0
        st.session_state.round = 1

    # Input participants only once
    if not st.session_state.participants:
        names_input = st.text_input("Enter participant names (comma-separated):")
        if st.button("Start Game") and names_input:
            st.session_state.participants = [name.strip() for name in names_input.split(",")]
            st.session_state.total_balances = [0.0] * len(st.session_state.participants)

    if st.session_state.participants:
        st.subheader(f"Round {st.session_state.round}")
        dealer = st.session_state.participants[st.session_state.dealer_index]
        st.info(f"🎲 Current Dealer: **{dealer}**")

        results = []
        st.write("Enter gains (+) or losses (-) for each player:")
        for name in st.session_state.participants:
            result = st.number_input(f"{name}:", key=f"round_{st.session_state.round}_{name}")
            results.append(result)

        if st.button("Submit Round"):
            if abs(sum(results)) > 0.01:
                st.warning("⚠️ Total net result is not zero. Please double-check the values.")
            st.session_state.total_balances = [
                total + result for total, result in zip(st.session_state.total_balances, results)
            ]
            st.session_state.dealer_index = rotate_dealer(
                st.session_state.dealer_index, len(st.session_state.participants)
            )
            st.session_state.round += 1

        if st.button("End Game"):
            st.subheader("🏁 Final Summary")
            for name, balance in zip(st.session_state.participants, st.session_state.total_balances):
                status = "gained" if balance >= 0 else "lost"
                st.write(f"**{name}** {status} **{abs(balance):.2f}** units.")
            st.balloons()

            # Reset everything for a new game
            if st.button("Start New Game"):
                for key in st.session_state.keys():
                    del st.session_state[key]

if __name__ == "__main__":
    main()
