import os
import yt_dlp
import pandas as pd
import concurrent.futures
from typing import List
import time

def download_single_video(video_url: str, output_path: str) -> bool:
    """Download a single video"""
    # Check if output directory exists, create if not
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Skip if file already exists
    if os.path.exists(output_path):
        print(f"Video already exists: {output_path}")
        return True
    
    # Configure yt-dlp options
    ydl_opts = {
        'format': 'best',  # Download highest quality
        'outtmpl': output_path,  # Output file path
        'quiet': True,  # Reduce output information
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Starting video download: {video_url}")
            ydl.download([video_url])
            print(f"Video saved to: {output_path}")
            return True
    except Exception as e:
        print(f"Download failed for {video_url}: {str(e)}")
        return False

def download_videos_from_csv(csv_path: str, output_dir: str, max_workers: int = 4) -> None:
    """Download videos from CSV file using multiple threads"""
    # Read CSV file
    try:
        df = pd.read_csv(csv_path)
        urls = df.iloc[:, 0].tolist()  # Get URLs from first column
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare download tasks
    tasks = []
    for i, url in enumerate(urls, 1):
        output_path = os.path.join(output_dir, f"video{i}.mp4")
        tasks.append((url, output_path))
    
    # Download videos using ThreadPoolExecutor
    successful_downloads = 0
    failed_downloads = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all download tasks
        future_to_url = {
            executor.submit(download_single_video, url, path): (url, path)
            for url, path in tasks
        }
        
        # Process completed downloads
        for future in concurrent.futures.as_completed(future_to_url):
            url, path = future_to_url[future]
            try:
                success = future.result()
                if success:
                    successful_downloads += 1
                else:
                    failed_downloads += 1
            except Exception as e:
                print(f"Error processing {url}: {str(e)}")
                failed_downloads += 1
    
    # Print summary
    print("\nDownload Summary:")
    print(f"Total videos: {len(urls)}")
    print(f"Successful downloads: {successful_downloads}")
    print(f"Failed downloads: {failed_downloads}")

if __name__ == "__main__":
    # CSV file path
    csv_path = "video_links.csv"
    
    # Output directory
    output_dir = "./videos"
    
    # Number of concurrent downloads
    max_workers = 4  # Adjust this number based on your system's capabilities
    
    # Start downloading
    start_time = time.time()
    download_videos_from_csv(csv_path, output_dir, max_workers)
    end_time = time.time()
    
    print(f"\nTotal time taken: {end_time - start_time:.2f} seconds") 