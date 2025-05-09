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
OPENAI_API_BASE=https://api.ai.it.cornell.edu  # For Cornell IT API
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
- Validate each prediction using GPT-4.1
- Save validation results in `validated_predictions/` directory:
  - `all_validations.json`: Detailed validation results for each prediction
  - `validation_metrics.json`: Summary metrics and statistics

## Latest Results

### Validation Metrics
- Total predictions analyzed: 97
- Overall accuracy: 29.90%
- High confidence accuracy: 36.25%

### Confidence Distribution
- High confidence (>=0.8): 80 predictions
- Medium confidence (0.5-0.8): 3 predictions
- Low confidence (<0.5): 14 predictions

### Video-wise Accuracy
- 100% accuracy: video1, video4, video8
- 25-40% accuracy: video5, video6, video7, video9, video10
- 0% accuracy: video12, video15, video16, video19, video20, video21, video23

## Project Structure

```
.
├── videos/                  # Downloaded videos
├── transcripts/            # Video transcripts (SRT and TXT)
├── predictions.json        # Extracted predictions
├── validated_predictions/  # Validation results
│   ├── all_validations.json  # Detailed validation results
│   └── validation_metrics.json  # Summary metrics
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
- API configuration supports Cornell IT API endpoints
