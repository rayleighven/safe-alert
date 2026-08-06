# backend/households/cart_classifier.py
"""
CART (Classification and Regression Tree) implementation for household
evacuation priority classification, per the SAFE-ALERT thesis methodology.

scikit-learn's DecisionTreeClassifier IS a CART implementation (it uses the
CART algorithm internally — that's the actual model doing the classifying).

Since no historical, labeled household assessment data exists yet, the tree
is bootstrapped on a synthetic training set generated from a transparent,
weighted risk-scoring rule (domain-informed: presence of vulnerable members,
housing quality, and hazard exposure). The rule function ONLY generates
labels for this bootstrap set — the tree itself learns its own split rules
from the data, it does not just re-encode the rule as if/else logic.

KNOWN LIMITATION (flag for thesis defense / future work): as real household
assessments accumulate in production, this synthetic training set should be
replaced or supplemented with actual labeled outcomes, and the tree retrained.
"""
import itertools
from decimal import Decimal

from sklearn.tree import DecisionTreeClassifier

from core.choices import HouseMaterial, Priority, RoofMaterial

FEATURE_NAMES = [
    'has_senior_citizen',
    'has_pwd',
    'has_pregnant_member',
    'has_child',
    'house_material_score',
    'roof_material_score',
    'hazard_zone_score',
    'flood_prone',
    'storm_surge_prone',
    'landslide_prone',
    'coastal_zone',
]

HOUSE_MATERIAL_SCORES = {
    HouseMaterial.CONCRETE: 0,
    HouseMaterial.MIXED: 1,
    HouseMaterial.LIGHT: 2,
    HouseMaterial.SALVAGED: 3,
}

ROOF_MATERIAL_SCORES = {
    RoofMaterial.CONCRETE: 0,
    RoofMaterial.MIXED: 1,
    RoofMaterial.GI_SHEET: 2,
    RoofMaterial.COGON: 3,
}

HAZARD_ZONE_SCORES = {
    Priority.LOW: 0,
    Priority.MEDIUM: 1,
    Priority.HIGH: 2,
}


def _vectorize(indicator):
    """Convert a VulnerabilityIndicator instance into a numeric feature vector."""
    return [
        int(indicator.has_senior_citizen),
        int(indicator.has_pwd),
        int(indicator.has_pregnant_member),
        int(indicator.has_child),
        HOUSE_MATERIAL_SCORES[indicator.house_material],
        ROOF_MATERIAL_SCORES[indicator.roof_material],
        HAZARD_ZONE_SCORES[indicator.hazard_zone],
        int(indicator.flood_prone),
        int(indicator.storm_surge_prone),
        int(indicator.landslide_prone),
        int(indicator.coastal_zone),
    ]


def _rule_based_risk_score(vector):
    """
    Weighted scoring rule used ONLY to generate labels for the bootstrap
    training set below. Weights reflect DRRM domain priorities: vulnerable
    household members and severe hazard exposure matter most.
    """
    (has_senior, has_pwd, has_pregnant, has_child,
     house_mat, roof_mat, hazard_zone,
     flood, storm_surge, landslide, coastal) = vector

    score = 0
    score += has_senior * 2
    score += has_pwd * 2
    score += has_pregnant * 2
    score += has_child * 1
    score += house_mat * 1.5
    score += roof_mat * 1
    score += hazard_zone * 2.5
    score += flood * 1.5
    score += storm_surge * 1.5
    score += landslide * 1.5
    score += coastal * 1
    return score


def _label_from_score(score, max_score):
    ratio = score / max_score
    if ratio >= 0.6:
        return Priority.HIGH
    elif ratio >= 0.3:
        return Priority.MEDIUM
    return Priority.LOW


def _build_training_set():
    """
    Generates a synthetic but domain-informed training set spanning a
    representative spread of feature combinations, labeled via the rule
    above, for the DecisionTreeClassifier to learn split rules from.
    """
    X = []
    y = []

    max_possible_score = _rule_based_risk_score([1, 1, 1, 1, 3, 3, 2, 1, 1, 1, 1])

    boolean_combos = list(itertools.product([0, 1], repeat=4))  # senior, pwd, pregnant, child
    hazard_combos = list(itertools.product([0, 1, 2], [0, 1, 2, 3], [0, 1, 2, 3]))  # hazard_zone, house_mat, roof_mat
    exposure_combos = list(itertools.product([0, 1], repeat=4))  # flood, storm_surge, landslide, coastal

    # Sweep 1: vary vulnerable-member composition against a rotating sample
    # of hazard/material/exposure combos.
    for i, (senior, pwd, pregnant, child) in enumerate(boolean_combos):
        hazard_zone, house_mat, roof_mat = hazard_combos[i % len(hazard_combos)]
        flood, storm_surge, landslide, coastal = exposure_combos[i % len(exposure_combos)]

        vector = [senior, pwd, pregnant, child, house_mat, roof_mat, hazard_zone, flood, storm_surge, landslide, coastal]
        X.append(vector)
        y.append(_label_from_score(_rule_based_risk_score(vector), max_possible_score))

    # Sweep 2: hold a fixed "typical family" member profile, vary every
    # hazard/material/exposure combo, so the tree sees hazard-driven
    # variation too, not just member-driven variation.
    for hazard_zone, house_mat, roof_mat in hazard_combos:
        for flood, storm_surge, landslide, coastal in exposure_combos:
            vector = [0, 0, 0, 1, house_mat, roof_mat, hazard_zone, flood, storm_surge, landslide, coastal]
            X.append(vector)
            y.append(_label_from_score(_rule_based_risk_score(vector), max_possible_score))

    return X, y


_X_train, _y_train = _build_training_set()

_classifier = DecisionTreeClassifier(max_depth=5, random_state=42, criterion='gini')
_classifier.fit(_X_train, _y_train)


def classify_household(indicator):
    """
    Runs the trained CART model against a household's VulnerabilityIndicator
    and returns (evacuation_priority, priority_score).

    priority_score is the model's confidence (max class probability) for the
    predicted class, expressed as a percentage (0.00-100.00) to fit the
    schema's DECIMAL(5,2) field.
    """
    vector = _vectorize(indicator)
    predicted_label = _classifier.predict([vector])[0]
    probabilities = _classifier.predict_proba([vector])[0]
    confidence = max(probabilities) * 100

    return predicted_label, Decimal(str(round(confidence, 2)))