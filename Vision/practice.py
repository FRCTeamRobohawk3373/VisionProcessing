import cv2

cam = cv2.VideoCapture(1)

while(True):
    _, processImg = cam.read()
    blur = cv2.medianBlur(processImg, 5)
    gray = cv2.cvtColor(blur, cv2.COLOR_BGR2GRAY)

    dark = cv2.inRange(gray, 0, 63)
    medium = cv2.inRange(gray, 64, 127)
    light = cv2.inRange(gray, 128, 191)
    bright = cv2.inRange(gray, 192, 255)

    darkCon, hierarchy = cv2.findContours(dark, mode=cv2.RETR_EXTERNAL,
                                          method=cv2.CHAIN_APPROX_SIMPLE)
    medCon, hierarchy = cv2.findContours(medium, mode=cv2.RETR_EXTERNAL,
                                         method=cv2.CHAIN_APPROX_SIMPLE)
    lightCon, hierarchy = cv2.findContours(light, mode=cv2.RETR_EXTERNAL,
                                           method=cv2.CHAIN_APPROX_SIMPLE)
    brightCon, hierarchy = cv2.findContours(bright, mode=cv2.RETR_EXTERNAL,
                                            method=cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawContours(processImg, darkCon, -1, (0, 0, 0))
    cv2.drawContours(processImg, medCon, -1, (0, 255, 0))
    cv2.drawContours(processImg, lightCon, -1, (0, 255, 255))
    cv2.drawContours(processImg, brightCon, -1, (0, 0, 255))

    cv2.imshow('image', processImg)
    cv2.imshow('preproc', gray)
    cv2.imshow('light', light)
    cv2.imshow('dark', dark)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
