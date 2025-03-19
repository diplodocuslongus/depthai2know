# notes:
# cv2.stereoCalibrate and cv2.stereoCalibrateExtended both perform stereo camera calib
# stereoCalibrateExtended offers more flexibility by allowing to specify the intrinsic param
# of the camera.
# stereoCalibrate estimates them
# capture images with the image_capture_for_calib code (images have to be capture at the same time)
# some settings:
# - folder where calibration images have been saved
# - pattern of the saved images (ex: oak_CAMB* , oak_CAMC*, etc...)
# - specs of the pattern (inner number of corners, row and columns)
# - set the reference camera (left for left-right (horizontal)  rig or top for vertical rig)
# - whether or not to perform the calibration and save the calibration matrices and distortion coefficients to a file, or to read the later from a file (must obviously have first performed calibration and saved results to file)

import cv2 as cv
import glob
import numpy as np
 
# calib_cam_flag = False # read from file
calib_cam_flag = True # do calibration from images and save calib results to files
reference_cam = 'CAMB' # chose which camera is top or left
if reference_cam == 'CAMB':
    secondary_cam = 'CAMC'
elif reference_cam == 'CAMC':
    secondary_cam = 'CAMB'

# read and save calibration results
# cameras matrices and distortion coefficients 
def save_cam_matx_distcoef(cam_matx,cam_distcoef,filename):
    cv_file = cv.FileStorage(filename, cv.FileStorage_WRITE)
    cv_file.write('cameraMatrix',cam_matx)
    cv_file.write('dist_coeffs',cam_distcoef)
    cv_file.release()

def save_cam_imagepoints(imagepoints,filename):
    '''
    iamgepoints is a list of 2D pixel coordinates
    '''
    cv_file = cv.FileStorage(filename, cv.FileStorage_WRITE)
    nbpts = len(imagepoints)
    cv_file.write('cameraImagePoints','')
    cv_file.write('nbPoses',nbpts)
    for i in range(nbpts):
        cv_file.write(f'pointsPose{i:02d}',imagepoints[i])
    cv_file.release()

def save_calibtarget_objpoints(objectpoints,filename):
    cv_file = cv.FileStorage(filename, cv.FileStorage_WRITE)
    nbpts = len(objectpoints)
    cv_file.write('calibTargetObjPoints','')
    cv_file.write('nbPoses',nbpts)
    for i in range(nbpts):
        cv_file.write(f'objectPointsPose{i:02d}',objectpoints[i])
    cv_file.release()

def read_cam_imagepoints(filename):
    cv_file = cv.FileStorage(filename, cv.FileStorage_READ)
    n = cv_file.getNode('nbPoses')
    nbpts = int(n.real())
    imgpts = []
    for i in range(nbpts):
        impt = cv_file.getNode(f'pointsPose{i:02d}').mat()
        imgpts.append(impt)
    cv_file.release()
    return imgpts

def read_calibtarget_objpoints(filename):
    cv_file = cv.FileStorage(filename, cv.FileStorage_READ)
    n = cv_file.getNode('nbPoses')
    nbpts = int(n.real())
    objpts = []
    for i in range(nbpts):
        obpt = cv_file.getNode(f'objectPointsPose{i:02d}').mat()
        objpts.append(obpt)
    cv_file.release()
    return objpts

def read_cam_matx_distcoef(filename):
    cv_file = cv.FileStorage(filename, cv.FileStorage_READ)
    matx = cv_file.getNode('cameraMatrix').mat()
    distcoef = cv_file.getNode('dist_coeffs').mat()
    cv_file.release()
    return matx,distcoef

def read_cam2cam_R_T(filename):
    cv_file = cv.FileStorage(filename, cv.FileStorage_READ)
    rot_matx = cv_file.getNode('rotationMatrix_cam1_to_cam2').mat()
    tr_matx = cv_file.getNode('translationMatrix_cam1_to_cam2').mat()
    cv_file.release()
    return rot_matx,tr_matx

# camera 1 to camera 2 rotation and translation matrices (stereo config)
def save_cam2cam_R_T(rot_matx,tr_matx,filename):
    cv_file = cv.FileStorage(filename, cv.FileStorage_WRITE)
    cv_file.write('rotationMatrix_cam1_to_cam2',rot_matx)
    cv_file.write('translationMatrix_cam1_to_cam2',tr_matx)
    cv_file.release()
