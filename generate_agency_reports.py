#!/usr/bin/env python3
"""
Agency Intelligence Report Generator
Generates personalized secret-URL reports for each BainUltra agency
"""

import json
import hashlib
import os
from datetime import datetime
from pathlib import Path

# Territory mapping
TERRITORIES = {
    "Phoenix S G, LLC": "NY/NJ/PA",
    "Alpha Sales": "New England",
    "Premier Decorative Group": "CA/AZ/NV",
    "BU Agent - Ontario": "ON",
    "The Shae Group": "IL/WI/MN",
    "DME Marketing": "BC/AB/SK/MB",
    "ADream Decor": "TX/LA/OK/AR",
    "ClearWater Sales LLC": "MI/OH/W.PA",
    "The Bridge Agency": "NC/SC/AL/MS/TN",
    "VJS Marketing": "MO/IA/KS/NE",
    "Summit Architectural Resource": "CO/NM",
    "Personal Touch Sales": "FL",
    "BainUltra Corporate": "Direct/Other",
    "Greater Montreal": "QC - Montreal",
    "JDL Associates": "VA/MD/DC/WV",
    "The Bridge Agency GA": "GA",
    "D'Antoni Sales Group": "IN/TN/KY",
    "The Rain Company": "WA/OR/ID/MT/AK",
    "Quebec excluding MTL (+ Ottawa Region)": "QC/Ottawa",
    "S & D Lighting Group": "NB/NS/NL/PE",
    "Utah - Wyoming": "UT/WY",
    "Upstate NewYork": "Upstate NY",
    "Mexico": "MX",
    "Hawaii": "HI"
}

