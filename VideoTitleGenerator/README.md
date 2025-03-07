# YouTube Shorts Topic Generator

This Python application helps YouTube creators find optimal topics for their Shorts content by analyzing their channel data, content performance, and current trends on YouTube.

## Features

- **Channel Analysis**: Analyzes your YouTube channel's existing content and performance metrics
- **Content Performance Tracking**: Identifies which topics perform best on your channel
- **Trend Integration**: Incorporates current YouTube trending topics
- **Smart Suggestions**: Generates topic ideas based on the intersection of your channel's strengths and current trends
- **Performance Visualization**: Creates visual charts of topic performance

## Requirements

- Python 3.6+
- Google account with access to YouTube Data API v3
- OAuth 2.0 client credentials

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2 pandas numpy matplotlib seaborn nltk
```

## Setup

1. Create a project in the [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the YouTube Data API v3
3. Create OAuth 2.0 credentials (Desktop application)
4. Download the credentials JSON file and save it as `client_secret.json` in the project directory

## Usage

Run the application with:

```bash
python youtube_shorts_topic_generator.py
```

The application will:

1. Authenticate with your YouTube account
2. Analyze your channel's content (focusing on Shorts by default)
3. Identify trending topics on YouTube
4. Generate topic suggestions based on your channel's performance and current trends
5. Optionally create visualizations of topic performance

## How It Works

The application uses natural language processing to extract topics from your video titles and descriptions, then correlates these topics with performance metrics like views and engagement. It also analyzes current trending content on YouTube to find opportunities where your channel's strengths align with popular topics.

## Notes

- The first time you run the application, it will open a browser window for authentication
- Your credentials are stored locally in a `token.pickle` file for future use
- The application respects YouTube API quotas and rate limits

## License

MIT