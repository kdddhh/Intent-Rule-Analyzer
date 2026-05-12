import ahocorasick

# 의도 규칙이랑 딕셔너리는 DB에 미리 정의해두고 가져오는 것도 괜찮을듯?
INTENT_RULES = {
    "cause_analysis": ["원인", "이유", "왜", "문제", "불량"],
    "trend_analysis": ["추이", "증가", "감소", "월별", "기간별"],
    "similar_case": ["유사", "비슷", "사례", "동일"],
    "supplier_analysis": ["협력사", "업체", "supplier"],
    "dtc_analysis": ["dtc", "고장코드", "p0"]
}
ENTITIES_DICT = {
    "vehicle": ["NX4", "CN7", "DN8"],
    "symptom": ["변속충격", "시동불량", "소음", "진동"]
}

class IntentAnalyzer:
    def __init__(self):
        self.automaton = ahocorasick.Automaton()
        self._build()

    def _build(self):
        combined_dict = {**INTENT_RULES, **ENTITIES_DICT}
        for category, keywords in combined_dict.items():
            for word in keywords:
                self.automaton.add_word(word, (category, word))
        self.automaton.make_automaton()

    def analyze(self, user_query: str):
        found_entities = []
        intent = "general_search"
        
        for _, (category, word) in self.automaton.iter(user_query):
            if category in INTENT_RULES:
                intent = category
            else:
                found_entities.append({"type": category, "value": word})
                
        return intent, found_entities

# 싱글톤 인스턴스 사용 : api 호출될 때마다 객체를 계속 새로 만들게 하면 CPU 연산 비용이랑 메모리 폭발할 수도..
analyzer_instance = IntentAnalyzer()