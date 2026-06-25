from typing import Dict, List, Any, Tuple
from datetime import datetime

DOMAIN_WEIGHTS = {
    "B": 1.5,  # Sleep
    "C": 1.5,  # Food & Eating
    "D": 1.0,  # Movement
    "E": 1.0,  # Stress
    "F": 1.5,  # Digestion
}

DOMAIN_MAX_POINTS = {
    "B": 15,
    "C": 15,
    "D": 10,
    "E": 10,
    "F": 15,
}

SCORE_MAPPING = {
    "A": 10, "B": 7, "C": 4, "D": 2, "E": 0
}


def score_option(option: str) -> int:
    """Convert option letter (A-E) to numeric score."""
    return SCORE_MAPPING.get(option, 0)


def evaluate_domain_b(responses: Dict[str, Any]) -> Tuple[float, float, List[str]]:
    """Sleep Audit - Weight: 1.5x, Max: 15 pts"""
    q7, q8, q9, q10, q11, q12 = responses.get("q7"), responses.get("q8"), responses.get("q9"), responses.get("q10"), responses.get("q11"), responses.get("q12")

    scores = [score_option(q) for q in [q7, q8, q9, q10, q11, q12] if q]
    b_raw = sum(scores) / len(scores) if scores else 0
    b_weighted = b_raw * 1.5

    flags = []

    # Q7 sleep time
    if q7 in ["C"]: flags.append("yellow_q7_sleep_time")
    elif q7 in ["D", "E"]: flags.append("orange_q7_sleep_time")

    # Q8 wake time
    if q8 == "D": flags.append("yellow_q8_wake_time")
    elif q8 == "E": flags.append("orange_q8_wake_time")

    # Q9 sleep duration
    if q9 == "C": flags.append("yellow_q9_duration")
    elif q9 in ["D", "E"]: flags.append("orange_q9_duration")

    # Q10 morning feeling - most clinically significant
    if q10 == "C": flags.append("yellow_q10_morning")
    elif q10 == "D": flags.append("orange_q10_morning")
    elif q10 == "E": flags.append("red_q10_morning_sleep_disorder")

    # Q10 E + Q9 A/B = sleep apnea indicator
    if q10 == "E" and q9 in ["A", "B"]:
        flags.append("red_sleep_apnea_combination")

    # Q11 screen use
    if q11 == "C": flags.append("yellow_q11_screens")
    elif q11 in ["D", "E"]: flags.append("orange_q11_screens")

    # Q12 difficulty falling asleep
    if q12 == "C": flags.append("yellow_q12_sleep_onset")
    elif q12 == "D": flags.append("orange_q12_sleep_onset")
    elif q12 == "E": flags.append("red_q12_sleep_disorder")

    return b_raw, min(b_weighted, DOMAIN_MAX_POINTS["B"]), flags


def evaluate_domain_c(responses: Dict[str, Any]) -> Tuple[float, float, List[str]]:
    """Food & Eating Habits - Weight: 1.5x, Max: 15 pts"""
    q13, q14, q15, q16, q17, q18, q19, q20 = (
        responses.get("q13"), responses.get("q14"), responses.get("q15"),
        responses.get("q16"), responses.get("q17"), responses.get("q18"),
        responses.get("q19"), responses.get("q20")
    )

    scores = [score_option(q) for q in [q13, q14, q15, q16, q17, q18, q19, q20] if q]
    c_raw = sum(scores) / len(scores) if scores else 0
    c_weighted = c_raw * 1.5

    flags = []

    # Q13 meal regularity
    if q13 == "C": flags.append("yellow_q13_meal_regularity")
    elif q13 in ["D", "E"]: flags.append("orange_q13_meal_regularity")

    # Q14 meal timing consistency
    if q14 == "C": flags.append("yellow_q14_timing_consistency")
    elif q14 == "D": flags.append("orange_q14_timing_consistency")

    # Q15 dinner timing - HIGHEST CLINICAL SIGNIFICANCE
    if q15 == "C": flags.append("yellow_q15_dinner_timing")
    elif q15 == "D": flags.append("orange_q15_dinner_timing")
    elif q15 == "E": flags.append("red_q15_dinner_timing")

    # Q15 D/E + Q17 D/E = CRITICAL
    if q15 in ["D", "E"] and q17 in ["D", "E"]:
        flags.append("red_late_eating_combination")

    # Q16 processed food
    if q16 == "C": flags.append("yellow_q16_processed")
    elif q16 in ["D", "E"]: flags.append("orange_q16_processed")

    # Q17 late night eating
    if q17 == "C": flags.append("yellow_q17_late_eating")
    elif q17 == "D": flags.append("orange_q17_late_eating")
    elif q17 == "E": flags.append("red_q17_late_eating")

    # Q18 sugar cravings
    if q18 == "C": flags.append("yellow_q18_sugar")
    elif q18 == "D": flags.append("orange_q18_sugar")

    # Q19 emotional eating
    if q19 == "C": flags.append("yellow_q19_emotional")
    elif q19 == "D": flags.append("orange_q19_emotional")

    # Q20 water intake
    if q20 in ["C", "D"]: flags.append("yellow_q20_water")

    return c_raw, min(c_weighted, DOMAIN_MAX_POINTS["C"]), flags


