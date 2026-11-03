# Controlled interest vocabularies, their display text, and the migration from the old vocabulary
# Source of the 23-term taxonomy: docs/interest_taxonomy_second_review.md (sections B2, C, D and the descriptions table)
# Status: owner-authorized implementation pending lecturer feedback (docs/interest_taxonomy_implementation.md)
# Pure data module with no project imports except text cleaning, so the engine and services can both use it

from dataclasses import dataclass

from src.data.preprocessing import clean_skill_text

# Taxonomy versions; a catalogue folder declares its version in dataset_manifest.json as "interest_taxonomy"
# A folder without that field uses the legacy vocabulary, which keeps the frozen v1.2.0 and v1.3.0 snapshots valid
LEGACY_TAXONOMY = "1.0"
CURRENT_TAXONOMY = "2.0"
MANIFEST_FIELD = "interest_taxonomy"
INTERESTS_PER_CAREER = 3
# Above this many selected interests the form shows a gentle warning; there is no hard cap (second review)
SOFT_SELECTION_LIMIT = 5

RIASEC_ORDER = ("Realistic", "Investigative", "Artistic", "Social", "Enterprising", "Conventional")
RIASEC_DESCRIPTIONS = {
    "Realistic": "Practical work with systems, tools, sites and physical things",
    "Investigative": "Finding out, analysing and solving problems",
    "Artistic": "Creating, designing and expressing ideas",
    "Social": "Teaching, caring for and helping people",
    "Enterprising": "Leading, persuading and running things",
    "Conventional": "Keeping information, systems, rules and money in order",
}


@dataclass(frozen=True)
class InterestTerm:
    label: str
    explanation: str
    example: str
    related_skill: str
    riasec: str
    label_fr_draft: str

    @property
    def key(self):
        # Stored form in careers.csv and profiles: the label lowercased with punctuation removed
        return clean_skill_text(self.label)


