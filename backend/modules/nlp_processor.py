"""
NLP Processing module using spaCy.
Extracts named entities: names, dates, amounts, organizations.
"""
import json
from typing import Dict, List
from utils.logger import get_logger
from config import SPACY_MODEL

logger = get_logger("nlp_processor")

_nlp = None


def _get_nlp():
    """Lazy-load spaCy model."""
    global _nlp
    if _nlp is None:
        import spacy
        logger.info(f"Loading spaCy model: {SPACY_MODEL}")
        try:
            _nlp = spacy.load(SPACY_MODEL)
        except OSError:
            logger.warning(f"Model {SPACY_MODEL} not found, downloading...")
            from spacy.cli import download
            download(SPACY_MODEL)
            _nlp = spacy.load(SPACY_MODEL)
        logger.info("spaCy model loaded")
    return _nlp


def extract_entities(text: str) -> Dict:
    """
    Extract named entities from text using spaCy NER.
    Categorizes into: persons, dates, amounts, organizations, locations, misc.
    """
    logger.info("Extracting named entities...")

    if not text or not text.strip():
        logger.warning("Empty text provided for NER")
        return _empty_result()

    nlp = _get_nlp()
    doc = nlp(text)

    entities = {
        "persons": [],
        "dates": [],
        "amounts": [],
        "organizations": [],
        "locations": [],
        "misc": [],
    }

    entity_map = {
        "PERSON": "persons",
        "DATE": "dates",
        "MONEY": "amounts",
        "CARDINAL": "amounts",
        "PERCENT": "amounts",
        "ORG": "organizations",
        "GPE": "locations",
        "LOC": "locations",
        "FAC": "locations",
        "NORP": "misc",
        "EVENT": "misc",
        "PRODUCT": "misc",
        "WORK_OF_ART": "misc",
        "LAW": "misc",
    }

    seen = set()
    all_entities = []

    for ent in doc.ents:
        key = f"{ent.label_}:{ent.text.strip()}"
        if key in seen:
            continue
        seen.add(key)

        category = entity_map.get(ent.label_, "misc")
        entity_info = {
            "text": ent.text.strip(),
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char,
        }

        entities[category].append(entity_info)
        all_entities.append(entity_info)

    # Extract key sentences
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    result = {
        "entities": entities,
        "all_entities": all_entities,
        "entity_count": len(all_entities),
        "summary": {
            "persons_count": len(entities["persons"]),
            "dates_count": len(entities["dates"]),
            "amounts_count": len(entities["amounts"]),
            "organizations_count": len(entities["organizations"]),
            "locations_count": len(entities["locations"]),
        },
        "sentences": sentences[:20],  # First 20 sentences
        "sentence_count": len(sentences),
    }

    logger.info(
        f"Extracted {len(all_entities)} entities: "
        f"{result['summary']}"
    )
    return result


def _empty_result() -> Dict:
    """Return empty NER result structure."""
    return {
        "entities": {
            "persons": [],
            "dates": [],
            "amounts": [],
            "organizations": [],
            "locations": [],
            "misc": [],
        },
        "all_entities": [],
        "entity_count": 0,
        "summary": {
            "persons_count": 0,
            "dates_count": 0,
            "amounts_count": 0,
            "organizations_count": 0,
            "locations_count": 0,
        },
        "sentences": [],
        "sentence_count": 0,
    }


def structure_extracted_info(ocr_text: str, entities: Dict) -> Dict:
    """
    Structure all extracted information into a meaningful JSON format.
    """
    return {
        "raw_text": ocr_text,
        "text_length": len(ocr_text),
        "word_count": len(ocr_text.split()),
        "entities": entities["entities"],
        "entity_summary": entities["summary"],
        "key_sentences": entities["sentences"][:10],
    }
