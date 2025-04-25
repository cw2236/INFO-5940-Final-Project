import os
import json
import time
from openai import OpenAI
from typing import Dict, Any, List

def load_predictions(file_path: str) -> List[Dict[str, Any]]:
    """Load prediction file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def validate_prediction(prediction: Dict[str, Any]) -> Dict[str, Any]:
    """Use GPT API to validate prediction accuracy"""
    prompt = f"""
    Please evaluate the accuracy of the following prediction. Use web search to find relevant information to verify if this prediction came true.

    Prediction content: {prediction['original']}
    Prediction summary: {prediction['summary']}
    Prediction subject: {prediction['subject']}
    Prediction target: {prediction['target']}
    Deadline: {prediction['deadline']}

    Please follow these steps:
    1. Use web search to find information related to this prediction
    2. Pay special attention to events after the deadline
    3. Based on search results, determine if the prediction was accurate
    4. Provide detailed verification process and evidence

    Please return in strict JSON format as follows:
    {{
        "is_accurate": "accurate",
        "reason": "detailed judgment based on web search, including specific events, dates and sources"
    }}
    or
    {{
        "is_accurate": "inaccurate",
        "reason": "detailed judgment based on web search, including specific events, dates and sources"
    }}
    or
    {{
        "is_accurate": "unclear",
        "reason": "detailed judgment based on web search, explaining why it cannot be determined"
    }}

    Note:
    1. Return only the JSON object, no other text
    2. is_accurate value can only be "accurate", "inaccurate" or "unclear"
    3. reason must include specific search evidence and sources
    """
    
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional prediction evaluation expert. Use web search to verify prediction accuracy. Your evaluation should be based on the latest web information and provide specific evidence and sources. Return results strictly in the specified JSON format, with no additional text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        print(f"API response: {result}")  # Debug output
        
        try:
            validation = json.loads(result)
            # Verify if returned JSON contains required fields
            if "is_accurate" not in validation or "reason" not in validation:
                raise ValueError("Returned JSON missing required fields")
            
            # Verify if is_accurate value is valid
            if validation["is_accurate"] not in ["accurate", "inaccurate", "unclear"]:
                raise ValueError("Invalid is_accurate value")
            
            # Add validation results to original prediction
            prediction.update(validation)
            return prediction
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            raise ValueError(f"Unable to parse API response JSON: {result}")
            
    except Exception as e:
        print(f"Error validating prediction: {str(e)}")
        # If validation fails, add error marker
        prediction.update({
            "is_accurate": "validation failed",
            "reason": f"Error during validation: {str(e)}"
        })
        return prediction

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
            validated_prediction = validate_prediction(prediction)
            validated_predictions.append(validated_prediction)
            
            # Avoid rate limit
            if i < len(predictions):
                time.sleep(1.5)
        
        # Save validated predictions
        save_validated_predictions(validated_predictions, output_path)
        
    except Exception as e:
        print(f"Error during processing: {str(e)}") 