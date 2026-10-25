import re
from typing import Dict, Any, List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import numpy as np

# Rule-based keyword mapping for Indian context
KEYWORD_RULES = {
    "Food and groceries": [
        "swiggy", "zomato", "blinkit", "zepto", "bigbasket", "instamart", "mcdonald", "starbucks",
        "dominos", "kfc", "burger king", "subway", "chai", "coffee", "restaurant", "cafe", "dhaba",
        "grocery", "supermarket", "dmart", "nature's basket", "milk", "vegetables", "fruits",
        "lunch", "dinner", "breakfast", "food", "snacks", "bakery", "haldiram", "biryani", "pizza"
    ],
    "Transportation": [
        "uber", "ola", "rapido", "metro", "irctc", "railway", "train", "flight", "indigo", "air india",
        "petrol", "diesel", "fuel", "hpcl", "iocl", "bpcl", "cng", "auto", "bus", "fastag", "toll",
        "parking", "cab", "rickshaw", "chalo", "redbus", "yulu"
    ],
    "Shopping": [
        "amazon", "flipkart", "myntra", "ajio", "meesho", "nykaa", "zara", "h&m", "uniqlo", "tatacliq",
        "clothes", "shoes", "tshirt", "jeans", "electronics", "croma", "reliance digital", "appliances",
        "watch", "sunglasses", "cosmetics", "mall", "shopping", "gift"
    ],
    "Education": [
        "coursera", "udemy", "unacademy", "byjus", "tuition", "coaching", "exam fee", "hostel fee",
        "college", "university", "school", "course", "textbook", "books", "stationery", "certification",
        "library", "sem fee", "semester"
    ],
    "Rent and housing": [
        "rent", "flat rent", "room rent", "pg rent", "hostel rent", "maintenance", "society",
        "landlord", "brokerage", "house rent", "nestaway", "nobroker", "colive", "stanza"
    ],
    "Bills and utilities": [
        "electricity", "power", "bescom", "tneb", "msedcl", "water bill", "gas", "indane", "bharat gas",
        "wifi", "broadband", "airtel", "jio", "vi", "vodafone", "recharge", "dth", "tatasky", "act fibernet",
        "piped gas", "utility"
    ],
    "Healthcare": [
        "apollo", "practo", "1mg", "netmeds", "pharmeasy", "pharmacy", "medical", "medicine", "doctor",
        "clinic", "dentist", "hospital", "lab test", "diagnostics", "pathology", "consultation", "chemist"
    ],
    "Entertainment": [
        "netflix", "spotify", "prime video", "disney", "hotstar", "youtube", "cinema", "pvr", "inox",
        "bookmyshow", "game", "steam", "playstation", "pubg", "amusement", "concert", "club", "party"
    ],
    "Travel": [
        "makemytrip", "goibibo", "cleartrip", "airbnb", "hotel", "resort", "oyo", "hostel", "tour",
        "vacation", "trip", "sightseeing", "homestay", "taj hotel", "marriott"
    ],
    "Salary and income": [
        "salary", "stipend", "bonus", "freelance", "upwork", "fiverr", "dividend", "interest credited",
        "payout", "commission", "cashback", "refund", "incentive"
    ],
    "Investments and savings": [
        "zerodha", "groww", "kuvera", "et money", "indmoney", "mutual fund", "sip", "stocks", "shares",
        "nifty", "gold", "sovereign", "fixed deposit", "fd", "rd", "ppf", "nps", "crypto", "coinbase"
    ]
}

# Initial seed training dataset for ML Classifier
SEED_TRAINING_DATA = [
    ("swiggy food order dinner", "Food and groceries"),
    ("zomato lunch biryani", "Food and groceries"),
    ("blinkit fresh vegetables and milk", "Food and groceries"),
    ("zepto grocery delivery", "Food and groceries"),
    ("starbucks hazelnut latte", "Food and groceries"),
    ("dmart monthly supermarket bill", "Food and groceries"),
    ("uber trip to tech park office", "Transportation"),
    ("ola auto ride to station", "Transportation"),
    ("rapido bike commute", "Transportation"),
    ("petrol refill iocl bunk", "Transportation"),
    ("delhi metro smart card recharge", "Transportation"),
    ("irctc train tickets to home", "Transportation"),
    ("amazon prime electronics order", "Shopping"),
    ("myntra sneakers and hoodie purchase", "Shopping"),
    ("flipkart phone charger cable", "Shopping"),
    ("zara casual cotton shirt", "Shopping"),
    ("college semester tuition fee", "Education"),
    ("udemy python web development course", "Education"),
    ("books and exam preparation materials", "Education"),
    ("coursera machine learning specialisation", "Education"),
    ("monthly flat house rent to owner", "Rent and housing"),
    ("pg accommodation and security fee", "Rent and housing"),
    ("apartment society maintenance charges", "Rent and housing"),
    ("bescom electricity monthly bill", "Bills and utilities"),
    ("airtel prepaid unlimited mobile recharge", "Bills and utilities"),
    ("act fibernet high speed broadband internet", "Bills and utilities"),
    ("indane lpg cooking gas cylinder booking", "Bills and utilities"),
    ("apollo pharmacy medicines and vitamins", "Healthcare"),
    ("practo doctor consultation fee", "Healthcare"),
    ("dental checkup and cleaning clinic", "Healthcare"),
    ("blood test diagnostic lab package", "Healthcare"),
    ("netflix monthly premium streaming plan", "Entertainment"),
    ("spotify family music subscription", "Entertainment"),
    ("pvr cinemas movie tickets and popcorn", "Entertainment"),
    ("bookmyshow standup comedy show ticket", "Entertainment"),
    ("makemytrip goa weekend flight tickets", "Travel"),
    ("airbnb mountain resort cottage booking", "Travel"),
    ("monthly salary credit from company tech corp", "Salary and income"),
    ("freelance client design project payout", "Salary and income"),
    ("zerodha kite equity stock purchase", "Investments and savings"),
    ("groww monthly mutual fund sip debit", "Investments and savings"),
    ("hdfc bank fixed deposit interest credited", "Investments and savings")
]


