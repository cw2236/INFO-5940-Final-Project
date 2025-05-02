# Video Prediction Analysis System

This project is a comprehensive system for analyzing predictions in videos. It includes tools for downloading videos, transcribing them, extracting predictions, and validating those predictions using AI.

## 🛠️ Prerequisites

Before starting, ensure you have the following installed on your system:

- Python 3.8 or higher
- Docker (Ensure Docker Desktop is running)
- VS Code
- VS Code Remote - Containers Extension
- Git
- OpenAI API Key
- FFmpeg (required for audio processing)

## 📦 Dependencies

Install the required Python packages:

```bash
pip install openai
pip install yt-dlp
pip install openai-whisper
```

## 📂 Project Structure

```
.
├── videos/              # Directory for downloaded videos
├── transcripts/         # Directory for video transcripts
├── predictions/         # Directory for extracted predictions
└── validated_predictions/  # Directory for validated predictions
```

## 🚀 Setup Guide

### 1️⃣ Configure OpenAI API Key

Since `docker-compose.yml` expects environment variables, follow these steps:

#### ➤ Option 1: Set the API Key in `.env` (Recommended)

Inside the project folder, create a `.env` file:

```sh
touch .env
```

Edit your API key and base URL in docker-compose.yml:

```plaintext
OPENAI_API_KEY=your-api-key-here
OPENAI_BASE_URL=https://api.ai.it.cornell.edu/
TZ=America/New_York
```

Make sure the `docker-compose.yml` include this `.env` file:

```yaml
version: '3.8'
services:
  devcontainer:
    container_name: info-5940-devcontainer
    build:
      dockerfile: Dockerfile
      target: devcontainer
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_BASE_URL=${OPENAI_BASE_URL}
      - TZ=${TZ}
    volumes:
      - '$HOME/.aws:/root/.aws'
      - '.:/workspace'
    env_file:
      - .env
```

Compose the container:

```sh
docker-compose up --build
```

Now, your API key will be automatically loaded inside the container.

### 2️⃣ Open in VS Code with Docker

1. Open Docker dashboard and run the image you just created (It should be called 5940)

2. Open VS Code and navigate to the project folder.

3. Open the Command Palette (`Ctrl+Shift+P` or `Cmd+Shift+P` on Mac) and search for:
   ```
   Remote-Containers: Rebuild and Reopen in Container"
   ```
4. Select From 'docker-compose.yml', then don't select any choice and click OK directly

5. Select this option. VS Code will build and open the project inside the container.

📌 **Note:** If you don't see this option, ensure that the Remote - Containers extension is installed.


## 🚀 Usage Guide

### 1. Download Video

Use `download_video.py` to download videos from YouTube or TikTok:

```bash
python download_video.py
```

The script will:
- Download the video in highest quality
- Save it to the `videos` directory
- Skip if the video already exists

### 2. Transcribe Video

Use `transcribe_video.py` to extract English subtitles from the video:

```bash
python transcribe_video.py
```

The script will:
- Use OpenAI's Whisper model to transcribe the video
- Generate both SRT and TXT files
- Save them to the `transcripts` directory
- Skip if files already exist

### 3. Extract Predictions

Use `extract_predictions.py` to identify predictions in the transcript:

```bash
python extract_predictions.py
```

The script will:
- Use GPT-4 to analyze the transcript
- Extract clear predictions about future events
- Save predictions to the `predictions` directory
- Format predictions with original text, summary, subject, target, and deadline

### 4. Validate Predictions

Use `validate_predictions.py` to verify the accuracy of predictions:

```bash
python validate_predictions.py
```

The script will:
- Use GPT-4 to validate each prediction
- Search for evidence to verify if predictions came true
- Save validation results to the `validated_predictions` directory
- Include detailed reasoning and evidence for each validation

## 📌 Features

- Download videos from YouTube/TikTok
- Extract English subtitles using Whisper
- Identify and extract predictions from transcripts
- Validate predictions using AI and web search
- Automatic file organization and management
- Skip processing for existing files

## 📝 Notes

- The system uses OpenAI's GPT-4 for prediction extraction and validation
- Whisper model "medium" is used for transcription
- All scripts include error handling and logging
- Files are organized in separate directories for better management

## 🙏 Acknowledgement

This project is developed as part of INFO-5940 at Cornell University.