def calibrate_camera(images_folder):
    images_names = sorted(glob.glob(images_folder))
    images = []
    for imname in images_names:
        im = cv.imread(imname, 1)
        images.append(im)
 
    #criteria used by checkerboard pattern detector.
    #can be adapted if poor corner detection
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
 
    # checkerboard specs
    rows = 6 
    columns = 9 
    world_scaling = 3.5 # target pattern square size (cm)
 
    # target squares coordinates in world coordinates
    objp = np.zeros((rows*columns,3), np.float32)
    objp[:,:2] = np.mgrid[0:rows,0:columns].T.reshape(-1,2)
    objp = world_scaling* objp
 
    # Frames can be of different size! (TODO find again ref and add)
    width = images[0].shape[1]
    height = images[0].shape[0]
 
    # checkerboards pixel coordinates (2D) (basically the chessboard corners)
    imgpoints = [] 
    # coordinates of the checkerboard in checkerboard world space.
    objpoints = [] # 3d point in real world space
 
    # chessBoardFlags = cv.CALIB_CB_ADAPTIVE_THRESH | cv.CALIB_CB_NORMALIZE_IMAGE | cv.CALIB_CB_FAST_CHECK
    chessBoardFlags = None
    imgCnt = 0
    for frame in images:
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        ret, corners = cv.findChessboardCorners(gray, (rows, columns), chessBoardFlags)
        if ret == True:
            # can improve corner detection
            conv_size = (11, 11)
            corners = cv.cornerSubPix(gray, corners, conv_size, (-1, -1), criteria)
            cv.drawChessboardCorners(frame, (rows,columns), corners, ret)
            cv.imshow('img', frame)
            k = cv.waitKey(100)
            objpoints.append(np.squeeze(objp)) # corner returns an array of shape nrow x ncols , 1, 2, the 1 isn't needed here so squeeze the array to remove that dimension
            imgpoints.append(np.squeeze(corners))
            # objpoints.append(objp)
            # imgpoints.append(corners)
            # print(f'corners: {corners,np.squeeze(corners)}')
        else:
            print(f'\nNO CORNER FouND in IMAGE {imgCnt}\n')
            k = cv.waitKey(1000)
        imgCnt +=1

    # do the actual calibration
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, (width, height), None, None)
    print('rmse:', ret)
    print('camera matrix:\n', mtx)
    print('distortion coeffs:', dist)
    print('Rs:\n', rvecs)
    print('Ts:\n', tvecs)
 
    return mtx, dist,imgpoints,objpoints

def stereo_calibrate(mtx1, dist1, mtx2, dist2 ,imgpoints1,imgpoints2,objpoints):
    # fine tune if needed (for stereo calibration)
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 100, 0.0001)
 
    rows = 6 
    columns = 9 
 
    # i chose the dims of the oak
    width = 640 
    height = 400
 
    stereocalibration_flags = cv.CALIB_FIX_INTRINSIC
    ret, CM1, dist1, CM2, dist2, R, T, E, F = \
        cv.stereoCalibrate(objpoints, imgpoints1, imgpoints2, mtx1, dist1, \
        mtx2, dist2, (width, height), criteria = criteria, flags = stereocalibration_flags)
 
    print(ret)
    return R, T,ret
