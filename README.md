# RSS Generator

RSS Generator is a command-line tool that creates RSS feeds for podcasts, with optional media conversion features. It supports both audio and video formats, automatically generating RSS metadata and iTunes-compatible podcast feeds.

## Features
- Create new RSS podcast feeds
- Add episodes to existing feeds
- Automatic media format conversion (MP4 to MP3 or MP3 to MP4 with images)
- iTunes-compatible metadata
- File size and MIME type detection

## Installation

### From PyPI
```bash
pip install rss-gen
```

### From Source
```bash
git clone https://github.com/dragonruler1000/rss-feed-gen.git
cd link-rss-gen
pip install .
```

## Usage

### Create a New Feed
```bash
rssgen create --file feed.xml \
            --title "My Podcast" \
            --link "https://podcast.yourdomain.com" \
            --description "A great podcast" \
            --owner_name "Your Name" \
            --owner_email "your_email@example.com" \
            --image "cover.jpg"
```

### Add Episode to Feed
```bash
rssgen add --file feed.xml \
         --title "Episode 1" \
         --link "https://podcast.yourdomain.com/ep1" \
         --description "First episode" \
         --audio "audio.mp3"
```

### Optional Conversion
Convert MP4 to MP3 or combine MP3 with an image into MP4:
```bash
rssgen add --file feed.xml \
         --title "Episode 2" \
         --link "https://podcast.yourdomain.com/ep2" \
         --description "Video episode" \
         --audio "video.mp4" \
         --format video \
         --image "thumbnail.jpg"
```

## Dependencies
- `feedgen`
- `requests`
- `ffmpeg`
- `xmltodict`

## License
This project is licensed under the MIT License.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

## Author
Zachariah Jackson
[rssgen@me.minecraftchest2.us]

## Acknowledgements
Inspired by podcast tools and open-source projects.