# 10-year revenue data (from Salesforce query)
AGENCY_YEARLY_DATA = {
    "ADream Decor": {
        2015: 1840908, 2016: 1688457, 2017: 1515152, 2018: 1406336, 2019: 1391078,
        2020: 1242748, 2021: 1293982, 2022: 1609017, 2023: 1335992, 2024: 1052664, 2025: 989144
    },
    "Alpha Sales": {
        2015: 1824809, 2016: 1809215, 2017: 1689887, 2018: 1399005, 2019: 1496353,
        2020: 1415004, 2021: 2299412, 2022: 2533397, 2023: 2059569, 2024: 1792908, 2025: 1732280
    },
    "BU Agent - Ontario": {
        2015: 1570645, 2016: 1778916, 2017: 1839712, 2018: 1662684, 2019: 1866501,
        2020: 1504861, 2021: 1983312, 2022: 2123414, 2023: 1660353, 2024: 1535104, 2025: 1168408
    },
    "BainUltra Corporate": {
        2015: 144165, 2016: 139774, 2017: 167539, 2018: 220529, 2019: 179427,
        2020: 308981, 2021: 521776, 2022: 529512, 2023: 457607, 2024: 439785, 2025: 475949
    },
    "ClearWater Sales LLC": {
        2015: 1312640, 2016: 1341114, 2017: 1324554, 2018: 1305721, 2019: 1261017,
        2020: 1054683, 2021: 1390552, 2022: 1603245, 2023: 1215017, 2024: 1258707, 2025: 928555
    },
    "D'Antoni Sales Group": {
        2015: 241392, 2016: 234080, 2017: 260661, 2018: 218381, 2019: 188756,
        2020: 235643, 2021: 229337, 2022: 282622, 2023: 222968, 2024: 242988, 2025: 170917
    },
    "DME Marketing": {
        2015: 1821604, 2016: 1680967, 2017: 1585074, 2018: 1560376, 2019: 1171687,
        2020: 1042157, 2021: 1374454, 2022: 1320489, 2023: 1225413, 2024: 1068560, 2025: 943288
    },
    "Greater Montreal": {
        2015: 302185, 2016: 379970, 2017: 384681, 2018: 281677, 2019: 263840,
        2020: 328375, 2021: 476618, 2022: 431334, 2023: 401597, 2024: 394130, 2025: 317353
    },
    "Hawaii": {
        2015: 10630, 2016: 4284, 2017: 2979, 2018: 4636, 2019: 2205,
        2020: 0, 2021: 8276, 2022: 10361, 2023: 8171, 2024: 15015, 2025: 15120
    },
    "JDL Associates": {
        2015: 559619, 2016: 505187, 2017: 501523, 2018: 480587, 2019: 443498,
        2020: 455472, 2021: 551099, 2022: 517529, 2023: 400408, 2024: 353847, 2025: 305407
    },
    "Mexico": {
        2015: 0, 2016: 0, 2017: 0, 2018: 0, 2019: 0,
        2020: 0, 2021: 0, 2022: 0, 2023: 5751, 2024: 31602, 2025: 14085
    },
    "Personal Touch Sales": {
        2015: 428138, 2016: 551746, 2017: 398063, 2018: 455597, 2019: 411493,
        2020: 483952, 2021: 473817, 2022: 695754, 2023: 567520, 2024: 616383, 2025: 530052
    },
    "Phoenix S G, LLC": {
        2015: 3054402, 2016: 2716761, 2017: 2850077, 2018: 3166851, 2019: 2778057,
        2020: 2610870, 2021: 3803528, 2022: 3648411, 2023: 2646655, 2024: 2506556, 2025: 2025316
    },
    "Premier Decorative Group": {
        2015: 2051853, 2016: 2312562, 2017: 2046706, 2018: 1803617, 2019: 1836056,
        2020: 1840180, 2021: 2414631, 2022: 2715550, 2023: 1837015, 2024: 1650812, 2025: 1509278
    },
    "Quebec excluding MTL (+ Ottawa Region)": {
        2015: 227645, 2016: 226016, 2017: 188036, 2018: 125865, 2019: 113862,
        2020: 119700, 2021: 180392, 2022: 220053, 2023: 156973, 2024: 167443, 2025: 137152
    },
    "S & D Lighting Group": {
        2015: 77087, 2016: 79093, 2017: 60456, 2018: 48635, 2019: 70224,
        2020: 43364, 2021: 91760, 2022: 122607, 2023: 64444, 2024: 93196, 2025: 88738
    },
    "Summit Architectural Resource": {
        2015: 383528, 2016: 504104, 2017: 491875, 2018: 532459, 2019: 520519,
        2020: 597791, 2021: 661376, 2022: 820077, 2023: 588282, 2024: 553182, 2025: 601218
    },
    "The Bridge Agency": {
        2015: 702075, 2016: 674991, 2017: 615462, 2018: 611878, 2019: 650182,
        2020: 670500, 2021: 897745, 2022: 1075421, 2023: 833866, 2024: 833098, 2025: 778170
    },
    "The Bridge Agency GA": {
        2015: 218430, 2016: 266855, 2017: 271999, 2018: 320455, 2019: 243583,
        2020: 219908, 2021: 221970, 2022: 369504, 2023: 211442, 2024: 254298, 2025: 206510
    },
    "The Rain Company": {
        2015: 345770, 2016: 188485, 2017: 136860, 2018: 172661, 2019: 185531,
        2020: 193380, 2021: 186157, 2022: 324528, 2023: 192066, 2024: 185713, 2025: 152049
    },
    "The Shae Group": {
        2015: 1055141, 2016: 1036456, 2017: 1277676, 2018: 1128502, 2019: 979012,
        2020: 1040739, 2021: 1604171, 2022: 1678870, 2023: 1276532, 2024: 1051655, 2025: 1085867
    },
    "Upstate NewYork": {
        2015: 190721, 2016: 101624, 2017: 93362, 2018: 76785, 2019: 100682,
        2020: 110359, 2021: 121887, 2022: 132441, 2023: 65515, 2024: 50693, 2025: 47700
    },
    "Utah - Wyoming": {
        2015: 104957, 2016: 119328, 2017: 93468, 2018: 130427, 2019: 105688,
        2020: 102379, 2021: 98268, 2022: 172276, 2023: 136379, 2024: 87944, 2025: 82267
    },
    "VJS Marketing": {
        2015: 817788, 2016: 766621, 2017: 748882, 2018: 625548, 2019: 619641,
        2020: 500415, 2021: 753406, 2022: 949627, 2023: 754251, 2024: 804480, 2025: 711216
    }
}

def generate_token(agency_name):
    """Generate a unique secret token for each agency"""
    secret = f"bainultra-2026-{agency_name}-secret"
    return hashlib.sha256(secret.encode()).hexdigest()[:12]

