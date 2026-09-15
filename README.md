# twitch-clip-downloader

A lightweight command line utility to download Twitch clips. It uses Twitch's internal GQL API to fetch direct video streams, so you don't have to register a developer account or deal with OAuth tokens.

## Installation

Clone the repository and install the single dependency:

```cmd
pip install -r requirements.txt
```

## Usage

Pass a clip URL or its slug to the script. By default, it saves the highest quality video to your current directory.

```cmd
python clip_downloader.py https://clips.twitch.tv/GloriousTiredSpindlePeanutButter-abc123xyz
```

You can specify an output directory and preferred resolution:

```cmd
python clip_downloader.py GloriousTiredSpindlePeanutButter-abc123xyz --out D:\Downloads --resolution 720
```

To view all options:

```cmd
python clip_downloader.py --help
```

<!-- last-checked: 2026-09-15 -->
