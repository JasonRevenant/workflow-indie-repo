import os
import time
import requests
import xml.etree.ElementTree as ET

from datetime import datetime, date, timezone, timedelta

# -------------------------
# Settings
# -------------------------
SCHEDULE_URL = "https://tm.tapi.videoready.tv/content-detail/pub/api/v2/channels/schedule"

OUTPUT_DIR  = "output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "TataPlay.xml")

EPG_DATE      = date.today()
FETCH_DAYS    = 3          # today, +1, +2 broadcast days
WINDOW_HOURS  = 48         # keep programmes from now → now + 48h
REQUEST_PAUSE = 2.2

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------
# Your channel list  (schedule_id, display_name, tvg_id)
# -------------------------
CHANNELS = [
    ("543",  "Colors",                 "tp.colors"),
    ("52",   "Colors HD",              "tp.colors-hd"),
    ("1902", "Colors HD",              "tp.colors-hd-2"),
    ("219",  "Discovery Channel",      "tp.discovery-channel"),
    ("341",  "Discovery HD World",     "tp.discovery-hd-world"),
    ("210",  "MN+ HD",                 "tp.mn-plus-hd"),
    ("234",  "MNX",                    "tp.mnx"),
    ("599",  "MNX HD",                 "tp.mnx-hd"),
    ("173",  "Movies Now",             "tp.movies-now"),
    ("562",  "Movies Now HD",          "tp.movies-now-hd"),
    ("103",  "MTV",                    "tp.mtv"),
    ("406",  "MTV HD",                 "tp.mtv-hd"),
    ("1937", "MTV HD",                 "tp.mtv-hd-2"),
    ("1893", "National Geographic HD", "tp.nat-geo-hd"),
    ("558",  "Sony Pix",               "tp.sony-pix"),
    ("32",   "Sony Pix HD",            "tp.sony-pix-hd"),
    ("150",  "Sony Sports Ten 1",      "tp.sony-sports-ten-1"),
    ("81",   "Sony Sports Ten 1 HD",   "tp.sony-sports-ten-1-hd"),
    ("170",  "Sony Sports Ten 2",      "tp.sony-sports-ten-2"),
    ("462",  "Sony Sports Ten 2 HD",   "tp.sony-sports-ten-2-hd"),
    ("273",  "Star Movies",            "tp.star-movies"),
    ("593",  "Star Movies Select HD",  "tp.star-movies-select-hd"),
]

# -------------------------
# Headers
# -------------------------
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36")

HEADERS = {
    "accept": "*/*",
    "accept-language": "en-IN,en;q=0.9",
    "content-type": "application/json",
    "locale": "ENG",
    "origin": "https://watch.tataplay.com",
    "referer": "https://watch.tataplay.com/",
    "sec-ch-ua": '"Chromium";v="146", "Not-A.Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": UA,
}


# -------------------------
# Time parser
# -------------------------
def parse_time(value):
    if isinstance(value, (int, float)):
        ts = int(value)
        return ts // 1000 if ts > 100_000_000_000 else ts
    if isinstance(value, str):
        try:
            n = int(value)
            return n // 1000 if n > 100_000_000_000 else n
        except ValueError:
            pass
        try:
            dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return int(dt.timestamp())
        except (ValueError, OverflowError):
            return None
    return None


# -------------------------
# Schedule
# -------------------------
def fetch_schedule_raw(session, channel_id, day):
    date_param = day.strftime("%d-%m-%Y")
    for attempt in range(2):
        response = session.post(
            SCHEDULE_URL,
            params={"date": date_param},
            json={"id": str(channel_id)},
            headers=HEADERS,
            timeout=30,
        )
        if response.status_code == 429 and attempt == 0:
            try:
                wait = int(response.headers.get("ratelimit-reset", 60))
            except (ValueError, TypeError):
                wait = 60
            wait = min(wait, 120)
            print(f"\nRate limited. Waiting {wait + 1}s...")
            time.sleep(wait + 1)
            continue
        response.raise_for_status()
        return response.json()
    raise RuntimeError("HTTP 429: Rate limit exceeded")


def parse_schedule(raw):
    epg = raw.get("data", {}).get("epg", []) if isinstance(raw, dict) else []
    if not isinstance(epg, list):
        return []
    programs = []
    for p in epg:
        if not isinstance(p, dict):
            continue
        start = parse_time(p.get("startTime"))
        end   = parse_time(p.get("endTime"))
        title = p.get("title")
        if start is None or end is None:
            continue
        if not isinstance(title, str) or not title.strip():
            continue
        desc = p.get("desc", "")
        if not isinstance(desc, str):
            desc = ""
        programs.append({
            "start": start, "end": end,
            "title": title.strip(), "desc": desc.strip(),
        })
    return programs


