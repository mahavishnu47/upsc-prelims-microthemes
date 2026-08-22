"""
UPSC CSE 2024 PYQ Microtheme Overlap Analyzer
Uses pre-computed nuanced microthemes and intelligent keyword matching
to find concept-level overlaps across CSE GS, CAPF GAI, and CDS GK PYQs.
"""

import pandas as pd
import json
import re
from pathlib import Path
from collections import defaultdict

# ============================================================
# SUBJECT NORMALIZATION MAP
# Maps varied subject names across exams to a unified taxonomy
# ============================================================
SUBJECT_NORMALIZE = {
    # History
    "Ancient History": "History",
    "Medieval History": "History",
    "Modern History": "History",
    "Art & Culture": "History",
    # Polity
    "Indian Polity": "Polity & Governance",
    "Polity": "Polity & Governance",
    # Geography
    "Indian Geography": "Geography",
    "Physical Geography": "Geography",
    "World Geography": "Geography",
    "Geography": "Geography",
    # Economy
    "Economy": "Economy",
    # Environment
    "Environment & Ecology": "Environment & Ecology",
    # Science
    "Science & Technology": "Science & Technology",
    "Science & Tech": "Science & Technology",
    # IR
    "International Relations": "International Relations",
    # Social Issues
    "Social Issues & Schemes": "Social Issues & Schemes",
    # Generic
    "General Knowledge": "General Knowledge",
    "General Studies & Mental Ability": "General Studies",
    "Quantitative Aptitude": "Quantitative Aptitude",
    "General Mental Ability": "General Mental Ability",
    "Defence & Security": "Defence & Security",
    "Current Affairs": "Current Affairs",
}

