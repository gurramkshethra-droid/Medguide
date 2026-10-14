"""
Red-flag triage rules.

These rules run on the patient's selected symptoms BEFORE any ML ranking.
Emergency and urgent outcomes are never overridden by the model.
"""

from __future__ import annotations

EMERGENCY = "emergency"
URGENT = "urgent"
ROUTINE = "routine"

# Feature names must match model.pkl exactly.
BREATHING = {"breathlessness"}
CHEST_PAIN = {"chest_pain"}
FAINTING_OR_COLLAPSE = {"coma"}
CONFUSION = {"altered_sensorium"}
SERIOUS_BLEEDING = {"stomach_bleeding", "blood_in_sputum", "bloody_stool"}
YELLOW_EYES = {"yellowing_of_eyes", "yellowish_skin"}
FEVER = {"high_fever", "mild_fever"}
VOMITING = {"vomiting"}


def _has(selected, names):
    return bool(set(selected) & names)


def assess_triage(selected_symptoms, severity="moderate", age_group="adult", history=None):
    """
    Return a structured triage result.

    Emergency examples from the project brief:
      severe breathing difficulty, chest pain with breathlessness,
      fainting, confusion, serious bleeding.

    Urgent example:
      yellow eyes with fever and repeated vomiting.
    """
    selected = [str(s) for s in (selected_symptoms or [])]
    selected_set = set(selected)
    history = history or []
    flags = []
    level = ROUTINE

    def raise_level(new_level):
        nonlocal level
        order = {ROUTINE: 0, URGENT: 1, EMERGENCY: 2}
        if order[new_level] > order[level]:
            level = new_level

    severe_breathing = _has(selected, BREATHING) and (
        severity == "severe" or "fast_heart_rate" in selected_set
    )
    if severe_breathing:
        raise_level(EMERGENCY)
        flags.append(
            "Severe breathing difficulty can be a medical emergency. "
            "Call local emergency services now if breathing is hard, noisy, or you cannot speak full sentences."
        )
    elif _has(selected, BREATHING):
        raise_level(URGENT)
        flags.append(
            "Breathlessness should be assessed promptly, especially if it is new or worsening."
        )

    if _has(selected, CHEST_PAIN) and _has(selected, BREATHING):
        raise_level(EMERGENCY)
        flags.append(
            "Chest pain together with breathlessness can be a medical emergency. "
            "Do not wait for an educational symptom ranking."
        )
    elif _has(selected, CHEST_PAIN):
        raise_level(URGENT)
        flags.append(
            "Chest pain should be assessed the same day. Call emergency services if it is crushing, "
            "spreads to the arm or jaw, or comes with sweating or shortness of breath."
        )

    if _has(selected, FAINTING_OR_COLLAPSE):
        raise_level(EMERGENCY)
        flags.append(
            "Fainting, unresponsiveness, or collapse needs emergency care."
        )

    if _has(selected, CONFUSION):
        raise_level(EMERGENCY)
        flags.append(
            "Confusion or altered awareness can be a stroke or other emergency. Seek emergency care immediately."
        )

    if _has(selected, SERIOUS_BLEEDING):
        raise_level(EMERGENCY)
        flags.append(
            "Serious bleeding (from the gut, lungs, or stools) needs urgent medical evaluation."
        )

    if (
        _has(selected, YELLOW_EYES)
        and _has(selected, FEVER)
        and _has(selected, VOMITING)
    ):
        raise_level(URGENT)
        flags.append(
            "Yellow eyes with fever and vomiting can indicate a liver or infection problem that needs same-day clinical care."
        )

    if "weakness_of_one_body_side" in selected_set:
        raise_level(EMERGENCY)
        flags.append(
            "Sudden one-sided weakness can be a stroke warning. Seek emergency care immediately."
        )

    if age_group == "child" and ("high_fever" in selected_set or "chest_pain" in selected_set):
        raise_level(URGENT)
        flags.append("Fever or chest symptoms in children need prompt clinical advice.")

    if age_group == "older_adult" and (
        "chest_pain" in selected_set or "breathlessness" in selected_set
    ):
        if level == ROUTINE:
            raise_level(URGENT)
        flags.append("Chest pain or breathlessness in older adults should be assessed the same day.")

    if "pregnancy" in history and (
        "vomiting" in selected_set or "high_fever" in selected_set or "chest_pain" in selected_set
    ):
        raise_level(URGENT)
        flags.append("These symptoms in pregnancy warrant same-day clinical advice.")

    if "immunosuppression" in history and "high_fever" in selected_set:
        raise_level(URGENT)
        flags.append("Fever with a weakened immune system should be reviewed promptly.")

    if not flags and severity == "moderate" and len(selected) >= 3:
        flags.append("If symptoms worsen, spread, or you feel newly unwell, contact a clinician.")

    labels = {
        EMERGENCY: "Emergency care now",
        URGENT: "Seek care today",
        ROUTINE: "Self-care and monitor",
    }
    summaries = {
        EMERGENCY: (
            "Emergency warning signs are present. Skip ordinary self-care and get emergency help now. "
            "The educational ranking below does not override this warning."
        ),
        URGENT: (
            "Same-day clinical advice is appropriate. Do not wait for symptoms to settle on their own. "
            "The educational ranking below does not override this warning."
        ),
        ROUTINE: (
            "No emergency warning signs were identified from the selected inputs. "
            "Ordinary guidance may follow, with uncertainty."
        ),
    }

    return {
        "level": level,
        "label": labels[level],
        "summary": summaries[level],
        "warning_flags": list(dict.fromkeys(flags)),
        "checked_before_guidance": True,
        "overrides_model": level in {EMERGENCY, URGENT},
    }
