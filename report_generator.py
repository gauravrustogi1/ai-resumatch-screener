import os
from datetime import datetime


def generateHTML(outputWithScores: list[dict]) -> str:
    sorted_output = sorted(outputWithScores, key=lambda x: x.get('oScore', 0), reverse=True)

    rows = ''
    for i, o in enumerate(sorted_output):
        score = o.get('oScore', 'N/A')
        href = o.get('href', '#')
        meta = o.get('meta', '')
        matches_well = o.get('matches_well', '').replace('\n', '<br>')
        missing = o.get('missing', '').replace('\n', '<br>')

        score_val = float(score) if score != 'N/A' else 0
        if score_val >= 8:
            score_class = 'score-high'
        elif score_val >= 6:
            score_class = 'score-mid'
        else:
            score_class = 'score-low'

        job_slug = href.split('/j/')[-1].split('?')[0] if '/j/' in href else href
        job_title = ' '.join(word.capitalize() for word in job_slug.replace('-', ' ').split()[:-1])

        rows += f'''
        <tr>
            <td class="score-cell">
                <span class="score-badge {score_class}">{score}</span>
            </td>
            <td class="job-cell">
                <div class="job-header">
                    <a href="{href}" target="_blank" class="job-link">{job_title}</a>
                    <button class="expand-btn" onclick="toggleDetails('details_{i}')">▼ Details</button>
                </div>
                <div id="details_{i}" class="details-panel" style="display:none;">
                    <div class="detail-meta">{meta}</div>
                    <div class="detail-section">
                        <div class="detail-label match-label">✓ What Matches Well</div>
                        <div class="detail-content">{matches_well}</div>
                    </div>
                    <div class="detail-section">
                        <div class="detail-label missing-label">✗ What's Missing</div>
                        <div class="detail-content">{missing}</div>
                    </div>
                </div>
            </td>
        </tr>'''

    run_date = datetime.now().strftime('%d %B %Y, %I:%M %p')
    total = len(sorted_output)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Match Report — {run_date}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: #0f1117;
            color: #e2e8f0;
            min-height: 100vh;
            padding: 32px 24px;
        }}

        .header {{
            max-width: 900px;
            margin: 0 auto 32px auto;
            border-left: 4px solid #6366f1;
            padding-left: 20px;
        }}

        .header h1 {{
            font-size: 1.6rem;
            font-weight: 700;
            color: #f1f5f9;
            letter-spacing: -0.5px;
        }}

        .header .subtitle {{
            font-size: 0.85rem;
            color: #64748b;
            margin-top: 4px;
        }}

        .header .subtitle span {{
            color: #6366f1;
            font-weight: 600;
        }}

        table {{
            width: 100%;
            max-width: 900px;
            margin: 0 auto;
            border-collapse: collapse;
        }}

        thead tr {{
            background: #1e2130;
            border-bottom: 2px solid #6366f1;
        }}

        thead th {{
            padding: 12px 16px;
            text-align: left;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #64748b;
        }}

        tbody tr {{
            background: #161822;
            border-bottom: 1px solid #1e2130;
            transition: background 0.15s;
        }}

        tbody tr:hover {{
            background: #1a1d2e;
        }}

        .score-cell {{
            width: 80px;
            text-align: center;
            padding: 16px 8px;
            vertical-align: top;
        }}

        .score-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 48px;
            height: 48px;
            border-radius: 12px;
            font-size: 1.2rem;
            font-weight: 700;
            border: 2px solid transparent;
        }}

        .score-high {{
            background: #0f2a1a;
            color: #4ade80;
            border-color: #166534;
        }}

        .score-mid {{
            background: #1a1a0f;
            color: #facc15;
            border-color: #713f12;
        }}

        .score-low {{
            background: #1f0f0f;
            color: #f87171;
            border-color: #7f1d1d;
        }}

        .job-cell {{
            padding: 16px;
            vertical-align: top;
        }}

        .job-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
        }}

        .job-link {{
            color: #a5b4fc;
            text-decoration: none;
            font-size: 0.95rem;
            font-weight: 600;
            line-height: 1.4;
            flex: 1;
        }}

        .job-link:hover {{
            color: #c7d2fe;
            text-decoration: underline;
        }}

        .expand-btn {{
            background: #1e2130;
            border: 1px solid #2d3148;
            color: #94a3b8;
            font-size: 0.75rem;
            padding: 5px 12px;
            border-radius: 6px;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.15s;
            flex-shrink: 0;
        }}

        .expand-btn:hover {{
            background: #2d3148;
            color: #e2e8f0;
            border-color: #6366f1;
        }}

        .details-panel {{
            margin-top: 14px;
            border-top: 1px solid #1e2130;
            padding-top: 14px;
        }}

        .detail-meta {{
            font-size: 0.75rem;
            color: #475569;
            margin-bottom: 12px;
            font-style: italic;
        }}

        .detail-section {{
            margin-bottom: 12px;
        }}

        .detail-label {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 6px;
        }}

        .match-label {{ color: #4ade80; }}
        .missing-label {{ color: #f87171; }}

        .detail-content {{
            font-size: 0.83rem;
            color: #94a3b8;
            line-height: 1.7;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Job Match Report</h1>
        <div class="subtitle">
            Run on {run_date} &nbsp;·&nbsp;
            <span>{total}</span> job{'' if total == 1 else 's'} analysed
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th style="text-align:center;">Score</th>
                <th>Job</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>

    <script>
        function toggleDetails(id) {{
            const panel = document.getElementById(id);
            const btn = panel.previousElementSibling.querySelector('.expand-btn');
            if (panel.style.display === 'none') {{
                panel.style.display = 'block';
                btn.textContent = '▲ Close';
            }} else {{
                panel.style.display = 'none';
                btn.textContent = '▼ Details';
            }}
        }}
    </script>
</body>
</html>'''

    return html


def saveReport(htmlContent: str) -> str:
    downloads = os.path.expanduser('~/code/jobagent/reports')
    folder = os.path.join(downloads, '')
    os.makedirs(folder, exist_ok=True)
    filename = datetime.now().strftime('%Y%m%d') + '.html'
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(htmlContent)
    return filepath


def generateAndSaveReport(outputWithScores: list[dict]) -> str:
    html = generateHTML(outputWithScores)
    filepath = saveReport(html)
    print(f"Report saved: file://{filepath} ")
    return filepath