def evaluate_domain_d(responses: Dict[str, Any]) -> Tuple[float, float, List[str]]:
    """Movement & Activity - Weight: 1x, Max: 10 pts"""
    q21, q22, q23, q24, q25 = (
        responses.get("q21"), responses.get("q22"), responses.get("q23"),
        responses.get("q24"), responses.get("q25")
    )

    scores = [score_option(q) for q in [q21, q22, q23, q24, q25] if q]
    d_raw = sum(scores) / len(scores) if scores else 0
    d_weighted = d_raw * 1.0

    flags = []

    # Q21 exercise frequency
    if q21 == "C": flags.append("yellow_q21_exercise")
    elif q21 in ["D", "E"]: flags.append("orange_q21_exercise")

    # Q22 daily walking
    if q22 == "C": flags.append("yellow_q22_walking")
    elif q22 == "D": flags.append("orange_q22_walking")

    # Q23 sitting duration - SEDENTARY RISK
    if q23 == "C": flags.append("yellow_q23_sitting")
    elif q23 == "D": flags.append("orange_q23_sitting")
    elif q23 == "E": flags.append("red_q23_sitting")

    # Q24 body pain
    if q24 == "C": flags.append("yellow_q24_pain")
    elif q24 == "D": flags.append("orange_q24_pain")

    # Q25 daytime energy
    if q25 == "C": flags.append("yellow_q25_afternoon_crash")
    elif q25 in ["D", "E"]: flags.append("orange_q25_energy")

    return d_raw, min(d_weighted, DOMAIN_MAX_POINTS["D"]), flags


def evaluate_domain_e(responses: Dict[str, Any]) -> Tuple[float, float, List[str]]:
    """Stress & Emotional Health - Weight: 1x, Max: 10 pts"""
    q26 = responses.get("q26")  # Scale 1-10, convert to 0-10 scoring
    q28 = responses.get("q28")  # Mood fluctuations
    q27_text = responses.get("q27_text", "")
    q29_text = responses.get("q29_text", "")
    q30_selection = responses.get("q30_selection", "")

    # Convert Q26 scale to score
    q26_score = 10
    if q26:
        try:
            val = int(q26)
            if 1 <= val <= 3: q26_score = 10
            elif 4 <= val <= 5: q26_score = 7
            elif 6 <= val <= 7: q26_score = 4
            elif 8 <= val <= 9: q26_score = 2
            elif val == 10: q26_score = 0
        except: pass

    q28_score = score_option(q28) if q28 else 0

    e_raw = (q26_score + q28_score) / 2
    e_weighted = e_raw * 1.0

    flags = []

    # Q26 stress level
    if q26:
        try:
            val = int(q26)
            if 6 <= val <= 7: flags.append("yellow_q26_stress")
            elif 8 <= val <= 9: flags.append("orange_q26_stress")
            elif val == 10: flags.append("red_q26_stress")
        except: pass

    # Q28 mood fluctuations
    if q28 == "C": flags.append("yellow_q28_mood")
    elif q28 == "D": flags.append("orange_q28_mood")

    # Q26 high stress + Q19 emotional eating = CRITICAL
    if q26 and q27_text:
        try:
            if int(q26) >= 8 and responses.get("q19") == "D":
                flags.append("orange_high_stress_emotional_eating")
        except: pass

    # Q28 D + Q25 C/D = glucose dysregulation affecting mood
    if q28 == "D" and responses.get("q25") in ["C", "D"]:
        flags.append("orange_mood_glucose_combo")

    return e_raw, min(e_weighted, DOMAIN_MAX_POINTS["E"]), flags


