"""Scrape the Clare Hall weekly menu (a Microsoft Sway) and write an .ics calendar
of the vegetarian main course for each lunch and dinner.

The Sway is overwritten each week, so parsed menus are kept in menus.json and the
calendar is built from the full history.
"""

import html
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

SWAY_URL = "https://sway.cloud.microsoft/b7Zz74Q2g96EIhE9?ref=Link&loc=play"
ROOT = Path(__file__).parent
DATA_FILE = ROOT / "menus.json"
ICS_FILE = ROOT / "public" / "menu.ics"

MEALS = {"LUNCH": ("1200", "1330"), "DINNER": ("1800", "1900")}
VEG_INDEX = 2  # soup, meat main, veg main, pudding

DAY_RE = re.compile(
    r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+"
    r"(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)\s+(\d{4})$"
)
END_MARKERS = ("Our Sustainability Initiatives",)

VTIMEZONE = """BEGIN:VTIMEZONE
TZID:Europe/London
BEGIN:DAYLIGHT
TZOFFSETFROM:+0000
TZOFFSETTO:+0100
TZNAME:BST
DTSTART:19700329T010000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0100
TZOFFSETTO:+0000
TZNAME:GMT
DTSTART:19701025T020000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
END:VTIMEZONE"""


class ParagraphParser(HTMLParser):
    """Collect the text of each <p> element, in document order."""

    def __init__(self):
        super().__init__()
        self.paragraphs, self._buf, self._depth = [], [], 0

    def handle_starttag(self, tag, attrs):
        if tag == "p":
            self._depth += 1

    def handle_endtag(self, tag):
        if tag == "p" and self._depth:
            self._depth -= 1
            text = " ".join("".join(self._buf).split())
            if text:
                self.paragraphs.append(text)
            self._buf = []

    def handle_data(self, data):
        if self._depth:
            self._buf.append(data)


def fetch_dom():
    chrome = next(
        (shutil.which(c) for c in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser") if shutil.which(c)),
        None,
    )
    if chrome is None:
        raise RuntimeError("No Chrome/Chromium found")
    out = subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--virtual-time-budget=20000", "--dump-dom", SWAY_URL],
        capture_output=True, text=True, timeout=120,
    )
    return out.stdout


def split_dish(line):
    """'Dish name - PB, GF' -> ('Dish name', 'PB, GF')."""
    name, sep, tags = line.rpartition(" -")
    if not sep:
        return line.strip(), ""
    return name.strip(), tags.strip()


def parse(paragraphs):
    """Return {date: {meal: [dish lines]}} for each day on the menu."""
    days, day, meal = {}, None, None
    for line in paragraphs:
        line = html.unescape(line).strip()
        if line.startswith(END_MARKERS):
            break
        m = DAY_RE.match(line)
        if m:
            date = datetime.strptime(f"{m[2]} {m[3]} {m[4]}", "%d %B %Y").date().isoformat()
            day, meal = days.setdefault(date, {}), None
            continue
        if day is None:
            continue
        if line.upper() in MEALS:
            meal = line.upper()
            day[meal] = []
        elif meal:
            day[meal].append(line)
    return days


def closed_title(dishes):
    text = " ".join(dishes)
    if "CLOSED" not in text.upper():
        return None
    return re.sub(r"formal hall", "Formal Hall", text.capitalize(), flags=re.I)


def ics_escape(s):
    return s.replace("\\", "\\\\").replace(";", r"\;").replace(",", r"\,").replace("\n", r"\n")


def fold(line):
    """Fold lines to 75 octets as required by RFC 5545."""
    out, cur = [], b""
    for ch in line:
        b = ch.encode()
        if len(cur) + len(b) > 74:
            out.append(cur.decode())
            cur = b" "
        cur += b
    out.append(cur.decode())
    return "\r\n".join(out)


def build_ics(menus):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//clare-hall-menu//EN",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
        "X-WR-CALNAME:Clare Hall menu", "X-WR-TIMEZONE:Europe/London",
        "REFRESH-INTERVAL;VALUE=DURATION:PT6H", "X-PUBLISHED-TTL:PT6H",
        *VTIMEZONE.splitlines(),
    ]
    for date in sorted(menus):
        for meal, dishes in menus[date].items():
            if not dishes:
                continue
            closed = closed_title(dishes)
            if closed:
                summary = closed
            elif len(dishes) > VEG_INDEX:
                summary = split_dish(dishes[VEG_INDEX])[0]
            else:
                summary = f"{meal.title()}: see menu"
            start, end = MEALS[meal]
            ymd = date.replace("-", "")
            lines += [
                "BEGIN:VEVENT",
                f"UID:{ymd}-{meal.lower()}@clare-hall-menu",
                f"DTSTAMP:{stamp}",
                f"DTSTART;TZID=Europe/London:{ymd}T{start}00",
                f"DTEND;TZID=Europe/London:{ymd}T{end}00",
                f"SUMMARY:{ics_escape(summary)}",
                f"DESCRIPTION:{ics_escape(meal.title() + ' menu:' + chr(10) + chr(10).join(dishes))}",
                "LOCATION:Clare Hall Dining Hall",
                f"URL:{SWAY_URL}",
                "TRANSP:TRANSPARENT",
                "END:VEVENT",
            ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(l) for l in lines) + "\r\n"


def main():
    parser = ParagraphParser()
    parser.feed(fetch_dom())
    new = parse(parser.paragraphs)
    if not new:
        raise SystemExit("No menu found on the Sway page; leaving calendar unchanged.")

    menus = json.loads(DATA_FILE.read_text()) if DATA_FILE.exists() else {}
    menus.update(new)
    DATA_FILE.write_text(json.dumps(menus, indent=2, ensure_ascii=False) + "\n")

    ICS_FILE.parent.mkdir(exist_ok=True)
    ICS_FILE.write_text(build_ics(menus), newline="")
    print(f"Parsed {len(new)} days; calendar has {len(menus)} days.")


if __name__ == "__main__":
    main()