class ExpenseCategorizer:
    def __init__(self):
        self.rules = KEYWORD_RULES
        self.model = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), lowercase=True, max_features=1000)),
            ("clf", MultinomialNB(alpha=0.5))
        ])
        self.is_trained = False
        self._initialize_model()

    def _initialize_model(self):
        texts = [x[0] for x in SEED_TRAINING_DATA]
        labels = [x[1] for x in SEED_TRAINING_DATA]
        self.model.fit(texts, labels)
        self.is_trained = True

    def _clean_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        return ' '.join(text.split())

    def match_rules(self, text: str) -> Tuple[Optional[str], float, Optional[str]]:
        clean = self._clean_text(text)
        for category, keywords in self.rules.items():
            for kw in keywords:
                # Whole word or substring pattern
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, clean):
                    return category, 0.95, kw
                elif kw in clean:
                    return category, 0.88, kw
        return None, 0.0, None

    def predict(self, title: str, description: str = "", merchant: str = "") -> Dict[str, Any]:
        combined_text = f"{title} {merchant} {description}".strip()
        
        # 1. First test high-confidence rule match (fast & deterministic for known Indian brands)
        rule_cat, rule_conf, rule_kw = self.match_rules(combined_text)
        if rule_cat and rule_conf >= 0.85:
            return {
                "predicted_category": rule_cat,
                "confidence": rule_conf,
                "model_type": "rules_engine",
                "explanation": f"Matched merchant/keyword '{rule_kw}' strongly indicating '{rule_cat}'.",
                "explanation_factors": [
                    f"Direct keyword match: '{rule_kw}'",
                    f"Mapped category domain: {rule_cat}",
                    f"Deterministic heuristic confidence: {int(rule_conf * 100)}%"
                ],
                "alternative_suggestions": [
                    {"category": "Other", "confidence": 0.05}
                ]
            }

        # 2. Use trained ML Classifier
        if self.is_trained:
            cleaned = self._clean_text(combined_text)
            probs = self.model.predict_proba([cleaned])[0]
            classes = self.model.classes_
            
            top_indices = np.argsort(probs)[::-1]
            top_category = classes[top_indices[0]]
            top_confidence = round(float(probs[top_indices[0]]), 2)

            # Alternatives
            alternatives = []
            for idx in top_indices[1:4]:
                alternatives.append({
                    "category": str(classes[idx]),
                    "confidence": round(float(probs[idx]), 2)
                })

            # Detect feature tokens matching vocabulary
            tfidf_step = self.model.named_steps.get("tfidf")
            vocab = tfidf_step.vocabulary_ if tfidf_step else {}
            tokens = [w for w in cleaned.split() if len(w) > 2]
            salient_terms = [t for t in tokens if t in vocab]

            # If rule had a lower match but ML is unsure, combine
            if rule_cat and rule_conf > top_confidence:
                return {
                    "predicted_category": rule_cat,
                    "confidence": rule_conf,
                    "model_type": "rules_engine",
                    "explanation": f"Matched keyword '{rule_kw}' associated with '{rule_cat}'.",
                    "explanation_factors": [
                        f"Keyword match: '{rule_kw}'",
                        f"Heuristic score: {int(rule_conf * 100)}%"
                    ],
                    "alternative_suggestions": alternatives
                }

            # If ML confidence is reasonably good (> 0.35)
            if top_confidence >= 0.35:
                terms_desc = f" ({', '.join(salient_terms[:3])})" if salient_terms else ""
                explanation_factors = [
                    "Classifier: Scikit-learn Multinomial Naive Bayes + TF-IDF",
                    f"Model probability score: {int(top_confidence * 100)}%"
                ]
                for term in salient_terms[:3]:
                    explanation_factors.append(f"Recognized vocabulary term: '{term}'")

                return {
                    "predicted_category": top_category,
                    "confidence": top_confidence,
                    "model_type": "machine_learning",
                    "explanation": f"Statistical text classifier identified pattern{terms_desc} matching '{top_category}'.",
                    "explanation_factors": explanation_factors,
                    "alternative_suggestions": alternatives
                }

        # 3. Fallback
        return {
            "predicted_category": "Other",
            "confidence": 0.30,
            "model_type": "fallback",
            "explanation": "No distinct keywords or trained patterns recognized; defaulting to 'Other'.",
            "explanation_factors": [
                "No heuristic keywords found in description or merchant name",
                "ML model probability below acceptance threshold (0.35)"
            ],
            "alternative_suggestions": [
                {"category": "Food and groceries", "confidence": 0.20},
                {"category": "Shopping", "confidence": 0.20}
            ]
        }

    def train_incremental(self, additional_samples: List[Tuple[str, str]]):
        """Retrain model with user-confirmed feedback."""
        if not additional_samples:
            return
        all_samples = list(SEED_TRAINING_DATA) + additional_samples
        texts = [x[0] for x in all_samples]
        labels = [x[1] for x in all_samples]
        self.model.fit(texts, labels)


categorizer_engine = ExpenseCategorizer()