def evaluate_domain_f(responses: Dict[str, Any]) -> Tuple[float, float, List[str]]:
    """Digestive & Functional Health - Weight: 1.5x, Max: 15 pts"""
    q31, q32, q33, q34, q35 = (
        responses.get("q31"), responses.get("q32"), responses.get("q33"),
        responses.get("q34"), responses.get("q35")
    )

    scores = [score_option(q) for q in [q31, q32, q33, q34, q35] if q]
    f_raw = sum(scores) / len(scores) if scores else 0
    f_weighted = f_raw * 1.5

    flags = []

    # Q31 bloating
    if q31 == "C": flags.append("yellow_q31_bloating")
    elif q31 in ["D", "E"]: flags.append("orange_q31_bloating")

    # Q32 bowel regularity
    if q32 == "C": flags.append("yellow_q32_bowel")
    elif q32 in ["D", "E"]: flags.append("orange_q32_bowel")

    # Q33 acidity - MEDICAL CONCERN
    if q33 == "C": flags.append("yellow_q33_acidity")
    elif q33 in ["D", "E"]: flags.append("orange_q33_acidity")

    # Q34 appetite
    if q34 == "C": flags.append("yellow_q34_appetite")
    elif q34 in ["D", "E"]: flags.append("orange_q34_appetite")

    # Q35 post-meal energy - HIGHEST CLINICAL SIGNIFICANCE IN DOMAIN F
    if q35 == "C": flags.append("yellow_q35_postmeal")
    elif q35 in ["D", "E"]: flags.append("orange_q35_postmeal")

    # Q35 D/E + Q31 D/E = severe gut-metabolic dysfunction
    if q35 in ["D", "E"] and q31 in ["D", "E"]:
        flags.append("orange_gut_metabolic_combo")

    return f_raw, min(f_weighted, DOMAIN_MAX_POINTS["F"]), flags


def calculate_total_score(b_weighted: float, c_weighted: float, d_weighted: float,
                         e_weighted: float, f_weighted: float) -> float:
    """Total score = B + C + D + E + F (max 65 pts)"""
    return b_weighted + c_weighted + d_weighted + e_weighted + f_weighted


def determine_zone(total_score: float) -> Tuple[str, str]:
    """Determine zone and get customer-facing message."""
    if total_score >= 50:
        zone = "Green"
        message = "Your lifestyle is working for you in most areas. The program will sharpen what is already good and build on a strong foundation. You are in the right place to get ahead of problems rather than reverse them."
    elif total_score >= 38:
        zone = "Yellow"
        message = "Your lifestyle has been drifting — not dramatically, but consistently. The good news is that drifting is reversible faster than it accumulated. The program will give you the structure to reverse it before it becomes a more serious concern."
    elif total_score >= 25:
        zone = "Orange"
        message = "Your score tells us that several areas of your lifestyle are working against your health at the same time. This is the most common pattern we see — and also the pattern that responds most dramatically to structured intervention. You are in exactly the right place."
    else:
        zone = "Red"
        message = "Your results show that your body has been under sustained pressure for some time. We are glad you are here. Before we design your program, one of our clinical team members will reach out to understand your situation personally."

    return zone, message


