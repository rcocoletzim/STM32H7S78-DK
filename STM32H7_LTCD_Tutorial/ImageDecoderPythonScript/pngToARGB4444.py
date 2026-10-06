import sys
import os
from PIL import Image

def convert_to_argb4444(png_path, out_header_path):
    img = Image.open(png_path).convert("RGBA")
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
                r, g, b, a = pixels[x, y]
                a4 = (a >> 4) & 0x0F
                r4 = (r >> 4) & 0x0F
                g4 = (g >> 4) & 0x0F
                b4 = (b >> 4) & 0x0F
                argb4444 = (a4 << 12) | (r4 << 8) | (g4 << 4) | b4

                f.write(f"0x{argb4444:04X}, ")
            f.write("\n")

        f.write("};\n\n")
        f.write(f"#endif // {var_name.upper()}_H\n")

    print(f"Generate {out_header_path} ({width}x{height} px, {width * height * 2} bytes)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Use: python pngToARGB4444.py <file.png> <output.h>")
        sys.exit(1)
    convert_to_argb4444(sys.argv[1], sys.argv[2])