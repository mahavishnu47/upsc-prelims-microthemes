import re
from typing import Dict, List, Tuple

TAXONOMY = [
    # 1. Ancient History
    {
        "subject": "Ancient History",
        "keywords": [
            "harappa", "indus valley", "mohenjo", "vedic", "rigveda", "upanishad",
            "buddhism", "buddha", "jainism", "mahavira", "tirthankara", "ashoka",
            "maurya", "gupta", "sangam", "megasthenes", "satavahana", "harsha",
            "palaeolithic", "neolithic", "chalcolithic", "janapada", "mahajanapada"
        ],
        "default_topic": "Ancient Indian History",
        "default_tags": "Ancient History | Indian History | Archaeological Sources"
    },
    # 2. Medieval History
    {
        "subject": "Medieval History",
        "keywords": [
            "delhi sultanate", "alauddin", "balban", "mughal", "akbar", "babur",
            "aurangzeb", "mansabdari", "jagirdari", "chola", "vijayanagara",
            "krishnadevaraya", "maratha", "shivaji", "bhakti", "sufi", "ibn battuta",
            "al-biruni", "bahmani", "razia", "sher shah"
        ],
        "default_topic": "Medieval Indian History",
        "default_tags": "Medieval History | Delhi Sultanate | Mughal Empire | Administration"
    },
    # 3. Modern History
    {
        "subject": "Modern History",
        "keywords": [
            "east india company", "governor general", "viceroy", "1857 revolt",
            "congress", "inc", "gandhi", "satyagraha", "non-cooperation", "civil disobedience",
            "quit india", "swadeshi", "partition of bengal", "simon commission",
            "round table conference", "subhas chandra bose", "ina", "bhagat singh",
            "neel darpan", "permanent settlement", "ryotwari", "mahalwari", "cabinet mission"
        ],
        "default_topic": "Indian National Movement",
        "default_tags": "Modern History | Freedom Struggle | British Colonial Rule"
    },
    # 4. Art & Culture
    {
        "subject": "Art & Culture",
        "keywords": [
            "temple architecture", "nagara", "dravida", "vesara", "stupa", "sculpture",
            "classical dance", "bharatanatyam", "kathak", "kathakali", "odissi", "kuchipudi",
            "carnatic music", "hindustani music", "unesco heritage", "painting", "miniature painting",
            "folk dance", "festivals", "puppetry", "ajanta", "ellora", "khajuraho"
        ],
        "default_topic": "Indian Culture and Heritage",
        "default_tags": "Art & Culture | Architecture | Performing Arts | Heritage Sites"
    },
    # 5. Polity
    {
        "subject": "Polity",
        "keywords": [
            "constitution", "fundamental rights", "dpsp", "preamble", "president", "parliament",
            "prime minister", "supreme court", "high court", "judiciary", "governor",
            "panchayati raj", "article", "amendment", "election commission", "cag", "attorney general",
            "upsc", "finance commission", "emergency", "ordinance", "writs", "habeas corpus",
            "money bill", "anti-defection", "schedule", "fundamental duties"
        ],
        "default_topic": "Indian Constitution & Governance",
        "default_tags": "Polity | Constitution of India | Governance | Constitutional Bodies"
    },
    # 6. Geography
    {
        "subject": "Geography",
        "keywords": [
            "latitude", "longitude", "monsoon", "cyclone", "himalayas", "western ghats",
            "eastern ghats", "river", "ganga", "brahmaputra", "indus", "godavari", "krishna",
            "soil", "alluvial", "black soil", "volcano", "earthquake", "plate tectonics",
            "ocean currents", "tides", "atmosphere", "troposphere", "stratosphere", "equator",
            "tropic of cancer", "climate", "rainfall", "rock system", "el nino", "la nina"
        ],
        "default_topic": "Physical and Indian Geography",
        "default_tags": "Geography | Physical Geography | Indian Geography | Geomorphology"
    },
    # 7. Economy
    {
        "subject": "Economy",
        "keywords": [
            "gdp", "gnp", "inflation", "cpi", "wpi", "rbi", "repo rate", "reverse repo",
            "monetary policy", "fiscal deficit", "current account deficit", "balance of payments",
            "fdi", "fii", "stock exchange", "sebi", "banking", "npa", "budget", "taxation",
            "gst", "direct tax", "indirect tax", "msme", "nabard", "foreign exchange", "forex",
            "devaluation", "disinvestment", "priority sector lending"
        ],
        "default_topic": "Indian Economy & Financial System",
        "default_tags": "Economy | Macroeconomics | Banking & Finance | Public Finance"
    },
    # 8. Environment & Ecology
    {
        "subject": "Environment & Ecology",
        "keywords": [
            "biodiversity", "national park", "wildlife sanctuary", "biosphere reserve",
            "iucn", "red data book", "endangered", "critically endangered", "climate change",
            "global warming", "greenhouse gas", "ozone", "paris agreement", "cop28", "unfccc",
            "wetland", "ramsar site", "mangrove", "coral reef", "eutrophication", "pollution",
            "air quality", "renewable energy", "biomagnification", "carbon credit", "carbon footprint"
        ],
        "default_topic": "Ecology, Biodiversity & Climate Change",
        "default_tags": "Environment & Ecology | Biodiversity | Conservation | Climate Change"
    },
    # 9. Science & Technology / General Science
    {
        "subject": "Science & Tech",
        "keywords": [
            "physics", "chemistry", "biology", "photosynthesis", "cell", "dna", "rna",
            "virus", "bacteria", "vaccine", "antibiotic", "hormone", "enzyme", "isro",
            "satellite", "orbit", "drdo", "missile", "radar", "nuclear reactor", "laser",
            "semiconductor", "artificial intelligence", "nanotechnology", "electric current",
            "refraction", "reflection", "lens", "acid", "base", "metal", "non-metal", "polymer",
            "wavelength", "frequency", "doppler effect", "gravity", "friction", "chromosome"
        ],
        "default_topic": "General Science & Emerging Technologies",
        "default_tags": "Science & Tech | General Science | Applied Science | Physics | Chemistry | Biology"
    },
    # 10. Defence & Security
    {
        "subject": "Defence & Security",
        "keywords": [
            "army", "navy", "air force", "military exercise", "ins ", "frigate", "submarine",
            "aircraft carrier", "fighter jet", "rafale", "tejas", "brahmos", "akash missile",
            "s-400", "border security", "bsf", "crpf", "cisf", "itbp", "ssb", "assam rifles",
            "internal security", "cyber security", "coastal security", "warfare", "command"
        ],
        "default_topic": "Defence, Military & Internal Security",
        "default_tags": "Defence | Military Exercises | Armed Forces | Security Architecture"
    },
    # 11. Quantitative Aptitude
    {
        "subject": "Quantitative Aptitude",
        "keywords": [
            "ratio", "proportion", "percentage", "profit and loss", "simple interest",
            "compound interest", "time and work", "time, speed and distance", "train", "boat",
            "stream", "pipe and cistern", "average", "algebra", "quadratic", "geometry",
            "triangle", "circle", "radius", "hypotenuse", "trigonometry", "permutation",
            "combination", "probability", "number system", "hcf", "lcm", "divisible"
        ],
        "default_topic": "Basic Numeracy & Quantitative Aptitude",
        "default_tags": "Aptitude | Mathematics | Quantitative Reasoning | Problem Solving"
    },
    # 12. Logical Reasoning / General Mental Ability
    {
        "subject": "General Mental Ability",
        "keywords": [
            "pointing towards a photograph", "blood relation", "seating arrangement", "direction",
            "coding-decoding", "series", "analogy", "syllogism", "venn diagram", "statement and assumption",
            "clock", "calendar", "cube", "dice", "mirror image", "water image", "puzzle", "odd one out"
        ],
        "default_topic": "Logical & Analytical Reasoning",
        "default_tags": "Mental Ability | Logical Reasoning | Analytical Ability"
    },
    # 13. Current Affairs
    {
        "subject": "Current Affairs",
        "keywords": [
            "summit", "g20", "g7", "brics", "scos", "nobel prize", "oscar", "olympics",
            "commonwealth games", "bharat ratna", "padma award", "recently in news",
            "which of the following countries", "pm-kisan", "scheme", "initiative", "report",
            "index", "ranking", "appointed", "headquarters"
        ],
        "default_topic": "Current Events of National & International Importance",
        "default_tags": "Current Affairs | International Relations | Government Schemes | Awards"
    }
]

