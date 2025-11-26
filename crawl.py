import os
import gzip
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
# Paste your tvg-ids directly (keep your long list here)
# -------------------------
tvg_ids_raw = """
and.flix.in
and.Flix.HD.in
AndFlix.HD.in
And.Prive.HD.in
MOVIES.NOW.in
MOVIES.NOW.in
Movies Now HD.in
Movies.Now.HD.in
MNX.in
MN+.HD.in
SONY PIX.in
SONY PIX HD.in
SONY.PIX.in
SONY.PIX.HD.in
STAR.MOVIES.HD.in
STAR.MOVIES.in
Star.Movies.in
STAR Movies.in
STAR.MOVIES.SELECT.HD.in
Star Movies Select.in
ZEE.CAFE.HD.in
ZEE.CAFE.in
Zee Cafe.in
ComedyCentral.uk
ROMEDY.NOW.in
DISCOVERY.HD.WORLD.in
Disney Channel HD.in
HISTORY.TV18.HD.in
NATIONAL.GEOGRAPHIC.HD.in
National Geographic HD.in
National Geographic.in
SONY.SPORTS.TEN.1.HD.in
SONY.SPORTS.TEN.1.in
Sony.Ten.1.in
Sony.Ten.1.HD.in
MTV.in
MTV HD.in
MTV.in
COLORS.in
Colors.in
Colors.HD.in
Colors HD.in
COLORS.HD.uk
Colors.uk
Colors.uk
Animax.in
50centaction.us
actionmax.us
amazonmovies.us
movies.us
amc.ca
amcthrillers.us
storiesamc.us
amc+.us
wbtvthemovies.us
backstage.us
cinemax.us
5starmax.us
actionmax.us
moremax.us
cinemaxwest.us
crave1.ca
crave2.ca
crave3.ca
crave4.ca
epix.us
epix2.us
epixdrivein.us
epixhits.us
fx.us
fxmovies.us
hbo.us
hbo2.us
hbo2.ca
hbo1.ca
hbocomedy.us
hbosignature.us
hbowest.us
hbozone.us
hdnetmovies.us
hollywoodsuite2000s.ca
Hollywood.Suite.2000s.ca2
hollywoodsuite2010s.ca
Hollywood.Suite.2010s+.ca2
hollywoodsuite70s.ca
hollywoodsuite80s.ca
lifetimemovienetwork.us
US1600002OK
68fa84637ac952737656ae5f-680adc83ea62ac6a05a626e6
5e20b730f2f8d5003d739db7-680adc83ea62ac6a05a626e6
lifetimemovies.us
lifetime.us
lifetime.ca
mgm+.us
mgm+drive.us
mgm+hits.us
mgm+marquee.us
miramaxmoviechannel.us
M.Movies.1.za
M.Movies.2.za
moremax.us
movieplex.us
movies.us
moviesphere.us
GBBA33000557H
6401d85a49839300087b116c
moviesphere.uk
MyTimemovienetwork.us
GBBA3300059BU
UK:.MyTime.Movie.Network.be
paramountnetwork.us
pixl.us
screenpix.us
screenpixaction.us
screenpixvoices.us
screenpixvoices.us
screenpixwesterns.us
screenpixwesterns.us
showtime.us
showtime2.us
showtimeextreme.us
showtimefamily.us
showtimenext.us
showtimeshowcase.us
showtimewomen.us
skycinemaaction.uk
skycinemaanimation.uk
skycinemacomedy.uk
skycinemadrama.uk
skycinemafamily.uk
skycinemagreats.uk
skycinemahits.uk
skycinemapremiere.uk
skycinemascihorror.uk
skycinemathriller.uk
sonymoviechannel.us
dummy-673623
starz.us
starzblack.us
starzblack.us
starzcinema.us
starzcinema.us
starzcomedy.us
starzcomedy.us
starzedge.us
starzencore.us
starzencoreaction.us
starzencoreblack.us
starzencoreclassic.us
starzencorefamily.us
starzencorewest.us
starzencorewesterns.us
starzkids&family.us
StarzKidsFamily.us
starzwest.us
starz1.ca
starz2.ca
superchannelfuse.ca
superchannelheart&home.ca
superchannelquest.ca
superchannelvault.ca
syfywest.us
themoviechannel.us
themovienetworkondemand.ca
skycinemaselect.uk
scaresshudder.us
10peachsydney.au
10shakesydney.au
9go.au
adultswim.ca
ahc.ca
aliennationbydust.us
dummy-1133115
5e20b730f2f8d5003d739db7-63dea56a2a2abb171ff6dadf
5e20b730f2f8d5003d739db7-686452b8fbd6d9b449de2be3
5e20b730f2f8d5003d739db7-65622fb65dbccec83a87b643
bet.us
cartoonnetwork.ca
cinevault.us
cleotv.us
cmt.us
cmt.ca
comedycentral.us
comedycentral.uk
comet.us
cozitv.us
crime+investigation.us
crunchyroll.us
ctvcomedy.ca
ctvdramachannel.ca
ctvscichannel.ca
cwgold.us
dejaview.ca
discoverycanada.ca
discoverychannel.us
discoverylife.us
discoveryscience.uk
discoveryscience.ca
disneychannel.us
disneychannelcanada.ca
dtour.ca
e!entertainment.us
filmrisefreemovies.us
filmriseaction.us
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
ifc.us
ifc.us
ion.us
ifcfilmspicks.us
indieplex.us
investigationdiscovery.uk
investigationdiscovery.ca
laffmore.us
laff.us
400000067
metvtoons.us
moviefavoriteslifetime.us
moviesphere.us
mtv-musictelevision.us
mtv.uk
mtv2.us
muchmusic.ca
natgeo.ca
nationalgeographic.us
nationalgeographic.uk
nickelodeon.us
nickelodeon.uk
hersphere.us
400000006
oxygen.us
peachtreetv.ca
pop.us
shoutmovies.us
showcase.ca
showtime.us
shoxbet.us
skyatlantic.uk
skycinemacomedy.uk
skydocumentaries.uk
skyhistory.uk
skyhistory2.uk
ktv.uk
skysci.uk
skyshowcase.uk
slice.ca
slightlyoffifc.us
tbs.us
tcm.ca
tnt.us
travelchannel.us
trutv.us
tvland.us
uptv.us
vh1.us
"""

