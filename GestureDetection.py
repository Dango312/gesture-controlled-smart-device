import cv2, asyncio
import mediapipe as mp
import numpy as np
from keras.models import load_model
from dotenv import load_dotenv
from HomeCommands import *

mp_holistic = mp.solutions.holistic 
model = load_model('LSTM_Actions20f4Smaller3.h5') 

all_actions = np.array(['Привет', 'Погода', 'Свет', 'Врач', 'IDLE', 'Синий', 'Красный', 'Жёлтый'])

def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False                 
    results = model.process(image)               
    image.flags.writeable = True                   
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) 
    return image, results

def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
    face = np.array([[res.x, res.y, res.z] for res in results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468*3)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose, face, lh, rh])

async def detection():
    sequence = []
    sentence = []
    predictions = []
    threshold = 0.4

    cap = cv2.VideoCapture(0)
    with mp_holistic.Holistic(min_dsetection_confidence=0.9, min_tracking_confidence=0.1) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()
            image, results = mediapipe_detection(frame, holistic)
        
            keypoints = extract_keypoints(results)
            sequence.append(keypoints)
            sequence = sequence[-20:]
        
            if len(sequence) == 20:
                res = model.predict(np.expand_dims(sequence, axis=0), verbose=0)[0]
                predictions.append(np.argmax(res))
            
                if np.unique(predictions[-10:])[0]==np.argmax(res): 
                    if res[np.argmax(res)] > threshold: 
                        if len(sentence) > 0: 
                            if all_actions[np.argmax(res)] != sentence[-1]:
                                sentence.append(all_actions[np.argmax(res)])
                                #print(sentence[-1])
                                await command_control(list(all_actions).index(sentence[-1]))
                        else:
                            sentence.append(all_actions[np.argmax(res)])
                if len(sentence) > 5: 
                    sentence = sentence[-4:]
        
            cv2.imshow('OpenCV Feed', image)
            if cv2.waitKey(10) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    load_dotenv()
    asyncio.run(detection())