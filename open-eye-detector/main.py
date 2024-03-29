from keras import backend as K
from keras.models import load_model
import numpy as np
from imutils import face_utils
import time
import dlib
import cv2,os,sys
import face_recognition
import tensorflow as tf
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--com', type=str, default='3', help='Set you COM port from device manager')
    parser.add_argument('--eyeclosednum', type=int, default=10, help='Set the time number of closing eye')
    
    return parser.parse_args()

args = parse_args() 

#-------------------pyserial config-------------------#
import serial
com = serial.Serial('COM'+ args.com, 115200)
close_eye_count = 0


#-------------------original code about eye-open-detector-------------------#
num_cores = 4
num_CPU = 1
num_GPU = 1

config = tf.compat.v1.ConfigProto(intra_op_parallelism_threads=num_cores,
                        inter_op_parallelism_threads=num_cores, 
                        allow_soft_placement=True,
                        device_count = {'CPU' : num_CPU,
                                        'GPU' : num_GPU}
                       )

session = tf.compat.v1.Session(config=config)
K.set_session(session)


class FacialLandMarksPosition:
    """
    The indices points to the various facial features like left ear, right ear, nose, etc.,
    that are mapped from the Facial Landmarks used by dlib's FacialLandmarks predictor.
    """
    left_eye_start_index, left_eye_end_index = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    right_eye_start_index, right_eye_end_index = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
   
facial_landmarks_predictor = './models/68_face_landmarks_predictor.dat'
predictor = dlib.shape_predictor(facial_landmarks_predictor)
 
model = load_model('./models/weights.149-0.01.hdf5')

def predict_eye_state(model, image):
    image = cv2.resize(image, (20, 10))
    image = image.astype(dtype=np.float32)
        
    image_batch = np.reshape(image, (1, 10, 20, 1))
    image_batch = tf.keras.applications.mobilenet.preprocess_input(image_batch)

    return np.argmax( model.predict(image_batch)[0] )

cap = cv2.VideoCapture(0)
scale = 0.5
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))    # 取得影像寬度
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 取得影像高度
fourcc = cv2.VideoWriter_fourcc(*'MJPG')          # 設定影片的格式為 MJPG
out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (width,  height))  # 產生空的影片

while(True):
    c = time.time()

    # Capture frame-by-frame
    ret, frame = cap.read()

    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    out.write(frame)       # 將取得的每一幀圖像寫入空的影片

    original_height, original_width = image.shape[:2]

    resized_image = cv2.resize(image,  (0, 0), fx=scale, fy=scale)
    lab = cv2.cvtColor(resized_image, cv2.COLOR_BGR2LAB)

    l, _, _ = cv2.split(lab)

    resized_height, resized_width = l.shape[:2]
    height_ratio, width_ratio = original_height / resized_height, original_width / resized_width

    face_locations = face_recognition.face_locations(l, model='hog')

    if len(face_locations):
        top, right, bottom, left = face_locations[0]
        x1, y1, x2, y2 = left, top, right, bottom

        x1 = int(x1 * width_ratio)
        y1 = int(y1 * height_ratio)
        x2 = int(x2 * width_ratio)
        y2 = int(y2 * height_ratio)

        # draw face rectangle

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        shape = predictor(gray, dlib.rectangle(x1, y1, x2, y2))
        
        face_landmarks = face_utils.shape_to_np(shape)

        left_eye_indices = face_landmarks[FacialLandMarksPosition.left_eye_start_index:
                                          FacialLandMarksPosition.left_eye_end_index]

        (x, y, w, h) = cv2.boundingRect(np.array([left_eye_indices]))
        left_eye = gray[y:y + h, x:x + w]

        right_eye_indices = face_landmarks[FacialLandMarksPosition.right_eye_start_index:
                                           FacialLandMarksPosition.right_eye_end_index]

        (x, y, w, h) = cv2.boundingRect(np.array([right_eye_indices]))
        right_eye = gray[y:y + h, x:x + w]

        left_eye_open = 'yes' if predict_eye_state(model=model, image=left_eye) else 'no'   
        right_eye_open = 'yes' if predict_eye_state(model=model, image=right_eye) else 'no'   

        print('left eye open: {0}    right eye open: {1}'.format(left_eye_open, right_eye_open))

        if left_eye_open == 'yes' and right_eye_open == 'yes':
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            # com.write('Y'.encode())
            com.write(b'Y\n')
            close_eye_count = 0
            print('Y')
        else:
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            close_eye_count += 1
            if close_eye_count % args.eyeclosednum == 0:
                # com.write('N'.encode())
                com.write(b'N\n')
                print('N')
            if close_eye_count % (args.eyeclosednum // 2) == 0:
                com.write(b'V\n')
                print('V')

        cv2.imshow('right_eye', right_eye)
        cv2.imshow('left_eye', left_eye)
       
    cv2.imshow('frame', cv2.flip(frame, 1))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()