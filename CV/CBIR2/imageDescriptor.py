import numpy as np
import cv2


class ImageDescriptor:
    def __init__(self, bins):
        self.bins = bins

    def describe(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        features = []

        # get dimensions
        (h, w) = image.shape[:2]

        # get image center
        (midX, midY) = (int(h * 0.5), int(w * 0.5))

        # divide image into 4 parts
        segments = [(0, midX, 0, midY), (midX, w, 0, midY), (midX, w, midY, h), (0, midX, midY, h)]
        # half of elliptical mask x, y axes
        (axesX, axesY) = (int(w * 0.75) / 2, int(h * 0.75) / 2)
        ellipseMask = np.zeros(image.shape[:2], dtype="uint8")
        # cv2.ellipse(image, (center), (half length of ellipse), angle, start angle, end angle, color, thickness)
        ellipseMask = cv2.ellipse(ellipseMask, (midX, midX), (axesX, axesY), 0, 0, 360, 255, -1)

        for (startX, endX, startY, endY) in segments:
            cornerMask = np.zeros(image.shape[:2], dtype="uint8")
            # cv2.rectangle(img, (pt1), (pt2), color, thickness)
            cornerMask = cv2.rectangle(cornerMask, (startX, startY), (endX, endY), 255, -1)
            # rectangle subtract the overlapped part with central ellipse
            cornerMask = cv2.subtract(cornerMask, ellipseMask)
            features.extend(self.histogram(image, cornerMask))
        hist = self.histogram(image, ellipseMask)
        features.extend(hist)
        return features

    def histogram(self, image, mask):
        # cv2.clcHist([images], [channels], mask, [hist sizes], [ranges])
        hist = cv2.calcHist([image], [0, 1, 2], mask, self.bins, [0, 180, 0, 256, 0, 256])
        # normalization, show percentage
        hist = cv2.normalize(hist, hist).flatten()
        return hist