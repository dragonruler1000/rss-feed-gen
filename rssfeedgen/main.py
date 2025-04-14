import os
import argparse
import subprocess
from feedgen.feed import FeedGenerator
from datetime import datetime
import email.utils
from datetime import UTC
import requests
from xml.etree import ElementTree as ET
import argcomplete


def download_if_url(path):
    """
    Downloads a remote file if given a URL and returns the local path.
    """
    if path.startswith("http://") or path.startswith("https://"):
        local_name = os.path.join("/tmp", os.path.basename(path))
        if not os.path.exists(local_name):  # Don't download again if already present
            print(f"⬇️ Downloading {path} ...")
            r = requests.get(path, stream=True)
            if r.status_code == 200:
                with open(local_name, 'wb') as f:
                    for chunk in r.iter_content(1024 * 1024):
                        f.write(chunk)
            else:
                raise Exception(f"Failed to download {path} (status {r.status_code})")
        return local_name
    return path


def get_audio_metadata(file_path):
    try:
        length = str(os.path.getsize(file_path))
        mime_type = "audio/mpeg" if file_path.endswith(".mp3") else "video/mp4"
        return length, mime_type
    except Exception as e:
        print(f"⚠️ Error fetching metadata for {file_path}: {e}")
        return "0", "audio/mpeg"


def convert_media(input_file, format, image=None):
    input_file = download_if_url(input_file)
    if image:
        image = download_if_url(image)

    url_path = '/'.join(input_file.split('/')[3:-1])
    save_dir = os.path.join(os.getcwd(), url_path)
    os.makedirs(save_dir, exist_ok=True)
    output_file = os.path.join(save_dir, os.path.basename(input_file).rsplit('.', 1)[0] + (".mp3" if format == "audio" else ".mp4"))

    if format == "audio":
        cmd = ["ffmpeg", "-hide_banner", "-y", "-i", input_file, "-q:a", "0", "-map", "a", output_file]
    elif format == "video" and image:
        cmd = [
            "ffmpeg", "-hide_banner", "-y", "-loop", "1", "-framerate", "2", "-i", image,
            "-i", input_file,
            "-vf", "scale=1280:720",
            "-c:v", "libx264", "-preset", "fast", "-tune", "stillimage",
            "-c:a", "aac", "-b:a", "192k",
            "-shortest", "-pix_fmt", "yuv420p", output_file
        ]
    else:
        return input_file  # No conversion needed

    try:
        subprocess.run(cmd, check=True)
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error during conversion: {e}")
        return input_file


def create_feed(feed_file, title, link, description, owner_name, owner_email, image_url):
    fg = FeedGenerator()
    fg.title(title)
    fg.link(href=link, rel='self')
    fg.description(description)
    fg.image(image_url)

    fg.load_extension('podcast')
    fg.podcast.itunes_author(owner_name)
    fg.podcast.itunes_owner(owner_name, owner_email)

    fg.rss_file(feed_file, pretty=True)

    if os.path.exists(feed_file):
        print(f"✅ RSS feed successfully created: {feed_file}")
    else:
        print("❌ Error: Feed file was not created.")


def add_item(feed_file, title, link, description, file_path, format=None, image=None, pubdate=None):
    if not os.path.exists(feed_file):
        print("⚠️ Feed file does not exist. Creating a new one...")
        create_feed(feed_file, "My Podcast", "https://example.com", "A great podcast", "Owner", "owner@example.com", "https://example.com/image.jpg")

    if format is None:
        format = "audio" if file_path.endswith(".mp3") else "video"

    converted_file = convert_media(file_path, format, image)
    if not os.path.exists(converted_file):
        print(f"❌ Error: Converted file was not created: {converted_file}")
        return

    try:
        tree = ET.parse(feed_file)
        root = tree.getroot()
        channel = root.find("channel")
    except ET.ParseError as e:
        print(f"❌ Error: Failed to parse feed file '{feed_file}': {e}")
        return

    length, mime_type = get_audio_metadata(converted_file)

    item = ET.Element("item")
    ET.SubElement(item, "title").text = title
    ET.SubElement(item, "link").text = link
    ET.SubElement(item, "description").text = description
    ET.SubElement(item, "pubDate").text = pubdate if pubdate else email.utils.format_datetime(datetime.now(UTC))

    enclosure = ET.SubElement(item, "enclosure")
    enclosure.set("url", link)
    enclosure.set("length", length)
    enclosure.set("type", mime_type)

    channel.append(item)
    tree.write(feed_file, encoding="utf-8", xml_declaration=True)
    print(f"✅ Added new episode: {title}")


def edit_item(feed_file, old_title, new_title=None, new_link=None, new_description=None, new_pubdate=None):
    if not os.path.exists(feed_file):
        print("❌ Error: Feed file does not exist.")
        return

    tree = ET.parse(feed_file)
    root = tree.getroot()
    channel = root.find("channel")
    items = channel.findall("item")

    for item in items:
        title_elem = item.find("title")
        if title_elem is not None and title_elem.text == old_title:
            if new_title:
                title_elem.text = new_title
            if new_link:
                item.find("link").text = new_link
                enclosure = item.find("enclosure")
                if enclosure is not None:
                    enclosure.set("url", new_link)
            if new_description:
                item.find("description").text = new_description
            if new_pubdate:
                item.find("pubDate").text = new_pubdate

            tree.write(feed_file, encoding="utf-8", xml_declaration=True)
            print(f"✅ Updated episode: {old_title}")
            return
    print(f"❌ Error: Episode with title '{old_title}' not found.")


def main():
    parser = argparse.ArgumentParser(description="RSS Feed Generator for Podcasts")
    parser.add_argument("action", choices=["create", "add", "edit"], help="Create a feed, add an episode, or edit an episode")
    parser.add_argument("--file", required=True, help="Path to the RSS feed file")
    parser.add_argument("--title", help="Title of the feed or episode")
    parser.add_argument("--link", help="Link of the feed or episode")
    parser.add_argument("--description", help="Description of the feed or episode")
    parser.add_argument("--audio", help="Path or URL to the audio or video file")
    parser.add_argument("--format", choices=["audio", "video"], help="Convert to audio-only or video with image")
    parser.add_argument("--image", help="Image file for video conversion")
    parser.add_argument("--pubdate", help="Publication date (RFC 2822 format)")
    parser.add_argument("--owner_name", help="Podcast owner's name (for create)")
    parser.add_argument("--owner_email", help="Podcast owner's email (for create)")
    parser.add_argument("--old_title", help="Old title to edit (for edit mode)")
    
    argcomplete.autocomplete(parser)

    args = parser.parse_args()

    if args.action == "create":
        if not args.title or not args.link or not args.description or not args.owner_name or not args.owner_email or not args.image:
            print("❌ Error: --title, --link, --description, --owner_name, --owner_email, and --image are required for creating a feed.")
        else:
            create_feed(args.file, args.title, args.link, args.description, args.owner_name, args.owner_email, args.image)

    elif args.action == "add":
        if not args.title or not args.link or not args.description or not args.audio:
            print("❌ Error: --title, --link, --description, and --audio are required for adding an episode.")
        else:
            add_item(args.file, args.title, args.link, args.description, args.audio, args.format, args.image, args.pubdate)

    elif args.action == "edit":
        if not args.old_title:
            print("❌ Error: --old_title is required for editing an episode.")
        else:
            edit_item(args.file, args.old_title, args.title, args.link, args.description, args.pubdate)


if __name__ == "__main__":
    main()