# ============================================================
# PRE-COMPUTED NUANCED MICROTHEMES FOR CSE 2024 GS
# Each question gets 3-6 precise, granular microthemes
# that capture the EXACT concept being tested
# ============================================================
CSE_2024_MICROTHEMES = {
    1: {
        "subject_area": "Ancient History",
        "microthemes": [
            "Chandraketugarh ancient port city West Bengal",
            "Inamgaon Chalcolithic site Maharashtra",
            "Megalithic sites in Kerala",
            "Salihundam Buddhist site Andhra Pradesh",
            "Archaeological site-state matching",
            "Chalcolithic and Megalithic period sites"
        ]
    },
    2: {
        "subject_area": "Ancient History",
        "microthemes": [
            "Upanishads parables and allegories",
            "Upanishads chronology vs Puranas",
            "Vedanta philosophy and Vedic literature",
            "Chandogya Upanishad Satyakama Jabala",
            "Dating of ancient Indian texts"
        ]
    },
    3: {
        "subject_area": "Ancient History",
        "microthemes": [
            "Epithets of Gautama Buddha",
            "Shakyamuni sage of Shakya clan",
            "Tathagata Buddhist epithet",
            "Nayaputta epithet of Mahavira not Buddha",
            "Buddhist terminology and titles"
        ]
    },
    4: {
        "subject_area": "Art & Culture",
        "microthemes": [
            "UNESCO Intangible Cultural Heritage List India",
            "Garba dance Gujarat UNESCO inscription 2023",
            "Chhau dance UNESCO 2010",
            "Durga Puja UNESCO 2021",
            "Kumbh Mela UNESCO 2017",
            "Chronology of Indian UNESCO ICH inscriptions"
        ]
    },
    5: {
        "subject_area": "Art & Culture",
        "microthemes": [
            "Ancient Sanskrit dramatists Bhasa",
            "Svapnavasavadatta Pancharatra plays",
            "Kalidasa Shudraka Bhavabhuti comparison",
            "Classical Indian theatre and playwrights",
            "Ancient Indian literary works attribution"
        ]
    },
    6: {
        "subject_area": "Art & Culture",
        "microthemes": [
            "Sarvastivada Buddhist school",
            "Buddhist Vinaya texts and literature",
            "Buddhist monastic rules and traditions",
            "Schools of Buddhism Theravada Mahayana",
            "Ancient Buddhist literary traditions"
        ]
    },
    7: {
        "subject_area": "Art & Culture",
        "microthemes": [
            "UNESCO World Heritage Sites in India",
            "Shantiniketan Rabindranath Tagore",
            "Rani-ki-Vav stepwell Gujarat",
            "Hoysala temples Karnataka",
            "India UNESCO WHS list recent additions"
        ]
    },
    8: {
        "subject_area": "Economy",
        "microthemes": [
            "Money market instruments India",
            "CBLO Collateral Borrowing and Lending Obligation",
            "Short-term liquidity management instruments",
            "Call money market Treasury bills",
            "RBI monetary instruments"
        ]
    },
    9: {
        "subject_area": "Economy",
        "microthemes": [
            "Exchange Traded Funds ETFs",
            "Currency swap agreements",
            "Financial derivatives instruments",
            "Capital market vs money market instruments",
            "Financial instruments classification"
        ]
    },
    10: {
        "subject_area": "Economy",
        "microthemes": [
            "NBFCs Non-Banking Financial Companies",
            "Liquidity Adjustment Facility LAF",
            "RBI monetary policy tools",
            "Foreign Institutional Investors FIIs",
            "Government Securities G-Secs market",
            "Debt securities and stock exchanges"
        ]
    },
    11: {
        "subject_area": "Economy",
        "microthemes": [
            "Financial market reforms India",
            "Debt market development in India",
            "Corporate bond market India",
            "Institutional investors in Indian markets",
            "Capital market infrastructure"
        ]
    },
    12: {
        "subject_area": "Economy",
        "microthemes": [
            "Financial inclusion India",
            "Microfinance institutions",
            "Self-Help Groups SHGs bank linkage",
            "Priority sector lending",
            "Rural banking and credit delivery"
        ]
    },
    13: {
        "subject_area": "Economy",
        "microthemes": [
            "Government budget fiscal deficit",
            "Revenue deficit vs fiscal deficit",
            "Primary deficit and effective revenue deficit",
            "Government borrowing and public debt",
            "Union Budget fiscal indicators"
        ]
    },
    14: {
        "subject_area": "Economy",
        "microthemes": [
            "Central bank digital currency CBDC",
            "Digital rupee e-Rupi",
            "RBI digital currency initiatives",
            "Cryptocurrency regulation India",
            "Digital payment infrastructure"
        ]
    },
    15: {
        "subject_area": "Economy",
        "microthemes": [
            "Lead bank scheme rural banking",
            "Regional Rural Banks RRBs",
            "Banking sector reforms India",
            "Priority sector lending agriculture",
            "District credit planning"
        ]
    },
    16: {
        "subject_area": "Economy",
        "microthemes": [
            "Direct tax reforms India",
            "Goods and Services Tax GST",
            "Tax revenue composition India",
            "Taxation policy and reform",
            "Indirect tax structure India"
        ]
    },
    17: {
        "subject_area": "Economy",
        "microthemes": [
            "Balance of payments India",
            "Current account deficit",
            "Foreign exchange reserves",
            "Capital account convertibility",
            "External sector indicators India"
        ]
    },
    18: {
        "subject_area": "Economy",
        "microthemes": [
            "NITI Aayog SDG India Index",
            "Sustainable Development Goals India",
            "State-wise SDG performance ranking",
            "Multidimensional Poverty Index India",
            "Development indicators India"
        ]
    },
    19: {
        "subject_area": "Economy",
        "microthemes": [
            "Agricultural marketing reforms APMC",
            "Minimum Support Price MSP",
            "e-NAM electronic trading platform",
            "Farm sector marketing infrastructure",
            "Agricultural produce market regulation"
        ]
    },
    20: {
        "subject_area": "Economy",
        "microthemes": [
            "Indian rupee depreciation",
            "Foreign exchange rate determination",
            "Managed floating exchange rate",
            "Capital flows and rupee value",
            "External value of Indian rupee"
        ]
    },
    21: {
        "subject_area": "Environment & Ecology",
        "microthemes": [
            "Biological nitrogen fixation",
            "Rhizobium bacteria symbiosis",
            "Nitrification and denitrification",
            "Nitrogen cycle in ecosystems",
            "Soil microbiology and nutrient cycling"
        ]
    },
    22: {
        "subject_area": "Environment & Ecology",
        "microthemes": [
            "Wetland conservation India",
            "Ramsar Convention wetlands",
            "Chilika Lake Loktak Lake",
            "Wetland ecosystem services",
            "India Ramsar sites recent additions"
        ]
    },
    23: {
        "subject_area": "Environment & Ecology",
        "microthemes": [
            "Invasive alien species in India",
            "Prosopis juliflora Lantana camara",
            "Biodiversity threats from invasive species",
            "Water hyacinth Eichhornia",
            "Impact on native ecosystems"
        ]
    },
    24: {
        "subject_area": "Environment & Ecology",
        "microthemes": [
            "Marine pollution oil spills",
            "Ballast water management",
            "Ocean acidification",
            "Microplastics in marine environment",
            "International maritime pollution conventions"
        ]
    },
    25: {
        "subject_area": "Environment & Ecology",
        "microthemes": [
            "UNFCCC COP climate negotiations",
            "Paris Agreement NDC targets",
            "Carbon trading emissions trading",
            "Climate finance Green Climate Fund",
            "Global climate governance"
        ]
    },
    26: {
        "subject_area": "Environment & Ecology",
        "microthemes": [
            "Protected areas National Parks India",
            "Wildlife sanctuaries biosphere reserves",
            "Tiger reserves Project Tiger",
            "Biodiversity hotspots India",
            "Conservation of endangered species"
        ]
    },
    27: {
        "subject_area": "Environment & Ecology",
        "microthemes": [
            "Environmental Impact Assessment EIA",
            "Environment Protection Act 1986",
            "Coastal Regulation Zone CRZ",
            "Green tribunal NGT",
            "Environmental governance India"
        ]
    },
    28: {
        "subject_area": "Environment & Ecology",
        "microthemes": [
            "Coral reef ecosystems",
            "Coral bleaching ocean temperature",
            "Great Barrier Reef marine biodiversity",
            "Symbiotic zooxanthellae algae",
            "Marine ecosystem threats"
        ]
    },
    29: {
        "subject_area": "Environment & Ecology",
        "microthemes": [
            "Biofuels ethanol blending India",
            "National Biofuel Policy",
            "Compressed Biogas CBG",
            "Second generation biofuels",
            "Renewable energy targets India"
        ]
    },
    30: {
        "subject_area": "Environment & Ecology",
        "microthemes": [
            "Species-specific conservation India",
            "IUCN Red List endangered species India",
            "One-horned rhino Kaziranga",
            "Asiatic lion Gir Forest",
            "Species recovery programmes"
        ]
    },
    31: {
        "subject_area": "Environment & Ecology",
        "microthemes": [
            "Forest conservation India Forest Rights Act",
            "Community forest resource rights",
            "Tribal forest dwellers rights",
            "Forest diversion proposals",
            "Compensatory afforestation"
        ]
    },
    32: {
        "subject_area": "Environment & Ecology",
        "microthemes": [
            "E-waste management rules India",
            "Extended Producer Responsibility EPR",
            "Hazardous waste management",
            "Waste management hierarchy",
            "Circular economy and recycling"
        ]
    },
    33: {
        "subject_area": "Geography",
        "microthemes": [
            "Indian monsoon mechanism",
            "Southwest monsoon onset withdrawal",
            "El Nino La Nina Indian monsoon",
            "Indian Ocean Dipole IOD",
            "Rainfall distribution India"
        ]
    },
    34: {
        "subject_area": "Geography",
        "microthemes": [
            "Himalayan river systems",
            "Peninsular river systems India",
            "Drainage patterns India",
            "Antecedent and consequent rivers",
            "River water disputes India"
        ]
    },
    35: {
        "subject_area": "Geography",
        "microthemes": [
            "Indian soil types classification",
            "Laterite soil alluvial soil",
            "Black cotton soil regur",
            "Soil formation factors India",
            "Soil conservation techniques"
        ]
    },
    36: {
        "subject_area": "Geography",
        "microthemes": [
            "Indian mineral resources",
            "Iron ore coal deposits India",
            "Mineral belts distribution India",
            "Mining industry India",
            "Strategic minerals India"
        ]
    },
    37: {
        "subject_area": "Geography",
        "microthemes": [
            "Physiographic divisions of India",
            "Northern Plains Deccan Plateau",
            "Western Ghats Eastern Ghats",
            "Coastal plains India",
            "Geological structure India"
        ]
    },
    38: {
        "subject_area": "Geography",
        "microthemes": [
            "Indian agriculture cropping patterns",
            "Kharif Rabi Zaid crops",
            "Green Revolution impact India",
            "Crop diversification India",
            "Agricultural productivity India"
        ]
    },
    39: {
        "subject_area": "Geography",
        "microthemes": [
            "Ocean currents global circulation",
            "Thermohaline circulation",
            "Gulf Stream Labrador Current",
            "Effect of ocean currents on climate",
            "Upwelling and downwelling"
        ]
    },
    40: {
        "subject_area": "Geography",
        "microthemes": [
            "Earthquake and volcanic zones",
            "Plate tectonics theory",
            "Seismic zones of India",
            "Ring of Fire Pacific",
            "Earthquake disaster management"
        ]
    },
    41: {
        "subject_area": "Geography",
        "microthemes": [
            "Population geography India",
            "Census 2011 demographic data",
            "Urbanization trends India",
            "Population density distribution India",
            "Demographic transition India"
        ]
    },
    42: {
        "subject_area": "Geography",
        "microthemes": [
            "Indian climate types Koppen classification",
            "Tropical monsoon climate India",
            "Arid semi-arid zones India",
            "Thar desert climate Rajasthan",
            "Climate regions of India"
        ]
    },
    43: {
        "subject_area": "Geography",
        "microthemes": [
            "Straits and channels world geography",
            "Strait of Malacca Hormuz",
            "Geopolitics of maritime chokepoints",
            "Important waterways world trade",
            "Strategic sea lanes"
        ]
    },
    44: {
        "subject_area": "Geography",
        "microthemes": [
            "Passes in the Himalayas",
            "Mountain passes India strategic importance",
            "Karakoram Pass Khyber Pass Nathu La",
            "Border pass connectivity",
            "Himalayan geography passes"
        ]
    },
    45: {
        "subject_area": "Geography",
        "microthemes": [
            "Lakes in India types formation",
            "Wular Lake Chilika Sambhar",
            "Oxbow lake glacial lake tectonic",
            "Freshwater saltwater lakes India",
            "Lake classification by origin"
        ]
    },
    46: {
        "subject_area": "Geography",
        "microthemes": [
            "Island territories India",
            "Andaman Nicobar Lakshadweep",
            "Coral islands volcanic islands",
            "Strategic importance Indian islands",
            "Island biogeography India"
        ]
    },
    47: {
        "subject_area": "Geography",
        "microthemes": [
            "Wind patterns global atmospheric circulation",
            "Trade winds westerlies polar easterlies",
            "Coriolis effect on wind direction",
            "Jet stream Indian monsoon",
            "Pressure belts and wind systems"
        ]
    },
    48: {
        "subject_area": "Geography",
        "microthemes": [
            "Types of rocks igneous sedimentary metamorphic",
            "Rock cycle transformation",
            "Mineral composition of rocks",
            "Geological formations India",
            "Fossils in sedimentary rocks"
        ]
    },
    49: {
        "subject_area": "Geography",
        "microthemes": [
            "Glaciers and glaciation",
            "Siachen glacier Gangotri glacier",
            "Glacial landforms India",
            "Impact of global warming on glaciers",
            "Himalayan glacier retreat"
        ]
    },
    50: {
        "subject_area": "Geography",
        "microthemes": [
            "Map reading contour lines",
            "Topographic maps India Survey of India",
            "GIS remote sensing applications",
            "Satellite imagery interpretation",
            "Geographic tools and techniques"
        ]
    },
    51: {
        "subject_area": "Geography",
        "microthemes": [
            "International boundaries longest borders",
            "India neighbours border length",
            "USA Canada border Mexico border",
            "Geopolitics of international boundaries",
            "Border disputes world"
        ]
    },
    52: {
        "subject_area": "Geography",
        "microthemes": [
            "Tribal areas Schedule V Schedule VI",
            "Tribal Sub-Plan PESA Act 1996",
            "Fifth Schedule areas India",
            "Particularly Vulnerable Tribal Groups PVTGs",
            "Tribal welfare governance India"
        ]
    },
    53: {
        "subject_area": "Geography",
        "microthemes": [
            "India state boundaries reorganization",
            "States Reorganisation Act 1956",
            "New states formation bifurcation",
            "Interstate boundary disputes India",
            "Linguistic reorganization of states"
        ]
    },
    54: {
        "subject_area": "Environment & Ecology",
        "microthemes": [
            "Mangrove ecosystems India",
            "Sundarbans mangrove conservation",
            "Mangrove species Rhizophora Avicennia",
            "Coastal ecosystem protection",
            "Mangrove ecosystem services"
        ]
    },
    55: {
        "subject_area": "Environment & Ecology",
        "microthemes": [
            "Renewable energy solar wind India",
            "Solar energy capacity India",
            "International Solar Alliance ISA",
            "National Solar Mission targets",
            "Clean energy transition India"
        ]
    },
    56: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Fundamental Rights Article 14-32",
            "Right to Equality Article 14",
            "Right to Freedom Article 19",
            "Writ jurisdiction Article 32 and 226",
            "Constitutional remedies"
        ]
    },
    57: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Directive Principles of State Policy DPSP",
            "DPSP Article 36-51",
            "Gandhian socialist liberal principles DPSP",
            "DPSP vs Fundamental Rights conflict",
            "Implementation of Directive Principles"
        ]
    },
    58: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Constitutional amendments India",
            "Amendment procedure Article 368",
            "Key constitutional amendments 42nd 44th 73rd 74th",
            "Basic structure doctrine Kesavananda Bharati",
            "Parliament power to amend constitution"
        ]
    },
    59: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Panchayati Raj institutions 73rd Amendment",
            "73rd and 74th Constitutional Amendments",
            "Three-tier Panchayati Raj system",
            "Gram Sabha powers and functions",
            "Local self-government India"
        ]
    },
    60: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Supreme Court of India jurisdiction",
            "Original appellate advisory jurisdiction",
            "Judicial review power",
            "PIL Public Interest Litigation",
            "Constitutional role of judiciary"
        ]
    },
    61: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Election Commission of India",
            "Model Code of Conduct elections",
            "Electronic Voting Machines EVMs",
            "Electoral reforms India",
            "Free and fair elections"
        ]
    },
    62: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Governor powers and discretion",
            "Governor role in state legislature",
            "Article 163 164 governor powers",
            "Appointment and removal of governor",
            "Centre-state relations governor"
        ]
    },
    63: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Finance Commission India",
            "Fiscal federalism India",
            "Tax devolution centre to states",
            "15th Finance Commission recommendations",
            "Grants-in-aid states"
        ]
    },
    64: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Citizenship India Article 5-11",
            "Citizenship Amendment Act CAA 2019",
            "Acquisition and loss of citizenship",
            "Citizenship by birth descent registration",
            "OCI PIO card holders"
        ]
    },
    65: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Anti-defection law Tenth Schedule",
            "Speaker role in disqualification",
            "Political party defection",
            "Kihoto Hollohan case",
            "Party whip and floor crossing"
        ]
    },
    66: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Emergency provisions India",
            "National emergency Article 352",
            "President rule Article 356",
            "Financial emergency Article 360",
            "Impact of emergency on fundamental rights"
        ]
    },
    67: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Constituent Assembly of India",
            "Constituent Assembly debates",
            "Dr Rajendra Prasad Sachidanand Sinha",
            "Provisional President Constituent Assembly",
            "Making of Indian Constitution"
        ]
    },
    68: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Centre-State relations India",
            "Legislative relations centre state",
            "Administrative relations centre state",
            "Financial relations centre state",
            "Inter-state council provisions"
        ]
    },
    69: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Municipalities Part IX-A Constitution",
            "Urban local government India",
            "74th Constitutional Amendment",
            "Emergency provisions Part XVIII",
            "Constitutional Parts organization"
        ]
    },
    70: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Money Bill Article 109 110",
            "Money Bill vs Finance Bill",
            "Rajya Sabha role Money Bill",
            "Speaker certification Money Bill",
            "Parliamentary financial procedure"
        ]
    },
    71: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Ethics Committee Lok Sabha",
            "Parliamentary committees India",
            "Code of conduct MPs",
            "Ad hoc vs standing committees",
            "Parliamentary accountability mechanisms"
        ]
    },
    72: {
        "subject_area": "Indian Polity",
        "microthemes": [
            "Women reservation bill 106th Amendment",
            "Nari Shakti Vandan Adhiniyam",
            "33% reservation women Parliament state legislatures",
            "Delimitation exercise link to reservation",
            "Gender representation legislature India"
        ]
    },
    73: {
        "subject_area": "International Relations",
        "microthemes": [
            "Venezuela economic crisis",
            "Venezuela refugee emigration crisis",
            "Latin America political instability",
            "India-Latin America relations",
            "Petro-state economic collapse"
        ]
    },
    74: {
        "subject_area": "International Relations",
        "microthemes": [
            "EU Net-Zero Industry Act",
            "European Union carbon neutrality target",
            "EU Green Deal climate policy",
            "Carbon Border Adjustment Mechanism CBAM",
            "European Parliament climate legislation"
        ]
    },
    75: {
        "subject_area": "International Relations",
        "microthemes": [
            "Sahel region security instability",
            "Military coups Africa Sahel",
            "Wagner Group Africa presence",
            "Mali Niger Burkina Faso coups",
            "Geopolitical instability Africa"
        ]
    },
    76: {
        "subject_area": "International Relations",
        "microthemes": [
            "Argentina economic crisis 2023-24",
            "Sudan civil war RSF vs military",
            "Turkey earthquake 2023",
            "Countries in news current affairs",
            "Global geopolitical events 2023-24"
        ]
    },
    77: {
        "subject_area": "International Relations",
        "microthemes": [
            "S Jaishankar The India Way",
            "Why Bharat Matters foreign policy book",
            "Indian foreign policy doctrine",
            "Multi-alignment India foreign policy",
            "Books by Indian diplomats"
        ]
    },
    78: {
        "subject_area": "International Relations",
        "microthemes": [
            "India Sri Lanka joint military exercise",
            "Mitra Shakti military exercise",
            "India bilateral defence exercises",
            "India neighbourhood military cooperation",
            "Joint military exercises India"
        ]
    },
    79: {
        "subject_area": "Medieval History",
        "microthemes": [
            "Portuguese colonial forts India",
            "Bhatkal port medieval trade",
            "Deccan kingdoms medieval India",
            "European trading posts India",
            "Portuguese Estado da India"
        ]
    },
    80: {
        "subject_area": "Modern History",
        "microthemes": [
            "Cornwallis revenue settlement",
            "Ryotwari settlement system",
            "Permanent Settlement Zamindari system",
            "British land revenue systems India",
            "Mahalwari Ryotwari Zamindari comparison"
        ]
    },
    81: {
        "subject_area": "Modern History",
        "microthemes": [
            "Indian political parties post-independence",
            "Bharatiya Jana Sangh Shyama Prasad Mukherjee",
            "Socialist Party Ram Manohar Lohia",
            "Congress for Democracy Jagjivan Ram",
            "Swatantra Party C Rajagopalachari"
        ]
    },
    82: {
        "subject_area": "Modern History",
        "microthemes": [
            "Government of India Act 1935",
            "All India Federation British India",
            "Provincial autonomy 1935 Act",
            "Federal Court establishment 1935",
            "Constitutional development British India"
        ]
    },
    83: {
        "subject_area": "Science & Technology",
        "microthemes": [
            "Pumped-storage hydropower",
            "Grid-scale energy storage solutions",
            "Renewable energy storage technologies",
            "Peak load power generation",
            "Hydroelectric power India"
        ]
    },
    84: {
        "subject_area": "Science & Technology",
        "microthemes": [
            "Hydrogels applications",
            "Controlled drug delivery systems",
            "Smart materials polymer science",
            "Biomedical applications of hydrogels",
            "Industrial applications of polymers"
        ]
    },
    85: {
        "subject_area": "Science & Technology",
        "microthemes": [
            "Fuel cell electric vehicles FCEV",
            "Hydrogen fuel cell technology",
            "Water as exhaust from fuel cells",
            "Green hydrogen economy",
            "Zero emission vehicle technology"
        ]
    },
    86: {
        "subject_area": "Science & Technology",
        "microthemes": [
            "Satellite radar technology applications",
            "Narcotics detection technology",
            "Weather monitoring precipitation radar",
            "Animal migration tracking technology",
            "Dual-use technology applications"
        ]
    },
    87: {
        "subject_area": "Science & Technology",
        "microthemes": [
            "Fighter aircraft generations",
            "Fifth generation fighter jets",
            "Rafale Tejas MiG-29 classification",
            "Indian Air Force fleet modernization",
            "Stealth fighter technology"
        ]
    },
    88: {
        "subject_area": "Science & Technology",
        "microthemes": [
            "Nitric oxide blood vessel dilation",
            "Vasodilators in human body",
            "Cardiovascular physiology",
            "Human body biochemistry",
            "Endothelium-derived relaxing factor"
        ]
    },
    89: {
        "subject_area": "Science & Technology",
        "microthemes": [
            "Stellar evolution giant vs dwarf stars",
            "Nuclear fusion in stars",
            "Star lifecycle Hertzsprung-Russell diagram",
            "Astronomy stellar physics",
            "Rate of nuclear reactions in stars"
        ]
    },
    90: {
        "subject_area": "Science & Technology",
        "microthemes": [
            "Radioisotope thermoelectric generators RTGs",
            "Nuclear batteries space missions",
            "Spacecraft power systems",
            "Plutonium-238 radioactive decay heat",
            "Deep space exploration power"
        ]
    },
    91: {
        "subject_area": "Science & Technology",
        "microthemes": [
            "Leguminous plants Fabaceae family",
            "Groundnut soybean horse-gram classification",
            "Pea family plants nitrogen fixation",
            "Botanical classification crop plants",
            "Plant taxonomy agricultural crops"
        ]
    },
    92: {
        "subject_area": "Science & Technology",
        "microthemes": [
            "Metaverse virtual world technology",
            "Web 3.0 decentralized internet",
            "Augmented reality virtual reality",
            "Digital avatar technology",
            "Emerging internet technologies"
        ]
    },
    93: {
        "subject_area": "Science & Technology",
        "microthemes": [
            "Distributed Energy Resources DER",
            "Rooftop solar photovoltaic",
            "Battery storage systems",
            "Fuel cells biomass generators",
            "Decentralized power generation"
        ]
    },
    94: {
        "subject_area": "Social Issues & Schemes",
        "microthemes": [
            "Corporate Social Responsibility CSR rules India",
            "Companies Act 2013 CSR provisions",
            "CSR spending mandates India",
            "CSR eligible activities Schedule VII",
            "Corporate governance India"
        ]
    },
    95: {
        "subject_area": "Social Issues & Schemes",
        "microthemes": [
            "100 Million Farmers initiative",
            "Sustainable agriculture global initiatives",
            "Organic farming movements",
            "Food security global organizations",
            "International agricultural cooperation"
        ]
    },
    96: {
        "subject_area": "Social Issues & Schemes",
        "microthemes": [
            "World Toilet Organization",
            "Swachh Bharat Mission sanitation",
            "World Toilet Day awareness",
            "Sanitation infrastructure India",
            "Global sanitation initiatives"
        ]
    },
    97: {
        "subject_area": "Social Issues & Schemes",
        "microthemes": [
            "Digital India Land Records Modernisation DILRMP",
            "Land records digitization India",
            "Unique Land Parcel Identification Number ULPIN",
            "Land governance reforms India",
            "National Generic Document Registration System"
        ]
    },
    98: {
        "subject_area": "Social Issues & Schemes",
        "microthemes": [
            "Pradhan Mantri Shram Yogi Maan-dhan PM-SYM",
            "Unorganised sector pension scheme",
            "Social security informal workers India",
            "Government pension schemes India",
            "Labour welfare schemes India"
        ]
    },
    99: {
        "subject_area": "Social Issues & Schemes",
        "microthemes": [
            "Pradhan Mantri Surakshit Matritva Abhiyan",
            "Maternal health antenatal care India",
            "Reproductive child health programmes",
            "Government health schemes pregnant women",
            "Safe motherhood programmes India"
        ]
    },
    100: {
        "subject_area": "Social Issues & Schemes",
        "microthemes": [
            "Operation Sadbhavana army civic action",
            "Indian Army upliftment remote areas",
            "Military civic action programmes",
            "Hearts and minds counter-insurgency",
            "Armed forces community development"
        ]
    }
}


