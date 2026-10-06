import argparse
import os
import re
import sys
from PIL import Image
import numpy as np

def decode_argb4444(pixel_16bit):
    a = ((pixel_16bit >> 12) & 0x0F) * 17
    r = ((pixel_16bit >> 8) & 0x0F) * 17
    g = ((pixel_16bit >> 4) & 0x0F) * 17
    b = (pixel_16bit & 0x0F) * 17
    return (r, g, b, a)

def decode_rgb565(pixel_16bit):
    r = (pixel_16bit >> 11) & 0x1F
    g = (pixel_16bit >> 5) & 0x3F
    b = pixel_16bit & 0x1F

    # Escala precisa de 5 y 6 bits a rango 0-255
    r8 = (r * 255) // 31
    g8 = (g * 255) // 63
    b8 = (b * 255) // 31
    return (r8, g8, b8, 255)

def detect_dimensions_and_packing(content, hex_count):
    w_match = re.search(r'#define\s+\w*(?:WIDTH|ANCHO)\w*\s+(\d+)', content, re.IGNORECASE)
    h_match = re.search(r'#define\s+\w*(?:HEIGHT|ALTO)\w*\s+(\d+)', content, re.IGNORECASE)
    if w_match and h_match:
        w, h = int(w_match.group(1)), int(h_match.group(1))
        packed = (hex_count < (w * h)) and (hex_count >= (w * h // 2))
        return w, h, packed

    dim_matches = re.findall(r'(\d{2,4})\s*[*xX]\s*(\d{2,4})', content)
    for w_str, h_str in dim_matches:
        w, h = int(w_str), int(h_str)
        target = w * h
        if hex_count == target:
            return w, h, False
        if hex_count == target // 2:
            return w, h, True

    arr_2d = re.findall(r'\[\s*(\d+)\s*\]\s*\[\s*(\d+)\s*\]', content)
    for d1_str, d2_str in arr_2d:
        d1, d2 = int(d1_str), int(d2_str)
        target = d1 * d2
        if hex_count in (target, target // 2):
            packed = (hex_count == target // 2)
            return (d2, d1, packed) if d2 >= d1 else (d1, d2, packed)

    standard_resolutions = [
        (480, 272), (320, 240), (240, 320), (800, 480), (480, 800),
        (240, 240), (128, 128), (128, 160), (160, 128), (1024, 600)
    ]
    for w, h in standard_resolutions:
        target = w * h
        if hex_count == target:
            return w, h, False
        if hex_count == target // 2:
            return w, h, True

    for packed, total in [(False, hex_count), (True, hex_count * 2)]:
        for i in range(int(total**0.5), 1, -1):
            if total % i == 0:
                w, h = total // i, i
                if 1.0 <= (w / h) <= 2.4:
                    return w, h, packed

    return 480, 272, (hex_count < (480 * 272))

def file_processing(file_path, color_format="rgb565", override_w=None, override_h=None):
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        hex_vals = re.findall(r'0x[0-9A-Fa-f]+', content)
        if not hex_vals:
            print("Error: No hexadecimal values found.")
            return

        hex_count = len(hex_vals)

        if override_w and override_h:
            width, height = override_w, override_h
            packed_32bit = hex_count < (width * height) and hex_count >= ((width * height) // 2)
        else:
            width, height, packed_32bit = detect_dimensions_and_packing(content, hex_count)

        total_pixels = width * height

        print(f"File: {file_path}")
        print(f"Format: {color_format.upper()}")
        print(f"Detected dimensions: {width}x{height} ({total_pixels} px)")
        print(f"Hex count: {hex_count} -> Mode: {'32-bit (2 px/val)' if packed_32bit else '16-bit (1 px/val)'}")

        decoder = decode_rgb565 if color_format.lower() == "rgb565" else decode_argb4444

        image_data = np.zeros((height, width, 4), dtype=np.uint8)
        pixel_idx = 0

        for hex_str in hex_vals:
            val = int(hex_str, 16)
            pixels_to_process = [(val >> 16) & 0xFFFF, val & 0xFFFF] if packed_32bit else [val & 0xFFFF]

            for px in pixels_to_process:
                if pixel_idx >= total_pixels:
                    break
                x = pixel_idx % width
                y = pixel_idx // width
                image_data[y, x] = decoder(px)
                pixel_idx += 1

            if pixel_idx >= total_pixels:
                break

        img = Image.fromarray(image_data, 'RGBA')

        base_path, _ = os.path.splitext(file_path)
        output_filename = f"{base_path}_{width}x{height}_{color_format.lower()}.png"
        img.save(output_filename)
        print(f"Output saved: {output_filename}")

        img.show()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process C array and export PNG image.')
    parser.add_argument('file', help='Path to .h or .c file')
    parser.add_argument('--format', '-f', choices=['rgb565', 'argb4444'], default='rgb565',
                        help='Input pixel format (default: rgb565)')
    parser.add_argument('--width', type=int, help='Manual width override')
    parser.add_argument('--height', type=int, help='Manual height override')
    args = parser.parse_args()

    file_processing(args.file, args.format, args.width, args.height)