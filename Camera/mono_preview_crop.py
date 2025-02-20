# crude crop, surely can be improved.
# run the code, left mouse to select top left start python3
# move to desired ROI, release to terminate the selection
# press c to crop, image will be saved to cropped_image.png
# the left image is used, can be changed.

import cv2
import depthai as dai

# for mouse interaction
roi_points = []
drawing = False
cropping = False
start_x, start_y = -1, -1
frame = None
left_frame = None

def mouse_callback(event, x, y, flags, param):
    global roi_points, cropping,drawing,frame,left_frame

    if event == cv2.EVENT_LBUTTONDOWN:
        roi_points = [(x, y)]
        start_x, start_y = x,y
        drawing = True
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            frame = left_frame.copy() # important: use a fresh copy each mouse move.
            cv2.rectangle(frame, roi_points[0], (x, y), (0, 255, 0), 2)
            cv2.imshow("Mono Camera", frame)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        cropping = True
        roi_points.append((x, y))
        cv2.rectangle(frame, roi_points[0], roi_points[1], (0, 255, 0), 2)
        cv2.imshow("Mono Camera", frame)

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
mono_left = pipeline.create(dai.node.MonoCamera)
mono_right = pipeline.create(dai.node.MonoCamera)
xout_left = pipeline.create(dai.node.XLinkOut)
xout_right = pipeline.create(dai.node.XLinkOut)

xout_left.setStreamName("left")
xout_right.setStreamName("right")

# Properties
mono_left.setCamera("left")
mono_left.setResolution(dai.MonoCameraProperties.SensorResolution.THE_480_P) # Or other resolutions
mono_right.setCamera("right")
mono_right.setResolution(dai.MonoCameraProperties.SensorResolution.THE_480_P)

# Linking
mono_left.out.link(xout_left.input)
mono_right.out.link(xout_right.input)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:
    left_queue = device.getOutputQueue(name="left", maxSize=4, blocking=False)
    right_queue = device.getOutputQueue(name="right", maxSize=4, blocking=False)

    cv2.namedWindow("Mono Camera", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Mono Camera", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN);
    cv2.setMouseCallback("Mono Camera", mouse_callback)

    while True:
        left_frame = left_queue.get().getCvFrame()
        right_frame = right_queue.get().getCvFrame()

        # Display the left frame (you can choose right or both)
        frame = left_frame.copy() # Make a copy to avoid modifying the original

        if not drawing and not cropping:
            cv2.imshow("Mono Camera", left_frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('c') and len(roi_points) == 2: # 'c' to crop
            x1, y1 = roi_points[0]
            x2, y2 = roi_points[1]
            cropped_image = left_frame[min(y1,y2):max(y1,y2), min(x1,x2):max(x1,x2)]
            cv2.imshow("Cropped Image", cropped_image)
            cv2.imwrite('cropped_image.png',cropped_image)

        elif key == ord('r'): # 'r' to reset ROI
            roi_points = []
            cv2.imshow("Mono Camera", left_frame) # Refresh the original frame

    cv2.destroyAllWindows()
