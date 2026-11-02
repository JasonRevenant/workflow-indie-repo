
import os
import gzip
import re
import xml.etree.ElementTree as ET
import requests
from difflib import get_close_matches
from datetime import datetime

# -------------------------
# Settings
# -------------------------
name = "Ind-Zpg"
save_as_gz = True

os.makedirs("output", exist_ok=True)
output_file = os.path.join("output", "Ind-Zpg.xml")
output_file_gz = output_file + ".gz"

# -------------------------
# Secret detection
# -------------------------

# VolcEngine Access Key IDs commonly use the AKLT prefix.
# This is a defensive detector, not a complete secret scanner.
VOLCENGINE_PATTERN = re.compile(
    r"AKLT[A-Z0-9]{10,}",
    re.IGNORECASE
)


def contains_secret(element):
    """Check an XML element and all its descendants for suspicious keys."""

    for elem in element.iter():

        # Check attributes
        for value in elem.attrib.values():
            if VOLCENGINE_PATTERN.search(value):
                return True

        # Check element text
        if elem.text and VOLCENGINE_PATTERN.search(elem.text):
            return True

        # Check tail text
        if elem.tail and VOLCENGINE_PATTERN.search(elem.tail):
            return True

    return False


def sanitize_xml(root, source_url):
    """Remove XML elements containing suspicious credentials."""

    removed = 0

    for child in list(root):
        if contains_secret(child):
            removed += 1
            print(
                f"[SECURITY] Removed contaminated "
                f"<{child.tag}> element from {source_url}"
            )
            root.remove(child)

    return removed


def verify_output(root):
    """Final security check before writing generated XML."""

    for element in root:
        if contains_secret(element):
            raise RuntimeError(
                "SECURITY ERROR: Suspicious credential detected "
                "in final XML. Output was not saved."
            )

    print("[SECURITY] Final XML check passed.")


# -------------------------
# Paste your tvg-ids directly
# -------------------------
tvg_ids_raw = """
MoviesNow.in
462
MNPlus.in
SONY PIX HD.in
SonyPix.in
StarMovies.in
StarMoviesSelect.in
ComedyCentral.uk
RomedyNow.in
DISCOVERY.HD.WORLD.in
146
National Geographic HD.in
3510
MTV HD.in
144
Colors.in
Colors.uk
50centaction.us
amazonmovies.us
movies.us
amc.ca
amcthrillers.us
StoriesbyAMC.us
AtTheMovies.us
backstage.us
cinemax.us
5starmax.us
actionmax.us
moremax.us
cinemaxwest.us
cinevault.us
crave1.ca
crave2.ca
crave3.ca
crave4.ca
filmrisefreemovies.us
filmriseaction.us
mgmplus.us
mgmplusdrivein.us
mgmplushits.us
mgmplusmarquee.us
fx.us
fxmovies.us
miramaxmoviechannel.us
hbo.us
hbo1.ca
hbowest.us
hbohits.us
hbo2.ca
hbocomedy.us
hbodrama.us
hbozone.us
hdnetmovies.us
Hollywood.Suite.2000s.ca2
Hollywood.Suite.2010s+.ca2
hollywoodsuite70s.ca
hollywoodsuite80s.ca
ifcfilmspicks.us
lifetime.us
lifetime.ca
lifetimemovienetwork.us
6a1610bebdf296985fd95603-680adc83ea62ac6a05a626e6
LifetimeMovieFavorites.us
movieplex.us
indieplex.us
moviesphere.us
6401d85a49839300087b116c
UK:.MyTime.Movie.Network.be
paramountnetwork.us
pixl.us
ScaresbyShudder.us
shoutmovies.us
showtime.us
showtime2.us
showtimeextreme.us
showtimefamily.us
showtimenext.us
showtimeshowcase.us
showtimewomen.us
skycinemaaction.uk
skycinemacomedy.uk
skycinemadrama.uk
skycinemafamily.uk
skycinemagreats.uk
skycinemahits.uk
skycinemapremiere.uk
skycinemascifihorror.uk
skycinemathriller.uk
skycinemaselect.uk
sonymoviechannel.us
starz.us
starzwest.us
starzkids&family.us
starzedge.us
starzcomedy.us
starzcinema.us
starzinblack.us
starzencore.us
starzencorewest.us
starzencoreaction.us
starzencoreblack.us
starzencoreclassic.us
starzencorefamily.us
starzencorewesterns.us
starz1.ca
starz2.ca
superchannelfuse.ca
superchannelheart&home.ca
superchannelquest.ca
superchannelvault.ca
syfywest.us
scifi.ca
tcm.ca
themoviechannel.us
screenpix.us
screenpixaction.us
screenpixvoices.us
screenpixwesterns.us
9go.au
adultswim.ca
ahc.ca
aliennationbydust.us
amc+.us
dummy-1133115
plex.tv.ANIME.x.HIDIVE.plex
6a1610bebdf296985fd95603-65622fb65dbccec83a87b643
bet.us
cartoonnetwork.ca
cleotv.us
cmt.us
comedycentral.us
comet.us
cozitv.us
crimeplusinvestigation.us
crunchyroll.us
ctvcomedy.ca
ctvdramachannel.ca
ctvscifichannel.ca
cwgold.us
dejaview.ca
discoverychannel.ca
discoverychannel.us
discovery.uk
discoverylife.us
discoveryscience.uk
discoveryscience.ca
disneychannel.us
disneychannelcanada.ca
dtour.ca
e!entertainmenttelevision.us
e4.uk
filmriseanime.us
freeform.us
freeformwest.us
fuse.us
fx.ca
fxx.us
fxx.ca
gametv.ca
dummy-1133353
h2.ca
700406
history.ca
hln.us
dummy-1133394
investigationdiscovery.us
investigationdiscovery.uk
investigationdiscovery.ca
ifc.us
ion.us
laffmore.us
laff.us
400000067
metvtoons.us
mtv.us
mtv.uk
mtv2.us
muchmusic.ca
natgeo.ca
nationalgeographic.us
nationalgeographic.uk
nickelodeon.us
nickelodeon.uk
400000006
oxygen.us
peachtreetv.ca
pop.us
showcase.ca
shoxbetwest.us
skyatlantic.uk
skydocumentaries.uk
skyhistory.uk
skyhistory2.uk
SkyMix.uk
skyscifi.uk
slice.ca
slightlyoffifc.us
tbs.us
tnt.us
travelchannel.us
trutv.us
tvland.us
uptv.us
vh1.us
wnetwork.ca
"""

