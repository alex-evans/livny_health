"""
Short term will eventually be moved to a database or external config.
"""

# Mapping of medication forms to standardized patterns
FORM_PATTERNS = {
    "Oral Tablet": "tablet",
    "Oral Capsule": "capsule",
    "Oral Solution": "liquid",
    "Oral Suspension": "liquid",
    "Injectable Solution": "injection",
    "Injection": "injection",
    "Topical Cream": "topical",
    "Topical Ointment": "topical",
    "Topical Gel": "topical",
    "Metered Dose Inhaler": "inhaler",
    "Inhalation Powder": "inhaler",
}



# Medication categories for default duration
ANTIBIOTICS = {
    "amoxicillin",
    "azithromycin",
    "ciprofloxacin",
    "doxycycline",
    "cephalexin",
    "augmentin",
    "amoxicillin/clavulanate",
}

SHORT_TERM_STEROIDS = {
    "prednisone",
}

PRN_MEDICATIONS = {
    "hydrocodone",
    "oxycodone",
    "ibuprofen",
    "acetaminophen",
    "albuterol",
    "tramadol",
}



# Dosing patterns keyed by generic drug name (lowercase)
# Each entry maps strength patterns to common dosing options
COMMON_DOSING_PATTERNS: dict[str, dict[str, list[str]]] = {
    "amoxicillin": {
        "250": ["250mg TID", "250mg BID"],
        "500": ["500mg TID", "500mg BID"],
        "875": ["875mg BID"],
        "_default": ["500mg TID", "500mg BID"],
    },
    "lisinopril": {
        "5": ["5mg daily"],
        "10": ["10mg daily"],
        "20": ["20mg daily"],
        "40": ["40mg daily"],
        "_default": ["10mg daily"],
    },
    "metformin": {
        "500": ["500mg BID", "500mg daily"],
        "850": ["850mg BID"],
        "1000": ["1000mg BID"],
        "_default": ["500mg BID"],
    },
    "atorvastatin": {
        "10": ["10mg daily at bedtime"],
        "20": ["20mg daily at bedtime"],
        "40": ["40mg daily at bedtime"],
        "80": ["80mg daily at bedtime"],
        "_default": ["20mg daily at bedtime"],
    },
    "omeprazole": {
        "20": ["20mg daily before breakfast"],
        "40": ["40mg daily before breakfast"],
        "_default": ["20mg daily before breakfast"],
    },
    "amlodipine": {
        "5": ["5mg daily"],
        "10": ["10mg daily"],
        "_default": ["5mg daily"],
    },
    "gabapentin": {
        "100": ["100mg TID"],
        "300": ["300mg TID"],
        "400": ["400mg TID"],
        "_default": ["300mg TID"],
    },
    "prednisone": {
        "_default": ["5mg daily", "Taper per instructions"],
    },
    "azithromycin": {
        "250": ["500mg day 1, then 250mg days 2-5"],
        "_default": ["500mg day 1, then 250mg days 2-5"],
    },
    "ciprofloxacin": {
        "250": ["250mg BID"],
        "500": ["500mg BID"],
        "750": ["750mg BID"],
        "_default": ["500mg BID"],
    },
    "albuterol": {
        "_default": ["2 puffs every 4-6 hours PRN"],
    },
    "hydrocodone": {
        "_default": ["1-2 tablets every 4-6 hours PRN"],
    },
    "oxycodone": {
        "5": ["5mg every 4-6 hours PRN"],
        "10": ["10mg every 4-6 hours PRN"],
        "_default": ["5mg every 4-6 hours PRN"],
    },
    "levothyroxine": {
        "_default": ["Take daily on empty stomach"],
    },
    "losartan": {
        "25": ["25mg daily"],
        "50": ["50mg daily"],
        "100": ["100mg daily"],
        "_default": ["50mg daily"],
    },
    "furosemide": {
        "20": ["20mg daily", "20mg BID"],
        "40": ["40mg daily", "40mg BID"],
        "_default": ["40mg daily"],
    },
    "sertraline": {
        "25": ["25mg daily"],
        "50": ["50mg daily"],
        "100": ["100mg daily"],
        "_default": ["50mg daily"],
    },
    "escitalopram": {
        "5": ["5mg daily"],
        "10": ["10mg daily"],
        "20": ["20mg daily"],
        "_default": ["10mg daily"],
    },
    "montelukast": {
        "10": ["10mg daily at bedtime"],
        "_default": ["10mg daily at bedtime"],
    },
    "pantoprazole": {
        "20": ["20mg daily before breakfast"],
        "40": ["40mg daily before breakfast"],
        "_default": ["40mg daily before breakfast"],
    },
    "ibuprofen": {
        "200": ["200-400mg every 4-6 hours PRN"],
        "400": ["400mg every 4-6 hours PRN"],
        "600": ["600mg TID with food"],
        "800": ["800mg TID with food"],
        "_default": ["400mg every 4-6 hours PRN"],
    },
    "acetaminophen": {
        "325": ["325-650mg every 4-6 hours PRN"],
        "500": ["500-1000mg every 4-6 hours PRN"],
        "_default": ["500-1000mg every 4-6 hours PRN"],
    },
    "metoprolol": {
        "25": ["25mg BID"],
        "50": ["50mg BID"],
        "100": ["100mg BID"],
        "_default": ["50mg BID"],
    },
    "carvedilol": {
        "3.125": ["3.125mg BID"],
        "6.25": ["6.25mg BID"],
        "12.5": ["12.5mg BID"],
        "25": ["25mg BID"],
        "_default": ["6.25mg BID"],
    },
    "warfarin": {
        "_default": ["Per INR monitoring"],
    },
    "apixaban": {
        "2.5": ["2.5mg BID"],
        "5": ["5mg BID"],
        "_default": ["5mg BID"],
    },
    "clopidogrel": {
        "75": ["75mg daily"],
        "_default": ["75mg daily"],
    },
    "simvastatin": {
        "10": ["10mg daily at bedtime"],
        "20": ["20mg daily at bedtime"],
        "40": ["40mg daily at bedtime"],
        "_default": ["20mg daily at bedtime"],
    },
    "pravastatin": {
        "10": ["10mg daily at bedtime"],
        "20": ["20mg daily at bedtime"],
        "40": ["40mg daily at bedtime"],
        "_default": ["40mg daily at bedtime"],
    },
    "rosuvastatin": {
        "5": ["5mg daily"],
        "10": ["10mg daily"],
        "20": ["20mg daily"],
        "_default": ["10mg daily"],
    },
    "tramadol": {
        "50": ["50mg every 4-6 hours PRN"],
        "_default": ["50mg every 4-6 hours PRN"],
    },
    "cyclobenzaprine": {
        "5": ["5mg TID"],
        "10": ["10mg TID"],
        "_default": ["10mg TID"],
    },
    "meloxicam": {
        "7.5": ["7.5mg daily"],
        "15": ["15mg daily"],
        "_default": ["15mg daily"],
    },
    "naproxen": {
        "250": ["250mg BID"],
        "500": ["500mg BID"],
        "_default": ["500mg BID"],
    },
    "doxycycline": {
        "100": ["100mg BID", "100mg daily"],
        "_default": ["100mg BID"],
    },
    "cephalexin": {
        "250": ["250mg QID"],
        "500": ["500mg QID", "500mg BID"],
        "_default": ["500mg QID"],
    },
    "augmentin": {
        "500": ["500/125mg BID"],
        "875": ["875/125mg BID"],
        "_default": ["875/125mg BID"],
    },
    "amoxicillin/clavulanate": {
        "500": ["500/125mg BID"],
        "875": ["875/125mg BID"],
        "_default": ["875/125mg BID"],
    },
    "fluticasone": {
        "_default": ["1-2 sprays each nostril daily"],
    },
    "cetirizine": {
        "10": ["10mg daily"],
        "_default": ["10mg daily"],
    },
    "loratadine": {
        "10": ["10mg daily"],
        "_default": ["10mg daily"],
    },
    "diphenhydramine": {
        "25": ["25-50mg at bedtime PRN"],
        "50": ["50mg at bedtime PRN"],
        "_default": ["25-50mg at bedtime PRN"],
    },
}

