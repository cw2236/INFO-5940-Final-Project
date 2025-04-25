import os
import json
from openai import OpenAI
from typing import Dict, Any

def load_transcript(file_path: str) -> str:
    """Load transcript file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_predictions(transcript: str) -> Dict[str, Any]:
    """Use GPT API to extract predictive statements from text"""
    prompt = f"""
    Please analyze the following text and extract ONLY clear predictions about future events or outcomes. 
    
    A valid prediction MUST:
    1. Make a specific claim about the future
    2. Include either:
       - A specific timeframe (e.g., "by 2024", "next year", "in 6 months")
       - A specific target or value (e.g., "$100,000", "50% increase")
       - A clear outcome or event (e.g., "will reach", "will achieve", "will happen")
    
    DO NOT include:
    - General statements about trends
    - Personal opinions without specific predictions
    - Vague possibilities without concrete outcomes
    - General goals without specific targets
    - Conditional statements without clear predictions
    
    Text to analyze:
    {transcript}

    For each valid prediction you find, format it as a JSON object with:
    {{
        "original": "exact quote from the text",
        "summary": "brief summary of the specific prediction",
        "subject": "what is being predicted about",
        "target": "specific target value or outcome",
        "deadline": "specific timeframe if mentioned"
    }}

    Return ONLY the JSON array of valid predictions, nothing else. Be strict about what counts as a prediction.
    """
    
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert at identifying specific, concrete predictions about future events or outcomes. Only extract predictions that include specific timeframes, targets, or clear outcomes. Be strict about what counts as a prediction."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        result = response.choices[0].message.content.strip()
        # Ensure the returned value is valid JSON
        return json.loads(result)
    except Exception as e:
        print(f"Error extracting predictions: {str(e)}")
        return []

def save_predictions(predictions: Dict[str, Any], output_path: str):
    """Save prediction results to file"""
    # Check if output directory exists, create if not
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save results
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(predictions, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(predictions)} predictions to: {output_path}")

if __name__ == "__main__":
    # Set OpenAI API key
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    
    # Input and output paths
    transcript_path = "./transcripts/video1.txt"
    output_path = "./predictions/video1.json"
    
    try:
        # Load transcript
        print("Loading transcript file...")
        transcript = load_transcript(transcript_path)
        
        # Extract predictions
        print("Extracting predictions...")
        predictions = extract_predictions(transcript)
        
        # Save results
        save_predictions(predictions, output_path)
        
    except Exception as e:
        print(f"Error during processing: {str(e)}") 