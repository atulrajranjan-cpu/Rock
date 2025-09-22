import cv2
import mediapipe as mp
import streamlit as st
import numpy as np
import random

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

st.title("Rock-Paper-Scissors: Hand Gesture Game")
st.write("Take a picture of your hand gesture to play!")
st.write("🖐️ Rock: 0 fingers up")
st.write("✌️ Scissors: 2 fingers up")
st.write("✋ Paper: 5 fingers up")

# Function to count fingers
def count_fingers(landmarks):
    # (Your existing count_fingers function goes here)
    finger_tips = [8, 12, 16, 20]
    finger_up = []
    if landmarks[4].x < landmarks[2].x:
        finger_up.append(True)
    else:
        finger_up.append(False)
    for tip_id in finger_tips:
        if landmarks[tip_id].y < landmarks[tip_id - 2].y:
            finger_up.append(True)
        else:
            finger_up.append(False)
    return finger_up.count(True)

# Use st.camera_input to get a picture from the user's webcam
img_file_buffer = st.camera_input("Take a picture")

if img_file_buffer is not None:
    # Convert the image from the buffer to a NumPy array
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    # Process the image with MediaPipe
    rgb_frame = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    player_choice = "Unknown"
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            landmarks = hand_landmarks.landmark
            finger_count = count_fingers(landmarks)
            
            if finger_count == 0:
                player_choice = "Rock"
            elif finger_count == 2:
                player_choice = "Scissors"
            elif finger_count == 5:
                player_choice = "Paper"

    if player_choice != "Unknown":
        choices = ["Rock", "Paper", "Scissors"]
        computer_choice = random.choice(choices)

        st.subheader("Results:")
        st.write(f"Your choice: **{player_choice}**")
        st.write(f"Computer's choice: **{computer_choice}**")

        if player_choice == computer_choice:
            st.warning("It's a tie!")
        elif (player_choice == "Rock" and computer_choice == "Scissors") or \
             (player_choice == "Scissors" and computer_choice == "Paper") or \
             (player_choice == "Paper" and computer_choice == "Rock"):
            st.success("You win!")
        else:
            st.error("Computer wins!")

    else:
        st.write("Could not detect a valid hand gesture. Try again.")

***
This video, titled "Streamlit FAQ on ModuleNotFoundError," provides a helpful guide on troubleshooting common dependency issues during Streamlit deployment.
[Streamlit FAQ on ModuleNotFoundError](https://www.youtube.com/watch?v=3YutfZE1K74)
http://googleusercontent.com/youtube_content/1
