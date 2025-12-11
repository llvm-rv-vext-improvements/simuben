#!/usr/bin/env python3

# This is a LLM-generated file. Do not edit it.
# Just throw it away and regenerate or rewrite.

import argparse
import sys
import csv
import html
from datetime import datetime

COLUMN_MAP = {
    "run_name": "Benchmark",
    "instructions_old": "Instructions (Old)",
    "instructions_new": "Instructions (New)",
    "instructions_diff_absolute": "Instructions Diff (Abs)",
    "instructions_diff_relative": "Instructions Diff (%)",
    "cycles_old": "Cycles (Old)",
    "cycles_new": "Cycles (New)",
    "cycles_diff_absolute": "Cycles Diff (Abs)",
    "cycles_diff_relative": "Cycles Diff (%)",
}

COLOR_CODED_COLUMNS = {
    "instructions_diff_absolute",
    "instructions_diff_relative",
    "cycles_diff_absolute",
    "cycles_diff_relative",
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SimuBen Report {time}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            background-color: #f8f9fa;
            color: #212529;
        }}
        .container {{
            max-width: 1200px;
            margin: 20px auto;
            padding: 20px;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #343a40;
            border-bottom: 2px solid #dee2e6;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px 15px;
            border: 1px solid #dee2e6;
            text-align: left;
            vertical-align: middle;
        }}
        thead {{
            background-color: #e9ecef;
        }}
        th button {{
            background: none;
            border: none;
            font-weight: bold;
            font-size: inherit;
            font-family: inherit;
            cursor: pointer;
            padding: 0;
            margin: 0;
            text-align: left;
            width: 100%;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        th button .sort-indicator {{
            color: #adb5bd;
            min-width: 1em;
        }}
        tbody tr td:first-child {{
            font-weight: bold;
        }}
        .positive {{
            color: #d9534f;
        }}
        .negative {{
            color: #5cb85c;
        }}
        .neutral {{
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>SimuBen Report {time}</h1>
        <table id="benchmarkTable">
            {table_head}
            {table_body}
        </table>
        <p><var>{old}</var> (old) vs <var>{new}</var> (new)</p>
    </div>
    <script>
        const sortState = {{}};

        function parseValue(value) {{
            const cleanedValue = value.replace(/%/g, '').trim();
            const num = parseFloat(cleanedValue);
            return isNaN(num) ? value.toLowerCase() : num;
        }}

        function sortTable(columnIndex) {{
            const table = document.getElementById('benchmarkTable');
            const tbody = table.tBodies[0];
            const rows = Array.from(tbody.rows);

            const currentDirection = sortState[columnIndex] || 1;
            const direction = currentDirection === 1 ? -1 : 1;
            sortState[columnIndex] = direction;

            for (const key in sortState) {{
                if (key != columnIndex) {{
                    delete sortState[key];
                }}
            }}

            rows.sort((rowA, rowB) => {{
                const valA = parseValue(rowA.cells[columnIndex].textContent);
                const valB = parseValue(rowB.cells[columnIndex].textContent);

                let comparison = 0;
                if (typeof valA === 'number' && typeof valB === 'number') {{
                    comparison = valA - valB;
                }} else {{
                    comparison = String(valA).localeCompare(String(valB));
                }}

                return comparison * direction;
            }});

            document.querySelectorAll('th button .sort-indicator').forEach(span => {{
                span.textContent = '';
            }});
            const indicator = table.tHead.rows[0].cells[columnIndex].querySelector('.sort-indicator');
            indicator.textContent = direction === -1 ? '▲' : '▼';

            tbody.innerHTML = '';
            rows.forEach(row => tbody.appendChild(row));
        }}
    </script>
</body>
</html>
"""


def generate_table_parts(header, data):
    theads = ["<thead><tr>"]
    for i, col_name in enumerate(header):
        display_name = COLUMN_MAP.get(col_name) or col_name
        theads.append(
            f'<th><button onclick="sortTable({i})">'
            f"<span>{html.escape(display_name)}</span>"
            f'<span class="sort-indicator"></span></button></th>'
        )
    theads.append("</tr></thead>")
    table_head = "".join(theads)

    tbodys = ["<tbody>"]
    color_coded_indices = {i for i, h in enumerate(header) if h in COLOR_CODED_COLUMNS}

    for row in data:
        tbodys.append("<tr>")
        for i, cell_value in enumerate(row):
            class_attr = ""
            if i in color_coded_indices:
                try:
                    numeric_value = float(cell_value.replace("%", ""))
                    if numeric_value > 0:
                        class_attr = ' class="positive"'
                    elif numeric_value < 0:
                        class_attr = ' class="negative"'
                    else:
                        class_attr = ' class="neutral"'
                except (ValueError, TypeError):
                    pass
            tbodys.append(f"<td{class_attr}>{html.escape(cell_value)}</td>")
        tbodys.append("</tr>")
    tbodys.append("</tbody>")
    table_body = "".join(tbodys)

    return table_head, table_body


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--old-tag",
        required=True,
    )
    parser.add_argument(
        "-n",
        "--new-tag",
        required=True,
    )
    return parser.parse_args()


if __name__ == "__main__":
    try:
        args = parse_args()

        csv_content = sys.stdin.read()

        if not csv_content.strip():
            print("Error: Received empty input from stdin.", file=sys.stderr)
            sys.exit(1)

        reader = csv.reader(csv_content.strip().splitlines())

        header = next(reader)
        data = list(reader)

        table_head, table_body = generate_table_parts(header, data)

        final_html = HTML_TEMPLATE.format(
            table_head=table_head,
            table_body=table_body,
            time=datetime.now().strftime("%Y-%m-%d %H:%M"),
            old=args.old_tag,
            new=args.new_tag,
        )
        print(final_html)

    except StopIteration:
        print("Error: CSV input is empty or contains only a header.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