def evaluate_audit(responses: Dict[str, Any]) -> Dict[str, Any]:
    """Complete audit evaluation with all scoring and flags."""
    b_raw, b_weighted, b_flags = evaluate_domain_b(responses)
    c_raw, c_weighted, c_flags = evaluate_domain_c(responses)
    d_raw, d_weighted, d_flags = evaluate_domain_d(responses)
    e_raw, e_weighted, e_flags = evaluate_domain_e(responses)
    f_raw, f_weighted, f_flags = evaluate_domain_f(responses)

    total_score = calculate_total_score(b_weighted, c_weighted, d_weighted, e_weighted, f_weighted)
    zone, message = determine_zone(total_score)

    # Determine lowest and highest domains
    domain_scores = {
        "Sleep": b_raw,
        "Food & Eating": c_raw,
        "Movement": d_raw,
        "Stress": e_raw,
        "Digestion": f_raw,
    }
    lowest_domain = min(domain_scores, key=domain_scores.get)
    highest_domain = max(domain_scores, key=domain_scores.get)

    # Collect all critical flags
    all_flags = b_flags + c_flags + d_flags + e_flags + f_flags
    critical_flags = [f for f in all_flags if "red" in f or "orange" in f]

    # Determine if BNYS review is required
    bnys_review_required = (
        "red_sleep_apnea_combination" in all_flags or
        "red_late_eating_combination" in all_flags or
        "red_q15_dinner_timing" in all_flags or
        "red_q33_acidity" in all_flags or
        "orange_high_stress_emotional_eating" in all_flags or
        zone == "Red"
    )

    baseline_labs_required = zone in ["Orange", "Red"]

    return {
        "section_b": {"q7": responses.get("q7"), "q8": responses.get("q8"), "q9": responses.get("q9"),
                     "q10": responses.get("q10"), "q11": responses.get("q11"), "q12": responses.get("q12"),
                     "b_raw": b_raw, "b_weighted": b_weighted, "flags": b_flags},
        "section_c": {"q13": responses.get("q13"), "q14": responses.get("q14"), "q15": responses.get("q15"),
                     "q16": responses.get("q16"), "q17": responses.get("q17"), "q18": responses.get("q18"),
                     "q19": responses.get("q19"), "q20": responses.get("q20"),
                     "c_raw": c_raw, "c_weighted": c_weighted, "flags": c_flags},
        "section_d": {"q21": responses.get("q21"), "q22": responses.get("q22"), "q23": responses.get("q23"),
                     "q24": responses.get("q24"), "q25": responses.get("q25"),
                     "d_raw": d_raw, "d_weighted": d_weighted, "flags": d_flags},
        "section_e": {"q26": responses.get("q26"), "q27": responses.get("q27"), "q28": responses.get("q28"),
                     "q29": responses.get("q29"), "q30": responses.get("q30"),
                     "e_raw": e_raw, "e_weighted": e_weighted, "flags": e_flags},
        "section_f": {"q31": responses.get("q31"), "q32": responses.get("q32"), "q33": responses.get("q33"),
                     "q34": responses.get("q34"), "q35": responses.get("q35"),
                     "f_raw": f_raw, "f_weighted": f_weighted, "flags": f_flags},
        "total_score": round(total_score, 2),
        "zone": zone,
        "zone_message": message,
        "lowest_domain": lowest_domain,
        "highest_domain": highest_domain,
        "critical_flags": critical_flags,
        "bnys_review_required": bnys_review_required,
        "baseline_labs_required": baseline_labs_required,
        "priority_intervention": determine_first_intervention(c_raw, domain_scores, critical_flags),
        "completed_at": datetime.utcnow().isoformat(),
    }


def determine_first_intervention(c_raw: float, domain_scores: Dict, critical_flags: List[str]) -> str:
    """Determine the first intervention to recommend."""
    if "red_late_eating_combination" in critical_flags or "red_q15_dinner_timing" in critical_flags:
        return "Early dinner protocol - CRITICAL"
    elif "orange_q15_dinner_timing" in critical_flags:
        return "Early dinner protocol - HIGH PRIORITY"
    elif "orange_gut_metabolic_combo" in critical_flags:
        return "Food order protocol + chewing protocol"
    elif domain_scores.get("Sleep", 0) < 3:
        return "Sleep timing anchor - fixed wake time first"
    elif domain_scores.get("Food & Eating", 0) < 3:
        return "Early dinner + food order protocol"
    else:
        return "Food order protocol - Week 1"
