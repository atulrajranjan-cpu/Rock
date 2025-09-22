import streamlit as st
import random
import time

# Try to import OpenCV and MediaPipe
try:
    import cv2
    import mediapipe as mp
    webcam_available = True
except:
    webcam_available = False

choices = ['rock', 'paper', 'scissors']
rounds_to_win = 3

# --- Gesture detection (only if webcam works locally) ---
if webcam_available:
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils

    def get_gesture(hand_landmarks):
        if not hand_landmarks:
            return None
        landmarks = hand_landmarks.landmark

        # Rock
        if (landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y >
            landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
            landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y >
            landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
            landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y >
            landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
            landmarks[mp_hands.HandLandmark.PINKY_TIP].y >
            landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
            return 'rock'

        # Paper
        elif (landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y <
              landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
              landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y <
              landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
              landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y <
              landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
              landmarks[mp_hands.HandLandmark.PINKY_TIP].y <
              landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
            return 'paper'

        # Scissors
        elif (landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y <
              landmarks[mp_hands.HandLandmark.INDEX_FINGER_PIP].y and
              landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y <
              landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y and
              landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y >
              landmarks[mp_hands.HandLandmark.RING_FINGER_PIP].y and
              landmarks[mp_hands.HandLandmark.PINKY_TIP].y >
              landmarks[mp_hands.HandLandmark.PINKY_PIP].y):
            return 'scissors'
        return None

def get_winner(player_choice, computer_choice):
    if player_choice == computer_choice:
        return "tie"
    elif (player_choice == 'rock' and computer_choice == 'scissors') or \
         (player_choice == 'paper' and computer_choice == 'rock') or \
         (player_choice == 'scissors' and computer_choice == 'paper'):
        return "player"
    else:
        return "computer"

# --- Streamlit App ---
st.title("✊✋✌ Rock, Paper, Scissors")
st.write("Play against the computer!")

player_score = 0
computer_score = 0

if webcam_available:
    st.write("Webcam detected. Show your hand to play!")
else:
    st.write("Webcam not available. Gestures will be simulated.")

play = st.button("Play Round")

if play:
    # If webcam available locally, you can implement real detection here
    if webcam_available:
        st.warning("Webcam input is not supported on Streamlit Cloud. Run locally to use your camera.")
        player_choice = random.choice(choices)
    else:
        player_choice = random.choice(choices)

    computer_choice = random.choice(choices)
    winner = get_winner(player_choice, computer_choice)

    if winner == "player":
        player_score += 1
        st.success(f"You chose {player_choice}, Computer chose {computer_choice} → You Win 🎉")
    elif winner == "computer":
        computer_score += 1
        st.error(f"You chose {player_choice}, Computer chose {computer_choice} → Computer Wins 🤖")
    else:
        st.info(f"You chose {player_choice}, Computer chose {computer_choice} → Tie 😅")