def calculate_metrics(agency_name, yearly_data):
    """Calculate all metrics for an agency"""
    years = sorted(yearly_data.keys())

    # Current year and comparisons
    rev_2025 = yearly_data.get(2025, 0)
    rev_2024 = yearly_data.get(2024, 0)

    # 10-year average (2015-2024)
    ten_year_values = [yearly_data.get(y, 0) for y in range(2015, 2025)]
    ten_year_avg = sum(ten_year_values) / len([v for v in ten_year_values if v > 0]) if any(ten_year_values) else 0

    # Pre-COVID average (2015-2019)
    pre_covid_values = [yearly_data.get(y, 0) for y in range(2015, 2020)]
    pre_covid_avg = sum(pre_covid_values) / len([v for v in pre_covid_values if v > 0]) if any(pre_covid_values) else 0

    # COVID peak (2021-2022)
    covid_peak = max(yearly_data.get(2021, 0), yearly_data.get(2022, 0))

    # YoY change
    yoy_change = ((rev_2025 - rev_2024) / rev_2024 * 100) if rev_2024 > 0 else 0

    # vs 10-year average
    vs_ten_year = ((rev_2025 - ten_year_avg) / ten_year_avg * 100) if ten_year_avg > 0 else 0

    # Trend (growing/stable/declining)
    if yoy_change > 3:
        trend = "growing"
    elif yoy_change < -10:
        trend = "declining"
    else:
        trend = "stable"

    return {
        "rev_2025": rev_2025,
        "rev_2024": rev_2024,
        "yoy_change": yoy_change,
        "ten_year_avg": ten_year_avg,
        "vs_ten_year": vs_ten_year,
        "pre_covid_avg": pre_covid_avg,
        "covid_peak": covid_peak,
        "trend": trend,
        "yearly_data": yearly_data
    }

def format_currency(amount):
    """Format number as currency"""
    if amount >= 1000000:
        return f"${amount/1000000:.1f}M"
    elif amount >= 1000:
        return f"${amount/1000:.0f}K"
    else:
        return f"${amount:.0f}"

