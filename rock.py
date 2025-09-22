import streamlit as st
import cv2
import mediapipe as mp
import random
import time
import numpy as np
from PIL import Image

# --- Game Variables ---
choices = ['rock', 'paper', 'scissors']
rounds_to_win = 3  # Best of 5

# --- Initialize MediaPipe Hands ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# --- Function to get gesture from hand landmarks ---
def get_gesture(hand_landmarks):
    if not hand_landmarks:
        return None
    
    landmarks = hand_landmarks.landmark
    
    # Check for closed fist (Rock)
    if (landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y > landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
        landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y > landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
        landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
        landmarks[mp_hands.HandLandmark.PINKY_FINGER_TIP].y > landmarks[mp_hands.HandLandmark.PINKY_FINGER_PIP].y):
        return 'rock'

    # Check for open hand (Paper)
    elif (landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
          landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
          landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
          landmarks[mp_hands.HandLandmark.PINKY_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.PINKY_FINGER_PIP].y):
        return 'paper'
        
    # Check for scissors (Index and middle fingers up)
    elif (landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
          landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
          landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y > landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
          landmarks[mp_hands.HandLandmark.PINKY_FINGER_TIP].y > landmarks[mp_hands.HandLandmark.PINKY_FINGER_PIP].y):
        return 'scissors'
    
    return None

# --- Main Streamlit App ---
def main():
    st.title("Rock, Paper, Scissors! 🪨📄✂️")
    st.markdown("Play against the computer using hand gestures. First to 3 wins!")
    
    # Initialize session state for game variables
    if 'player_score' not in st.session_state:
        st.session_state.player_score = 0
    if 'computer_score' not in st.session_state:
        st.session_state.computer_score = 0
    if 'game_started' not in st.session_state:
        st.session_state.game_started = False
        
    status_text = st.empty()
    status_text.write("Click 'Start Game' to begin.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Your Move")
        player_image_placeholder = st.empty()
    with col2:
        st.subheader("Computer's Move")
        computer_image_placeholder = st.empty()

    if st.button("Start Game"):
        st.session_state.game_started = True
        st.session_state.player_score = 0
        st.session_state.computer_score = 0
        status_text.write("Game is starting...")
        time.sleep(1)
        st.experimental_rerun()

    if st.session_state.game_started and st.session_state.player_score < rounds_to_win and st.session_state.computer_score < rounds_to_win:
        st.write("Show your hand gesture to the camera after the countdown.")
        countdown_placeholder = st.empty()
        
        for i in range(3, 0, -1):
            countdown_placeholder.markdown(f"**Get ready... {i}**", unsafe_allow_html=True)
            time.sleep(1)
        
        countdown_placeholder.markdown("**SHOW!**", unsafe_allow_html=True)
        
        frame = st.camera_input("Take a photo of your hand")
        
        if frame is not None:
            # Convert the Streamlit frame to a format OpenCV can use
            file_bytes = np.asarray(bytearray(frame.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            # Process the image with MediaPipe
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(img_rgb)
            
            player_gesture = None
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    player_gesture = get_gesture(hand_landmarks)
                    mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            player_image_placeholder.image(img, channels="BGR", caption="Your Hand")

            computer_choice = random.choice(choices)

            if player_gesture:
                st.write(f"You chose: **{player_gesture.upper()}**")
                st.write(f"Computer chose: **{computer_choice.upper()}**")

                # Determine the winner
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
    
    # Final winner announcement
    if st.session_state.player_score >= rounds_to_win or st.session_state.computer_score >= rounds_to_win:
        if st.session_state.player_score > st.session_state.computer_score:
            st.success(f"**Congratulations! You won the game {st.session_state.player_score} to {st.session_state.computer_score}! 🏆**")
        else:
            st.error(f"**Sorry, the computer won the game {st.session_state.computer_score} to {st.session_state.player_score}. 🤖**")
        st.session_state.game_started = False
        st.button("Play Again?")

if __name__ == '__main__':
    main()