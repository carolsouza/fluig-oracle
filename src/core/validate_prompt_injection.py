from transformers import pipeline

def get_detector():
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")


def detect_prompt_injection(text: str) -> bool:
    detector = get_detector()
    candidate_labels = ["prompt injection", "normal query", "instructions query"]
    result = detector(text, candidate_labels)
    label = result["labels"][0]
    return label == "prompt injection"