valid_tvg_ids_original = [line.strip() for line in tvg_ids_raw.splitlines() if line.strip()]
valid_tvg_ids_lower = [id.lower() for id in valid_tvg_ids_original]

# -------------------------
# Fetch XML and decompress
# -------------------------
def fetch_and_extract_xml(url):
    try:
        response = requests.get(url, timeout=60)
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return None

    if response.status_code != 200:
        print(f"Failed to fetch {url} — status {response.status_code}")
        return None

    data = response.content
    if url.endswith('.gz') or (data[:2] == b'\x1f\x8b'):
        try:
            decompressed_data = gzip.decompress(data)
            return ET.fromstring(decompressed_data)
        except Exception as e:
            print(f"Failed to decompress/parse {url}: {e}")
            return None
    else:
        try:
            return ET.fromstring(data)
        except Exception as e:
            print(f"Failed to parse XML from {url}: {e}")
            return None

def parse_epg_time(ts):
    try:
        if " " in ts:
            base, offset = ts.split(" ", 1)
            dt = datetime.strptime(base, "%Y%m%d%H%M%S")
            return f"{dt} {offset}"
        else:
            return datetime.strptime(ts[:14], "%Y%m%d%H%M%S")
    except Exception:
        return f"Invalid ({ts})"

def filter_and_build_epg(urls):
    root = ET.Element('tv')
    found_lower = set()
    all_xml_ids_lower = set()
    all_xml_ids_original = []

    for url in urls:
        print(f"Fetching xml ({url})...")
        epg_data = fetch_and_extract_xml(url)
        if epg_data is None:
            continue

        for channel in epg_data.findall('channel'):
            tvg_id = channel.get('id')
            if not tvg_id:
                continue
            all_xml_ids_lower.add(tvg_id.lower())
            all_xml_ids_original.append(tvg_id)
            if tvg_id.lower() in valid_tvg_ids_lower:
                root.append(channel)
                found_lower.add(tvg_id.lower())

        for programme in epg_data.findall('programme'):
            tvg_id = programme.get('channel')
            if not tvg_id:
                continue
            all_xml_ids_lower.add(tvg_id.lower())
            all_xml_ids_original.append(tvg_id)
            if tvg_id.lower() in valid_tvg_ids_lower:
                root.append(programme)
                found_lower.add(tvg_id.lower())

    # Save final XML
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(f"Saved XML to {output_file}")

    if save_as_gz:
        with gzip.open(output_file_gz, 'wb') as f:
            tree.write(f, encoding='utf-8', xml_declaration=True)
        print(f"Saved GZ to {output_file_gz}")

    # Optional: print report summary
    missing_ids = [orig for orig, lower in zip(valid_tvg_ids_original, valid_tvg_ids_lower) if lower not in found_lower]
    print(f"Total matched: {len(valid_tvg_ids_original) - len(missing_ids)}")
    print(f"Total missing: {len(missing_ids)}")

# -------------------------
# URL list
# -------------------------
urls = [
    #"https://epgshare01.online/epgshare01/epg_ripper_IN4.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_IN1.xml.gz",
    "https://iptv-epg.org/files/epg-in.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_UK1.xml.gz",
    "https://iptv-epg.org/files/epg-gb.xml.gz",
    "https://www.open-epg.com/files/india1.xml.gz",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg6.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_CA2.xml.gz",
    "https://raw.githubusercontent.com/matthuisman/i.mjh.nz/refs/heads/master/SamsungTVPlus/gb.xml.gz",
    "https://raw.githubusercontent.com/matthuisman/i.mjh.nz/refs/heads/master/PlutoTV/gb.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_RAKUTEN1.xml.gz",
    "https://raw.githubusercontent.com/matthuisman/i.mjh.nz/refs/heads/master/Plex/us.xml.gz",
    "https://epgshare01.online/epgshare01/epg_ripper_ZA1.xml.gz",
]

if __name__ == "__main__":
    filter_and_build_epg(urls)