def normalize_subject(subject: str) -> str:
    """Normalize subject names across different exams."""
    if pd.isna(subject):
        return "Unknown"
    return SUBJECT_NORMALIZE.get(subject.strip(), subject.strip())


def extract_tags(tag_str: str) -> set:
    """Extract individual tag keywords from pipe-delimited Tags field."""
    if pd.isna(tag_str) or not tag_str.strip():
        return set()
    tags = set()
    for tag in str(tag_str).split("|"):
        cleaned = tag.strip().lower()
        # Filter out generic/useless tags
        if cleaned and cleaned not in {
            "general knowledge", "upsc cds", "prelims",
            "general ability", "upsc capf", "general science",
            "applied science", "aptitude", "mathematics",
            "quantitative reasoning", "problem solving",
            "mental ability", "logical reasoning", "analytical ability"
        }:
            tags.add(cleaned)
    return tags


def extract_question_keywords(question_text: str) -> set:
    """Extract meaningful keywords from question text for matching."""
    if pd.isna(question_text) or not question_text.strip():
        return set()
    
    text = str(question_text).lower()
    
    # Remove common UPSC question patterns
    text = re.sub(r'consider the following statements?:?', '', text)
    text = re.sub(r'which of the following', '', text)
    text = re.sub(r'select the correct answer using the code given below', '', text)
    text = re.sub(r'select the answer using the code given below', '', text)
    text = re.sub(r'with reference to', '', text)
    text = re.sub(r'statement[\s-]*[i12][\s:]*', '', text)
    text = re.sub(r'\d+\.', '', text)
    text = re.sub(r'[|(){}\[\]"\',:;!?]', ' ', text)
    
    # Extract meaningful words (3+ chars)
    words = set(re.findall(r'\b[a-z]{3,}\b', text))
    
    # Remove common stop words
    stop_words = {
        'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can',
        'has', 'her', 'was', 'one', 'our', 'out', 'had', 'hot', 'how',
        'its', 'let', 'may', 'new', 'now', 'old', 'see', 'way', 'who',
        'did', 'get', 'got', 'him', 'his', 'she', 'too', 'use', 'that',
        'this', 'what', 'when', 'will', 'with', 'from', 'have', 'been',
        'they', 'them', 'their', 'there', 'which', 'these', 'those',
        'above', 'about', 'after', 'again', 'below', 'could', 'every',
        'given', 'below', 'only', 'also', 'into', 'more', 'most', 'some',
        'than', 'then', 'very', 'such', 'both', 'does', 'each', 'following',
        'correct', 'incorrect', 'statements', 'statement', 'among', 'answer',
        'regard', 'respect', 'code', 'pair', 'pairs', 'matched', 'correctly',
        'many', 'none', 'recently', 'referred', 'known', 'called', 'india'
    }
    words -= stop_words
    return words


