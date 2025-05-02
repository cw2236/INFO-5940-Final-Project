# Video Prediction Extraction and Validation

This project provides tools for downloading videos, extracting predictions from video transcripts, and validating these predictions using GPT-4.

## Features

- **Video Download**: Download videos from various platforms (YouTube, TikTok, etc.) using `yt-dlp`
- **Video Transcription**: Extract English subtitles from videos using OpenAI's Whisper model
- **Prediction Extraction**: Extract predictions from video transcripts using GPT-4
- **Prediction Validation**: Validate predictions using GPT-4 with web search capabilities

## Prerequisites

- Python 3.8+
- OpenAI API key
- Docker (optional, for containerized environment)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/cw2236/INFO-5940-Final-Project.git
cd INFO-5940-Final-Project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

### 1. Download Videos

Create a `video_links.csv` file with video URLs in the first column, then run:
```bash
python download_video.py
```

The script will:
- Download videos from the URLs in `video_links.csv`
- Save videos in the `./videos` directory
- Use multithreading for faster downloads
- Skip existing videos

### 2. Transcribe Videos

Run the transcription script:
```bash
python transcribe_video.py
```

The script will:
- Process all videos in the `./videos` directory
- Extract English subtitles using Whisper
- Save transcripts in both SRT and TXT formats in `./transcripts`
- Skip already transcribed videos

### 3. Extract Predictions

Run the prediction extraction script:
```bash
python extract_predictions.py
```

The script will:
- Process all transcript files in `./transcripts`
- Extract predictions using GPT-4
- Save results in `predictions.json`
- Include video publish dates for each prediction
- Handle rate limits with automatic retries

### 4. Validate Predictions

Run the validation script:
```bash
python validate_predictions.py
```

The script will:
- Read predictions from `predictions.json`
- Validate each prediction using GPT-4
- Perform web searches to verify predictions
- Save validation results in `validated_predictions.json`

## Project Structure

```
.
├── videos/                  # Downloaded videos
├── transcripts/            # Video transcripts (SRT and TXT)
├── predictions.json        # Extracted predictions
├── validated_predictions/  # Validation results
├── download_video.py      # Video download script
├── transcribe_video.py    # Transcription script
├── extract_predictions.py # Prediction extraction script
└── validate_predictions.py # Prediction validation script
```

## Notes

- The project uses rate limiting and retry mechanisms to handle API limits
- All scripts include progress bars and detailed logging
- Results are saved in JSON format for easy analysis
- The project is containerized using Docker for easy deployment

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.