from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
import requests


USERNAME = "Austine192-A"
OUTPUT = Path("assets/contributions/contributions.svg")

GRAPHQL_URL = "https://api.github.com/graphql"

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            color
            contributionLevel
          }
        }
      }
    }
  }
}
"""


def fetch_contributions():
    token = os.getenv("GITHUB_TOKEN")

    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN is not set. Set it before running the generator."
        )

    today = datetime.now(timezone.utc)
    one_year_ago = today - timedelta(days=365)

    response = requests.post(
        GRAPHQL_URL,
        json={
            "query": QUERY,
            "variables": {
                "login": USERNAME,
                "from": one_year_ago.isoformat(),
                "to": today.isoformat(),
            },
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise RuntimeError(data["errors"])

    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def escape_xml(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def generate_svg(calendar):
    cell_size = 11
    gap = 3
    step = cell_size + gap

    left = 36
    top = 48

    columns = len(calendar["weeks"])
    rows = 7

    graph_width = columns * step
    graph_height = rows * step

    width = left + graph_width + 18
    height = top + graph_height + 48

    total = calendar["totalContributions"]

    month_labels = []
    seen_months = set()

    for column, week in enumerate(calendar["weeks"]):
        first_day = week["contributionDays"][0]
        date = datetime.strptime(first_day["date"], "%Y-%m-%d")

        key = (date.year, date.month)

        if key not in seen_months:
            seen_months.add(key)

            month_labels.append(
                {
                    "label": date.strftime("%b"),
                    "column": column,
                }
            )

    parts = [
        f'''<svg xmlns="http://www.w3.org/2000/svg"
        width="{width}"
        height="{height}"
        viewBox="0 0 {width} {height}"
        role="img"
        aria-label="GitHub contribution calendar for {escape_xml(USERNAME)}">''',

        """
        <style>
            :root {
                color-scheme: light dark;
            }

            .title {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                    Helvetica, Arial, sans-serif;
                font-size: 14px;
                font-weight: 600;
                fill: #1f2328;
            }

            .month,
            .weekday,
            .legend {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                    Helvetica, Arial, sans-serif;
                fill: #656d76;
            }

            .month {
                font-size: 10px;
            }

            .weekday {
                font-size: 9px;
            }

            .legend {
                font-size: 9px;
            }

            .cell {
                stroke: rgba(27, 31, 36, 0.06);
                stroke-width: 1;
                rx: 2;
                ry: 2;
                transform-box: fill-box;
                transform-origin: center;
                opacity: 0;
                animation: reveal 0.4s ease forwards;
            }

            .empty-cell {
                fill: #ebedf0 !important;
            }

            .legend-empty {
                fill: #ebedf0;
            }

            @keyframes reveal {
                from {
                    opacity: 0;
                    transform: scale(0.65);
                }

                to {
                    opacity: 1;
                    transform: scale(1);
                }
            }

            @media (prefers-color-scheme: dark) {
                .title {
                    fill: #f0f6fc;
                }

                .month,
                .weekday,
                .legend {
                    fill: #8b949e;
                }

                .cell {
                    stroke: rgba(255, 255, 255, 0.08);
                }

                .empty-cell,
                .legend-empty {
                    fill: #161b22 !important;
                }
            }
        </style>
        """,

        f'''
        <text x="0" y="18" class="title">
            {total:,} contributions in the last year
        </text>
        ''',
    ]

    # Month labels
    for month in month_labels:
        x = left + month["column"] * step

        parts.append(
            f'''
            <text x="{x}" y="35" class="month">
                {escape_xml(month["label"])}
            </text>
            '''
        )

    # Weekday labels
    weekday_labels = [
        (1, "Mon"),
        (3, "Wed"),
        (5, "Fri"),
    ]

    for row, label in weekday_labels:
        y = top + row * step + 8

        parts.append(
            f'''
            <text x="0" y="{y}" class="weekday">
                {label}
            </text>
            '''
        )

    # Contribution cells
    animation_index = 0

    for column, week in enumerate(calendar["weeks"]):
        for row, day in enumerate(week["contributionDays"]):

            x = left + column * step
            y = top + row * step

            is_empty = day["contributionLevel"] == "NONE"

            # Active cells use GitHub's exact color.
            # Empty cells use GitHub's theme-aware background.
            color = "#ebedf0" if is_empty else day["color"]

            cell_class = "cell empty-cell" if is_empty else "cell"

            count = day["contributionCount"]
            date = day["date"]

            delay = animation_index * 0.008

            contribution_word = (
                "contribution" if count == 1 else "contributions"
            )

            parts.append(
                f'''
                <rect
                    class="{cell_class}"
                    x="{x}"
                    y="{y}"
                    width="{cell_size}"
                    height="{cell_size}"
                    fill="{escape_xml(color)}"
                    style="animation-delay:{delay:.3f}s"
                >
                    <title>
                        {count} {contribution_word} on {escape_xml(date)}
                    </title>
                </rect>
                '''
            )

            animation_index += 1

    # Legend
    legend_y = top + graph_height + 27

    parts.append(
        f'''
        <text x="0" y="{legend_y + 9}" class="legend">
            Less
        </text>
        '''
    )

    legend_colors = [
        "#ebedf0",
        "#9be9a8",
        "#40c463",
        "#30a14e",
        "#216e39",
    ]

    legend_start = 28

    for index, color in enumerate(legend_colors):
        x = legend_start + index * 17

        legend_class = "legend-empty" if index == 0 else ""

        parts.append(
            f'''
            <rect
                class="{legend_class}"
                x="{x}"
                y="{legend_y}"
                width="11"
                height="11"
                rx="2"
                ry="2"
                fill="{color}"
            />
            '''
        )

    parts.append(
        f'''
        <text
            x="{legend_start + len(legend_colors) * 17 + 4}"
            y="{legend_y + 9}"
            class="legend"
        >
            More
        </text>
        '''
    )

    parts.append("</svg>")

    return "\n".join(parts)


def main():
    calendar = fetch_contributions()

    svg = generate_svg(calendar)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg, encoding="utf-8")

    print(f"Generated: {OUTPUT}")
    print(f"Total contributions: {calendar['totalContributions']}")


if __name__ == "__main__":
    main()