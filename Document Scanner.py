import cv2
import numpy as np
 
###################################
widthImg=540
heightImg =640
#####################################
 
cap = cv2.VideoCapture(1)
cap.set(10,150)
 
def preProcessing(img):
    imgGray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray,(5,5),1)
    imgCanny = cv2.Canny(imgBlur,200,200)
    kernel = np.ones((5,5))
    imgDial = cv2.dilate(imgCanny,kernel,iterations=2)
    imgThres = cv2.erode(imgDial,kernel,iterations=1)
    return imgThres
 
def getContours(img):
    biggest = np.array(&#91;])
    maxArea = 0
    contours,hierarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area>5000:
            #cv2.drawContours(imgContour, cnt, -1, (255, 0, 0), 3)
            peri = cv2.arcLength(cnt,True)
            approx = cv2.approxPolyDP(cnt,0.02*peri,True)
            if area >maxArea and len(approx) == 4:
                biggest = approx
                maxArea = area
    cv2.drawContours(imgContour, biggest, -1, (255, 0, 0), 20)
    return biggest
 
def reorder (myPoints):
    myPoints = myPoints.reshape((4,2))
    myPointsNew = np.zeros((4,1,2),np.int32)
    add = myPoints.sum(1)
    #print("add", add)
    myPointsNew&#91;0] = myPoints&#91;np.argmin(add)]
    myPointsNew&#91;3] = myPoints&#91;np.argmax(add)]
    diff = np.diff(myPoints,axis=1)
    myPointsNew&#91;1]= myPoints&#91;np.argmin(diff)]
    myPointsNew&#91;2] = myPoints&#91;np.argmax(diff)]
    #print("NewPoints",myPointsNew)
    return myPointsNew
 
def getWarp(img,biggest):
    biggest = reorder(biggest)
    pts1 = np.float32(biggest)
    pts2 = np.float32(&#91;&#91;0, 0], &#91;widthImg, 0], &#91;0, heightImg], &#91;widthImg, heightImg]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgOutput = cv2.warpPerspective(img, matrix, (widthImg, heightImg))
 
    imgCropped = imgOutput&#91;20:imgOutput.shape&#91;0]-20,20:imgOutput.shape&#91;1]-20]
    imgCropped = cv2.resize(imgCropped,(widthImg,heightImg))
 
    return imgCropped
 
 
def stackImages(scale,imgArray):
    rows = len(imgArray)
    cols = len(imgArray&#91;0])
    rowsAvailable = isinstance(imgArray&#91;0], list)
    width = imgArray&#91;0]&#91;0].shape&#91;1]
    height = imgArray&#91;0]&#91;0].shape&#91;0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray&#91;x]&#91;y].shape&#91;:2] == imgArray&#91;0]&#91;0].shape &#91;:2]:
                    imgArray&#91;x]&#91;y] = cv2.resize(imgArray&#91;x]&#91;y], (0, 0), None, scale, scale)
                else:
                    imgArray&#91;x]&#91;y] = cv2.resize(imgArray&#91;x]&#91;y], (imgArray&#91;0]&#91;0].shape&#91;1], imgArray&#91;0]&#91;0].shape&#91;0]), None, scale, scale)
                if len(imgArray&#91;x]&#91;y].shape) == 2: imgArray&#91;x]&#91;y]= cv2.cvtColor( imgArray&#91;x]&#91;y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = &#91;imageBlank]*rows
        hor_con = &#91;imageBlank]*rows
        for x in range(0, rows):
            hor&#91;x] = np.hstack(imgArray&#91;x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray&#91;x].shape&#91;:2] == imgArray&#91;0].shape&#91;:2]:
                imgArray&#91;x] = cv2.resize(imgArray&#91;x], (0, 0), None, scale, scale)
            else:
                imgArray&#91;x] = cv2.resize(imgArray&#91;x], (imgArray&#91;0].shape&#91;1], imgArray&#91;0].shape&#91;0]), None,scale, scale)
            if len(imgArray&#91;x].shape) == 2: imgArray&#91;x] = cv2.cvtColor(imgArray&#91;x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver
 
while True:
    success, img = cap.read()
    img = cv2.resize(img,(widthImg,heightImg))
    imgContour = img.copy()
 
    imgThres = preProcessing(img)
    biggest = getContours(imgThres)
    if biggest.size !=0:
        imgWarped=getWarp(img,biggest)
        # imageArray = (&#91;img,imgThres],
        #           &#91;imgContour,imgWarped])
        imageArray = (&#91;imgContour, imgWarped])
        cv2.imshow("ImageWarped", imgWarped)
    else:
        # imageArray = (&#91;img, imgThres],
        #               &#91;img, img])
        imageArray = (&#91;imgContour, img])
 
    stackedImages = stackImages(0.6,imageArray)
    cv2.imshow("WorkFlow", stackedImages)
 
    if cv2.waitKey(1) and 0xFF == ord('q'):
        break