import ahocorasick
import re
from typing import Any

DTC_REGEX = re.compile(r'\b[PFCBU]\d{4}\b', re.IGNORECASE)

INTENT_KEYWORDS = {
    "trend_analysis": ["추이", "증가", "감소", "월별", "시계열"],
    "similar_case": ["유사", "과거", "이력", "사례", "비슷"],
    "supplier_analysis": ["협력사", "공급업체", "업체", "납품"],
    "cause_analysis": ["원인", "이유", "왜", "문제"]
}

class SmartIntentRouter:
    def __init__(self):
        self.automaton = ahocorasick.Automaton()
        self._build()

    def _build(self):
        for model in ["NX4", "CN7", "DN8", "GV80"]:
            self.automaton.add_word(model.upper(), ("model", model.upper()))
        for intent, keywords in INTENT_KEYWORDS.items():
            for word in keywords:
                self.automaton.add_word(word, ("intent", intent))
        self.automaton.make_automaton()

    def route(self, user_query: str) -> dict[str, Any]:
        dtc_match = DTC_REGEX.search(user_query)
        if dtc_match:
            return {
                "fast_path": True,
                "intent": "dtc_analysis",
                "params": {"dtc": dtc_match.group().upper()}
            }

        detected_model = None
        detected_intent = "cause_analysis" 
        
        for _, (category, value) in self.automaton.iter(user_query.upper()):
            if category == "model": detected_model = value
            elif category == "intent": detected_intent = value

        return {
            "fast_path": False,
            "intent": detected_intent,
            "params": {"model": detected_model, "raw_query": user_query}
        }

router = SmartIntentRouter()