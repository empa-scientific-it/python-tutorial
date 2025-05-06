import cv2
import numpy as np
import pytest


def reference_scale_image(image, scale_factor):
    # Get the current dimensions
    height, width = image.shape[:2]

    # Calculate the new dimensions
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    new_size = (new_width, new_height)

    # Resize the image
    return cv2.resize(image, new_size)


@pytest.mark.parametrize("scale_factor", [0.5, 1.0, 2.0])
def test_scale_image(scale_factor, function_to_test):
    image = np.ones((32, 32, 3), dtype=np.uint8) * 255
    image_test = function_to_test(image, scale_factor)
    image_reference = reference_scale_image(image, scale_factor)
    assert image_test.shape == image_reference.shape


def reference_crop_image(image, x: int, y: int, width: int, height: int):
    x1, x2, y1, y2 = x, x + width, y, y + height
    return image[y : y + height, x : x + width]


@pytest.mark.parametrize(
    "x, y, width, height", [(2, 2, 2, 2), (5, 5, 4, 4), (10, 10, 6, 6)]
)
def test_crop_image(x, y, width, height, function_to_test):
    image = np.ones((32, 32, 3), dtype=np.uint8) * 255
    image_test = function_to_test(image, x, y, width, height)
    image_reference = reference_crop_image(image, x, y, width, height)
    assert image_test.shape == image_reference.shape


def reference_horizontal_flip_image(image):
    return cv2.flip(image, 1)


def test_horizontal_flip_image(function_to_test):
    image = np.ones((32, 32, 3), dtype=np.uint8) * 255
    image_test = function_to_test(image)
    image_reference = reference_horizontal_flip_image(image)
    assert np.allclose(image_test, image_reference)


def reference_vertical_flip_image(image):
    return cv2.flip(image, 0)


def test_vertical_flip_image(function_to_test):
    image = np.ones((32, 32, 3), dtype=np.uint8) * 255
    image_test = function_to_test(image)
    image_reference = reference_vertical_flip_image(image)
    assert np.allclose(image_test, image_reference)


def reference_rotate_image(image, angle: float):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, scale=1.0)

    # Compute new bounding dimensions
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    # Adjust rotation matrix for translation
    M[0, 2] += (new_w / 2) - center[0]
    M[1, 2] += (new_h / 2) - center[1]

    # Perform rotation with expanded canvas
    return cv2.warpAffine(image, M, (new_w, new_h))


@pytest.mark.parametrize("angle", [5, 10, 20, 30])
def test_rotate_image(angle, function_to_test):
    image = np.ones((32, 32, 3), dtype=np.uint8) * 255
    image_test = function_to_test(image, angle)
    image_reference = reference_rotate_image(image, angle)
    assert np.allclose(image_test, image_reference)


def reference_average_filter(image, kernel_size):
    return cv2.blur(image, kernel_size)


@pytest.mark.parametrize("kernel_size", [(3, 3), (5, 5)])
def test_average_filter(kernel_size, function_to_test):
    image = np.ones((32, 32, 3), dtype=np.uint8) * 255
    image_test = function_to_test(image, kernel_size)
    image_reference = reference_average_filter(image, kernel_size)
    assert np.allclose(image_test, image_reference)


def reference_median_filter(image, ksize):
    return cv2.medianBlur(image, ksize)


@pytest.mark.parametrize("ksize", [3, 5])
def test_median_filter(ksize, function_to_test):
    image = np.ones((32, 32, 3), dtype=np.uint8) * 255
    image_test = function_to_test(image, ksize)
    image_reference = reference_median_filter(image, ksize)
    assert np.allclose(image_test, image_reference)


def reference_gaussian_filter(image, kernel_size, sigma):
    return cv2.GaussianBlur(image, kernel_size, sigma)


@pytest.mark.parametrize(
    "kernel_size, sigma", [((3, 3), 0), ((5, 5), 0), ((3, 3), 1), ((5, 5), 1)]
)
def test_gaussian_filter(kernel_size, sigma, function_to_test):
    image = np.ones((32, 32, 3), dtype=np.uint8) * 255
    image_test = function_to_test(image, kernel_size, sigma)
    image_reference = reference_gaussian_filter(image, kernel_size, sigma)
    assert np.allclose(image_test, image_reference)


def reference_adjust_brightness(image, brightness_value):
    return cv2.convertScaleAbs(image, beta=brightness_value)


@pytest.mark.parametrize("brightness_value", [-30, -20, -10, 0, 10, 20, 30])
def test_adjust_brightness(brightness_value, function_to_test):
    image = np.ones((32, 32, 3), dtype=np.uint8) * 255
    image_test = function_to_test(image, brightness_value)
    image_reference = reference_adjust_brightness(image, brightness_value)
    assert np.allclose(image_test, image_reference)


def reference_adjust_contrast(image, contrast_value):
    return cv2.convertScaleAbs(image, alpha=contrast_value)


@pytest.mark.parametrize("contrast_value", [0.5, 1.0, 1.5, 2.0])
def test_adjust_contrast(contrast_value, function_to_test):
    image = np.ones((32, 32, 3), dtype=np.uint8) * 255
    image_test = function_to_test(image, contrast_value)
    image_reference = reference_adjust_contrast(image, contrast_value)
    assert np.allclose(image_test, image_reference)


def reference_adjust_saturation(image, saturation_factor):
    # Convert the image from BGR to HSV
    image_hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

    # Split the HSV image into Hue, Saturation, and Value channels
    hue, saturation, value = cv2.split(image_hsv)

    # Adjust the saturation channel (Ensure it stays within valid range)
    saturation = np.clip(saturation * saturation_factor, 0, 255)

    # Merge the channels back
    image_hsv_adjusted = cv2.merge([hue, saturation.astype(np.uint8), value])

    # Convert the adjusted image back to BGR
    return cv2.cvtColor(image_hsv_adjusted, cv2.COLOR_HSV2RGB)


@pytest.mark.parametrize("saturation_factor", [0.5, 1.0, 1.5, 2.0])
def test_adjust_saturation(saturation_factor, function_to_test):
    image = np.ones((32, 32, 3), dtype=np.uint8) * 255
    image_test = function_to_test(image, saturation_factor)
    image_reference = reference_adjust_saturation(image, saturation_factor)
    assert np.allclose(image_test, image_reference)