valid_tvg_ids_original = [
    line.strip()
    for line in tvg_ids_raw.splitlines()
    if line.strip()
]

valid_tvg_ids_lower = [
    tvg_id.lower()
    for tvg_id in valid_tvg_ids_original
]

valid_tvg_ids_set = set(valid_tvg_ids_lower)


# -------------------------
# Fetch XML and decompress
# -------------------------
def fetch_and_extract_xml(url):

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

    data = response.content

    if url.endswith(".gz") or data[:2] == b"\x1f\x8b":

        try:
            decompressed_data = gzip.decompress(data)
            return ET.fromstring(decompressed_data)

        except Exception as e:
            print(f"Failed to decompress/parse {url}: {e}")
            return None

    try:
        return ET.fromstring(data)

    except Exception as e:
        print(f"Failed to parse XML from {url}: {e}")
        return None


# -------------------------
# Parse EPG time
# -------------------------
def parse_epg_time(ts):

    try:
        if " " in ts:
            base, offset = ts.split(" ", 1)
            dt = datetime.strptime(base, "%Y%m%d%H%M%S")
            return f"{dt} {offset}"

        else:
            return datetime.strptime(
                ts[:14],
                "%Y%m%d%H%M%S"
            )

    except Exception:
        return f"Invalid ({ts})"


# -------------------------
# Filter and build EPG
# -------------------------
def filter_and_build_epg(urls):

    root = ET.Element("tv")

    found_lower = set()

    total_removed = 0

    for url in urls:

        print(f"\nFetching XML ({url})...")

        epg_data = fetch_and_extract_xml(url)

        if epg_data is None:
            continue

        # Check each top-level channel/programme independently.
        # This allows clean EPG entries from the same feed to remain.

        for channel in epg_data.findall("channel"):

            tvg_id = channel.get("id")

            if not tvg_id:
                continue

            if tvg_id.lower() not in valid_tvg_ids_set:
                continue

            if contains_secret(channel):
                total_removed += 1
                print(
                    f"[SECURITY] Skipped contaminated channel: "
                    f"{tvg_id} ({url})"
                )
                continue

            root.append(channel)
            found_lower.add(tvg_id.lower())

        for programme in epg_data.findall("programme"):

            tvg_id = programme.get("channel")

            if not tvg_id:
                continue

            if tvg_id.lower() not in valid_tvg_ids_set:
                continue

            if contains_secret(programme):
                total_removed += 1
                print(
                    f"[SECURITY] Skipped contaminated programme: "
                    f"{tvg_id} ({url})"
                )
                continue

            root.append(programme)
            found_lower.add(tvg_id.lower())

    # -------------------------
    # Final security verification
    # -------------------------

    verify_output(root)

    # -------------------------
    # Save final XML
    # -------------------------

    tree = ET.ElementTree(root)

    tree.write(
        output_file,
        encoding="utf-8",
        xml_declaration=True
    )

    print(f"\nSaved XML to {output_file}")

    # -------------------------
    # Save GZ
    # -------------------------

    if save_as_gz:

        with gzip.open(output_file_gz, "wb") as f:

            tree.write(
                f,
                encoding="utf-8",
                xml_declaration=True
            )

        print(f"Saved GZ to {output_file_gz}")

    # -------------------------
    # Report summary
    # -------------------------

    missing_ids = [
        orig
        for orig, lower in zip(
            valid_tvg_ids_original,
            valid_tvg_ids_lower
        )
        if lower not in found_lower
    ]

    matched = len(valid_tvg_ids_original) - len(missing_ids)

    print("\n========== EPG SUMMARY ==========")
    print(f"Total matched: {matched}")
    print(f"Total missing: {len(missing_ids)}")
    print(f"Contaminated entries skipped: {total_removed}")
    print("=================================")


# -------------------------
# URL list
# -------------------------
urls = [
    #"https://epgshare01.online/epgshare01/epg_ripper_IN4.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_IN1.xml.gz",
    "https://www.open-epg.com/files/india1.xml.gz",
    "https://iptv-epg.org/files/epg-in.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz",
    "https://iptv-epg.org/files/epg-gb.xml.gz",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg6.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_CA2.xml.gz",
    "https://raw.githubusercontent.com/matthuisman/i.mjh.nz/refs/heads/master/SamsungTVPlus/gb.xml.gz",
    "https://raw.githubusercontent.com/matthuisman/i.mjh.nz/refs/heads/master/PlutoTV/gb.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_RAKUTEN1.xml.gz",
    "https://raw.githubusercontent.com/matthuisman/i.mjh.nz/refs/heads/master/Plex/us.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_ZA1.xml.gz",
    "https://github.com/mitthu786/tvepg/raw/refs/heads/main/jiotv/epg.xml.gz",
]


# -------------------------
# Main
# -------------------------
if __name__ == "__main__":

    filter_and_build_epg(urls)
