print('Setting UP')
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import cv2
import numpy as np
from utlis import *
import sudukoSolver


pathImage="Resources/1.jpg"
heightImg=450
widthImg=450
model= intializePredectionModel()


# 1. PREPARE THE IMAGE
img=cv2.imread(pathImage)
img=cv2.resize(img, (widthImg, heightImg))
imgBlank=np.zeros((heightImg, widthImg, 3), np.uint8)
imgThreshold=preProcess(img)

# 2. FINDING ALL CONTOUR
imgContours= img.copy()
imgBigContour= img.copy()
contours, hierarchy= cv2.findContours(imgThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 3)


# 3. FIND THE BIGGEST CONTOUR
biggest, maxArea=biggestContour(contours)
if biggest.size !=0:
    biggest=reorder(biggest)
    cv2.drawContours(imgBigContour, biggest, -1, (0, 0, 255), 25)
    pts1=np.float32(biggest)
    pts2=np.float32([[0,0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
    matrix=cv2.getPerspectiveTransform(pts1, pts2)
    imgWarpColored= cv2.warpPerspective(img, matrix, (widthImg, heightImg))
    imgDetectedDigits= imgBlank.copy()
    imgWarpColored=cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)


# 4.  SPLIT THE IMAGE AND FIND EACH DIGIT AVAILABLE
    imgSolvedDigits=imgBlank.copy()
    boxes=splitBoxes(imgWarpColored)
    print(len(boxes))
    # cv2.imshow("Sample",boxes[1])
    numbers=getPrediction(boxes, model)
    # print(numbers)
    imgDetectedDigits = displayNumbers(imgDetectedDigits, numbers, color=(255, 0, 255))
    numbers = np.asarray(numbers)
    posArray = np.where(numbers > 0, 0, 1)
    print(posArray)

    board = np.array_split(numbers, 9)
    print(board)
    try:
        sudukoSolver.solve(board)
    except:
        pass
    print(board)
    flatList = []
    for sublist in board:
        for item in sublist:
            flatList.append(item)
    solvedNumbers = flatList * posArray
    imgSolvedDigits = displayNumbers(imgSolvedDigits, solvedNumbers)



    pts2 = np.float32(biggest)  # PREPARE POINTS FOR WARP
    pts1 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])  # PREPARE POINTS FOR WARP
    matrix = cv2.getPerspectiveTransform(pts1, pts2)  # GER
    imgInvWarpColored = img.copy()
    imgInvWarpColored = cv2.warpPerspective(imgSolvedDigits, matrix, (widthImg, heightImg))
    inv_perspective = cv2.addWeighted(imgInvWarpColored, 1, img, 0.5, 1)
    imgDetectedDigits = drawGrid(imgDetectedDigits)
    imgSolvedDigits = drawGrid(imgSolvedDigits)



    imageArray=([img,imgThreshold,imgInvWarpColored],
                [imgWarpColored,imgSolvedDigits,inv_perspective])
    stackedImage=stackImages(imageArray, 1)
    cv2.imshow('Stacked Images', stackedImage)
else:
    print("no suduko found")
cv2.waitKey(0)


# import cv2
# import numpy as np
# import threading
# from utlis import *
# import sudukoSolver
#
# # Initialize Camera
# heightImg = 450
# widthImg = 450
# model = intializePredectionModel()  # Load trained digit recognition model
#
# cap = cv2.VideoCapture(0)  # Capture from webcam
# cap.set(3, 640)  # Set width
# cap.set(4, 480)  # Set height
# cap.set(10, 150)  # Set brightness
#
# frame_count = 0
# solved_board = None
# posArray = None
# show_digits = False  # Flag to display detected numbers
#
#
# def processSudoku(imgWarpColored):
#     """Runs Sudoku detection and solving in a separate thread to avoid lag."""
#     global solved_board, posArray, show_digits
#
#     imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
#     boxes = splitBoxes(imgWarpGray)
#     numbers = getPrediction(boxes, model)
#     numbers = np.asarray(numbers)
#     posArray = np.where(numbers > 0, 0, 1)  # Find empty positions
#
#     board = np.array_split(numbers, 9)  # Convert to 9x9 Sudoku grid
#     solved_board = board.copy()  # Copy for solving
#
#     try:
#         if sudukoSolver.solve(solved_board):
#             show_digits = True  # Enable number display only if solved
#     except:
#         solved_board = None
#         show_digits = False
#
#
# while True:
#     success, img = cap.read()
#     if not success:
#         continue
#
#     img = cv2.resize(img, (widthImg, heightImg))
#     imgThreshold = preProcess(img)  # Apply edge detection + thresholding
#
#     contours, _ = cv2.findContours(imgThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     biggest, maxArea = biggestContour(contours)
#
#     if biggest.size != 0:
#         biggest = reorder(biggest)  # Reorder points for perspective transform
#         pts1 = np.float32(biggest)
#         pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
#         matrix = cv2.getPerspectiveTransform(pts1, pts2)
#         imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))
#
#         if frame_count % 15 == 0:  # Run Sudoku solver every 15 frames (~0.5 sec)
#             threading.Thread(target=processSudoku, args=(imgWarpColored,)).start()
#
#         if show_digits and solved_board is not None:
#             flatList = [item for sublist in solved_board for item in sublist]
#             solvedNumbers = flatList * posArray  # Only display solved numbers
#             imgSolvedDigits = displayNumbers(np.zeros((heightImg, widthImg, 3), np.uint8), solvedNumbers)
#
#             # Warp solved numbers back onto original image
#             matrix = cv2.getPerspectiveTransform(pts2, pts1)
#             imgInvWarpColored = cv2.warpPerspective(imgSolvedDigits, matrix, (widthImg, heightImg))
#             imgFinal = cv2.addWeighted(img, 0.7, imgInvWarpColored, 1, 0)
#         else:
#             imgFinal = img.copy()
#     else:
#         imgFinal = img.copy()
#
#     cv2.imshow("Sudoku Solver Live", imgFinal)  # Show real-time Sudoku feed
#     frame_count += 1
#
#     if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
#         break
#
# cap.release()
# cv2.destroyAllWindows()
