from pathlib import Path

from PIL import Image, ImageOps, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "assets" / "portrait" / "profile.jpg"
OUTPUT = ROOT / "assets" / "portrait" / "portrait.svg"

# Dense terminal-style character ramp.
# Dark -> bright
ASCII_CHARS = " .:-=+*#%@"

ASCII_WIDTH = 100
FONT_SIZE = 11
LINE_HEIGHT = 11


def prepare_image(image):
    image = image.convert("RGB")

    # Convert to grayscale.
    image = ImageOps.grayscale(image)

    # Strong terminal-style contrast.
    image = ImageEnhance.Contrast(image).enhance(2.8)

    # Slightly darken the image.
    image = ImageEnhance.Brightness(image).enhance(0.88)

    # Sharpen facial details.
    image = image.filter(
        ImageFilter.UnsharpMask(
            radius=1.5,
            percent=200,
            threshold=2
        )
    )

    original_width, original_height = image.size

    # Characters are taller than they are wide.
    character_ratio = 0.48

    height = max(
        1,
        int(
            (original_height / original_width)
            * ASCII_WIDTH
            * character_ratio
        )
    )

    image = image.resize(
        (ASCII_WIDTH, height),
        Image.Resampling.LANCZOS
    )

    return image


def image_to_ascii(image):
    pixels = list(image.get_flattened_data())

    width, height = image.size

    lines = []

    for y in range(height):
        row = []

        for x in range(width):
            pixel = pixels[y * width + x]

            index = int(
                pixel / 255 * (len(ASCII_CHARS) - 1)
            )

            row.append(ASCII_CHARS[index])

        lines.append("".join(row).rstrip())

    return lines


def escape_xml(text):
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def generate_svg(lines):
    svg_width = 1150

    top_padding = 30

    svg_height = (
        top_padding
        + len(lines) * LINE_HEIGHT
        + 30
    )

    text_elements = []

    for index, line in enumerate(lines):
        y = top_padding + index * LINE_HEIGHT

        safe_line = escape_xml(line)

        delay = index * 0.035

        text_elements.append(
            f"""
            <text
                x="50%"
                y="{y}"
                text-anchor="middle"
                class="ascii-line"
                style="animation-delay:{delay:.3f}s"
            >{safe_line}</text>
            """
        )

    text_content = "\n".join(text_elements)

    return f"""<?xml version="1.0" encoding="UTF-8"?>

<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{svg_width}"
    height="{svg_height}"
    viewBox="0 0 {svg_width} {svg_height}"
    role="img"
    aria-label="Terminal ASCII portrait of Austine Otieno"
>

<rect
    width="100%"
    height="100%"
    fill="#000000"
 />

<style>

.ascii-line {{
    font-family:
        "Courier New",
        "Consolas",
        "Liberation Mono",
        monospace;

    font-size: {FONT_SIZE}px;

    font-weight: 700;

    letter-spacing: 0;

    fill: #ffffff;

    white-space: pre;

    opacity: 0;

    animation:
        terminalReveal
        0.08s
        steps(1, end)
        forwards;
}}

@keyframes terminalReveal {{

    from {{
        opacity: 0;
    }}

    to {{
        opacity: 1;
    }}

}}

@media (prefers-reduced-motion: reduce) {{

    .ascii-line {{
        animation: none;
        opacity: 1;
    }}

}}

</style>

<g>

{text_content}

</g>

</svg>
"""


def main():

    if not INPUT.exists():
        raise FileNotFoundError(
            f"Profile image not found: {INPUT}"
        )

    print("======================================")
    print("  AUSTINE192-A // ASCII GENERATOR")
    print("======================================")
    print()

    print("[1/4] Loading profile image...")

    image = Image.open(INPUT)

    print(
        f"      Source: {image.width}x{image.height}"
    )

    print()

    print("[2/4] Preparing terminal rendering...")

    image = prepare_image(image)

    print(
        f"      ASCII: {image.width}x{image.height}"
    )

    print()

    print("[3/4] Converting image to ASCII...")

    lines = image_to_ascii(image)

    print(
        f"      Rows: {len(lines)}"
    )

    print()

    print("[4/4] Building animated SVG...")

    svg = generate_svg(lines)

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print()
    print("======================================")
    print("  GENERATION COMPLETE")
    print("======================================")
    print()
    print(f"Output: {OUTPUT}")
    print()


if __name__ == "__main__":
    main()