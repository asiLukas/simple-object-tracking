import math
import cv2
import numpy as np
from collections import defaultdict


from utils import Tracker, DetectedObject


def get_obj_color(image, x, y, w, h) -> np.uint8:
    """
    retrieves the most common rgb value out of a specific roi

    :param image(np.array()): the input image(frame) where we want to find the color
    :param x(int): x position of the roi
    :param y(int): y position of the roi
    :param w(int): width of the roi
    :param h(int): height of the roi
    :returns np.array(): color as an int numpy array object
    """
    roi = image[y : y + h, x : x + w]
    pixels_rgb = roi.reshape(
        -1, 3
    )  # reshapes the array so the rows are pixels and cols rgb values
    unique_colors, counts = np.unique(pixels_rgb, axis=0, return_counts=True)

    # NOTE incosistency - when the object gets near border, the color fluctuates
    most_common_index = np.argmax(counts)
    most_common_color = unique_colors[most_common_index]
    return most_common_color.astype(int)


def remove_redundant_objects(history) -> None:
    """
    removes redundant objects that lasted less than 5 frames

    :param history(dict): history of the object movements
    :returns: null
    """
    redundant_objects = []
    for key, value in history.items():
        if len(value) < 5:
            redundant_objects.append(key)
    for key in redundant_objects:
        del history[key]


def object_tracking(frame, tracker, detections, history) -> None:
    """
    tracks and keeps history of tracking of detected objects

    :param frame(np.array()): current frame of the video
    :param tracker(Tracker): Tracker instance
    :param detections(list): list of detected objects
    :param history(dict): current history of tracked objects
    """
    rects = tracker.update(detections)
    for rect in rects:
        rect.color = rect.color.tolist()
        history[str(rect.id)].append(rect)
        cv2.rectangle(frame, (rect.x, rect.y, rect.w, rect.h), (255, 255, 255))
        cv2.putText(
            frame,
            str(rect),
            (rect.x, rect.y - 15),
            cv2.FONT_HERSHEY_PLAIN,
            1,
            (255, 255, 255),
        )


def object_detection(src) -> dict:
    """
    detects and tracks each individual moving object on a black canvas

    :param src: source video
    :returns dict: history of the tracked objects
    """
    tracker = Tracker()
    history = defaultdict(list)
    frame_count = 1
    while True:
        _, frame = src.read()
        if frame is None:
            break

        # TRESH_OTSU has problems with objects that are very dark
        bright_frame = cv2.addWeighted(
            frame, 4.3, np.zeros(frame.shape, frame.dtype), 0, 20
        )

        # create a mask that will track objects on a black canvas
        gray = cv2.cvtColor(bright_frame, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detections = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area <= 50:  # filter noise
                break

            # NOTE incosictency - when two contours collide, they merge into one boundingRect
            x, y, w, h = cv2.boundingRect(cnt)
            perimeter = cv2.arcLength(cnt, True)
            circularity = (4 * math.pi * area) / math.pow(perimeter, 2)
            object_type = "rectangle" if circularity < 0.8 else "circle"

            detections.append(
                DetectedObject(
                    x,
                    y,
                    w,
                    h,
                    get_obj_color(frame, x, y, w, h),
                    object_type,
                    frame_count,
                )
            )

        object_tracking(frame, tracker, detections, history)
        cv2.imshow("input", frame)

        key = cv2.waitKey(10)
        frame_count += 1

        # break the loop upon the press of esc
        if key == 27:
            break

    return history


def output_visualization(out, background, history) -> None:
    """
    displays the visualization of the object tracking and saves it into an mp4 file

    :param out: the output video source
    :param background: default background for each frame
    :param history(list): current history of tracked objects
    """
    max_frames = int(src.get(cv2.CAP_PROP_FRAME_COUNT))
    last_frame = max([max(sublist, key=lambda x: x.frame).frame for sublist in history])
    frame_count = 1
    while frame_count < max_frames and frame_count < last_frame:
        frame = background.copy()

        for sublist in history:
            # NOTE this is needed due to the incosictency when objects are colliding
            w = sublist[0].w
            h = sublist[0].h
            _type = sublist[0]._type
            color = sublist[0].color
            for obj in sublist:
                if obj.frame == frame_count:
                    if _type == "rectangle":
                        cv2.rectangle(frame, (obj.x, obj.y, w, h), color, -1)
                    else:
                        cv2.circle(frame, (obj.x, obj.y), w // 2, color, -1)

        out.write(frame)
        cv2.imshow("output", frame)
        key = cv2.waitKey(20)

        # break the loop upon the press of esc
        if key == 27:
            break
        frame_count += 1


src = cv2.VideoCapture("inp.mp4")
window_w = int(src.get(3))
window_h = int(src.get(4))
history = object_detection(src)
remove_redundant_objects(history)

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
output = cv2.VideoWriter(
    "out.mp4", fourcc, src.get(cv2.CAP_PROP_FPS), (window_w, window_h)
)
background = np.zeros((window_h, window_w, 3), dtype=np.uint8)
history_sublists = [sublist for sublist in history.values()]
output_visualization(output, background, history_sublists)

src.release()
output.release()
