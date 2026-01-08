import cv2
import numpy as np

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    rect[0] = pts[np.argmin(s)]     # top-left
    rect[2] = pts[np.argmax(s)]     # bottom-right
    rect[1] = pts[np.argmin(diff)]  # top-right
    rect[3] = pts[np.argmax(diff)]  # bottom-left

    return rect

def crop_quadrat_from_points(image_bytes, points):
    img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    pts = np.array(points, dtype=np.float32)

    rect = order_points(pts)

    # draw context outline
    context = img.copy()
    for i in range(4):
        cv2.line(
            context,
            tuple(rect[i].astype(int)),
            tuple(rect[(i + 1) % 4].astype(int)),
            (0, 0, 255),
            4
        )

    w = int(max(
        np.linalg.norm(rect[2] - rect[3]),
        np.linalg.norm(rect[1] - rect[0])
    ))
    h = int(max(
        np.linalg.norm(rect[1] - rect[2]),
        np.linalg.norm(rect[0] - rect[3])
    ))

    dst = np.array([[0,0],[w-1,0],[w-1,h-1],[0,h-1]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(rect, dst)
    cropped = cv2.warpPerspective(img, M, (w, h))

    return {
        "cropped_image": cv2.imencode(".png", cropped)[1].tobytes(),
        "context_image": cv2.imencode(".png", context)[1].tobytes(),
    }