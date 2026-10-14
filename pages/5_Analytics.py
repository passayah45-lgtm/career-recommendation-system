# Dataset statistics and learner-specific charts, kept in separate sections

import streamlit as st

from src.services.profiles import ProfileValidationError
from src.services.recommendations import recommend
from src.services.skill_gap import analyze_skill_gap
from src.ui.charts import bar_chart, contribution_chart, coverage_chart
from src.ui.components import need_profile_message, page_setup, score_disclaimer, sidebar_profile_summary
from src.ui.state import get_catalog, get_profile, get_top_k
from src.ui.views import category_counts, contribution_rows, education_counts, required_skill_frequency

page_setup("Analytics")
catalog = get_catalog()
profile = get_profile()
sidebar_profile_summary(profile)

st.caption("This page shows descriptive charts only. The synthetic-profile evaluation (Precision@5, MAP) "
           "is documented in docs/evaluation_report.md in the repository.")

dataset_tab, learner_tab = st.tabs(["Dataset statistics", "Your results"])

with dataset_tab:
    st.markdown("These charts describe the career dataset. They are the same for every learner.")
    m1, m2, m3 = st.columns(3)
    m1.metric("Careers", len(catalog.careers))
    m2.metric("Unique skills", len(catalog.known_skills))
    m3.metric("Learning resources", len(catalog.resources))
    st.plotly_chart(bar_chart(category_counts(catalog.careers), "Category", "Careers", "Careers by category"),
                    width="stretch")
    st.plotly_chart(bar_chart(education_counts(catalog.careers), "Level", "Careers",
                              "Typical entry education level"), width="stretch")
    st.caption("Most careers share level 3, which is why education carries only 5% of the score.")
    st.plotly_chart(bar_chart(required_skill_frequency(catalog.careers, limit=15), "Skill", "Careers",
                              "Most common required skills (top 15)", horizontal=True), width="stretch")

with learner_tab:
    if not profile:
        need_profile_message()
    else:
        st.markdown("These charts use your saved assessment and the same results as the Recommendations page.")
        try:
            result = recommend(profile, catalog, top_k=get_top_k())
        except (ProfileValidationError, ValueError) as exc:
            st.error(f"Your saved assessment could not be used: {exc}.")
        else:
            recs = result["recommendations"]
            score_disclaimer()
            st.plotly_chart(contribution_chart(contribution_rows(recs)), width="stretch")
            by_id = {r["career_id"]: r for r in recs}
            cid = st.selectbox("Skill coverage for", options=list(by_id),
                               format_func=lambda c: f"{by_id[c]['rank']}. {by_id[c]['career_title']}")
            gap = analyze_skill_gap(profile, cid, catalog, include_resources=False)
            st.plotly_chart(coverage_chart(gap), width="stretch")