def dedupe_and_filter(programs, now_ts, window_end):
    seen, unique = set(), []
    for p in programs:
        key = (p["start"], p["title"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    unique.sort(key=lambda p: p["start"])
    return [p for p in unique if p["end"] > now_ts and p["start"] < window_end]


# -------------------------
# XMLTV
# -------------------------
def xmltv_time(ts):
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y%m%d%H%M%S +0000")


def generate_xml(channels):
    root = ET.Element("tv")
    n_ch = n_pr = 0

    for ch in channels:
        if not ch["programs"]:
            continue
        cel = ET.SubElement(root, "channel", id=ch["tvg_id"])
        ET.SubElement(cel, "display-name", lang="en").text = ch["name"]

        for p in ch["programs"]:
            el = ET.SubElement(root, "programme",
                               start=xmltv_time(p["start"]),
                               stop=xmltv_time(p["end"]),
                               channel=ch["tvg_id"])
            ET.SubElement(el, "title", lang="en").text = p["title"]
            if p["desc"]:
                ET.SubElement(el, "desc", lang="en").text = p["desc"]

        n_ch += 1
        n_pr += len(ch["programs"])

    tree = ET.ElementTree(root)
    try:
        ET.indent(tree, space="  ")
    except AttributeError:
        pass
    tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    return n_ch, n_pr


# -------------------------
# Main
# -------------------------
def main():
    now = datetime.now(timezone.utc)
    window_end = now + timedelta(hours=WINDOW_HOURS)
    now_ts = int(now.timestamp())
    window_end_ts = int(window_end.timestamp())

    print("=" * 55)
    print("TATA PLAY EPG GENERATOR")
    print("=" * 55)
    print(f"Window   : {now.strftime('%Y-%m-%d %H:%M %Z')}  →  "
          f"{window_end.strftime('%Y-%m-%d %H:%M %Z')}  ({WINDOW_HOURS}h)")
    print(f"Fetching : {FETCH_DAYS} broadcast day(s) per channel")
    print(f"Channels : {len(CHANNELS)}")
    print(f"Requests : ~{len(CHANNELS) * FETCH_DAYS} "
          f"(~{len(CHANNELS) * FETCH_DAYS * REQUEST_PAUSE / 60:.1f} min)")
    print("-" * 55)

    session = requests.Session()
    xml_channels = []
    status_counts = {"OK": 0, "No EPG": 0, "Error": 0}

    try:
        total = len(CHANNELS)
        for i, (cid, name, tvg_id) in enumerate(CHANNELS, 1):
            print(f"[{i}/{total}] {name} ({cid} → {tvg_id})", end=" ")

            try:
                all_programs = []
                days_ok = 0

                for offset in range(FETCH_DAYS):
                    day = EPG_DATE + timedelta(days=offset)
                    try:
                        raw = fetch_schedule_raw(session, cid, day)
                        batch = parse_schedule(raw)
                        all_programs.extend(batch)
                        if batch:
                            days_ok += 1
                    except Exception as e:
                        print(f"(day {day} fail: {e})", end=" ")
                    time.sleep(REQUEST_PAUSE)

                filtered = dedupe_and_filter(all_programs, now_ts, window_end_ts)

                if filtered:
                    print(f"- {len(filtered)} programmes "
                          f"({days_ok}/{FETCH_DAYS} days)")
                    xml_channels.append({
                        "tvg_id": tvg_id, "name": name, "programs": filtered,
                    })
                    status_counts["OK"] += 1
                else:
                    print(f"- 0 programmes in window")
                    status_counts["No EPG"] += 1

            except Exception as e:
                print(f"- FAILED: {e}")
                status_counts["Error"] += 1

        print("-" * 55)
        print("Generating XMLTV...")
        n_ch, n_pr = generate_xml(xml_channels)

        print("=" * 55)
        print("DONE")
        print(f"Channels requested : {total}")
        print(f"  with EPG         : {status_counts['OK']}")
        print(f"  no EPG in window : {status_counts['No EPG']}")
        print(f"  errors           : {status_counts['Error']}")
        print(f"Total programmes   : {n_pr}")
        print(f"XML   : {os.path.abspath(OUTPUT_FILE)}")
        print("=" * 55)

    except Exception as e:
        print(f"\nERROR: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
