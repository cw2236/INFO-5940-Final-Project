import os
import json
import time
from openai import OpenAI
from typing import Dict, Any, List

def load_predictions(file_path: str) -> List[Dict[str, Any]]:
    """Load prediction file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_prediction(prediction: Dict, video_id: str) -> Dict:
    """
    Validate a single prediction using GPT-4
    """
    try:
        # Construct the prompt
        prompt = f"""You are an expert at validating predictions. Analyze this prediction and determine if it has come true.

Prediction Details:
- Time: {prediction['time']}
- Event: {prediction['event']}
- Prediction: {prediction['prediction']}
- Made at: {prediction['made_at']}

Please provide a detailed analysis in the following JSON format:
{{
    "is_valid": true/false,
    "confidence": 0-1,
    "reasoning": "Detailed explanation of why the prediction is considered valid or invalid",
    "evidence": [
        {{
            "source": "Source of evidence",
            "description": "Description of the evidence",
            "url": "URL of the evidence (if available)"
        }}
    ],
    "notes": "Additional observations or caveats"
}}

Important:
1. Be thorough in your analysis
2. Search for concrete evidence
3. Consider the timeframe specified in the prediction
4. If the prediction is about a future event, mark it as not yet validated
5. Provide specific examples and sources when possible
6. Consider both direct and indirect evidence
7. If the prediction is vague or unclear, explain why it's difficult to validate

Please respond with ONLY the JSON object, no additional text."""

        # Get validation from GPT-4
        response = OpenAI().chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at validating predictions. Provide detailed analysis with evidence."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )

        # Parse the response
        validation = json.loads(response.choices[0].message.content)
        
        # Add original prediction details
        validation['original_prediction'] = {
            'time': prediction['time'],
            'event': prediction['event'],
            'prediction': prediction['prediction'],
            'made_at': prediction['made_at']
        }
        
        return validation

    except Exception as e:
        print(f"Error validating prediction: {str(e)}")
        return {
            'is_valid': False,
            'confidence': 0,
            'reasoning': f"Error during validation: {str(e)}",
            'evidence': [],
            'notes': "Validation failed due to an error",
            'original_prediction': {
                'time': prediction['time'],
                'event': prediction['event'],
                'prediction': prediction['prediction'],
                'made_at': prediction['made_at']
            }
        }

def save_validated_predictions(predictions: List[Dict[str, Any]], output_path: str):
    """Save validated predictions to file"""
    # Check if output directory exists, create if not
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Save results
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(predictions, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(predictions)} validated predictions to: {output_path}")

if __name__ == "__main__":
    # Set OpenAI API key
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    
    # Input and output paths
    input_path = "./predictions/video1.json"
    output_path = "./validated_predictions/video1_validated.json"
    
    try:
        # Load predictions
        print("Loading prediction file...")
        predictions = load_predictions(input_path)
        
        # Validate each prediction
        validated_predictions = []
        for i, prediction in enumerate(predictions, 1):
            print(f"Validating prediction {i}/{len(predictions)}...")
            validated_prediction = validate_prediction(prediction, "video1")
            validated_predictions.append(validated_prediction)
            
            # Avoid rate limit
            if i < len(predictions):
                time.sleep(1.5)
        
        # Save validated predictions
        save_validated_predictions(validated_predictions, output_path)
        
    except Exception as e:
        print(f"Error during processing: {str(e)}") 