if calib_cam_flag: 
    if reference_cam == 'CAMB':
        # calibrate oak to tof (oak as "left" or top or reference)
        mtx1, dist1 ,imgpoints1,objpoints= calibrate_camera(images_folder = './calib_imgs/smalltarget/oak_CAMB*')
        mtx2, dist2 ,imgpoints2,objpoints= calibrate_camera(images_folder = './calib_imgs/smalltarget/oak_CAMC*')
    else:
        mtx1, dist1 ,imgpoints1,objpoints= calibrate_camera(images_folder = './calib_imgs/smalltarget/oak_CAMC*')
        mtx2, dist2 ,imgpoints2,objpoints= calibrate_camera(images_folder = './calib_imgs/smalltarget/oak_CAMB*')
    # print(imgpoints1,type(imgpoints1),len(imgpoints1),imgpoints1[0].shape) # ,imgpoints1.dtype)
    R, T,reproerror = stereo_calibrate(mtx1, dist1, mtx2, dist2,imgpoints1,imgpoints2,objpoints)
    print(f'R, T = {R,T}, reprojection error = {reproerror}')

    save_cam2cam_R_T(R,T,'cameraToCamera_RotTrans.xml')
    save_cam_matx_distcoef(mtx1,dist1,f'cameraParam_{reference_cam}.xml')
    save_cam_matx_distcoef(mtx2,dist2,f'cameraParam_{secondary_cam}.xml')
    save_cam_imagepoints(imgpoints1,f'cameraImgPoints_{reference_cam}.xml')
    save_cam_imagepoints(imgpoints2,f'cameraImgPoints_{secondary_cam}.xml')
    save_calibtarget_objpoints(objpoints,f'calibTargetObjectPoints.xml')
else:
    # read from file
    mtx1, dist1 = read_cam_matx_distcoef(f'cameraParam_{reference_cam}.xml')
    mtx2, dist2 = read_cam_matx_distcoef(f'cameraParam_{secondary_cam}.xml')
    imgpoints1= read_cam_imagepoints(f'cameraImgPoints_{reference_cam}.xml')
    imgpoints2= read_cam_imagepoints(f'cameraImgPoints_{secondary_cam}.xml')
    objpoints = read_calibtarget_objpoints(f'calibTargetObjectPoints.xml')
    R,T=read_cam2cam_R_T(f'cameraToCamera_RotTrans.xml')



# R, T,reproerror = stereo_calibrate(mtx1, dist1, mtx2, dist2,imgpoints1,imgpoints2,objpoints)
# print(f'R, T = {R,T}, reprojection error = {reproerror}')
#
# save_cam2cam_R_T(R,T,'cameraToCamera_RotTrans.xml')
    

def compute_mapxy(K1, D1, K2, D2, R, T,imsz,alpha = 0.8,flag_R = True,flag_rectify = None):
    """
    computes mapping mapx and mapy for stereo rig

    Args:
        K1, D1: Intrinsic matrix and distortion coefficients for camera 1.
        K2, D2: Intrinsic matrix and distortion coefficients for camera 2.
        R, T: Rotation and translation between the cameras.
        alpha: alpha parameter of opencv stereoRectify
        flag_R: use the physical rotation matrix (true, default) or the calculated R1 and R2
        flag_rectify: optionally make the camera centers coincide (default = None) with cv.CALIB_ZERO_DISPARITY 

    Returns:
        map1x,map1y,map2x,map2y
    """

    h, w,_ = imsz #image1.shape[:2]
    # print(f'in compute_mapxy: h,w = {h,w}')
    # rectify_flag = # makes the principal pt of both cameras to be = same coordinates in the recrified views
    R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv.stereoRectify(
        K1, D1, K2, D2, (w, h), R, T,
        alpha=alpha,
        flags=flag_rectify
    )
    print(f'validPixROI1 = {validPixROI1}, validPixROI2 = {validPixROI2}')
    print(f'R1 =\n{R1},\nR2 =\n{R2},\nP1 =\n{P1},\nP2 =\n{P2}')

    if flag_R:
        map1x, map1y = cv.initUndistortRectifyMap(K1, D1, R, P1, (w, h), cv.CV_32FC1)
        map2x, map2y = cv.initUndistortRectifyMap(K2, D2, R, P2, (w, h), cv.CV_32FC1)
    else:
        map1x, map1y = cv.initUndistortRectifyMap(K1, D1, R1, P1, (w, h), cv.CV_32FC1)
        map2x, map2y = cv.initUndistortRectifyMap(K2, D2, R2, P2, (w, h), cv.CV_32FC1)
    if P2[0,3] != 0:
        rig_config = 'H'
    elif P2[1,3] != 0:
        rig_config = 'V'
    else:
        rig_config = 'unknown'

    return map1x,map1y,map2x,map2y,rig_config

