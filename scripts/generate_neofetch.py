from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

OUTPUT = (
    ROOT
    / "assets"
    / "neofetch"
    / "neofetch.svg"
)


ASCII_LOGO = [
    "       ███████╗",
    "       ██╔════╝",
    "       █████╗  ",
    "       ██╔══╝  ",
    "       ██║     ",
    "       ╚═╝     ",
]


INFO = [
    ("user", "Austine Otieno"),
    ("role", "Full Stack Developer"),
    ("focus", "Software + Cloud"),
    ("stack", "React · Python · AWS"),
    ("backend", "Node.js · PHP · PostgreSQL"),
    ("tools", "Git · GitHub · VS Code"),
    ("status", "Building"),
]


def escape_xml(text):
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def generate_svg():

    width = 760
    height = 360

    elements = []

    # Terminal window
    elements.append(
        """
        <rect
            x="0"
            y="0"
            width="760"
            height="360"
            rx="10"
            fill="#0d1117"
            stroke="#30363d"
            stroke-width="1"
        />
        """
    )

    # Terminal header
    elements.append(
        """
        <circle cx="20" cy="20" r="5" fill="#484f58"/>
        <circle cx="38" cy="20" r="5" fill="#484f58"/>
        <circle cx="56" cy="20" r="5" fill="#484f58"/>

        <text
            x="380"
            y="24"
            text-anchor="middle"
            fill="#8b949e"
            font-family="monospace"
            font-size="11"
        >
            austine@github ~ neofetch
        </text>
        """
    )

    # ASCII logo
    logo_lines = []

    for index, line in enumerate(ASCII_LOGO):

        y = 90 + index * 25

        delay = index * 0.12

        logo_lines.append(
            f"""
            <text
                x="55"
                y="{y}"
                fill="#f0f6fc"
                font-family="monospace"
                font-size="20"
                font-weight="700"
                class="logo-line"
                style="animation-delay:{delay:.3f}s"
            >{escape_xml(line)}</text>
            """
        )

    elements.extend(logo_lines)

    # Information
    info_lines = []

    start_y = 85

    for index, (label, value) in enumerate(INFO):

        y = start_y + index * 32

        delay = 0.5 + index * 0.08

        info_lines.append(
            f"""
            <text
                x="260"
                y="{y}"
                fill="#8b949e"
                font-family="monospace"
                font-size="13"
                class="info-line"
                style="animation-delay:{delay:.3f}s"
            >{escape_xml(label)}:</text>

            <text
                x="370"
                y="{y}"
                fill="#f0f6fc"
                font-family="monospace"
                font-size="13"
                font-weight="700"
                class="info-line"
                style="animation-delay:{delay:.3f}s"
            >{escape_xml(value)}</text>
            """
        )

    elements.extend(info_lines)

    content = "\n".join(elements)

    return f"""<?xml version="1.0" encoding="UTF-8"?>

<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{width}"
    height="{height}"
    viewBox="0 0 {width} {height}"
    role="img"
    aria-label="Neofetch-style developer information for Austine Otieno"
>

<style>

.logo-line,
.info-line {{
    opacity: 0;

    animation:
        reveal
        0.35s
        ease-out
        forwards;
}}

@keyframes reveal {{

    from {{
        opacity: 0;
        transform: translateX(-8px);
    }}

    to {{
        opacity: 1;
        transform: translateX(0);
    }}

}}

@media (prefers-reduced-motion: reduce) {{

    .logo-line,
    .info-line {{
        animation: none;
        opacity: 1;
    }}

}}

</style>

{content}

</svg>
"""


def main():

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Generating neofetch card...")

    svg = generate_svg()

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print("Neofetch generated successfully.")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()