# Labels, explanations, examples and related skills are copied from the second review without change
# RIASEC is the primary display group from section D; it is never used in scoring
# label_fr_draft: DRAFT translations written for this implementation; not in either audit; not yet reviewed
INTEREST_TERMS = (
    InterestTerm("Setting up and running computer systems and networks",
                 "You enjoy installing, connecting and keeping computers and networks working",
                 "Setting up a school's Wi-Fi and servers", "Linux, networking", "Realistic",
                 "Installer et gérer des systèmes informatiques et des réseaux"),
    InterestTerm("Working with tools, machines and equipment",
                 "You enjoy practical work with tools, instruments or machines",
                 "Testing an electrical circuit or a prototype", "CAD, laboratory techniques", "Realistic",
                 "Travailler avec des outils, des machines et des équipements"),
    InterestTerm("Working outdoors and with the natural environment",
                 "You enjoy working outside, on sites, with land, rocks, water or nature",
                 "Visiting a mine or a river to take measurements", "Geology, environmental science", "Realistic",
                 "Travailler en plein air et avec l'environnement naturel"),
    InterestTerm("Designing buildings, structures and physical products",
                 "You enjoy planning how a building, structure or object is shaped and works",
                 "Drawing a bridge or a better chair", "Product design, structural analysis", "Realistic",
                 "Concevoir des bâtiments, des structures et des produits physiques"),
    InterestTerm("Analysing data and information",
                 "You enjoy looking at facts and figures to find patterns and answers",
                 "Finding out why sales went down from a table of numbers", "Statistics, data visualization",
                 "Investigative", "Analyser des données et des informations"),
    InterestTerm("Researching and investigating",
                 "You enjoy asking questions and finding out how or why things happen",
                 "Reading studies and testing an idea", "Research methods", "Investigative",
                 "Faire des recherches et mener des enquêtes"),
    InterestTerm("Working with numbers and calculations",
                 "You enjoy solving problems with numbers and formulas",
                 "Working out costs, measurements or probabilities", "Engineering mathematics, statistics",
                 "Investigative", "Travailler avec les chiffres et les calculs"),
    InterestTerm("Scientific and laboratory work",
                 "You enjoy experiments, samples and scientific tests",
                 "Testing water or soil samples in a lab", "Chemistry, laboratory techniques", "Investigative",
                 "Travail scientifique et de laboratoire"),
    InterestTerm("Writing software and building apps",
                 "You enjoy writing code to make programs and apps",
                 "Building a small app that tracks homework", "Python, Java", "Investigative",
                 "Écrire des logiciels et créer des applications"),
    InterestTerm("Creating visual art and graphics",
                 "You enjoy drawing, illustration, animation or visual style",
                 "Designing a poster or an animated character", "Graphic design, illustration", "Artistic",
                 "Créer des arts visuels et des graphismes"),
    InterestTerm("Designing apps, websites and user experiences",
                 "You enjoy planning how a digital product looks and how people use it",
                 "Sketching screens for a banking app", "UI design, user research", "Artistic",
                 "Concevoir des applications, des sites web et des expériences utilisateur"),
    InterestTerm("Writing and editing",
                 "You enjoy putting ideas into clear words",
                 "Writing a report, story or article", "Technical writing, content writing", "Artistic",
                 "Écrire et réviser des textes"),
    InterestTerm("Teaching and training others",
                 "You enjoy explaining things and helping people learn",
                 "Tutoring a classmate in maths", "Lesson planning", "Social",
                 "Enseigner et former les autres"),
    InterestTerm("Caring for people's health",
                 "You enjoy looking after people who are ill or want to stay healthy",
                 "Helping patients recover", "Patient care, pharmacology", "Social",
                 "Prendre soin de la santé des personnes"),
    InterestTerm("Helping and advising people",
                 "You enjoy listening to people and helping them with problems or decisions",
                 "Advising a friend on which course to choose", "Counseling", "Social",
                 "Aider et conseiller les personnes"),
    InterestTerm("Working with communities",
                 "You enjoy working with groups, villages, neighbourhoods or the public",
                 "Organising a meeting about a local project", "Community development, stakeholder engagement",
                 "Social", "Travailler avec les communautés"),
    InterestTerm("Leading people and projects",
                 "You enjoy taking charge, planning and getting a team to finish on time",
                 "Leading a student club event", "Project management", "Enterprising",
                 "Diriger des personnes et des projets"),
    InterestTerm("Running and growing a business",
                 "You enjoy commercial decisions, customers, markets and profit",
                 "Starting a small online shop", "Business management", "Enterprising",
                 "Gérer et développer une entreprise"),
    InterestTerm("Persuading, presenting and negotiating",
                 "You enjoy convincing others, presenting ideas and reaching agreements",
                 "Pitching an idea to a panel", "Communication", "Enterprising",
                 "Convaincre, présenter et négocier"),
    InterestTerm("Keeping information, records and procedures in order",
                 "You enjoy accurate, well-organised files, data and step-by-step procedures",
                 "Keeping a club's membership records correct", "Data modeling, medical coding", "Conventional",
                 "Tenir en ordre les informations, les dossiers et les procédures"),
    InterestTerm("Keeping computer systems and data safe",
                 "You enjoy protecting computers and information from attacks and mistakes",
                 "Finding a weak password policy and fixing it", "Network security", "Conventional",
                 "Protéger les systèmes informatiques et les données"),
    InterestTerm("Working with laws, rules and regulations",
                 "You enjoy reading rules and laws and applying them to real cases",
                 "Checking whether a contract is fair", "Contract law, taxation", "Conventional",
                 "Travailler avec les lois, les règles et les règlements"),
    InterestTerm("Managing money and financial information",
                 "You enjoy budgets, accounts and decisions about money",
                 "Planning a budget for an event", "Accounting, financial analysis", "Conventional",
                 "Gérer l'argent et les informations financières"),
)

TERMS_BY_KEY = {t.key: t for t in INTEREST_TERMS}
CURRENT_INTERESTS = tuple(sorted(TERMS_BY_KEY))
# Draft French names are accepted as input only; they are not shown in the interface until reviewed
FRENCH_DRAFT_TO_KEY = {clean_skill_text(t.label_fr_draft): t.key for t in INTEREST_TERMS}

# The 20-term vocabulary used up to dataset v1.3.0, kept for the frozen evaluation snapshots
LEGACY_INTERESTS = (
    "analysis", "building software", "business", "communication", "design", "engineering",
    "environment", "healthcare", "helping people", "leadership", "mathematics", "organization",
    "problem solving", "research", "science", "security", "teaching", "technology",
    "visual arts", "writing",
)

