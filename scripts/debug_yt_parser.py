import xml.etree.ElementTree as ET
import requests

def debug_parser():
    url = "https://www.youtube.com/feeds/videos.xml?channel_id=UC7usMJDHmtbs_oegmzQKKMA"
    resp = requests.get(url)
    xml_content = resp.text
    
    root = ET.fromstring(xml_content)
    ns = {'yt': 'http://www.youtube.com/xml/schemas/2015', 
          'atom': 'http://www.w3.org/2005/Atom'}
    
    print(f"Total Entries: {len(root.findall('{http://www.w3.org/2005/Atom}entry'))}")
    
    for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
        vid_id_tag = entry.find("{http://www.youtube.com/xml/schemas/2015}videoId")
        title_tag = entry.find("{http://www.w3.org/2005/Atom}title")
        
        vid_id = vid_id_tag.text if vid_id_tag is not None else "N/A"
        title = title_tag.text if title_tag is not None else "N/A"
        
        print(f"[{vid_id}] {title}")

if __name__ == "__main__":
    debug_parser()
