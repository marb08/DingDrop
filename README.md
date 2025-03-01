# 🔖 DingBot - Telegram to Linkding Bookmark Bot

DingBot is a Telegram bot that allows you to quickly save bookmarks to your **Linkding** instance via Telegram. Simply send a link, and it will be added to your bookmark collection effortlessly.

## Features
- 📌 Save bookmarks to Linkding via Telegram
- 📝 Add tags to the saved bookmark
- 🔒 Secure API token authentication

## Screenshot
![Screenshot](.img/service-selection.png?raw=true "Screenshot")
![Screenshot](.img/bookmark-saved.png?raw=true "Screenshot")

## 🔹New Feature: Readeck Integration

The bot now supports **Readeck** as a second service for saving bookmarks, alongside Linkding. When you send a link, the bot will prompt you to choose between **Linkding** or **Readeck**, and it will save the bookmark accordingly.

### 🔧 How to Enable Readeck Support

To enable Readeck, you need to rename specific files in your setup:

1. Locate all files with the `-dual` suffix in the project directory.
2. Remove the `-dual` suffix from their filenames.
3. Use these renamed files to run the bot.

This change ensures that the bot correctly recognizes and interacts with the Readeck APIs.

### 🛠 Required Configuration

Make sure to add the following environment variables in your `.env` file:

```ini
READECK_API_URL=<your-readeck-api-url>
READECK_API_TOKEN=<your-readeck-api-token>
```
> **💡 Remember:** Once these variables are set and the files renamed, it is necessay to rebuild the Docker image with the new Dockerfile provided.

Happy bookmarking! 🚀

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
- Special thanks to [mariomaz87](https://mariomaz87) for the inspiration from his project [Telegram-Wallabag-Bot](https://github.com/mariomaz87/Telegram-Wallabag-Bot).
