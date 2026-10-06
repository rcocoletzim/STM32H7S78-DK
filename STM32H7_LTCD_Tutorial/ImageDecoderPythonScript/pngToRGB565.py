import os
import sys
from PIL import Image

def convert_to_rgb565(png_path, out_header_path):
    img = Image.open(png_path).convert("RGB")
    width, height = img.size
    pixels = img.load()

    var_name = os.path.splitext(os.path.basename(png_path))[0].replace(" ", "_").replace("-", "_")

    with open(out_header_path, "w") as f:
        f.write(f"#ifndef {var_name.upper()}_H\n")
        f.write(f"#define {var_name.upper()}_H\n\n")
        f.write("#include <stdint.h>\n\n")
        f.write(f"#define {var_name.upper()}_WIDTH  {width}\n")
        f.write(f"#define {var_name.upper()}_HEIGHT {height}\n\n")
        f.write(f"const uint16_t {var_name}_map[{width * height}] = {{\n")

        for y in range(height):
            f.write("    ")
            for x in range(width):
                r, g, b = pixels[x, y]

                r5 = (r >> 3) & 0x1F
                g6 = (g >> 2) & 0x3F
                b5 = (b >> 3) & 0x1F
                rgb565 = (r5 << 11) | (g6 << 5) | b5

                f.write(f"0x{rgb565:04X}, ")
            f.write("\n")

        f.write("};\n\n")
        f.write(f"#endif\n")

    print(f"Generated {out_header_path} ({width}x{height} px, {width * height * 2} bytes)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pngToRGB565.py <input.png> <output.h>")
        sys.exit(1)
    convert_to_rgb565(sys.argv[1], sys.argv[2])