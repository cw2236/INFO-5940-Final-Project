import os
import json
import time
from typing import Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential
from tqdm import tqdm
import datetime
import openai

# 从环境变量获取API配置
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = os.getenv('OPENAI_API_BASE', 'https://api.ai.it.cornell.edu')

def load_predictions(file_path: str = "predictions.json") -> Dict[str, List[Dict[str, Any]]]:
    """Load prediction file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=60))
def validate_prediction(prediction: Dict, video_id: str) -> Dict:
    """
    Validate a single prediction using GPT-4 with retry mechanism
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
        response = openai.ChatCompletion.create(
            model="openai.gpt-4.1",
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
        
        # Add original prediction details and metadata
        validation['original_prediction'] = prediction
        validation['video_id'] = video_id
        validation['validation_date'] = datetime.datetime.now().strftime("%Y-%m-%d")
        
        return validation

    except Exception as e:
        print(f"Error validating prediction: {str(e)}")
        return {
            'is_valid': False,
            'confidence': 0,
            'reasoning': f"Error during validation: {str(e)}",
            'evidence': [],
            'notes': "Validation failed due to an error",
            'original_prediction': prediction,
            'video_id': video_id,
            'validation_date': datetime.datetime.now().strftime("%Y-%m-%d")
        }

def save_validated_predictions(predictions: List[Dict[str, Any]], output_path: str):
    """Save validated predictions to file"""
    # Create output directory if it doesn't exist
    os.makedirs('validated_predictions', exist_ok=True)
    
    # Save results
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(predictions, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(predictions)} validated predictions to: {output_path}")

def calculate_accuracy(validated_predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate accuracy metrics for validated predictions"""
    total = len(validated_predictions)
    if total == 0:
        return {
            'total_predictions': 0,
            'accuracy': 0.0,
            'high_confidence_accuracy': 0.0,
            'validation_date': datetime.datetime.now().strftime("%Y-%m-%d"),
            'predictions_by_confidence': {
                'high': 0,
                'medium': 0,
                'low': 0
            }
        }
    
    valid_count = sum(1 for p in validated_predictions if p['is_valid'])
    high_confidence_valid = sum(1 for p in validated_predictions 
                              if p['is_valid'] and p['confidence'] >= 0.8)
    high_confidence_total = sum(1 for p in validated_predictions 
                              if p['confidence'] >= 0.8)
    
    # Count predictions by confidence level
    high_conf = sum(1 for p in validated_predictions if p['confidence'] >= 0.8)
    medium_conf = sum(1 for p in validated_predictions if 0.5 <= p['confidence'] < 0.8)
    low_conf = sum(1 for p in validated_predictions if p['confidence'] < 0.5)
    
    # Calculate accuracy by video
    video_accuracies = {}
    for pred in validated_predictions:
        video_id = pred['video_id']
        if video_id not in video_accuracies:
            video_accuracies[video_id] = {'total': 0, 'valid': 0}
        video_accuracies[video_id]['total'] += 1
        if pred['is_valid']:
            video_accuracies[video_id]['valid'] += 1
    
    for video_id in video_accuracies:
        stats = video_accuracies[video_id]
        stats['accuracy'] = stats['valid'] / stats['total']
    
    return {
        'total_predictions': total,
        'accuracy': valid_count / total,
        'high_confidence_accuracy': high_confidence_valid / high_confidence_total if high_confidence_total > 0 else 0.0,
        'validation_date': datetime.datetime.now().strftime("%Y-%m-%d"),
        'predictions_by_confidence': {
            'high': high_conf,
            'medium': medium_conf,
            'low': low_conf
        },
        'accuracy_by_video': video_accuracies
    }

if __name__ == "__main__":
    # Input and output paths
    input_path = "predictions.json"
    output_path = "validated_predictions/all_validations.json"
    metrics_path = "validated_predictions/validation_metrics.json"
    
    try:
        # Load predictions
        print("Loading predictions...")
        predictions_by_video = load_predictions(input_path)
        
        # Flatten predictions for processing
        all_predictions = []
        for video_id, preds in predictions_by_video.items():
            for pred in preds:
                all_predictions.append((video_id, pred))
        
        print(f"Found {len(all_predictions)} predictions across {len(predictions_by_video)} videos")
        
        # Validate each prediction with progress bar
        validated_predictions = []
        for video_id, prediction in tqdm(all_predictions, desc="Validating predictions"):
            validated_prediction = validate_prediction(prediction, video_id)
            validated_predictions.append(validated_prediction)
            
            # Add delay between requests to avoid rate limits
            time.sleep(2)
            
            # Save partial results periodically
            if len(validated_predictions) % 5 == 0:
                save_validated_predictions(validated_predictions, output_path)
                print("\nSaved partial results...")
        
        # Save final validated predictions
        save_validated_predictions(validated_predictions, output_path)
        
        # Calculate and save metrics
        metrics = calculate_accuracy(validated_predictions)
        
        # Save metrics to file
        with open(metrics_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
        
        # Display metrics
        print("\nValidation Metrics:")
        print(f"Total predictions: {metrics['total_predictions']}")
        print(f"Overall accuracy: {metrics['accuracy']:.2%}")
        print(f"High confidence accuracy: {metrics['high_confidence_accuracy']:.2%}")
        print("\nPredictions by confidence level:")
        print(f"High confidence (>=0.8): {metrics['predictions_by_confidence']['high']}")
        print(f"Medium confidence (0.5-0.8): {metrics['predictions_by_confidence']['medium']}")
        print(f"Low confidence (<0.5): {metrics['predictions_by_confidence']['low']}")
        print("\nAccuracy by video:")
        for video_id, stats in metrics['accuracy_by_video'].items():
            print(f"{video_id}: {stats['accuracy']:.2%} ({stats['valid']}/{stats['total']} correct)")
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        # Save any partial results
        if validated_predictions:
            save_validated_predictions(validated_predictions, output_path)
            print("Saved partial results before error") 