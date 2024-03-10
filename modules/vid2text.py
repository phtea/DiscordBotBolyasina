import io
import cv2
from PIL import Image
import timeit
from memory_profiler import profile

def video_to_frames(path_to_video: str, width: int, step: float) -> list[str]:
    images = video_to_images(path_to_video)
    frames = images_to_frames(images, width, step)
    return frames

def video_to_images(path_to_video: str) -> list[bytes]:
    images: list = []
    cap = cv2.VideoCapture(path_to_video)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    for _ in range(frame_count):
        _, image = cap.read()
        _, buffer = cv2.imencode(".png", image)
        del image
        byte_image: bytes = buffer.tobytes()
        images.append(byte_image)
    return images

def images_to_frames(images: list, width: int, step: float) -> list[str]:
    step = int(step)
    frames = []
    new_images = [images[i] for i in range(len(images)) if i%step==0]
    for image in new_images:
        frames.append(generate_image(image, width))
    return frames

def resize(image, new_width: int):
    (old_width, old_height) = image.size
    aspect_ratio = float(old_height) / float(old_width)
    symbol_aspect_ratio = 2.75
    final_aspect_ratio = aspect_ratio / symbol_aspect_ratio
    new_height: int = int((final_aspect_ratio * new_width))
    new_dim = (new_width, new_height)
    new_image = image.resize(new_dim)
    return new_image, new_width, new_height

ASCII_CHARS = list("  .,,;")

def pixelize_image(image):
    global ASCII_CHARS
    buckets = 256 // (len(ASCII_CHARS) - 1)
    initial_pixels = list(image.getdata())
    new_pixels = [ASCII_CHARS[pixel_value // buckets] for pixel_value in initial_pixels]
    return ''.join(new_pixels)

def modify_image(image, new_width):
    image, new_width, new_height = resize(image, new_width)
    image = image.convert('L') # turn_gray
    pixels = pixelize_image(image)
    len_pixels = len(pixels)
    new_image = [pixels[index:index + int(new_width)] for index in range(0, len_pixels, int(new_width))]
    return '\n'.join(new_image)

def generate_image(image, width):
    try:
        image = Image.open(io.BytesIO(image))
    except Exception as e:
        print(e)
        return
    image = modify_image(image, width)
    return image

if __name__ == '__main__':
    video_path = 'test.mp4'
    # video_to_images(video_path)
    time_1 = timeit.timeit(lambda: video_to_images(video_path), number=5)
    # time_2 = timeit.timeit(lambda: video_to_images_test(video_path), number=5)
    # dif = (time_1/time_2*100)-100
    print(time_1)