import cv2
import numpy as np

def rectContour(contours):

    rectCon = []
    for i in contours:
        area = cv2.contourArea(i)
        # print(area)
        if area > 50:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            if len(approx)==4:
                rectCon.append(i)

    rectCon = sorted(rectCon, key = cv2.contourArea, reverse = True)

    return rectCon


def getCornerPoints(cont):
    peri = cv2.arcLength(cont, True)
    approx = cv2.approxPolyDP(cont, 0.02 * peri, True)
    return approx

def reorder(myPoints):
    myPoints = myPoints.reshape((4,2))
    myPointsNew = np.zeros((4,1,2), np.int32)
    add = myPoints.sum(1)
    # print(add)
    myPointsNew[0] = myPoints[np.argmin(add)]
    myPointsNew[3] = myPoints[np.argmax(add)]
    diff = np.diff(myPoints,axis=1)
    myPointsNew[1] = myPoints[np.argmin(diff)]
    myPointsNew[2] = myPoints[np.argmax(diff)]
    # print(diff)

    return myPointsNew

#adjust the number of vsplit to change the number of questions of the exam 
def splitBoxes(img,questions,choices):
    rows = np.vsplit(img, questions)
    boxes = []
    for r in rows:
        cols = np.hsplit(r, choices)
        for box in cols:
            boxes.append(box)
    return boxes

def showAnswers(img, myIndex, grading, ans, questions, choices):
    secW = int(img.shape[1]/questions)
    secH = int(img.shape[0]/choices)
    # print(myIndex, grading, ans, questions, choices)
    print((int(img.shape[1])),(int(img.shape[0])))

    for x in range (0, questions):
        myAns = myIndex[x]
        cX = (myAns*secW) + secW//2
        cY = (x*secH) + secH//2
        
        if grading[x] == 1:
            myColor = (0,255,0)
        else:
            myColor = (0,0,255)
            correctAns = ans[x]
            cv2.circle(img, ((correctAns * secW) + secW//2 , (x*secH) + secH // 2) , 20 , (0,255,0) ,cv2.FILLED)

        cv2.circle(img,(cX,cY),50,myColor,cv2.FILLED)

    return img
