import os
import cv2
import numpy as np

filename = "CS01_HIGH0_21JULY2022_red2"
image_path = f"./Data/Capt. Sinclair/{filename}.jpg"
img = cv2.imread(image_path)
original = img.copy()

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# red color ranges
lower_red1 = np.array([0, 150, 150])
upper_red1 = np.array([6, 255, 255])
lower_red2 = np.array([174, 150, 150])
upper_red2 = np.array([180, 255, 255])

mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
red_mask = cv2.bitwise_or(mask1, mask2)

cv2.imshow("Red Mask (raw)", red_mask)
cv2.waitKey(0)

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

cv2.imshow("Red Dots Mask", red_mask)
cv2.waitKey(0)

contours, x = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

filtered = []

for c in contours:
    area = cv2.contourArea(c)
    if area < 150:      # <-- increase from 100
        continue
    perimeter = cv2.arcLength(c, True)
    if perimeter == 0:
        continue
    circularity = 4 * np.pi * area / (perimeter * perimeter)
    if circularity < 0.4:  # noise and line fragments fail this
        continue
    filtered.append(c)

contours = filtered

if len(contours) > 4:
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:4]

if len(contours) != 4:
    raise RuntimeError(f"Expected 4 red dots, found {len(contours)}")

# if not contours:
#     raise RuntimeError("No red dots found")
#
# print(len(contours))
# if len(contours) > 4:
#     contours = [c for c in contours if cv2.contourArea(c) > 100]

# contours2 = []
# if len(contours) > 4:
#     for c in contours:
#         if cv2.contourArea(c) > 100:
#             contours2.append(c)
#
# print(contours2)

if len(contours) < 4:
    raise RuntimeError(f"Expected 4 red dots, found {len(contours)}")

centers = []

# get the centers of the red dots
for c in contours:
    M = cv2.moments(c)
    if M["m00"] == 0:               # area of the contour
        continue
    cx = int(M["m10"] / M["m00"])   # sum of x coordinates weighted by area
    cy = int(M["m01"] / M["m00"])   # sum of y coordinates weighted by area
    centers.append([cx, cy])

centers = np.array(centers, dtype=np.float32)

# keep the 4 largest dots if extra red dots exist
if len(centers) > 4:
    contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)[:4]
    centers = []
    for c in contours_sorted:
        M = cv2.moments(c)
        centers.append([
            int(M["m10"]/M["m00"]),
            int(M["m01"]/M["m00"])
        ])
    centers = np.array(centers, dtype=np.float32)

debug = img.copy()
for (x, y) in centers:
    cv2.circle(debug, (int(x), int(y)), 10, (0,255,0), -1)

cv2.imshow("Detected Corner Dots", debug)
cv2.waitKey(0)

def order_points(pts):
    rect = np.zeros((4,2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    rect[0] = pts[np.argmin(s)]    # top-left
    rect[2] = pts[np.argmax(s)]    # bottom-right
    rect[1] = pts[np.argmin(diff)] # top-right
    rect[3] = pts[np.argmax(diff)] # bottom-left
    return rect

rect = order_points(centers)

# Draw red lines connecting the quadrat corners
outlined = original.copy()

for i in range(4):
    p1 = tuple(rect[i].astype(int))
    p2 = tuple(rect[(i + 1) % 4].astype(int))  # wraps last → first
    cv2.line(outlined, p1, p2, (0, 0, 255), 4)

# Optional: draw corner dots on top
for (x, y) in rect:
    cv2.circle(outlined, (int(x), int(y)), 8, (0, 255, 0), -1)

cv2.imshow("Quadrat Outline", outlined)
cv2.waitKey(0)

# Save context image
os.makedirs("./Data/Context", exist_ok=True)
out_path = f"./Data/Context/{filename}_context.jpg"
cv2.imwrite(out_path, outlined)
print(f"Saved context image to {out_path}")


widthA = np.linalg.norm(rect[2] - rect[3])
widthB = np.linalg.norm(rect[1] - rect[0])
maxWidth = int(max(widthA, widthB))

heightA = np.linalg.norm(rect[1] - rect[2])
heightB = np.linalg.norm(rect[0] - rect[3])
maxHeight = int(max(heightA, heightB))

dst = np.array([
    [0, 0],
    [maxWidth - 1, 0],
    [maxWidth - 1, maxHeight - 1],
    [0, maxHeight - 1]
], dtype="float32")

M = cv2.getPerspectiveTransform(rect, dst)
warped = cv2.warpPerspective(original, M, (maxWidth, maxHeight))

cv2.imshow("Warped Quadrat", warped)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Save cropped image
os.makedirs("./Data/Cropped", exist_ok=True)
out_path = f"./Data/Cropped/{filename}_cropped.jpg"
cv2.imwrite(out_path, warped)
print(f"Saved cropped image to {out_path}")
