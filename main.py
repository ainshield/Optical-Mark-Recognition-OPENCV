import cv2
import numpy as np
from flask import Flask, url_for, render_template, Response, request
import utils
import db

#GLOBAL VARIABLES##########
app = Flask(__name__)
heightImg = 1280//2
widthImg  = 720//2

#change question count according to test paper
questions=50
choices=5
imgpath = 'img1.jpg'
# ans = [1,2,0,2,4]
count=0
webcamFeed = False

###########################

@app.route('/', methods = ['GET','POST'])
def index():

    uniqueCode = [(request.form.get('code'))]
    global ans
    ans = db.sqlquery(uniqueCode)
    try:
        ans = ans.split(",")
        ans = [int(i) for i in ans]
    except:
        pass
    
    return render_template('index.html')

def omr_processing():
##Video Capture
    cap = cv2.VideoCapture(0)
    cap.set(10,150)
    
    while True: 
        if webcamFeed:success, frame = cap.read()
        else:frame = cv2.imread(imgpath)

##OMR PROCESSING##
##processed_frame gets outputted to video_feed
##frame gets outputted to index.html
    
    
        frame = cv2.resize(frame, (widthImg, heightImg))
        imgFinal = frame.copy()
        imgContours = frame.copy()
        imgBiggestContours = frame.copy()

        ###PREPROCESSING
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 1)
        canny = cv2.Canny(blur, 10, 50)

        try:
            #FIND CONTOURS
            contours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)

            #FIND RECTANGLES
            rectCon = utils.rectContour(contours)
            biggestContour = utils.getCornerPoints(rectCon[0])
            # print(biggestContour)
            gradePoints = utils.getCornerPoints(rectCon[1])
            # print(gradePoints)

            if biggestContour.size != 0 and gradePoints.size != 0:
                
                cv2.drawContours(imgBiggestContours, biggestContour, -1, (0, 255, 0), 20)
                cv2.drawContours(imgBiggestContours, gradePoints, -1, (255, 0, 0), 20)
                
                biggestContour = utils.reorder(biggestContour)
                gradePoints = utils.reorder(gradePoints)

                pt1 = np.float32(biggestContour)
                pt2 = np.float32([[0,0],[widthImg,0],[0,heightImg],[widthImg,heightImg]])
                matrix = cv2.getPerspectiveTransform(pt1,pt2)
                imgWarpColored = cv2.warpPerspective(frame,matrix,(widthImg,heightImg))
                
                #fix suggestion: tweak matrixG to adjust to test paper size
                ptG1 = np.float32(gradePoints)
                ptG2 = np.float32([[0,0],[325,0],[0,150],[325,150]])
                matrixG = cv2.getPerspectiveTransform(ptG1,ptG2)
                imgGradeDisplay = cv2.warpPerspective(frame,matrixG,(325,150))

                #APPLY THRESHOLD
                imgWarpGray = cv2.cvtColor(imgWarpColored,cv2.COLOR_BGR2GRAY)
                imgThresh = cv2.threshold(imgWarpGray, 170, 255, cv2.THRESH_BINARY_INV)[1]

                boxes = utils.splitBoxes(imgThresh)
                
                #GETTING NON ZERO PIXEL VALUES OF EACH BOX
                myPixelVal = np.zeros((questions,choices))
                countC = 0
                countR = 0

                for image in boxes:
                    totalPixels = cv2.countNonZero(image)
                    myPixelVal [countR][countC] = totalPixels
                    countC += 1
                    if (countC == choices): countR += 1; countC = 0
                # print(myPixelVal)

                #FINDING INDEX VALUES OF THE MARKINGS
                myIndex = []
                for x in range (0,questions):
                    arr = myPixelVal[x]
                    myIndexVal = np.where(arr == np.amax(arr))
                    myIndex.append(myIndexVal[0][0])
                # print(myIndex)

                #GETTING CORRECT ANSWER
                grading = []
                for x in range (0, questions):
                    if ans[x] == myIndex[x]:
                        grading.append(1)
                    else:
                        grading.append(0)
                    # print(grading)

                #FINAL GRADE
                score = sum(grading)/questions * 100 
                # print(score)

                #DISPLAYING ANSWERS
                imgResult = imgWarpColored.copy()
                imgResult = utils.showAnswers(imgResult, myIndex, grading, ans, questions, choices)
                imgRawDrawing = np.zeros_like(imgWarpColored)
                imgResult = utils.showAnswers(imgRawDrawing, myIndex, grading, ans, questions, choices)
                invMatrix = cv2.getPerspectiveTransform(pt2,pt1)
                imgInvWarp = cv2.warpPerspective(imgRawDrawing,invMatrix,(widthImg,heightImg))
                
                imgRawGrade = np.zeros_like(imgGradeDisplay)
                cv2.putText(imgRawGrade, str(int(score)) + "%", (60, 100), cv2.FONT_HERSHEY_COMPLEX, 3, (0, 255, 255), 3)
                invMatrixG = cv2.getPerspectiveTransform(ptG2,ptG1)
                imgInvGradeDisplay = cv2.warpPerspective(imgRawGrade,invMatrixG,(widthImg,heightImg))

                imgFinal = cv2.addWeighted(imgFinal,1,imgInvWarp,1,0)
                imgFinal = cv2.addWeighted(imgFinal,1,imgInvGradeDisplay,1,0)
        
        except:
            pass

        ###CONVERT FRAMES TO BYTES
        ret,buffer = cv2.imencode('.jpg', imgFinal)
        frame = buffer.tobytes()

        ###VIDEO FEED
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(omr_processing(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)