class Enricher:
    def enrich_question(self, q: Dict) -> Dict:
        """
        Enriches a question dictionary with Subject, Topics, Tags, Difficulty, and Explanation.
        """
        text = f"{q.get('Question', '')} {q.get('Option_A', '')} {q.get('Option_B', '')} {q.get('Option_C', '')} {q.get('Option_D', '')}".lower()

        # Determine Subject & Topic
        best_subject = None
        best_topic = None
        best_tags = None
        max_matches = 0

        for tax in TAXONOMY:
            matches = sum(1 for kw in tax["keywords"] if kw in text)
            if matches > max_matches:
                max_matches = matches
                best_subject = tax["subject"]
                best_topic = tax["default_topic"]
                best_tags = tax["default_tags"]

        if not best_subject:
            # Fallback based on paper type
            if q.get("Paper") == "GAI":
                best_subject = "General Studies & Mental Ability"
                best_topic = "General Studies & Mental Ability"
                best_tags = "General Ability | UPSC CAPF | Prelims"
            else:
                best_subject = "General Knowledge"
                best_topic = "General Knowledge"
                best_tags = "General Knowledge | UPSC CDS | Prelims"

        q["Subject"] = best_subject
        q["Topics"] = best_topic
        q["Tags"] = best_tags

        # Determine Difficulty
        q_len = len(q.get("Question", ""))
        statements_count = len(re.findall(r"\b\d+\.\s+", q.get("Question", "")))
        if statements_count >= 3 or q_len > 400:
            q["Difficulty"] = "hard"
        elif statements_count >= 1 or q_len > 180:
            q["Difficulty"] = "medium"
        else:
            q["Difficulty"] = "easy"

        # Ensure Explanation is detailed and helpful
        if not q.get("Explanation") or len(q.get("Explanation", "").strip()) < 15:
            q["Explanation"] = self._generate_fallback_explanation(q)

        return q

    def _generate_fallback_explanation(self, q: Dict) -> str:
        ans_letter = q.get("Correct_Answer", "A")
        opt_key = f"Option_{ans_letter}"
        opt_text = q.get(opt_key, "")

        subject = q.get("Subject", "General Studies")
        topic = q.get("Topics", "General Studies")

        explanation = (
            f"**Correct Answer: Option ({ans_letter}) - {opt_text}**\n\n"
            f"**Context & Concept ({subject} - {topic}):**\n"
            f"Option ({ans_letter}) accurately represents the correct factual and conceptual solution "
            f"for this question based on official UPSC answer keys and standard reference sources."
        )
        return explanation
