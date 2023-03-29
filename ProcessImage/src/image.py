import boto3

import hashlib
from io import BytesIO
import os
import imghdr
import time


from math import sqrt
from typing import Callable
from PIL import Image, ImageFile, ImageDraw, ImageFont
from PIL.ExifTags import TAGS, GPSTAGS


rekognition = boto3.client('rekognition')


def rational_to_float(rational):
    return float(rational[0]) / float(rational[1])


def is_serializable(value):
    return isinstance(value, (str, bool, int, float, list, dict))


def remove_non_serializable_entries(input_dict):
    serializable_dict = {}
    for key, value in input_dict.items():
        if is_serializable(value):
            serializable_dict[key] = value
        elif key == 'dpi':
            serializable_dict[key] = (float(str(value[0])), float(str(value[1])))
    return serializable_dict


def get_gps_info(img):
    gps_info = {}
    if hasattr(img, '_getexif'):
        exif = img._getexif()
        if exif:
            for tag, value in exif.items():
                if TAGS.get(tag) == 'GPSInfo':
                    gps_info = value
                    break

    if not gps_info:
        return None

    gps_data = {}
    for t in gps_info:
        tagName = GPSTAGS.get(t, t)
        gps_data[tagName] = gps_info[t]

    if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
        lat = [rational_to_float(x) for x in gps_data['GPSLatitude']]
        lon = [rational_to_float(x) for x in gps_data['GPSLongitude']]
        lat_ref = gps_data.get('GPSLatitudeRef', 'N')
        lon_ref = gps_data.get('GPSLongitudeRef', 'W')
        lat = round(lat[0] + lat[1] / 60 + lat[2] / 3600, 6) * (-1 if lat_ref == 'S' else 1)
        lon = round(lon[0] + lon[1] / 60 + lon[2] / 3600, 6) * (-1 if lon_ref == 'W' else 1)
        gps_data['latitude'] = lat
        gps_data['longitude'] = lon

    return gps_data


# Map image mode to color depth
color_depth_map = {
    '1': 1,      # 1-bit pixels, black and white
    'L': 8,      # 8-bit pixels, greyscale
    'P': 8,      # 8-bit pixels, mapped to any other mode using a color palette
    'RGB': 24,   # 8-bit x 3 channels, true color
    'RGBA': 32,  # 8-bit x 4 channels, true color with transparency
    'CMYK': 32,  # 8-bit x 4 channels, color separation
    'YCbCr': 24, # 8-bit x 3 channels, color video format
    'LAB': 24,   # 8-bit x 3 channels, the L*a*b color space
    'HSV': 24,   # 8-bit x 3 channels, Hue, Saturation, Value
    'I': 32,     # 32-bit signed integer pixels
    'F': 32,     # 32-bit floating point pixels
}


def detect_labels(image_bytes: bytes, min_confidence=80, min_bound=0.01):
    return rekognition.detect_labels(
                Image={'Bytes': image_bytes},
                MinConfidence=min_confidence
            )['Labels']


def detect_texts(image_bytes: bytes, min_confidence=80, min_bound=0.01):
    return rekognition.detect_text(
                Image={'Bytes': image_bytes},
                Filters={
                    'WordFilter': {
                        'MinConfidence': min_confidence,
                        'MinBoundingBoxHeight': min_bound,
                        'MinBoundingBoxWidth': min_bound
                    }
                })['TextDetections']


def process_image(key: str, path: str, save: Callable[[str, dict], None], min_confidence=80, min_bound=0.01):
    with open(path, 'rb') as image_file:
        image_bytes = image_file.read()

        labelRecords = detect_labels(image_bytes, min_confidence, min_bound)
        textRecords  = detect_texts(image_bytes, min_confidence, min_bound)
        
        labels = {}
        for record in labelRecords:
            if 'Instances' in record and record['Confidence'] >= min_confidence:
                max_size = 0
                for instance in record['Instances']:
                    box = instance['BoundingBox']
                    if box['Width'] >= min_bound and box['Height'] > min_bound:
                        size = sqrt(box['Width']*box['Width'] + box['Height']*box['Height'])
                        if size > 0.02 and size >= max_size:
                            label = record['Name'].lower()
                            labels[label] = round(size * 10000)
                            max_size = size
        
        texts = {}
        for item in textRecords:
            if item['Type'] == 'WORD':
                text = item['DetectedText'].lower().rstrip(".,!?:#")
                if len(text) > 2:
                    geometry = item['Geometry']
                    box = geometry['BoundingBox']
                    size = sqrt(box['Width']*box['Width'] + box['Height']*box['Height'])
                    if size > 0.02:
                        texts[text] = round(size * 10000)

    # Open the image file
    with Image.open(path) as img:
        width, height = img.size

        created = os.path.getctime(path)
        modified = os.path.getmtime(path)

        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        hash_value = hash_md5.hexdigest()

        file_size = os.path.getsize(path)
        file_type = imghdr.what(path)
        img_info = remove_non_serializable_entries(img.info)
        gps_data = get_gps_info(img)

        color_mode = img.mode
        color_depth = color_depth_map.get(color_mode, 'Unknown')
        color_info = {
            'depth': color_depth,
            'mode': color_mode
        }

        metadata = {
            'width': width,
            'height': height,
            'created': time.ctime(created),
            'modified': time.ctime(modified),
            'hash': hash_value,
            'size': file_size,
            'type': file_type,
            'gps': gps_data,
            'color': color_info,
            'image': img_info,
            'labels': labels,
            'texts': texts
        }
        
        name = key + '--metadata.json'
        save(name, metadata)
