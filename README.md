# 🔖 DingBot - Telegram to Linkding Bookmark Bot

DingBot is a Telegram bot that allows you to quickly save bookmarks to your **Linkding** instance via Telegram. Simply send a link, and it will be added to your bookmark collection effortlessly.

## Features
- 📌 Save bookmarks to Linkding via Telegram
- 📝 Add tags to the saved bookmark
- 🔒 Secure API token authentication

## Screenshot
![Screenshot](.img/url-send.png?raw=true "Screenshot")


## Local Installation

### Prerequisites
- A **Linkding** self-hosted instance ([Linkding Repo](https://github.com/sissbruecker/linkding))
- A **Telegram Bot Token** from [BotFather](https://core.telegram.org/bots#botfather)
- Python 3.8+

### Setup

1. **Clone this repository**
   ```sh
   git clone https://github.com/marb08/dingdrop.git
   cd dingdrop/
   ```

2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   - Edit `example.env` with your details.
   - Rename `example.env` to `.env`.

4. **Run the bot**
   ```sh
   python bot.py
   ```

## Self-Hosting - Docker 

You can also deploy DingBot using Docker and **docker-compose**.

1. **Clone this repository**
   ```sh
   git clone https://github.com/marb08/dingdrop.git
   cd dingdrop/
   ```

2. **Modify environment variables**
   - Edit `example.env` with your details.
   - Rename `example.env` to `.env`.

3. **Build and start the container**
   ```sh
   docker-compose build
   docker-compose up -d
   ```
This will launch the bot in a Docker container, allowing it to run in background.

## Usage
- Send a URL to the bot, and it will be saved automatically.
- Send comma separated tags to be added to the bookmark (/skip to skip the tags)

## Future Improvements
- [ ] Retrieve the list of all saved bookmarks
- [ ] Fetch and search existing bookmarks
- [ ] Modify an existing bookmark
- [ ] Create/Modify new tags

## Contributing
Pull requests are welcome! Feel free to submit issues or feature requests to improve DingBot.

## Acknowledgments
- Thanks to the developers of [Linkding](https://github.com/sissbruecker/linkding) for creating an awesome bookmarking tool!
- Special thanks to [mariomaz87](https://github.com/mariomaz87) for the inspiration from his project [Telegram-Wallabag-Bot](https://github.com/mariomaz87/Telegram-Wallabag-Bot).
