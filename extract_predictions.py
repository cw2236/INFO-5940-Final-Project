import os
import json
import openai
import pandas as pd
from typing import List, Dict
from tqdm import tqdm
from datetime import datetime
import yt_dlp
import time
from tenacity import retry, stop_after_attempt, wait_exponential

def split_text(text: str, max_tokens: int = 3000) -> List[str]:
    """
    Split text into chunks that are within token limits
    """
    # Simple splitting by sentences
    sentences = text.split('. ')
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        # Approximate token count (roughly 4 chars per token)
        sentence_tokens = len(sentence) // 4
        
        if current_length + sentence_tokens > max_tokens and current_chunk:
            chunks.append('. '.join(current_chunk) + '.')
            current_chunk = []
            current_length = 0
            
        current_chunk.append(sentence)
        current_length += sentence_tokens
        
    if current_chunk:
        chunks.append('. '.join(current_chunk) + '.')
        
    return chunks

def get_video_upload_date(url: str) -> str:
    """
    Get video upload date using yt-dlp
    """
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'force_generic_extractor': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Try different date fields based on platform
            if 'upload_date' in info:  # YouTube format
                upload_date = info['upload_date']
                return f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
            elif 'timestamp' in info:  # TikTok format
                timestamp = info['timestamp']
                if timestamp:
                    date = datetime.fromtimestamp(timestamp)
                    return date.strftime('%Y-%m-%d')
            elif 'uploader_date' in info:  # Alternative TikTok format
                uploader_date = info['uploader_date']
                if uploader_date:
                    return uploader_date
            
            # If no date found, return None
            return None
            
    except Exception as e:
        print(f"Error getting upload date for {url}: {str(e)}")
    return None

def get_video_dates() -> Dict[str, str]:
    """
    Get video publish dates from video_links.csv and platform metadata
    """
    try:
        # Read CSV file with proper encoding and handle line breaks in fields
        df = pd.read_csv('video_links.csv', encoding='utf-8', lineterminator='\n')
        video_dates = {}
        unknown_dates = []
        
        # Extract video ID from filename (e.g., "video1" from "video1.txt")
        for filename in os.listdir('./transcripts'):
            if filename.endswith('.txt'):
                video_id = os.path.splitext(filename)[0]
                try:
                    # Get the corresponding row from the CSV
                    index = int(video_id.replace('video', '')) - 1
                    if index < len(df):
                        row = df.iloc[index]
                        url = str(row['Link']).strip()  # Convert to string and strip whitespace
                        
                        # Try to get upload date from platform
                        if pd.notna(url):
                            upload_date = get_video_upload_date(url)
                            if upload_date:
                                video_dates[video_id] = upload_date
                                print(f"Found upload date for {video_id}: {upload_date}")
                                continue
                        
                        # If we can't get the date, mark it as unknown
                        video_dates[video_id] = "unknown"
                        unknown_dates.append(video_id)
                        print(f"Could not determine upload date for {video_id}")
                        
                except (ValueError, IndexError) as e:
                    print(f"Error processing {video_id}: {str(e)}")
                    video_dates[video_id] = "unknown"
                    unknown_dates.append(video_id)
        
        # Print summary of videos with unknown dates
        if unknown_dates:
            print("\nVideos with unknown publish dates:")
            for video_id in unknown_dates:
                print(f"- {video_id}")
                    
        return video_dates
    except Exception as e:
        print(f"Error reading video dates: {str(e)}")
        return {}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=60))
def extract_predictions_from_text(text: str, publish_date: str = None) -> List[Dict]:
    """
    Extract predictions from text using OpenAI API with retry mechanism
    """
    try:
        # Split text if it's too long
        chunks = split_text(text)
        all_predictions = []
        
        for chunk in chunks:
            system_prompt = """You are an expert at identifying specific predictions about future events or outcomes. 
            Extract ONLY clear predictions that meet ALL of these criteria:
            1. Must make a specific claim about the future
            2. Must include either:
               - A specific timeframe (e.g., "by 2024", "next year", "in 6 months")
               - A specific target or value (e.g., "$100,000", "50% increase")
               - A clear outcome or event (e.g., "will reach", "will achieve", "will happen")
            
            IMPORTANT: You must return a valid JSON array of prediction objects. Each prediction object should have:
            {
                "time": "specific timeframe if mentioned",
                "event": "what is being predicted about",
                "prediction": "the specific prediction content",
                "made_at": "when this prediction was made (video publish date)"
            }
            
            Example response format:
            [
                {
                    "time": "by 2024",
                    "event": "AI development",
                    "prediction": "AI will achieve human-level intelligence",
                    "made_at": "2023-01-15"
                }
            ]
            
            Return ONLY valid predictions that meet ALL criteria. Be strict about what counts as a prediction.
            If no predictions are found, return an empty array: []"""
            
            if publish_date:
                system_prompt += f"\n\nNote: The video was published on {publish_date}. Use this as the 'made_at' date for all predictions."
            
            # Add delay between requests to avoid rate limits
            time.sleep(2)
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": system_prompt
                    },
                    {
                        "role": "user", 
                        "content": f"Extract predictions from this text:\n\n{chunk}"
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            try:
                content = response.choices[0].message.content
                # Parse the response as JSON
                predictions = json.loads(content)
                if isinstance(predictions, list):
                    all_predictions.extend(predictions)
            except json.JSONDecodeError:
                print(f"Failed to parse prediction response as JSON. Response was: {content}")
                continue
                
        return all_predictions
    except Exception as e:
        print(f"Error extracting predictions: {str(e)}")
        raise  # Re-raise the exception for retry mechanism

def process_transcripts(input_dir: str, output_file: str) -> None:
    """
    Process all transcript files and extract predictions
    """
    # Get all txt files
    txt_files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]
    
    if not txt_files:
        print("No transcript files found")
        return
    
    print(f"Processing {len(txt_files)} transcript files")
    
    # Get video publish dates
    video_dates = get_video_dates()
    print("Video publish dates loaded")
    
    all_predictions = {}
    
    # Process each file
    for filename in tqdm(txt_files, desc="Processing transcripts"):
        file_path = os.path.join(input_dir, filename)
        video_id = os.path.splitext(filename)[0]
        
        try:
            # Read transcript text
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Get publish date for this video
            publish_date = video_dates.get(video_id)
            
            # Extract predictions with retry mechanism
            predictions = extract_predictions_from_text(text, publish_date)
            
            if predictions:
                all_predictions[video_id] = predictions
                print(f"Extracted {len(predictions)} predictions from {video_id}")
            else:
                print(f"No predictions found in {video_id}")
                
            # Add delay between files to avoid rate limits
            time.sleep(5)
                
        except Exception as e:
            print(f"Error processing file {filename}: {str(e)}")
            # Save partial results in case of error
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_predictions, f, ensure_ascii=False, indent=2)
            print(f"Partial results saved to {output_file}")
            continue
    
    # Save final results
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_predictions, f, ensure_ascii=False, indent=2)
    
    print(f"\nProcessing complete! Results saved to {output_file}")
    print(f"Total predictions extracted from {len(all_predictions)} videos")

if __name__ == "__main__":
    # Set input/output paths
    input_dir = "./transcripts"
    output_file = "./predictions.json"
    
    # Set OpenAI API key
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    # Start processing
    process_transcripts(input_dir, output_file) 