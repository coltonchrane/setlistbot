# Setlist Bot 🎸

A high-performance, polyglot Discord bot that retrieves historical concert setlists using the MusicBrainz and Setlist.fm APIs. 

This project has been re-architected from a monolithic Python script into a modern microservices system to support cloud scalability and live portfolio integration.

## 🏗️ Architecture

The system is split into two distinct services:

1.  **Backend API (.NET 10):** A robust REST API that handles data fetching, artist disambiguation via MusicBrainz, and setlist parsing. Designed for high concurrency and easy integration with other platforms (like a web portfolio).
2.  **Discord Client (Python):** A lean, asynchronous Discord bot that acts as the user interface, calling the .NET API to deliver formatted setlists to servers.

## 🚀 Key Features

- **Polyglot Design:** Leverages C#/.NET for backend logic and Python for the Discord interface.
- **Improved Accuracy:** Uses MusicBrainz MBIDs for precise artist matching, reducing "wrong artist" errors.
- **CI/CD Ready:** Automated testing and deployment workflows via GitHub Actions.
- **Cloud Native:** Optimized for hosting on Azure App Services.

## 🛠️ Project Structure

- `/SetlistApi`: ASP.NET Core Web API (The "Brain").
- `/SetlistApi.Tests`: xUnit test suite for the API.
- `setlist_bot.py`: The refactored Discord client (The "Face").
- `.github/workflows`: CI (testing) and CD (Azure deployment) configurations.

## 📥 Installation & Setup

### Local Development
1. **Clone the repo:**
   ```bash
   git clone https://github.com/coltonchrane/setlistbot.git
   ```
2. **Run the API:**
   ```bash
   cd SetlistApi
   dotnet run --apikey YOUR_SETLIST_FM_KEY
   ```
3. **Run the Bot:**
   ```bash
   # Set environment variables first
   export TOKEN="YOUR_DISCORD_TOKEN"
   export SETLIST_API_URL="http://localhost:5000/api/setlist"
   python setlist_bot.py
   ```

## 🚢 Deployment (Azure)

This repo is configured for automated deployment to Azure App Service.

### Required GitHub Secrets:
- `AZURE_SETLIST_API_NAME`: Your .NET API App Service name.
- `AZURE_SETLIST_API_PUBLISH_PROFILE`: API Publish Profile (XML).
- `AZURE_SETLIST_BOT_NAME`: Your Python Bot App Service name.
- `AZURE_SETLIST_BOT_PUBLISH_PROFILE`: Bot Publish Profile (XML).

### Required Environment Variables (Azure Portal):
- `SETLIST_FM_API_KEY` (API App Service)
- `TOKEN` (Bot App Service)
- `SETLIST_API_URL` (Bot App Service - Points to your deployed API)

## 🤖 Commands

- `$set {artist} {date}` - Get a specific setlist (Date format: DD-MM-YYYY).
- `$dead {date}` - Quick command for Grateful Dead setlists.
- `$bmfs {date}` - Quick command for Billy Strings setlists.
- `$help` - Display command list.

---
*Created by [Colton Chrane](https://github.com/coltonchrane)*
