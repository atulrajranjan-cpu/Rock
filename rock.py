import streamlit as st
import cv2
import random
import time
import numpy as np
from cvzone.HandTrackingModule import HandDetector

# --- Game Variables ---
choices = ['rock', 'paper', 'scissors']
rounds_to_win = 3  # Best of 5

# --- Initialize Hand Detector ---
detector = HandDetector(detectionCon=0.7, maxHands=1)

# --- Function to get gesture from hand landmarks ---
def get_gesture_from_fingers(fingers):
    if fingers == [0, 0, 0, 0, 0]:
        return 'rock'
    elif fingers == [1, 1, 1, 1, 1]:
        return 'paper'
    elif fingers == [0, 1, 1, 0, 0]:
        return 'scissors'
    return None

# --- Main Streamlit App ---
def main():
    st.title("Rock, Paper, Scissors! 🪨📄✂️")
    st.markdown("Play against the computer using hand gestures. First to 3 wins!")

    if 'player_score' not in st.session_state:
        st.session_state.player_score = 0
    if 'computer_score' not in st.session_state:
        st.session_state.computer_score = 0
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False

    status_text = st.empty()
    status_text.write("Click 'Start Game' to begin.")

    st.markdown(f"**Current Score:** You {st.session_state.player_score} - {st.session_state.computer_score} Computer")

    if st.button("Start Game"):
        st.session_state.game_started = True
        st.session_state.player_score = 0
        st.session_state.computer_score = 0
        st.rerun()

    if st.session_state.game_started and st.session_state.player_score < rounds_to_win and st.session_state.computer_score < rounds_to_win:
        st.write("Show your hand gesture to the camera after the countdown.")
        countdown_placeholder = st.empty()

        for i in range(3, 0, -1):
            countdown_placeholder.markdown(f"**Get ready... {i}**", unsafe_allow_html=True)
            time.sleep(1)

        countdown_placeholder.markdown("**SHOW!**", unsafe_allow_html=True)

        frame = st.camera_input("Take a photo of your hand")

        if frame is not None:
            file_bytes = np.asarray(bytearray(frame.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            hands_list, img_drawn = detector.findHands(img, flipType=False)

            player_gesture = None
            if hands_list:
                hand = hands_list[0]
                fingers = detector.fingersUp(hand)
                player_gesture = get_gesture_from_fingers(fingers)

                st.image(img_drawn, channels="BGR", caption="Your Hand")

            computer_choice = random.choice(choices)

            if player_gesture:
                st.write(f"You chose: **{player_gesture.upper()}**")
                st.write(f"Computer chose: **{computer_choice.upper()}**")

                if player_gesture == computer_choice:
                    st.write("It's a tie!")
                elif (player_gesture == 'rock' and computer_choice == 'scissors') or \
                     (player_gesture == 'paper' and computer_choice == 'rock') or \
                     (player_gesture == 'scissors' and computer_choice == 'paper'):
                    st.session_state.player_score += 1
                    st.balloons()
                    st.success("You win this round! 🎉")
                else:
                    st.session_state.computer_score += 1
                    st.error("Computer wins this round! 💻")
            else:
                st.warning("Could not detect a clear gesture. Please try again.")

            st.markdown(f"**Current Score:** You {st.session_state.player_score} - {st.session_state.computer_score} Computer")

    if st.session_state.player_score >= rounds_to_win or st.session_state.computer_score >= rounds_to_win:
        if st.session_state.player_score > st.session_state.computer_score:
            st.success(f"**Congratulations! You won the game {st.session_state.player_score} to {st.session_state.computer_score}! 🏆**")
        else:
            st.error(f"**Sorry, the computer won the game {st.session_state.computer_score} to {st.session_state.player_score}. 🤖**")
        st.session_state.game_started = False
        if st.button("Play Again?"):
            st.rerun()

if __name__ == '__main__':
    main()
