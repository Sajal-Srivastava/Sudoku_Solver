import cv2
import numpy as np
from tensorflow.keras.models import load_model


# 1. Preprocessing Image
def preProcess(img):
    imgGray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur=cv2.GaussianBlur(imgGray, (5,5), 1)
    imgThreshold=cv2.adaptiveThreshold(imgBlur, 255, 1,1,11,2)
    return imgThreshold


def biggestContour(contours):
    biggest=np.array([])
    max_area=0
    for i in contours:
        area=cv2.contourArea(i)
        if area>50:
            peri=cv2.arcLength(i, True)
            approx=cv2.approxPolyDP(i, 0.02*peri, True)
            if area>max_area and len(approx)==4:
                biggest=approx
                max_area=area
    return biggest, max_area

def reorder(myPoints):
    myPoints=myPoints.reshape((4,2))
    myPointsNew= np.zeros((4, 1, 2), dtype=np.int32)
    add=myPoints.sum(1)
    myPointsNew[0]=myPoints[np.argmin(add)]
    myPointsNew[3]=myPoints[np.argmax(add)]
    diff=np.diff(myPoints, axis=1)
    myPointsNew[1]= myPoints[np.argmin(diff)]
    myPointsNew[2] = myPoints[np.argmax(diff)]
    return myPointsNew

# TO SPLIT IN 81 DIFFERENT IMAGES
def splitBoxes(img):
    rows=np.vsplit(img, 9)
    boxes=[]
    for r in rows:
        cols=np.hsplit(r,9)
        for box in cols:
            boxes.append(box)
    return boxes


def intializePredectionModel():
    model=load_model('Resources/model_trained_OCR.keras')
    return model


def getPrediction(boxes, model):
    result = []
    for image in boxes:
        ## PREPROCESS IMAGE
        img = np.asarray(image)
        img = cv2.resize(img, (32, 32))  # Resize to (32x32)

        # Convert to Grayscale (1 channel) if needed
        if len(img.shape) == 3:  # If image is in RGB format
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        img = img / 255.0  # Normalize
        img = img.reshape(1, 32, 32, 1)  # Reshape for model (1 channel)

        ## GET PREDICTION
        predictions = model.predict(img)
        classIndex = np.argmax(predictions, axis=-1)  # Get highest probability class
        probabilityValue = np.amax(predictions)  # Confidence score
        print(classIndex, probabilityValue)

        ## SAVE RESULT
        if probabilityValue > 0.8:
            result.append(classIndex[0])  # Append predicted digit
        else:
            result.append(0)  # If confidence is low, return 0 (empty cell)

    return result


def displayNumbers(img,numbers,color = (0,255,0)):
    secW = int(img.shape[1]/9)
    secH = int(img.shape[0]/9)
    for x in range (0,9):
        for y in range (0,9):
            if numbers[(y*9)+x] != 0 :
                 cv2.putText(img, str(numbers[(y*9)+x]),
                               (x*secW+int(secW/2)-10, int((y+0.8)*secH)), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                            2, color, 2, cv2.LINE_AA)
    return img


def drawGrid(img):
    secW = int(img.shape[1]/9)
    secH = int(img.shape[0]/9)
    for i in range (0,9):
        pt1 = (0,secH*i)
        pt2 = (img.shape[1],secH*i)
        pt3 = (secW * i, 0)
        pt4 = (secW*i,img.shape[0])
        cv2.line(img, pt1, pt2, (255, 255, 0),2)
        cv2.line(img, pt3, pt4, (255, 255, 0),2)
    return img


def stackImages(imgArray, scale):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]

    if rowsAvailable:
        for x in range(rows):
            for y in range(cols):
                imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                if len(imgArray[x][y].shape) == 2:  # If grayscale, convert to 3-channel
                    imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)

        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank] * rows

        for x in range(rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(rows):
            imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            if len(imgArray[x].shape) == 2:
                imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)

        ver = np.hstack(imgArray)

    return ver