# Old learner interest to new interest, only where the first audit's section 7 gives a direct or default mapping
LEGACY_TO_CURRENT = {
    "analysis": "analysing data and information",
    "building software": "writing software and building apps",
    "business": "running and growing a business",
    "environment": "working outdoors and with the natural environment",
    "healthcare": "caring for peoples health",
    "helping people": "helping and advising people",
    "leadership": "leading people and projects",
    "mathematics": "working with numbers and calculations",
    "organization": "keeping information records and procedures in order",
    "research": "researching and investigating",
    "science": "scientific and laboratory work",
    "security": "keeping computer systems and data safe",
    "teaching": "teaching and training others",
    "visual arts": "creating visual art and graphics",
    "writing": "writing and editing",
}
# Old terms with no single replacement; they are reported to the learner, never guessed
RETIRED_LEGACY = {
    "communication": "is now a skill only; you can add it under skills, or choose Persuading, presenting and negotiating",
    "design": "was split; choose Creating visual art and graphics, Designing apps, websites and user experiences, "
              "or Designing buildings, structures and physical products",
    "engineering": "named a career category; choose the kinds of engineering work you enjoy",
    "problem solving": "described an ability rather than a kind of work; choose the activities you enjoy",
    "technology": "was too broad; choose the kinds of technology work you enjoy",
}


def vocabulary_for(version):
    # Returns the tuple of stored interest keys for a taxonomy version
    if version == CURRENT_TAXONOMY:
        return CURRENT_INTERESTS
    if version in (None, LEGACY_TAXONOMY):
        return LEGACY_INTERESTS
    raise ValueError(f"Unknown interest taxonomy version: {version!r}")


def taxonomy_of(vocabulary):
    # Infers the taxonomy version from a vocabulary; anything that is not the current set is treated as legacy
    return CURRENT_TAXONOMY if frozenset(vocabulary) == frozenset(CURRENT_INTERESTS) else LEGACY_TAXONOMY


def label_for(key):
    # Display text for a stored key; legacy or unknown values are shown as they are
    term = TERMS_BY_KEY.get(key)
    return term.label if term else key


def labels_for(keys):
    return tuple(label_for(k) for k in keys)


def terms_by_group():
    # {RIASEC type: [InterestTerm, ...]} in RIASEC order, terms in the second review's order
    return {g: [t for t in INTEREST_TERMS if t.riasec == g] for g in RIASEC_ORDER}


@dataclass(frozen=True)
class Resolution:
    status: str  # recognized, migrated, retired or unknown
    raw: str
    key: str = ""
    note: str = ""


def resolve_interest(raw, vocabulary):
    # Maps one raw learner interest to a stored key for the given vocabulary
    # Legacy vocabulary: exact cleaned match only (the frozen behaviour)
    # Current vocabulary: label or key, draft French name, migrated old term, or a reported retired term
    text = (raw or "").strip()
    value = clean_skill_text(text)
    if not value:
        return Resolution("empty", text)
    known = frozenset(vocabulary)
    if value in known:
        return Resolution("recognized", text, value)
    if taxonomy_of(known) != CURRENT_TAXONOMY:
        return Resolution("unknown", text)
    if value in FRENCH_DRAFT_TO_KEY:
        return Resolution("recognized", text, FRENCH_DRAFT_TO_KEY[value])
    if value in LEGACY_TO_CURRENT:
        return Resolution("migrated", text, LEGACY_TO_CURRENT[value])
    if value in RETIRED_LEGACY:
        return Resolution("retired", text, note=RETIRED_LEGACY[value])
    return Resolution("unknown", text)


def migrate_interest_list(raw_interests, vocabulary=CURRENT_INTERESTS):
    # Returns (keys, migrated pairs, retired pairs, unknown) for saved sessions and API input
    keys, migrated, retired, unknown = [], [], [], []
    for raw in raw_interests or ():
        r = resolve_interest(raw, vocabulary)
        if r.key and r.key not in keys:
            keys.append(r.key)
        if r.status == "migrated":
            migrated.append((r.raw, r.key))
        elif r.status == "retired":
            retired.append((r.raw, r.note))
        elif r.status == "unknown":
            unknown.append(r.raw)
    return tuple(keys), tuple(migrated), tuple(retired), tuple(unknown)
