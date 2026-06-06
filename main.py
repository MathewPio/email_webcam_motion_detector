# import cv2
# import time
# from emailing import send_email
# import glob
# import os
# from threading import Thread

# video = cv2.VideoCapture(0)
# time.sleep(1)

# first_frame = None
# status_list = []
# count = 1

# def clean_folder():
#     print("clean folder func started")
#     images = glob.glob("images/*.png")
#     for image in images:
#         os.remove(image)
#     print("folder func completed")

# while True:
#     status = 0
#     check, frame = video.read()
#     gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)
    
#     if first_frame is None:
#         first_frame = gray_frame_gau
        
#     delta_frame = cv2.absdiff(first_frame, gray_frame_gau)
    
#     thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
#     dil_frame = cv2.dilate(thresh_frame, None, iterations=2)
#     cv2.imshow("My Video", dil_frame)
    
#     contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
#     for contour in contours:
#         if cv2.contourArea(contour) < 5000:
#             continue
#         x, y, w, h = cv2.boundingRect(contour)
#         rectangle = cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255, 0), 3)
#         if rectangle.any():
#             status = 1
#             cv2.imwrite(f"images/{count}.png", frame)
#             count = count + 1
            
#             all_images = glob.glob("images/*.png")
            
#             index = int(len(all_images) / 2)
            
#             image_with_object = all_images[index]
            
            
        
            
#     status_list.append(status)
#     status_list = status_list[-2:]
    
#     if status_list[0] == 1 and status_list[1] == 0:
#         if image_with_object:
#             email_thread = Thread(target=send_email, args=(image_with_object, )) 
#             email_thread.daemon = True
#             email_thread.start()
    
#         clean_thread = Thread(target=clean_folder)
#         clean_thread.daemon = True      
#         clean_thread.start() 
         
        
#     print(status_list)
    
#     cv2.imshow("video", frame)
#     key = cv2.waitKey(1)
    
#     if key == ord("q"):
#         break
    
# video.release()


import cv2
import time
import glob
import os
from threading import Thread
from emailing import send_email

# ---------------- SETUP ----------------
video = cv2.VideoCapture(0)
time.sleep(1)

first_frame = None
status_list = [0, 0]
count = 1

image_with_object = None


# ---------------- CLEAN FOLDER ----------------
def clean_folder():
    print("clean folder func started")

    # wait so files are fully released (VERY IMPORTANT on Windows)
    time.sleep(3)

    images = glob.glob("images/*.png")

    for image in images:
        try:
            os.remove(image)
        except PermissionError:
            print(f"Skipping locked file: {image}")

    print("folder func completed")


# ---------------- MAIN LOOP ----------------
while True:
    status = 0

    check, frame = video.read()
    if not check:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # set first frame
    if first_frame is None:
        first_frame = gray
        continue

    # motion detection
    delta_frame = cv2.absdiff(first_frame, gray)
    thresh = cv2.threshold(delta_frame, 25, 255, cv2.THRESH_BINARY)[1]
    dilated = cv2.dilate(thresh, None, iterations=2)

    cv2.imshow("Motion", dilated)

    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 2000:
            continue

        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        status = 1

        # save image
        os.makedirs("images", exist_ok=True)
        cv2.imwrite(f"images/{count}.png", frame)
        count += 1

        # pick middle image safely
        all_images = glob.glob("images/*.png")
        if all_images:
            image_with_object = all_images[len(all_images) // 2]

    # ---------------- STATUS TRACKING ----------------
    status_list.append(status)
    status_list = status_list[-2:]

    # ---------------- MOTION START EVENT ----------------
    if status_list[0] == 1 and status_list[1] == 0:

        print("Motion detected!")

        # send email safely
        if image_with_object:
            email_thread = Thread(target=send_email, args=(image_with_object,))
            email_thread.daemon = True
            email_thread.start()

        # cleanup AFTER delay (prevents WinError 32)
        clean_thread = Thread(target=clean_folder)
        clean_thread.daemon = True
        clean_thread.start()

    # ---------------- DISPLAY ----------------
    cv2.imshow("Video", frame)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break


# ---------------- EXIT CLEANLY ----------------
video.release()
cv2.destroyAllWindows()