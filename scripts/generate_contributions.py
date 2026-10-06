from pathlib import Path
from datetime import datetime, timedelta, timezone
import os
import requests


ROOT = Path(__file__).resolve().parent.parent

OUTPUT = (
    ROOT
    / "assets"
    / "contributions"
    / "contributions.svg"
)

GITHUB_USERNAME = "Austine192-A"

GRAPHQL_URL = "https://api.github.com/graphql"


def get_github_token():
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN environment variable is not set."
        )

    return token


def fetch_contributions(token):
    today = datetime.now(timezone.utc).date()

    start_date = today - timedelta(days=365)

    query = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
        user(login: $login) {
            contributionsCollection(
                from: $from
                to: $to
            ) {
                contributionCalendar {
                    totalContributions

                    weeks {
                        contributionDays {
                            contributionCount
                            date
                            weekday
                        }
                    }
                }
            }
        }
    }
    """

    variables = {
        "login": GITHUB_USERNAME,
        "from": f"{start_date}T00:00:00Z",
        "to": f"{today}T23:59:59Z",
    }

    response = requests.post(
        GRAPHQL_URL,
        json={
            "query": query,
            "variables": variables,
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    response.raise_for_status()

    payload = response.json()

    if "errors" in payload:
        raise RuntimeError(
            f"GitHub GraphQL error: {payload['errors']}"
        )

    user = payload.get("data", {}).get("user")

    if not user:
        raise RuntimeError(
            f"GitHub user '{GITHUB_USERNAME}' was not found."
        )

    calendar = (
        user[
            "contributionsCollection"
        ][
            "contributionCalendar"
        ]
    )

    return calendar


def contribution_level(count, maximum):
    if count == 0:
        return 0

    if maximum <= 0:
        return 0

    ratio = count / maximum

    if ratio <= 0.20:
        return 1

    if ratio <= 0.40:
        return 2

    if ratio <= 0.70:
        return 3

    return 4


def build_svg(calendar):
    weeks = calendar["weeks"]

    maximum = max(
        (
            day["contributionCount"]
            for week in weeks
            for day in week["contributionDays"]
        ),
        default=0,
    )

    cell_size = 12
    gap = 3

    left_padding = 45
    top_padding = 35

    width = (
        left_padding
        + len(weeks) * (cell_size + gap)
        + 20
    )

    height = (
        top_padding
        + 7 * (cell_size + gap)
        + 35
    )

    # Terminal-inspired monochrome palette.
    colors = [
        "#161b22",
        "#30363d",
        "#6e7681",
        "#8b949e",
        "#f0f6fc",
    ]

    cells = []

    for week_index, week in enumerate(weeks):

        for day in week["contributionDays"]:

            weekday = day["weekday"]

            count = day["contributionCount"]

            level = contribution_level(
                count,
                maximum
            )

            x = (
                left_padding
                + week_index * (cell_size + gap)
            )

            y = (
                top_padding
                + weekday * (cell_size + gap)
            )

            date = day["date"]

            delay = (
                week_index * 0.025
                + weekday * 0.01
            )

            cells.append(
                f"""
                <rect
                    x="{x}"
                    y="{y}"
                    width="{cell_size}"
                    height="{cell_size}"
                    rx="2"
                    fill="{colors[level]}"
                    class="contribution-cell"
                    style="animation-delay:{delay:.3f}s"
                >
                    <title>
                        {count} contributions on {date}
                    </title>
                </rect>
                """
            )

    cells_markup = "\n".join(cells)

    total = calendar["totalContributions"]

    generated_at = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d %H:%M UTC")

    return f"""<?xml version="1.0" encoding="UTF-8"?>

<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{width}"
    height="{height}"
    viewBox="0 0 {width} {height}"
    role="img"
    aria-label="GitHub contribution activity for {GITHUB_USERNAME}"
>

<rect
    width="100%"
    height="100%"
    rx="8"
    fill="#0d1117"
/>

<style>

.contribution-cell {{
    opacity: 0;
    transform-box: fill-box;
    transform-origin: center;
    animation:
        revealCell
        0.25s
        steps(1, end)
        forwards;
}}

@keyframes revealCell {{

    from {{
        opacity: 0;
        transform: scale(0.4);
    }}

    to {{
        opacity: 1;
        transform: scale(1);
    }}

}}

@media (prefers-reduced-motion: reduce) {{

    .contribution-cell {{
        animation: none;
        opacity: 1;
        transform: none;
    }}

}}

</style>

<text
    x="20"
    y="20"
    fill="#f0f6fc"
    font-family="monospace"
    font-size="13"
    font-weight="700"
>
    GITHUB CONTRIBUTIONS
</text>

<text
    x="{width - 20}"
    y="20"
    text-anchor="end"
    fill="#8b949e"
    font-family="monospace"
    font-size="11"
>
    {total} contributions
</text>

<g>

{cells_markup}

</g>

<text
    x="{width - 20}"
    y="{height - 8}"
    text-anchor="end"
    fill="#484f58"
    font-family="monospace"
    font-size="9"
>
    Generated {generated_at}
</text>

</svg>
"""


def main():

    print("======================================")
    print("  AUSTINE192-A // CONTRIBUTIONS")
    print("======================================")
    print()

    print("[1/3] Authenticating with GitHub...")

    token = get_github_token()

    print("      Authentication token found.")
    print()

    print("[2/3] Fetching contribution data...")

    calendar = fetch_contributions(token)

    print(
        f"      Total contributions: "
        f"{calendar['totalContributions']}"
    )

    print()

    print("[3/3] Generating SVG...")

    svg = build_svg(calendar)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

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