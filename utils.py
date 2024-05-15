import math


class DetectedObject:
    def __init__(self, x, y, w, h, color, _type, frame, id=0) -> None:
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self._type = _type
        self.frame = frame
        self.id = id

    def __str__(self) -> str:
        return (
            f"ID: {self.id} X: {self.x}, Y: {self.y}, W: {self.w}, H: {self.h}"
            f" COLOR: {self.color}, TYPE: {self._type}, FRAME NUM: {self.frame}"
        )

    __repr__ = __str__


class Tracker:
    def __init__(self):
        self.last_coords = dict()  # stores the last position and color of each object
        self.id = 1

    def update(self, objects_rect: list[DetectedObject]) -> list:
        """
        tracks DetectedObjects movements

        :param objects_rect: list of DetectedObject instances
        :returns list: history of the tracked objects
        """
        objects = []

        for rect in objects_rect:
            # Get center point of new object
            cx = (rect.x + rect.x + rect.w) // 2
            cy = (rect.y + rect.y + rect.h) // 2

            # Find out if that object was detected already
            same_object_detected = False
            for id, pt in self.last_coords.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])
                if (self.last_coords[id][2] == rect.color).all() and dist < 100:
                    self.last_coords[id] = (
                        cx,
                        cy,
                        rect.color,
                    )
                    rect.id = id
                    objects.append(rect)
                    same_object_detected = True
                    break

            # new object -> new id
            if not same_object_detected:
                self.last_coords[self.id] = (
                    cx,
                    cy,
                    rect.color,
                )
                rect.id = self.id
                objects.append(rect)
                self.id += 1

        return objects
