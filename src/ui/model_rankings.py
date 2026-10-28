# "How the Models Rank Your Careers": the formula's top 5 next to three trained models for the saved profile
# Display only; rankings and explanations come from src/ml/comparison.py

from html import escape

import streamlit as st

from src.ml.comparison import FORMULA, ComparisonUnavailableError, compare_methods
from src.services.profiles import ProfileValidationError
from src.ui.components import ASSESSMENT_PAGE
from src.ui.state import get_live_models

EXPLANATION_NOTES = {
    "formula": "Points are the weighted parts of the formula score and add up to it.",
    "logistic_regression": "Numbers are each feature's effect on the model's log-odds compared with an average "
                           "training pair. Positive values raise the score.",
    "decision_tree": "The tree sends each career down one path of yes or no questions. All careers on the same path "
                     "get the same score.",
    "random_forest": "Numbers are the average change in the 300 trees' score caused by splits on each feature. Every "
                     "career starts at {bias:.2f} before any split.",
}
GRID = (("formula", "logistic_regression"), ("decision_tree", "random_forest"))


def score_text(method, score):
    return f"{score:.1f} / 100" if method == FORMULA else f"{score:.3f}"


def method_card(entry):
    method = entry["method"]
    with st.container(border=True, key=f"panel_rank_{method}", height="stretch"):
        if entry["primary"]:
            st.markdown(":green-badge[:material/verified: Primary method, used by this app]")
        else:
            st.markdown(":blue-badge[:material/science: Trained model, comparison only]")
        st.markdown(f"#### {escape(entry['label'])}")
        if entry["error"]:
            st.warning(f"This model could not rank careers for your profile ({entry['error']}).",
                       icon=":material/warning:")
            return
        st.caption(entry["score_name"])
        lines = []
        for row in entry["careers"]:
            extra = "" if entry["primary"] else f" :gray[formula rank {row['formula_rank']}]"
            lines.append(f"{row['rank']}. **{row['career_title']}** :gray[{score_text(method, row['score'])}]{extra}")
        st.markdown("  \n".join(lines))
        if not entry["primary"]:
            st.caption(f"{entry['shared_with_formula']} of {len(entry['careers'])} careers are also in the "
                       "formula's top 5.")
            if entry.get("tied_outside"):
                st.caption(f":material/drag_handle: {entry['tied_outside']} more careers have the same score as "
                           "the last one shown. Ties are ordered by career id, so the end of this list is "
                           "partly arbitrary.")
        with st.expander("Why these careers"):
            bias = entry["careers"][0].get("detail", {}).get("bias", 0.0) if entry["careers"] else 0.0
            st.caption(EXPLANATION_NOTES[method].format(bias=bias))
            for row in entry["careers"]:
                st.markdown(f"**{row['rank']}. {row['career_title']}**")
                st.markdown("\n".join(f"- {line}" for line in row["explanation"]))


def model_rankings_section(profile, catalog):
    st.subheader("How the Models Rank Your Careers", anchor=False)
    st.markdown(
        "Your saved answers ranked by the **weighted formula** the app uses, and by three machine-learning models "
        "trained for comparison. All four see the same 50 careers and the same 13 features built from your "
        "skills, interests and education. The formula stays the primary method. Your Interested and Not for me "
        "feedback is not included here, so every method gets exactly the same input."
    )
    if not profile:
        st.info("Complete the career assessment to see how each method ranks careers for your answers.",
                icon=":material/assignment:")
        st.page_link(ASSESSMENT_PAGE, label="Go to the Career Assessment", icon=":material/arrow_forward:")
        return
    models, error = get_live_models()
    if models is None:
        st.info(f"The model comparison is not available right now ({error}). The rest of the app works as usual.",
                icon=":material/info:")
        return
    try:
        result = compare_methods(profile, catalog, models)
    except (ProfileValidationError, ValueError, ComparisonUnavailableError) as exc:
        st.error(f"Your saved assessment could not be compared: {exc}.", icon=":material/error:")
        return
    methods = result["methods"]
    formula_top = methods[FORMULA]["careers"]
    if formula_top and formula_top[0]["score"] == 0:
        st.warning("None of your skills or interests match any career yet, so every method is ranking on "
                   "tie-breaks only. Add skills or interests in the assessment for a meaningful comparison.",
                   icon=":material/warning:")
    for row in GRID:
        cols = st.columns(len(row))
        for col, method in zip(cols, row):
            if method in methods:
                with col:
                    method_card(methods[method])
    info = models.info
    st.caption(
        f":material/info: Model scores (0 to 1) are relative ranking scores, not your chance of success. The "
        f"models were trained with balanced class weights on {info['profiles']} synthetic profiles "
        f"({info['pairs']:,} learner-career pairs, {info['relevant_pairs']} labelled relevant) written and labelled "
        "by the project author. Agreement here shows how the methods differ for your answers, not which one is "
        "right for you."
    )
    st.caption(f":material/timer: Measured on this server: models trained once in {info['seconds']:.2f} s and "
               f"reused for every visitor; this comparison took {result['seconds'] * 1000:.0f} ms.")
