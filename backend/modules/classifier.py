"""
Document Classification module.
Classifies documents as invoice, form, resume, report, or letter
based on keyword analysis and entity distributions.
"""
from typing import Dict
from utils.logger import get_logger

logger = get_logger("classifier")

# Classification keywords
DOCUMENT_PATTERNS = {
    "invoice": {
        "keywords": [
            "invoice", "bill", "total", "subtotal", "tax", "amount due",
            "payment", "due date", "invoice number", "inv#", "billing",
            "purchase order", "po number", "unit price", "quantity",
            "discount", "vat", "gst", "remit", "payable",
        ],
        "weight": 1.0,
    },
    "resume": {
        "keywords": [
            "resume", "curriculum vitae", "cv", "experience", "education",
            "skills", "objective", "references", "employment", "qualification",
            "certification", "proficiency", "achievements", "career",
            "bachelor", "master", "university", "gpa", "internship",
        ],
        "weight": 1.0,
    },
    "form": {
        "keywords": [
            "form", "application", "applicant", "signature", "date of birth",
            "address", "phone number", "email", "checkbox", "please fill",
            "tick", "mark", "select", "first name", "last name",
            "social security", "ssn", "passport", "id number",
        ],
        "weight": 1.0,
    },
    "report": {
        "keywords": [
            "report", "analysis", "summary", "findings", "conclusion",
            "recommendation", "methodology", "abstract", "introduction",
            "table of contents", "appendix", "figure", "chart",
            "quarterly", "annual", "fiscal", "performance",
        ],
        "weight": 1.0,
    },
    "letter": {
        "keywords": [
            "dear", "sincerely", "regards", "to whom it may concern",
            "yours faithfully", "kind regards", "best regards",
            "re:", "subject:", "attention", "enclosed", "herewith",
            "respectfully", "cordially",
        ],
        "weight": 1.0,
    },
    "receipt": {
        "keywords": [
            "receipt", "paid", "transaction", "change", "cash",
            "credit card", "debit", "merchant", "store", "shop",
            "item", "qty", "price", "thank you for your purchase",
        ],
        "weight": 1.0,
    },
    "contract": {
        "keywords": [
            "agreement", "contract", "terms", "conditions", "party",
            "parties", "whereas", "hereby", "clause", "provision",
            "terminate", "liability", "indemnify", "governing law",
            "jurisdiction", "witness", "notary",
        ],
        "weight": 1.0,
    },
}


def classify_document(text: str, entities: Dict = None) -> Dict:
    """
    Classify document type based on keyword analysis.
    Returns document type with confidence score.
    """
    logger.info("Classifying document...")

    if not text or not text.strip():
        return {
            "document_type": "unknown",
            "confidence": 0,
            "scores": {},
        }

    text_lower = text.lower()
    scores = {}

    for doc_type, config in DOCUMENT_PATTERNS.items():
        score = 0
        matched_keywords = []

        for keyword in config["keywords"]:
            count = text_lower.count(keyword.lower())
            if count > 0:
                score += count * config["weight"]
                matched_keywords.append(keyword)

        # Bonus from entity distribution
        if entities:
            entity_data = entities.get("summary", {})
            if doc_type == "invoice" and entity_data.get("amounts_count", 0) > 2:
                score += 5
            if doc_type == "resume" and entity_data.get("persons_count", 0) >= 1:
                score += 3
            if doc_type == "letter" and entity_data.get("dates_count", 0) >= 1:
                score += 2

        scores[doc_type] = {
            "score": round(score, 2),
            "matched_keywords": matched_keywords[:10],
        }

    # Find best match
    if scores:
        best_type = max(scores, key=lambda k: scores[k]["score"])
        best_score = scores[best_type]["score"]
        total_score = sum(s["score"] for s in scores.values())

        confidence = round(
            (best_score / total_score * 100) if total_score > 0 else 0, 2
        )
    else:
        best_type = "unknown"
        confidence = 0

    result = {
        "document_type": best_type if confidence > 15 else "general",
        "confidence": confidence,
        "scores": {k: v["score"] for k, v in scores.items()},
        "top_keywords": scores.get(best_type, {}).get("matched_keywords", []),
    }

    logger.info(
        f"Classification: {result['document_type']} "
        f"(confidence: {result['confidence']}%)"
    )
    return result