def rectify_images_precalc(image1, image2, map1x,map1y,map2x,map2y):
    """
    rectifies and aligns two images using stereo rectification.
    when mapxy are precalculated

    Args:
        image1: Left camera image.
        image2: Right camera image.

    Returns:
        Rectified images (image1_rect, image2_rect).
    """

    image1_rect = cv.remap(image1, map1x, map1y, cv.INTER_LINEAR)
    image2_rect = cv.remap(image2, map2x, map2y, cv.INTER_LINEAR)
    # image1_rect = cv.remap(image1, map2x, map2y, cv.INTER_LINEAR)
    # image2_rect = cv.remap(image2, map1x, map1y, cv.INTER_LINEAR)

    return image1_rect, image2_rect

def rectify_images(image1, image2, K1, D1, K2, D2, R, T):
    """
    Calculate mapping mapxy for each imeages and 
    rectifies and aligns two images using stereo rectification.

    Args:
        image1: Left camera image.
        image2: Right camera image.
        K1, D1: Intrinsic matrix and distortion coefficients for camera 1.
        K2, D2: Intrinsic matrix and distortion coefficients for camera 2.
        R, T: Rotation and translation between the cameras.

    Returns:
        Rectified images (image1_rect, image2_rect).
    """

    # h, w = image2.shape[:2]
    h, w = image1.shape[:2]
    rectify_flag = None
    # rectify_flag = cv.CALIB_ZERO_DISPARITY # makes the principal pt of both cameras to be = same coordinates in the recrified views
    R1, R2, P1, P2, Q, validPixROI1, validPixROI2 = cv.stereoRectify(
        K1, D1, K2, D2, (w, h), R, T,
        # alpha=1.
        # alpha=0.8
        alpha=0.8,
        flags=rectify_flag
    )
    print(f'validPixROI1 = {validPixROI1}, validPixROI2 = {validPixROI2}')
    print(f'R1 =\n{R1},\nR2 =\n{R2},\nP1 =\n{P1},\nP2 =\n{P2}')

    map1x, map1y = cv.initUndistortRectifyMap(K1, D1, R, P1, (w, h), cv.CV_32FC1)
    map2x, map2y = cv.initUndistortRectifyMap(K2, D2, R, P2, (w, h), cv.CV_32FC1)
    # map1x, map1y = cv.initUndistortRectifyMap(K1, D1, R1, P1, (w, h), cv.CV_32FC1)
    # map2x, map2y = cv.initUndistortRectifyMap(K2, D2, R2, P2, (w, h), cv.CV_32FC1)

    # print(f'map1x =\n{map1x},\nmap1y =\n{map1y}')
    # print(f'map2x =\n{map2x},\nmap2y =\n{map2y}')
    image1_rect = cv.remap(image1, map1x, map1y, cv.INTER_LINEAR)
    image2_rect = cv.remap(image2, map2x, map2y, cv.INTER_LINEAR)
    # image1_rect = cv.remap(image1, map2x, map2y, cv.INTER_LINEAR)
    # image2_rect = cv.remap(image2, map1x, map1y, cv.INTER_LINEAR)

    return image1_rect, image2_rect

# def 

def shift_image_left_with_margin(image, shift_pixels, margin_color=(0, 0, 0)):
    """
    Shifts the content of an image to the left and adds a margin to the right.

    Args:
        image: The input image (NumPy array).
        shift_pixels: The number of pixels to shift to the left.
        margin_color: The color of the margin (BGR tuple).

    Returns:
        The shifted image with the margin.
    """

    rows, cols = image.shape[:2]

    # Define the transformation matrix for the shift
    M = np.float32([[1, 0, -shift_pixels], [0, 1, 0]])

    # Calculate the new width of the output image
    new_width = cols + shift_pixels

    # Apply the affine transformation
    shifted_image = cv.warpAffine(image, M, (cols, rows))
    # shifted_image = cv.warpAffine(image, M, (new_width, rows))

    # Fill the margin with the specified color
    # shifted_image[:, cols:] = margin_color #this will work with simple bgr, but not with transparent images.

    # for i in range(cols, new_width):
    #     shifted_image[:,i] = margin_color;
    for i in range(cols-shift_pixels, cols):
        shifted_image[:,i] = margin_color;

    return shifted_image