def build_microtheme_keywords(microthemes: list) -> set:
    """Convert microtheme phrases into searchable keyword sets."""
    keywords = set()
    for theme in microthemes:
        # Split each microtheme into individual words
        words = set(re.findall(r'\b[a-zA-Z]{3,}\b', theme.lower()))
        keywords.update(words)
    
    # Remove very common words
    stop = {'the', 'and', 'for', 'not', 'its', 'has', 'are', 'was', 'were',
            'with', 'from', 'this', 'that', 'than', 'india', 'indian'}
    keywords -= stop
    return keywords


def compute_similarity(microtheme_kws: set, pyq_kws: set) -> float:
    """Compute Jaccard-like similarity between keyword sets."""
    if not microtheme_kws or not pyq_kws:
        return 0.0
    intersection = microtheme_kws & pyq_kws
    if len(intersection) < 2:  # Need at least 2 keyword matches
        return 0.0
    # Weighted by intersection relative to microtheme size
    return len(intersection) / len(microtheme_kws)


def run_analysis(csv_path: str, output_path: str, book_json_path: str = "dashboard/data/book_microthemes.json"):
    """
    Main analysis function.
    Combines:
    1. Canonical 179 microtheme taxonomy from 'UPSC Prelims_Microthemes (2009-25).pdf'
    2. Nuanced microtheme concepts
    3. Multi-exam PYQ corpus matching across CSE, CDS, and CAPF
    """
    print("[Analyzer] Loading dataset...")
    df = pd.read_csv(csv_path, dtype=str)
    
    # Load canonical book microthemes if available
    book_data = {}
    if Path(book_json_path).exists():
        with open(book_json_path, 'r', encoding='utf-8') as f:
            book_data = json.load(f)
        print(f"[Analyzer] Loaded {len(book_data.get('records', []))} questions from book taxonomy.")
    
    # Separate CSE 2024 target and PYQ corpus
    cse_2024 = df[(df['Paper'] == 'GS') & (df['Year'] == '2024')].reset_index(drop=True)
    pyq_corpus = df[~((df['Paper'] == 'GS') & (df['Year'] == '2024'))].reset_index(drop=True)
    
    print(f"[Analyzer] CSE 2024 questions: {len(cse_2024)}")
    print(f"[Analyzer] PYQ corpus: {len(pyq_corpus)}")
    
    # Pre-compute PYQ keyword sets
    print("[Analyzer] Pre-computing PYQ keyword sets...")
    pyq_data = []
    for idx, row in pyq_corpus.iterrows():
        tags = extract_tags(row.get('Tags', ''))
        q_kws = extract_question_keywords(row.get('Question', ''))
        topics_kws = set()
        if pd.notna(row.get('Topics', '')):
            topics_kws = set(re.findall(r'\b[a-zA-Z]{3,}\b', str(row['Topics']).lower()))
        
        all_kws = tags | q_kws | topics_kws
        
        pyq_data.append({
            'index': idx,
            'id': row.get('Id', ''),
            'year': row.get('Year', ''),
            'paper': row.get('Paper', ''),
            'subject': row.get('Subject', ''),
            'norm_subject': normalize_subject(row.get('Subject', '')),
            'topics': row.get('Topics', '') if pd.notna(row.get('Topics')) else '',
            'tags': row.get('Tags', '') if pd.notna(row.get('Tags')) else '',
            'question': str(row.get('Question', '')),
            'option_a': str(row.get('Option_A', '')) if pd.notna(row.get('Option_A')) else '',
            'option_b': str(row.get('Option_B', '')) if pd.notna(row.get('Option_B')) else '',
            'option_c': str(row.get('Option_C', '')) if pd.notna(row.get('Option_C')) else '',
            'option_d': str(row.get('Option_D', '')) if pd.notna(row.get('Option_D')) else '',
            'correct_answer': str(row.get('Correct_Answer', '')) if pd.notna(row.get('Correct_Answer')) else '',
            'explanation': str(row.get('Explanation', '')) if pd.notna(row.get('Explanation')) else '',
            'keywords': all_kws,
        })
    
    # Map 2024 questions to canonical book records
    pdf_2024 = [r for r in book_data.get('records', []) if r.get('year') == '2024']
    
    # Analyze each CSE 2024 question
    print("[Analyzer] Running microtheme matching with book taxonomy...")
    results = {
        "target_exam": "UPSC CSE 2024 GS Paper",
        "taxonomy_source": "UPSC Prelims Microthemes (2009-2025)",
        "total_questions": len(cse_2024),
        "pyq_corpus_size": len(pyq_corpus),
        "total_canonical_microthemes": len(book_data.get('catalog', {})),
        "questions": [],
        "aggregate": {},
        "subject_breakdown": {},
        "year_heatmap": {},
        "exam_contribution": {},
        "top_microthemes": [],
    }
    
    # Track aggregates
    questions_with_pyq_match = 0
    questions_with_strong_match = 0
    subject_stats = defaultdict(lambda: {"total": 0, "matched": 0, "strong": 0})
    year_match_counts = defaultdict(int)
    exam_match_counts = defaultdict(int)
    microtheme_frequency = defaultdict(int)
    
    SIMILARITY_THRESHOLD = 0.15
    
    for q_idx in range(len(cse_2024)):
        row = cse_2024.iloc[q_idx]
        q_num = q_idx + 1
        q_text_orig = str(row.get('Question', ''))
        
        # 1. Match against Book 2024 questions
        orig_words = set(re.findall(r'\b[a-z]{4,}\b', q_text_orig.lower()))
        best_book_match = None
        best_overlap = 0
        for prec in pdf_2024:
            pdf_words = set(re.findall(r'\b[a-z]{4,}\b', prec.get('question_text', '').lower()))
            overlap = len(orig_words & pdf_words)
            if overlap > best_overlap:
                best_overlap = overlap
                best_book_match = prec
        
        canonical_subj = best_book_match.get('subject', 'General') if best_book_match else 'General'
        canonical_theme = best_book_match.get('microtheme', 'General') if best_book_match else 'General'
        
        cat_key = f"{canonical_subj} :: {canonical_theme}"
        cat_info = book_data.get('catalog', {}).get(cat_key, {})
        past_book_questions = [q for q in cat_info.get('questions', []) if int(q.get('year', 0)) < 2024]
        
        # 2. Get pre-computed nuanced microthemes
        mt_data = CSE_2024_MICROTHEMES.get(q_num, {
            "subject_area": canonical_subj,
            "microthemes": [canonical_theme, str(row.get('Topics', '')), str(row.get('Tags', ''))]
        })
        
        microthemes = mt_data["microthemes"]
        if canonical_theme not in microthemes:
            microthemes = [canonical_theme] + microthemes
            
        subject_area = canonical_subj if canonical_subj != 'General' else mt_data["subject_area"]
        norm_subject = normalize_subject(subject_area)
        
        # Build keyword set from microthemes
        mt_keywords = build_microtheme_keywords(microthemes)
        q_text_kws = extract_question_keywords(q_text_orig)
        combined_kws = mt_keywords | q_text_kws
        
        # Find matching PYQs across CSE, CDS, CAPF
        matches = []
        for pyq in pyq_data:
            sim = compute_similarity(combined_kws, pyq['keywords'])
            if sim >= SIMILARITY_THRESHOLD:
                matches.append({
                    "pyq_id": pyq['id'],
                    "year": pyq['year'],
                    "paper": pyq['paper'],
                    "subject": pyq['subject'],
                    "topics": pyq['topics'],
                    "question": pyq['question'],
                    "option_a": pyq['option_a'],
                    "option_b": pyq['option_b'],
                    "option_c": pyq['option_c'],
                    "option_d": pyq['option_d'],
                    "correct_answer": pyq['correct_answer'],
                    "explanation": pyq['explanation'],
                    "similarity": round(sim, 3),
                    "matching_keywords": sorted(list(combined_kws & pyq['keywords']))[:15],
                })
        
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Deduplicate - keep top match per year per exam
        seen = set()
        deduped_matches = []
        for m in matches:
            key = (m['year'], m['paper'])
            if key not in seen:
                seen.add(key)
                deduped_matches.append(m)
        
        top_matches = deduped_matches[:20]
        
        has_match = len(top_matches) > 0 or len(past_book_questions) > 0
        best_sim = top_matches[0]['similarity'] if top_matches else (0.4 if past_book_questions else 0)
        has_strong_match = best_sim >= 0.3 or len(past_book_questions) >= 3
        
        if has_match:
            questions_with_pyq_match += 1
        if has_strong_match:
            questions_with_strong_match += 1
        
        subject_stats[norm_subject]["total"] += 1
        if has_match:
            subject_stats[norm_subject]["matched"] += 1
        if has_strong_match:
            subject_stats[norm_subject]["strong"] += 1
        
        for m in top_matches:
            year_match_counts[m['year']] += 1
            exam_match_counts[m['paper']] += 1
        
        # Microtheme frequency tracking
        microtheme_frequency[canonical_theme] += cat_info.get('question_count', len(top_matches))
        
        # Build question result
        q_result = {
            "question_number": q_num,
            "question_text": q_text_orig,
            "option_a": str(row.get('Option_A', '')) if pd.notna(row.get('Option_A')) else '',
            "option_b": str(row.get('Option_B', '')) if pd.notna(row.get('Option_B')) else '',
            "option_c": str(row.get('Option_C', '')) if pd.notna(row.get('Option_C')) else '',
            "option_d": str(row.get('Option_D', '')) if pd.notna(row.get('Option_D')) else '',
            "correct_answer": str(row.get('Correct_Answer', '')) if pd.notna(row.get('Correct_Answer')) else '',
            "explanation": str(row.get('Explanation', '')) if pd.notna(row.get('Explanation')) else '',
            "subject": subject_area,
            "normalized_subject": norm_subject,
            "canonical_subject": canonical_subj,
            "canonical_microtheme": canonical_theme,
            "theme_total_pyq_count": cat_info.get('question_count', 0),
            "past_cse_same_theme_count": len(past_book_questions),
            "past_cse_same_theme_questions": past_book_questions[:8],
            "original_topics": str(row.get('Topics', '')) if pd.notna(row.get('Topics')) else '',
            "original_tags": str(row.get('Tags', '')) if pd.notna(row.get('Tags')) else '',
            "nuanced_microthemes": microthemes,
            "total_pyq_matches": len(top_matches),
            "best_similarity": best_sim,
            "has_pyq_coverage": has_match,
            "has_strong_coverage": has_strong_match,
            "difficulty": str(row.get('Difficulty', 'medium')) if pd.notna(row.get('Difficulty')) else 'medium',
            "matching_pyqs": top_matches,
            "years_with_matches": sorted(list(set([m['year'] for m in top_matches] + [q['year'] for q in past_book_questions]))),
            "exams_with_matches": sorted(list(set(m['paper'] for m in top_matches))),
        }
        
        results["questions"].append(q_result)
        
        if q_num % 10 == 0:
            print(f"  Processed Q{q_num}/100...")
    
    # Build aggregate statistics
    results["aggregate"] = {
        "questions_with_any_pyq_match": questions_with_pyq_match,
        "questions_with_strong_match": questions_with_strong_match,
        "pct_any_match": round(questions_with_pyq_match / len(cse_2024) * 100, 1),
        "pct_strong_match": round(questions_with_strong_match / len(cse_2024) * 100, 1),
        "avg_matches_per_question": round(sum(q['total_pyq_matches'] for q in results['questions']) / len(cse_2024), 1),
    }
    
    # Subject breakdown
    results["subject_breakdown"] = {
        subj: {
            "total": stats["total"],
            "matched": stats["matched"],
            "strong": stats["strong"],
            "pct_matched": round(stats["matched"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0,
            "pct_strong": round(stats["strong"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0,
        }
        for subj, stats in sorted(subject_stats.items())
    }
    
    # Year heatmap
    all_years = sorted(set(year_match_counts.keys()))
    results["year_heatmap"] = {
        year: year_match_counts[year] for year in all_years
    }
    
    # Exam contribution
    results["exam_contribution"] = dict(exam_match_counts)
    
    # Top canonical microthemes
    top_mts = sorted(microtheme_frequency.items(), key=lambda x: x[1], reverse=True)[:30]
    results["top_microthemes"] = [{"theme": t, "match_count": c} for t, c in top_mts if c > 0]
    
    # Save JSON
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[Analyzer] Analysis complete with Book Microtheme integration!")
    print(f"  Questions with ANY PYQ match: {questions_with_pyq_match}/{len(cse_2024)} ({results['aggregate']['pct_any_match']}%)")
    print(f"  Questions with STRONG match: {questions_with_strong_match}/{len(cse_2024)} ({results['aggregate']['pct_strong_match']}%)")
    print(f"  Avg matches per question: {results['aggregate']['avg_matches_per_question']}")
    print(f"  Results saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    run_analysis(
        csv_path="output/all_exams_prelims.csv",
        output_path="dashboard/data/analysis_results.json"
    )
