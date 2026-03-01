from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from collections import Counter
import re

app = FastAPI()

class TextInput(BaseModel):
    text: str

# Λέξεις για ανάλυση
absolute_words = ["ποτέ","κανείς","τίποτα","πάντα","όλοι","όλα"]
first_person_words = ["εγώ","μου","με","εμένα"]

# Patterns για γνωστικές στρεβλώσεις
catastrophizing_patterns = [
    r"τίποτα δεν", r"όλα είναι χάλια", r"δεν θα τα καταφέρω",
    r"κανείς δεν με", r"είμαι άχρηστος", r"όλα φταίνε", r"πάντα αποτυγχάνω",
    r"καταστράφηκα", r"είναι τρομερό", r"αδύνατον", r"φρικτό"
]
overgeneralization_patterns = [
    r"πάντα", r"ποτέ", r"κανείς", r"τίποτα", r"όλοι", r"όλα",
    r"συνέχεια", r"διαρκώς"
]
personalization_patterns = [
    r"όλα είναι δικό μου λάθος", r"εγώ φταίω", r"όλα εξαρτώνται από μένα",
    r"εγώ ευθύνομαι", r"εγώ φταίω για όλα"
]

def analyze_text(text):
    text_lower = text.lower()
    # Tokenization ελληνικών με regex (λειτουργεί κανονικά)
    tokens = re.findall(r'\w{2,}', text_lower)

    total_words = len(tokens)
    unique_words = len(set(tokens))
    ttr = unique_words / total_words if total_words else 0
    lexical_score = min(int(ttr*100), 100)

    word_counts = Counter(tokens)
    first_person_count = sum(word_counts[w] for w in first_person_words if w in word_counts)
    absolute_count = sum(word_counts[w] for w in absolute_words if w in word_counts)

    distortions = set()
    for pattern in catastrophizing_patterns:
        if re.search(pattern, text_lower):
            distortions.add("Καταστροφολογία")
    for pattern in overgeneralization_patterns:
        if re.search(pattern, text_lower):
            distortions.add("Υπερ-γενίκευση")
    for pattern in personalization_patterns:
        if re.search(pattern, text_lower):
            distortions.add("Προσωποποίηση")

    top_words = word_counts.most_common(10)
    if not top_words:
        top_words = [(tokens[0], 1)] if tokens else [("(καμία λέξη)", 1)]

    return {
        "total_words": total_words,
        "lexical_diversity": round(ttr, 2),
        "lexical_score": lexical_score,
        "first_person_ratio": round(first_person_count/total_words, 2) if total_words else 0,
        "absolute_expression_ratio": round(absolute_count/total_words, 2) if total_words else 0,
        "top_repeated_words": top_words,
        "cognitive_distortions": list(distortions)
    }

@app.post("/analyze")
def analyze(input: TextInput):
    return analyze_text(input.text)

# Αν δεν έχεις static folder, μπορείς να σχολιάσεις αυτή τη γραμμή
# app.mount("/", StaticFiles(directory="static", html=True), name="static")
