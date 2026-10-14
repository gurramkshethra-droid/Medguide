"""
Skin Health Guide helpers.

There is no trained skin-image model in this project. This module only stores
educational ABCDE text. It must never call the symptom classifier on photos.
"""

ABCDE_CRITERIA = [
    {
        "letter": "A",
        "feature": "Asymmetry",
        "description": "One half of the spot does not match the other half.",
    },
    {
        "letter": "B",
        "feature": "Border",
        "description": "The edges are irregular, ragged, notched, or blurred.",
    },
    {
        "letter": "C",
        "feature": "Colour",
        "description": "Colour is not even. Brown, black, red, white, or blue patches may appear.",
    },
    {
        "letter": "D",
        "feature": "Diameter",
        "description": "The spot is larger than about 6 millimetres, roughly the size of a pencil eraser.",
    },
    {
        "letter": "E",
        "feature": "Evolving",
        "description": "The spot is changing in size, shape, colour, or symptoms such as itch or bleeding.",
    },
]

WHEN_TO_SEE_DERMATOLOGIST = [
    "A mole or patch is new, changing, or matches any ABCDE feature.",
    "A spot bleeds, crusts, or does not heal.",
    "You have many moles, very fair skin, or a family history of skin cancer — ask a clinician about checks.",
    "A rash is painful, spreading rapidly, or you feel unwell with fever.",
]

FUTURE_SCOPE_NOTE = (
    "Photo analysis is future scope. It would require a clinically evaluated image model "
    "(for example trained and tested on a dermoscopic dataset) and independent clinical review. "
    "This project does not analyse skin photographs and does not reuse the symptom model on images."
)
