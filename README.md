# RSS Generator

**RSS Generator** is a command-line tool for creating and managing podcast RSS feeds with built-in media conversion. It supports both audio and video formats, auto-generates iTunes-compatible metadata, and allows full control over feed entries — all from your terminal.

---

## 🚀 Features

- 📡 Create new podcast RSS feeds with iTunes metadata
- 🎧 Add new episodes with audio or video content
- 🔄 Automatic media conversion (MP4 → MP3 or MP3 + image → MP4)
- 🖼️ Video episodes from static images and audio
- ✍️ Edit existing episode entries
- 📆 Works with local files and HTTP(S) URLs
- 🧠 Tab-completion support (via [`argcomplete`](https://pypi.org/project/argcomplete/))

---

## 📦 Installation

### 🔧 Set Up a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 📅 Install from PyPI
```bash
pip install rss-feed-gen
```

### 🛠️ Or Install from Source
```bash
git clone https://github.com/dragonruler1000/rss-feed-gen.git
cd rss-feed-gen
pip install .
```

---

## 🧪 Usage

### 📁 Create a New Feed
```bash
rssgen create --file feed.xml \
              --title "My Podcast" \
              --link "https://podcast.yourdomain.com" \
              --description "A great podcast" \
              --owner_name "Your Name" \
              --owner_email "your_email@example.com" \
              --image "cover.jpg"
```

### ➕ Add an Episode
```bash
rssgen add --file feed.xml \
           --title "Episode 1" \
           --link "https://podcast.yourdomain.com/ep1" \
           --description "First episode" \
           --audio "audio.mp3"
```

### 🎞️ Add a Video Episode (MP3 + Image)
```bash
rssgen add --file feed.xml \
           --title "Episode 2" \
           --link "https://podcast.yourdomain.com/ep2" \
           --description "Video episode" \
           --audio "audio.mp3" \
           --format video \
           --image "cover.jpg"
```

### ✏️ Edit an Existing Episode
```bash
rssgen edit --file feed.xml \
            --old_title "Episode 1" \
            --title "Updated Title" \
            --link "https://newlink.com" \
            --description "New description"
```

---

## ⚙️ Dependencies

- [`feedgen`](https://pypi.org/project/feedgen/)
- [`requests`](https://pypi.org/project/requests/)
- [`ffmpeg`](https://ffmpeg.org/) (system dependency)
- [`argcomplete`](https://pypi.org/project/argcomplete/) (optional, for tab-completion)

> 🛠️ Make sure `ffmpeg` is installed and in your system path.

---

## 🧠 Enable Tab Completion (Optional)

```bash
pip install argcomplete
activate-global-python-argcomplete --user
# OR for bash only:
eval "$(register-python-argcomplete rssgen)"
```

---

## 📜 License

MIT License — see [LICENSE](./LICENSE) for full text.

---

## 🤝 Contributing

Pull requests are welcome!  
For major changes, please open an issue to discuss ideas first.

---

## 👤 Author

**Zachariah Jackson**  
📧 rssgen@me.minecraftchest2.us

---

## 🙏 Acknowledgements

Inspired by podcasting tools, open-source media projects, and everyone making the web more creative.

