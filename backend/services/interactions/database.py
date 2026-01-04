"""
Drug interaction database.

This contains known drug-drug interactions for the prescribing workflow.
In production, this would be backed by a real drug interaction database like
DrugBank, RxNorm, or a clinical decision support system.
"""

# Each interaction lists the two drugs involved, severity, and a clinical description
DRUG_INTERACTIONS = [
    # Warfarin interactions (anticoagulant - many interactions)
    {
        "drugs": ["warfarin", "amoxicillin"],
        "severity": "moderate",
        "description": "May increase warfarin effects - monitor INR",
    },
    {
        "drugs": ["warfarin", "aspirin"],
        "severity": "major",
        "description": "Increased risk of bleeding - avoid combination or use with extreme caution",
    },
    {
        "drugs": ["warfarin", "ibuprofen"],
        "severity": "major",
        "description": "Increased risk of bleeding and GI ulceration - avoid NSAIDs with warfarin",
    },
    {
        "drugs": ["warfarin", "metronidazole"],
        "severity": "major",
        "description": "Significantly increases warfarin effect - reduce warfarin dose and monitor INR closely",
    },
    {
        "drugs": ["warfarin", "fluconazole"],
        "severity": "major",
        "description": "Significantly increases warfarin effect - monitor INR closely",
    },
    # Metformin interactions (diabetes medication)
    {
        "drugs": ["metformin", "alcohol"],
        "severity": "moderate",
        "description": "Increased risk of lactic acidosis - limit alcohol consumption",
    },
    {
        "drugs": ["metformin", "contrast dye"],
        "severity": "major",
        "description": "Risk of lactic acidosis - hold metformin before and after contrast procedures",
    },
    # Statin interactions
    {
        "drugs": ["simvastatin", "amiodarone"],
        "severity": "major",
        "description": "Increased risk of myopathy - limit simvastatin to 20mg daily",
    },
    {
        "drugs": ["simvastatin", "erythromycin"],
        "severity": "major",
        "description": "Increased risk of myopathy/rhabdomyolysis - avoid combination",
    },
    {
        "drugs": ["atorvastatin", "clarithromycin"],
        "severity": "moderate",
        "description": "Increased statin levels - monitor for muscle pain/weakness",
    },
    # SSRI interactions
    {
        "drugs": ["sertraline", "tramadol"],
        "severity": "major",
        "description": "Risk of serotonin syndrome - monitor closely or avoid",
    },
    {
        "drugs": ["fluoxetine", "maoi"],
        "severity": "major",
        "description": "CONTRAINDICATED - severe serotonin syndrome risk",
    },
    # ACE inhibitor / ARB interactions
    {
        "drugs": ["lisinopril", "potassium"],
        "severity": "moderate",
        "description": "Risk of hyperkalemia - monitor potassium levels",
    },
    {
        "drugs": ["lisinopril", "spironolactone"],
        "severity": "moderate",
        "description": "Risk of hyperkalemia - monitor potassium levels closely",
    },
    # Antibiotic interactions
    {
        "drugs": ["ciprofloxacin", "tizanidine"],
        "severity": "major",
        "description": "CONTRAINDICATED - dramatically increases tizanidine levels",
    },
    {
        "drugs": ["metronidazole", "alcohol"],
        "severity": "major",
        "description": "Severe nausea/vomiting (disulfiram-like reaction) - avoid alcohol",
    },
    # Opioid interactions
    {
        "drugs": ["oxycodone", "benzodiazepine"],
        "severity": "major",
        "description": "Risk of profound sedation and respiratory depression - avoid if possible",
    },
    {
        "drugs": ["morphine", "benzodiazepine"],
        "severity": "major",
        "description": "Risk of profound sedation and respiratory depression - avoid if possible",
    },
    # Common OTC interactions
    {
        "drugs": ["lisinopril", "ibuprofen"],
        "severity": "moderate",
        "description": "May reduce antihypertensive effect and worsen kidney function",
    },
    {
        "drugs": ["methotrexate", "ibuprofen"],
        "severity": "major",
        "description": "Increased methotrexate toxicity - avoid combination",
    },
]
