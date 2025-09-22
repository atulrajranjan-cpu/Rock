import streamlit as st
import cv2
import mediapipe as mp
import random
import numpy as np
import time

# --- Game Variables ---
choices = ['rock', 'paper', 'scissors']
rounds_to_win = 3  # Best of 5

# --- Streamlit Session State ---
if 'player_score' not in st.session_state:
    st.session_state.player_score = 0
if 'computer_score' not in st.session_state:
    st.session_state.computer_score = 0
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'winner_message' not in st.session_state:
    st.session_state.winner_message = ""

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

# --- Game Logic ---
def determine_winner(player_choice, computer_choice):
    if player_choice == computer_choice:
        return "It's a tie!"
    elif (player_choice == 'rock' and computer_choice == 'scissors') or \
         (player_choice == 'paper' and computer_choice == 'rock') or \
         (player_choice == 'scissors' and computer_choice == 'paper'):
        st.session_state.player_score += 1
        return "You win this round! 🎉"
    else:
        st.session_state.computer_score += 1
        return "Computer wins this round! 💻"

# --- Main App Body ---
st.title("Rock, Paper, Scissors! 🪨📄✂️")
st.markdown("Play against the computer by showing your hand to the camera!")

st.markdown(f"**Current Score:** You {st.session_state.player_score} - {st.session_state.computer_score} Computer")

if st.session_state.player_score >= rounds_to_win or st.session_state.computer_score >= rounds_to_win:
    if st.session_state.player_score > st.session_state.computer_score:
        st.success(f"**Congratulations! You won the game {st.session_state.player_score} to {st.session_state.computer_score}! 🏆**")
    else:
        st.error(f"**Sorry, the computer won the game {st.session_state.computer_score} to {st.session_state.player_score}. 🤖**")
    
    if st.button("Play Again?"):
        st.session_state.player_score = 0
        st.session_state.computer_score = 0
        st.rerun()
else:
    st.write("Show your hand gesture to the camera to play the next round!")
    frame = st.camera_input("Take a photo of your hand")
    
    if frame is not None:
        file_bytes = np.asarray(bytearray(frame.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        results = hands.process(img_rgb)
        
        player_gesture = None
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                player_gesture = get_gesture(hand_landmarks)
        
        st.image(img, channels="BGR", caption="Your Hand")
        
        computer_choice = random.choice(choices)

        if player_gesture:
            st.write(f"You chose: **{player_gesture.upper()}**")
            st.write(f"Computer chose: **{computer_choice.upper()}**")
            result = determine_winner(player_gesture, computer_choice)
            st.subheader(result)
        else:
            st.warning("Could not detect a clear gesture. Please try again.")
