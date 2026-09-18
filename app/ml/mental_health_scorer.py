import json
from typing import List, Dict, Tuple

def calculate_wellness_score(survey_responses: List[Dict]) -> Tuple[int, str, dict]:
    """
    Calculate mental wellness score from survey responses.
    Returns: (score: 0-100, risk_level: str, factors: dict)
    """
    score = 100
    factors = {"positive": 0, "negative": 0}
    
    for response in survey_responses:
        q_id = response.get("question_id")
        answer = response.get("answer", "").lower()
        items = [i.strip() for i in answer.split(",")]
        
        if q_id == 1:
            for item in items:
                if item:
                    score -= 5
                    factors["negative"] += 1
        elif q_id == 2:
            if "very high" in answer: score -= 15
            elif "high" in answer: score -= 10
            elif "moderate" in answer: score -= 5
            if "high" in answer or "very high" in answer:
                factors["negative"] += 1
        elif q_id == 3:
            for item in items:
                if item and item != "none":
                    score -= 2
        elif q_id == 4:
            if "poor" in answer: score -= 10
            elif "very poor" in answer: score -= 15
            elif "good" in answer or "excellent" in answer:
                score += 5
                factors["positive"] += 1
        elif q_id == 5:
            if "isolated" in answer: score -= 10
            elif "active" in answer or "very active" in answer:
                score += 10
                factors["positive"] += 1
        elif q_id == 6:
            hobbies = len([i for i in items if i])
            score += (hobbies * 3)
            if hobbies > 0:
                factors["positive"] += 1
        elif q_id == 7:
            stressors = len([i for i in items if i])
            score -= (stressors * 3)
        elif q_id == 9:
            if "daily" in answer or "4-5" in answer:
                score += 10
                factors["positive"] += 1
            elif "never" in answer:
                score -= 5
    
    score = max(0, min(100, score))
    
    if score >= 80:
        risk_level = "low"
    elif score >= 60:
        risk_level = "moderate"
    elif score >= 40:
        risk_level = "high"
    else:
        risk_level = "critical"
        
    return score, risk_level, factors