def generate_html_report(agency_name, metrics, token):
    """Generate HTML report for an agency"""
    territory = TERRITORIES.get(agency_name, "Unknown")

    # Determine trend color
    if metrics["trend"] == "growing":
        trend_color = "#10b981"
        trend_icon = "+"
    elif metrics["trend"] == "declining":
        trend_color = "#ef4444"
        trend_icon = ""
    else:
        trend_color = "#eab308"
        trend_icon = ""

    # Build yearly chart data
    years = sorted(metrics["yearly_data"].keys())
    chart_labels = [str(y) for y in years]
    chart_data = [metrics["yearly_data"][y] / 1000 for y in years]  # In thousands

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BainUltra | {agency_name} Territory Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-dark: #0a0a0f;
            --bg-card: #12121a;
            --bg-card-hover: #1a1a25;
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --accent-yellow: #eab308;
            --accent-purple: #8b5cf6;
            --text-primary: #ffffff;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --border-color: #1e293b;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            text-align: center;
            margin-bottom: 3rem;
            padding: 2rem;
            background: linear-gradient(135deg, rgba(59,130,246,0.1), rgba(139,92,246,0.1));
            border-radius: 16px;
            border: 1px solid var(--border-color);
        }}
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }}
        .header .territory {{
            color: var(--text-secondary);
            font-size: 1.25rem;
        }}
        .header .date {{
            color: var(--text-muted);
            font-size: 0.875rem;
            margin-top: 1rem;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        @media (max-width: 900px) {{ .metrics-grid {{ grid-template-columns: repeat(2, 1fr); }} }}
        @media (max-width: 500px) {{ .metrics-grid {{ grid-template-columns: 1fr; }} }}
        .metric-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
        }}
        .metric-label {{
            font-size: 0.75rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
        }}
        .metric-subtext {{
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-top: 0.25rem;
        }}
        .positive {{ color: var(--accent-green); }}
        .negative {{ color: var(--accent-red); }}
        .neutral {{ color: var(--accent-yellow); }}
        .chart-container {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        .chart-title {{
            font-size: 1.125rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }}
        .section {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        .section-title {{
            font-size: 1.25rem;
            font-weight: 700;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .insight-box {{
            background: rgba(59,130,246,0.1);
            border-left: 4px solid var(--accent-blue);
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin: 1rem 0;
        }}
        .insight-box p {{
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}
        .stats-row {{
            display: flex;
            gap: 2rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }}
        .stat-item {{
            flex: 1;
            min-width: 150px;
        }}
        .stat-label {{
            font-size: 0.75rem;
            color: var(--text-muted);
        }}
        .stat-value {{
            font-size: 1.5rem;
            font-weight: 600;
        }}
        .footer {{
            text-align: center;
            color: var(--text-muted);
            font-size: 0.75rem;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid var(--border-color);
        }}
        .confidential {{
            background: rgba(239,68,68,0.1);
            border: 1px solid rgba(239,68,68,0.3);
            color: #fca5a5;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-size: 0.75rem;
            display: inline-block;
            margin-bottom: 1rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="confidential">CONFIDENTIAL - For {agency_name} internal use only</div>

        <div class="header">
            <h1>{agency_name}</h1>
            <div class="territory">Territory: {territory}</div>
            <div class="date">Report Generated: {datetime.now().strftime('%B %d, %Y')}</div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">2025 YTD Revenue</div>
                <div class="metric-value">{format_currency(metrics["rev_2025"])}</div>
                <div class="metric-subtext">Through Dec 23, 2025</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">vs 2024</div>
                <div class="metric-value {'positive' if metrics['yoy_change'] > 0 else 'negative' if metrics['yoy_change'] < -5 else 'neutral'}">{trend_icon}{metrics["yoy_change"]:.1f}%</div>
                <div class="metric-subtext">{format_currency(abs(metrics["rev_2025"] - metrics["rev_2024"]))} {'more' if metrics["yoy_change"] > 0 else 'less'}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">vs 10-Year Avg</div>
                <div class="metric-value {'positive' if metrics['vs_ten_year'] > 0 else 'negative' if metrics['vs_ten_year'] < -5 else 'neutral'}">{'+' if metrics['vs_ten_year'] > 0 else ''}{metrics["vs_ten_year"]:.1f}%</div>
                <div class="metric-subtext">Avg: {format_currency(metrics["ten_year_avg"])}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Trend</div>
                <div class="metric-value" style="color: {trend_color};">{metrics["trend"].upper()}</div>
                <div class="metric-subtext">Based on 3-year pattern</div>
            </div>
        </div>

        <div class="chart-container">
            <div class="chart-title">10-Year Revenue Trend</div>
            <canvas id="revenueChart"></canvas>
        </div>

        <div class="section">
            <div class="section-title">Key Insights</div>
            <div class="insight-box">
                <p><strong>Context:</strong> {'Your territory is performing above the 10-year average.' if metrics['vs_ten_year'] > 0 else 'Your territory has returned to pre-COVID baseline levels.' if metrics['vs_ten_year'] > -15 else 'Your territory is significantly below historical averages - investigation needed.'}</p>
            </div>
            <div class="stats-row">
                <div class="stat-item">
                    <div class="stat-label">Pre-COVID Avg (2015-2019)</div>
                    <div class="stat-value">{format_currency(metrics["pre_covid_avg"])}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">COVID Peak (2021-22)</div>
                    <div class="stat-value">{format_currency(metrics["covid_peak"])}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">Current vs Peak</div>
                    <div class="stat-value negative">{((metrics["rev_2025"] - metrics["covid_peak"]) / metrics["covid_peak"] * 100) if metrics["covid_peak"] > 0 else 0:.0f}%</div>
                </div>
            </div>
        </div>

        <div class="section">
            <div class="section-title">Recommendations</div>
            <ul style="color: var(--text-secondary); padding-left: 1.5rem;">
                {'<li style="margin-bottom: 0.5rem;">Continue current strategy - territory is growing</li>' if metrics["trend"] == "growing" else ''}
                {'<li style="margin-bottom: 0.5rem;">Focus on reactivating dormant accounts</li>' if metrics["trend"] == "declining" else ''}
                <li style="margin-bottom: 0.5rem;">Q1 (Jan-Mar) is historically your strongest period - prepare promotional push</li>
                <li style="margin-bottom: 0.5rem;">Review top 5 accounts for growth opportunities</li>
                <li style="margin-bottom: 0.5rem;">Identify any churned accounts from 2023-2024 for win-back campaigns</li>
            </ul>
        </div>

        <div class="footer">
            <p>BainUltra Agency Intelligence Report</p>
            <p>Data Source: Salesforce CRM | Report ID: {token}</p>
            <p style="margin-top: 0.5rem;">Questions? Contact your BainUltra Territory Manager</p>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('revenueChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {chart_labels},
                datasets: [{{
                    label: 'Revenue ($K)',
                    data: {chart_data},
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4,
                    pointBackgroundColor: '#3b82f6'
                }}, {{
                    label: '10-Year Average',
                    data: Array({len(years)}).fill({metrics["ten_year_avg"]/1000:.0f}),
                    borderColor: '#94a3b8',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 2.5,
                plugins: {{
                    legend: {{
                        position: 'top',
                        labels: {{ color: '#94a3b8' }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.dataset.label + ': $' + context.parsed.y.toLocaleString() + 'K';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        grid: {{ color: '#1e293b' }},
                        ticks: {{ color: '#94a3b8' }}
                    }},
                    y: {{
                        grid: {{ color: '#1e293b' }},
                        ticks: {{
                            color: '#94a3b8',
                            callback: function(value) {{
                                return '$' + value.toLocaleString() + 'K';
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''

    return html

def generate_index_page(agencies_data):
    """Generate internal index page with all agency links"""
    rows = ""
    for agency, data in sorted(agencies_data.items(), key=lambda x: x[1]["metrics"]["rev_2025"], reverse=True):
        metrics = data["metrics"]
        trend_class = "positive" if metrics["trend"] == "growing" else "negative" if metrics["trend"] == "declining" else "neutral"
        rows += f'''
            <tr>
                <td><strong>{agency}</strong><br><span style="color: var(--text-muted); font-size: 0.75rem;">{data["territory"]}</span></td>
                <td>{format_currency(metrics["rev_2025"])}</td>
                <td class="{trend_class}">{metrics["yoy_change"]:+.1f}%</td>
                <td><a href="{data["token"]}.html" style="color: var(--accent-blue);">View Report</a></td>
            </tr>'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BainUltra | Agency Reports Index (Internal)</title>
    <style>
        :root {{
            --bg-dark: #0a0a0f;
            --bg-card: #12121a;
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --accent-yellow: #eab308;
            --text-primary: #ffffff;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --border-color: #1e293b;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            padding: 2rem;
        }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        h1 {{ margin-bottom: 2rem; }}
        .warning {{
            background: rgba(239,68,68,0.1);
            border: 1px solid rgba(239,68,68,0.3);
            color: #fca5a5;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: var(--bg-card);
            border-radius: 12px;
            overflow: hidden;
        }}
        th, td {{
            padding: 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        th {{
            background: rgba(59,130,246,0.1);
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
        }}
        .positive {{ color: var(--accent-green); }}
        .negative {{ color: var(--accent-red); }}
        .neutral {{ color: var(--accent-yellow); }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Agency Reports Index</h1>
        <div class="warning">
            <strong>INTERNAL USE ONLY</strong> - Do not share this page. Each agency report has a unique secret URL.
        </div>
        <table>
            <thead>
                <tr>
                    <th>Agency</th>
                    <th>2025 Revenue</th>
                    <th>YoY Change</th>
                    <th>Report</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        <p style="color: var(--text-muted); margin-top: 2rem; font-size: 0.875rem;">
            Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}
        </p>
    </div>
</body>
</html>'''
    return html

def main():
    output_dir = Path("/Users/jm/powerhouse/salesforce-dashboard/ceo-dashboard/sales-analysis-presentation/agency-reports")
    output_dir.mkdir(exist_ok=True)

    agencies_data = {}

    # Process each agency
    for agency_name, yearly_data in AGENCY_YEARLY_DATA.items():
        # Skip agencies with minimal data
        if sum(yearly_data.values()) < 50000:
            continue

        token = generate_token(agency_name)
        metrics = calculate_metrics(agency_name, yearly_data)
        territory = TERRITORIES.get(agency_name, "Unknown")

        agencies_data[agency_name] = {
            "token": token,
            "territory": territory,
            "metrics": metrics
        }

        # Generate HTML report
        html = generate_html_report(agency_name, metrics, token)

        # Write to file
        output_file = output_dir / f"{token}.html"
        with open(output_file, "w") as f:
            f.write(html)

        print(f"Generated: {agency_name} -> {token}.html")

    # Generate index page
    index_html = generate_index_page(agencies_data)
    with open(output_dir / "_index.html", "w") as f:
        f.write(index_html)

    print(f"\nGenerated {len(agencies_data)} agency reports")
    print(f"Index page: {output_dir}/_index.html")

    # Print URL mapping
    print("\n=== Agency URL Mapping ===")
    for agency, data in sorted(agencies_data.items()):
        print(f"{agency}: {data['token']}.html")

if __name__ == "__main__":
    main()