'''
# for test....
R = np.array([[0.999, -0.01, 0.005],
              [0.01, 0.999, -0.008],
              [-0.005, 0.008, 1.0]])

t = np.array([[10],
              [5],
              [20]])

K1 = np.array([[1000, 0, image1.shape[1]/2],
              [0, 1000, image1.shape[0]/2],
              [0, 0, 1]])

K2 = np.array([[1000, 0, image2.shape[1]/2],
              [0, 1000, image2.shape[0]/2],
              [0, 0, 1]])
'''
print(f'R = {R}, type {type(R),R.dtype}')
print(f'T = {T}, type {type(T),T.dtype}')
t = T
K1 = mtx1
K2 = mtx2
D1 = dist1
D2 = dist2
# image1 = cv.imread('calib_imgs/smalltarget/tof_frame0005.png')
# image2 = cv.imread('calib_imgs/smalltarget/oak_frame0005.png')
# image1 = cv.imread('calib_imgs/for_test/tof_frame0000.png')
# image2 = cv.imread('calib_imgs/for_test/oak_frame0000.png')
# path2img = '/mnt/Data_3TB/Data/TestImages/oak_tof_calib/set1'
path2img = './calib_imgs/smalltarget'
# path2img = '/home/pi/Pictures'
# image1 = cv.imread('/home/pi/Pictures/tof_frame0001.png')
# image2 = cv.imread('/home/pi/Pictures/oak_frame0001.png')
# image1 = cv.imread(path2img+'/tof_frame0001.png')
# image2 = cv.imread(path2img+'/oak_frame0001.png')
if reference_cam == 'CAMB':
    image1 = cv.imread(path2img+'/oak_CAMB-2L_0000.png')
    image2 = cv.imread(path2img+'/oak_CAMC-2L_0000.png')
    # image1 = cv.imread(path2img+'/tof_frame0071.png')
    # image2 = cv.imread(path2img+'/oak_frame0071.png')
elif reference_cam == 'CAMC':
    image1 = cv.imread(path2img+'/oak_CAMC-2L_0000.png')
    image2 = cv.imread(path2img+'/oak_CAMB-2L_0000.png')

flag_rectify = None
# flag_rectify = cv.CALIB_ZERO_DISPARITY # or None
map1x,map1y,map2x,map2y,rig_config = compute_mapxy(K1, D1, K2, D2, R, T,image1.shape,alpha = 0.2,flag_R = False,flag_rectify = flag_rectify)
# map1x,map1y,map2x,map2y = compute_mapxy(K1, D1, K2, D2, R, T,image2.shape,alpha = 0.8,flag_R = True,flag_rectify = 0)
image1_rect, image2_rect = rectify_images_precalc(image1, image2, map1x,map1y,map2x,map2y)
# this is the correct way:
# image1_rect, image2_rect = rectify_images(image1, image2, K1, D1, K2, D2, R, T)
# image1_rect, image2_rect = rectify_images(image2, tof_im_rsz, K2, D2, K1, D1, R, T)
# shift result image
draw_lines = True
if rig_config == 'H':
    outim = np.hstack((image1_rect,image2_rect))
    inim = np.hstack((image1,image2))
    if draw_lines:
        cv.line(outim,(0,100),(outim.shape[1],100),color=(0,255,0),thickness=2)
        cv.line(inim,(0,100),(inim.shape[1],100),color=(0,255,0),thickness=2)
elif rig_config == 'V':
    outim = np.vstack((image1_rect,image2_rect))
    inim = np.vstack((image1,image2))
    if draw_lines:
        cv.line(outim,(100,0),(100,outim.shape[0]),color=(0,255,0),thickness=2)
        cv.line(outim,(outim.shape[1]-100,0),(outim.shape[1]-100,outim.shape[0]),color=(0,255,0),thickness=2)
        cv.line(inim,(100,0),(100,inim.shape[0]),color=(0,255,0),thickness=2)
        cv.line(inim,(inim.shape[1]-100,0),(inim.shape[1]-100,inim.shape[0]),color=(0,255,0),thickness=2)
# outim = np.vstack((image1_rect,image2_rect))
cv.imshow("reference Image", inim)
cv.imshow("Rectified", outim)
cv.waitKey(0)

