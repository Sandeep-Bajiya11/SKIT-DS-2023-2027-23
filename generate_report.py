#!/usr/bin/env python3
"""Generate a Form-3-style report from Git history.

Weekly interval is the college evaluation week: Friday 00:00 through Thursday
23:59:59 in Asia/Kolkata. The report measures Git metadata, not code quality.
"""
from __future__ import annotations

import datetime as dt
import html
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)

IST = ZoneInfo("Asia/Kolkata")
COLLEGE_NAME = "Swami Keshvanand Institute of Technology, Management & Gramothan, Jaipur"
DEPARTMENT_NAME = "Department of Computer Science & Engineering"
REPO_ID = "SKIT-DS-2023-2027-23"


def repo_info():
    try:
        root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        name = Path(root).name
    except Exception:
        name = Path.cwd().name
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True,
            stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        branch = "unknown"
    return name, branch


def week_bounds(today=None):
    today = today or dt.datetime.now(IST).date()
    # Monday=0 ... Friday=4. Find the Friday on or before today.
    days_since_friday = (today.weekday() - 4) % 7
    friday = today - dt.timedelta(days=days_since_friday)
    thursday = friday + dt.timedelta(days=6)
    start = dt.datetime.combine(friday, dt.time.min, tzinfo=IST)
    end = dt.datetime.combine(thursday, dt.time(23, 59, 59), tzinfo=IST)
    return start, end


def git_metrics(interval):
    now = dt.datetime.now(IST)
    if interval == "weekly":
        start, end = week_bounds(now.date())
        # If generated before Friday ends, still report the current Friday-Thursday
        # cycle's commits so far; the scheduled run is Thursday night.
        since = start.isoformat()
        until = end.isoformat()
        scope = f"{start:%Y-%m-%d} 00:00 IST to {end:%Y-%m-%d} 23:59 IST"
    elif interval == "monthly":
        start_date = now.date() - dt.timedelta(days=30)
        since = dt.datetime.combine(start_date, dt.time.min, tzinfo=IST).isoformat()
        until = now.isoformat()
        scope = f"Last 30 days since {start_date:%Y-%m-%d} (IST)"
    else:
        since = None
        until = None
        scope = "Complete project lifecycle (all commits)"

    cmd = [
        "git", "log", "--no-merges",
        "--pretty=format:COMMIT%x1f%an%x1f%ae%x1f%aI%x1f%h%x1f%s",
        "--numstat",
    ]
    if since:
        cmd.append(f"--since={since}")
    if until:
        cmd.append(f"--until={until}")

    try:
        raw = subprocess.check_output(cmd, text=True, errors="replace")
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise RuntimeError("Git log failed. Run this script inside a Git repository with history.") from exc

    students = defaultdict(lambda: {
        "commits": 0, "added": 0, "deleted": 0, "days": set(), "logs": []
    })
    current = None
    for raw_line in raw.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("COMMIT\x1f"):
            parts = line.split("\x1f", 5)
            if len(parts) < 6:
                current = None
                continue
            _, author, email, iso_date, sha, subject = parts
            if "bot" in author.lower() or "github-actions" in email.lower():
                current = None
                continue
            try:
                stamp = dt.datetime.fromisoformat(iso_date.replace("Z", "+00:00")).astimezone(IST)
            except ValueError:
                current = None
                continue
            current = author
            item = students[current]
            item["commits"] += 1
            item["days"].add(stamp.date().isoformat())
            item["logs"].append((stamp.strftime("%Y-%m-%d"), sha, subject))
        elif current:
            parts = line.split("\t")
            if len(parts) == 3 and parts[0].isdigit() and parts[1].isdigit():
                students[current]["added"] += int(parts[0])
                students[current]["deleted"] += int(parts[1])

    return students, scope


