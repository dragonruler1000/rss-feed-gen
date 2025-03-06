import os
import argparse
import subprocess
from feedgen.feed import FeedGenerator
from datetime import datetime
import email.utils
from datetime import UTC
import requests
from xml.etree import ElementTree as ET

def get_audio_metadata(file_path):
    """
    Fetches the content length and MIME type of an audio file.
    """
    try:
        length = str(os.path.getsize(file_path))
        mime_type = "audio/mpeg" if file_path.endswith(".mp3") else "video/mp4"
        return length, mime_type
    except Exception as e:
        print(f"⚠️ Error fetching metadata for {file_path}: {e}")
        return "0", "audio/mpeg"

def convert_media(input_file, format, image=None):
    """
    Converts MP4 to MP3 (audio-only) or combines MP3 with an image into MP4.
    Saves the file in a directory structure matching the URL path.
    """
    url_path = '/'.join(input_file.split('/')[3:-1])
    save_dir = os.path.join(os.getcwd(), url_path)
    os.makedirs(save_dir, exist_ok=True)
    output_file = os.path.join(save_dir, os.path.basename(input_file).rsplit('.', 1)[0] + (".mp3" if format == "audio" else ".mp4"))
    
    if format == "audio":
        cmd = ["ffmpeg", "-i", input_file, "-q:a", "0", "-map", "a", output_file]
    elif format == "video" and image:
        cmd = ["ffmpeg", "-loop", "1", "-i", image, "-i", input_file,
               "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k", "-shortest", output_file]
    else:
        return input_file  # Return original if no conversion needed
    
    try:
        subprocess.run(cmd, check=True)
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Error during conversion: {e}")
        return input_file

def create_feed(feed_file, title, link, description, owner_name, owner_email, image_url):
    """
    Creates a new RSS feed with iTunes-specific metadata.
    """
    fg = FeedGenerator()
    fg.title(title)
    fg.link(href=link, rel='self')
    fg.description(description)
    fg.image(image_url)
    
    # Add iTunes metadata
    fg.load_extension('podcast')
    fg.podcast.itunes_author(owner_name)
    fg.podcast.itunes_owner(owner_name, owner_email)

    # Generate feed string
    fg.rss_file(feed_file, pretty=True)
    
    if os.path.exists(feed_file):
        print(f"✅ RSS feed successfully created: {feed_file}")
    else:
        print("❌ Error: Feed file was not created.")

def add_item(feed_file, title, link, description, file_path, format=None, image=None, pubdate=None):
    """
    Adds a new episode entry to the RSS feed.
    """
    if not os.path.exists(feed_file):
        print("⚠️ Feed file does not exist. Creating a new one...")
        create_feed(feed_file, "My Podcast", "https://podcast.yourdomain.com", "A great podcast", "Owner Name", "owner@example.com", "https://example.com/podcast.jpg")
    
    # Determine format based on file extension if not provided
    if format is None:
        format = "audio" if file_path.endswith(".mp3") else "video"
    
    converted_file = convert_media(file_path, format, image)
    
    # Ensure file was actually created
    if not os.path.exists(converted_file):
        print(f"❌ Error: Converted file was not created: {converted_file}")
        return
    
    # Parse existing feed
    tree = ET.parse(feed_file)
    root = tree.getroot()
    channel = root.find("channel")

    # Fetch audio metadata
    length, mime_type = get_audio_metadata(converted_file)

    # Create new item element
    item = ET.Element("item")
    ET.SubElement(item, "title").text = title
    ET.SubElement(item, "link").text = converted_file
    ET.SubElement(item, "description").text = description
    ET.SubElement(item, "pubDate").text = pubdate if pubdate else email.utils.format_datetime(datetime.now(UTC))

    # Add enclosure for podcast episode
    enclosure = ET.SubElement(item, "enclosure")
    enclosure.set("url", converted_file)
    enclosure.set("length", length)
    enclosure.set("type", mime_type)

    # Append new item to channel
    channel.append(item)

    # Save updated feed
    tree.write(feed_file, encoding="utf-8", xml_declaration=True)
    print(f"✅ Added new episode: {title}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RSS Feed Generator for Podcasts")
    parser.add_argument("action", choices=["create", "add"], help="Create a new feed or add an episode")
    parser.add_argument("--file", required=True, help="Path to the RSS feed file")
    parser.add_argument("--title", help="Title of the feed or episode")
    parser.add_argument("--link", help="Link of the feed or episode")
    parser.add_argument("--description", help="Description of the feed or episode")
    parser.add_argument("--audio", help="Path to the audio or video file")
    parser.add_argument("--format", choices=["audio", "video"], help="Optional: Convert MP4 to MP3 (audio) or combine MP3 with image into MP4 (video)")
    parser.add_argument("--image", help="Image file for video conversion")
    parser.add_argument("--pubdate", help="Publication date for episode (RFC 2822 format)")
    parser.add_argument("--owner_name", help="Name of the podcast owner")
    parser.add_argument("--owner_email", help="Email address of the podcast owner")

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