def make_chart(students, path):
    names = list(students)
    fig, ax = plt.subplots(figsize=(8.5, 2.4))
    if names:
        net = [students[n]["added"] - students[n]["deleted"] for n in names]
        ax.bar(names, net)
        ax.set_ylabel("Net LOC (added - deleted)")
        ax.set_title("Contribution volume by Git author")
        ax.tick_params(axis="x", labelrotation=20)
        ax.grid(axis="y", linestyle="--", alpha=0.35)
    else:
        ax.text(0.5, 0.5, "No student commits found in this period",
                ha="center", va="center", transform=ax.transAxes)
        ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def generate(interval="weekly"):
    repo, branch = repo_info()
    students, scope = git_metrics(interval)
    today = dt.datetime.now(IST).date()
    suffix = {"weekly": "Weekly_Progress_Report_Form-3",
              "monthly": "Monthly_Progress_Report_Form-3",
              "final": "Final_Project_Report"}.get(interval, "Weekly_Progress_Report_Form-3")
    filename = f"{repo}_{suffix}_{today.isoformat()}.pdf"
    chart_path = Path(".form3_contributions.png")
    make_chart(students, chart_path)

    styles = getSampleStyleSheet()
    title = ParagraphStyle("College", parent=styles["Title"], fontSize=13, leading=16,
                           textColor=colors.HexColor("#0F172A"), alignment=1)
    subtitle = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=9, leading=12,
                             textColor=colors.HexColor("#475569"), alignment=1)
    small = ParagraphStyle("Small", parent=styles["BodyText"], fontSize=7.5, leading=9)
    story = [
        Paragraph(html.escape(COLLEGE_NAME), title),
        Paragraph(html.escape(DEPARTMENT_NAME), subtitle),
        Spacer(1, 5),
        Paragraph("<b>" + html.escape("Weekly Progress Report (Form-3)" if interval == "weekly"
                                      else f"{interval.title()} Project Report") + "</b>",
                  ParagraphStyle("ReportTitle", parent=title, fontSize=12)),
        Spacer(1, 8),
        Paragraph(f"<b>Project ID / Repository:</b> {html.escape(repo)}"
                  f" &nbsp;&nbsp; <b>Branch:</b> {html.escape(branch)}", styles["BodyText"]),
        Paragraph(f"<b>Evaluation window:</b> {html.escape(scope)}"
                  f" &nbsp;&nbsp; <b>Generated:</b> {today.isoformat()} (IST)", small),
        Spacer(1, 8),
        Paragraph("<b>1. Individual Contribution Breakdown</b>", styles["Heading2"]),
    ]

    total_commits = sum(s["commits"] for s in students.values())
    rows = [["Git author", "Commits", "Share", "Lines added", "Lines deleted", "Net LOC", "Active days"]]
    for name, data in sorted(students.items()):
        share = 100 * data["commits"] / total_commits if total_commits else 0
        rows.append([
            Paragraph(html.escape(name), small), str(data["commits"]), f"{share:.1f}%",
            f"+{data['added']:,}", f"-{data['deleted']:,}",
            f"{data['added'] - data['deleted']:,}", str(len(data["days"]))
        ])
    if not students:
        rows.append(["No commits found in this period", "-", "-", "-", "-", "-", "-"])
    table = Table(rows, repeatRows=1, colWidths=[1.75*inch, .55*inch, .55*inch, .75*inch, .8*inch, .65*inch, .7*inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story += [table, Spacer(1, 8), Paragraph("<b>2. Contribution Volume</b>", styles["Heading2"]),
              Image(str(chart_path), width=7.6*inch, height=2.15*inch),
              Paragraph("<b>3. Detailed Commit Logs and Mentor Evaluation</b>", styles["Heading2"])]

    for name, data in sorted(students.items()):
        story.append(Paragraph(f"<b>{html.escape(name)}</b> — {len(data['logs'])} commit(s)", styles["Heading3"]))
        log_rows = [["Date (IST)", "Hash", "Commit message", "Mentor marks (/10)"]]
        for i, (date, sha, subject) in enumerate(data["logs"]):
            log_rows.append([date, sha, Paragraph(html.escape(subject or "(no message)"), small),
                             "_____ / 10" if i == 0 else ""])
        log_table = Table(log_rows, repeatRows=1, colWidths=[.9*inch, .65*inch, 4.65*inch, 1.1*inch])
        log_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#475569")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), .4, colors.HexColor("#CBD5E1")),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("SPAN", (3, 1), (3, max(1, len(log_rows)-1))) if len(log_rows) > 1 else ("ALIGN", (3, 1), (3, -1), "CENTER"),
        ]))
        story.extend([log_table, Spacer(1, 6)])

    story += [
        Spacer(1, 10),
        Table([[
            Paragraph("<b>Project Mentor</b><br/>Name: ______________________<br/>Signature: __________________", styles["BodyText"]),
            Paragraph("<b>Lab Coordinator</b><br/>Name: ______________________<br/>Signature: __________________", styles["BodyText"]),
        ]], colWidths=[4*inch, 4*inch],
          style=TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING",(0,0),(-1,-1),0)]))
    ]
    doc = SimpleDocTemplate(filename, pagesize=landscape(letter),
                            rightMargin=28, leftMargin=28, topMargin=24, bottomMargin=24)
    doc.build(story)
    try:
        chart_path.unlink()
    except OSError:
        pass
    print(f"[SUCCESS] Generated {filename} with {len(students)} Git author(s) and {total_commits} commit(s).")
    print("Reminder: verify Git author names/emails and report contents before submission.")


if __name__ == "__main__":
    interval = sys.argv[1].lower() if len(sys.argv) > 1 else "weekly"
    if interval not in {"weekly", "monthly", "final"}:
        raise SystemExit("Usage: python generate_report.py [weekly|monthly|final]")
    generate(interval)
