# Dataset statistics and learner-specific charts, kept in separate sections

import streamlit as st

from src.data.validation import CATEGORIES
from src.services.profiles import ProfileValidationError
from src.services.recommendations import recommend
from src.services.skill_gap import analyze_skill_gap
from src.ui.charts import bar_chart, contribution_chart, coverage_chart, donut_chart
from src.ui.components import (
    need_profile_message, page_setup, score_disclaimer, sidebar_profile_summary, stat_card,
)
from src.ui.state import get_catalog, get_profile, get_top_k
from src.ui.theme import BLUE, CATEGORY_PALETTE, TEAL
from src.ui.views import (
    category_counts, contribution_rows, education_counts, load_ml_report, model_comparison_rows,
    required_skill_frequency,
)

page_setup("Analytics", subtitle="Explore the dataset and your recommendation results.")
catalog = get_catalog()
profile = get_profile()
sidebar_profile_summary(profile)

st.caption(":material/info: Dataset and personal charts are descriptive. The Model comparison tab shows saved "
           "evaluation results on synthetic profiles; full details are in the research folder of the repository.")

CHART_CONFIG = {"displayModeBar": False}
CATEGORY_COLORS = dict(zip(CATEGORIES, CATEGORY_PALETTE))
# Same height as the education donut, so the two chart cards line up
DONUT_HEIGHT = 430

dataset_tab, learner_tab, model_tab = st.tabs([":material/dataset: Dataset overview", ":material/person: Your results",
                                              ":material/model_training: Model comparison"])

with dataset_tab:
    st.markdown("These charts describe the career dataset. They are the same for every learner.")
    with st.container(key="stats"):
        m1, m2, m3 = st.columns(3)
        stat_card(m1, "Careers", len(catalog.careers), ":material/work:", "blue", "a_careers")
        stat_card(m2, "Unique skills", len(catalog.known_skills), ":material/lightbulb:", "green", "a_skills")
        stat_card(m3, "Learning resources", len(catalog.resources), ":material/menu_book:", "orange", "a_resources")
    left, right = st.columns(2)
    with left, st.container(border=True, key="panel_categories", height="stretch"):
        rows = sorted(category_counts(catalog.careers), key=lambda r: -r["Careers"])
        colors = [CATEGORY_COLORS[r["Category"]] for r in rows]
        st.plotly_chart(bar_chart(rows, "Category", "Careers", "Careers by category", x_title="",
                                  y_title="Number of careers", horizontal=True, colors=colors,
                                  height=DONUT_HEIGHT),
                        width="stretch", config=CHART_CONFIG)
    with right, st.container(border=True, key="panel_education", height="stretch"):
        st.plotly_chart(donut_chart(education_counts(catalog.careers), "Level", "Careers",
                                    "Education level distribution",
                                    center_text=f"<b>{len(catalog.careers)}</b><br>careers", height=DONUT_HEIGHT),
                        width="stretch", config=CHART_CONFIG)
        st.caption("Most careers share level 3, which is why education carries only 5% of the score.")
    with st.container(border=True, key="panel_skills"):
        st.plotly_chart(bar_chart(required_skill_frequency(catalog.careers, limit=15), "Skill", "Careers",
                                  "Top required skills (top 15)", x_title="", y_title="Number of careers",
                                  horizontal=True, colors=[BLUE]),
                        width="stretch", config=CHART_CONFIG)

with learner_tab:
    if not profile:
        need_profile_message()
    else:
        st.markdown("These charts use your saved assessment and the same results as the Recommendations page.")
        try:
            result = recommend(profile, catalog, top_k=get_top_k())
        except (ProfileValidationError, ValueError) as exc:
            st.error(f"Your saved assessment could not be used: {exc}.", icon=":material/error:")
        else:
            recs = result["recommendations"]
            score_disclaimer()
            with st.container(border=True, key="panel_contrib"):
                st.plotly_chart(contribution_chart(contribution_rows(recs)), width="stretch", config=CHART_CONFIG)
            by_id = {r["career_id"]: r for r in recs}
            with st.container(border=True, key="panel_coverage"):
                cid = st.selectbox("Skill coverage for", options=list(by_id),
                                   format_func=lambda c: f"{by_id[c]['rank']}. {by_id[c]['career_title']}")
                gap = analyze_skill_gap(profile, cid, catalog, include_resources=False)
                st.plotly_chart(coverage_chart(gap), width="stretch", config=CHART_CONFIG)

with model_tab:
    rows = model_comparison_rows(load_ml_report())
    if not rows:
        st.info("The saved model comparison results are not available.", icon=":material/info:")
    else:
        st.markdown(
            "Four machine-learning models were trained on learner-career pairs and compared with the weighted "
            "formula this app uses. Every profile was tested by models that never saw it during training. "
            "**No trained model ranked careers better than the formula, and no difference is statistically "
            "significant**, so the app keeps the formula, whose scores can be explained."
        )
        with st.container(border=True, key="panel_models"):
            colors = [TEAL if not r["Trained model"] else BLUE for r in rows]
            short = [{"Method": r["Method"].replace(" (used by this app)", ""), "MAP": r["MAP"]} for r in rows]
            fig = bar_chart(short, "Method", "MAP", "Mean average precision (higher is better)",
                            x_title="", y_title="MAP", horizontal=True, colors=colors)
            # Room on the right so the value labels are not cut off on narrow screens
            fig.update_xaxes(range=[0, 1.18], tickvals=[0, 0.25, 0.5, 0.75, 1.0])
            st.plotly_chart(fig, width="stretch", config=CHART_CONFIG)
            st.caption("Green: the weighted formula used by this app. Blue: trained models.")
        table = [{k: v for k, v in r.items() if k != "Trained model"} for r in rows]
        st.dataframe(table, hide_index=True, width="stretch")
        st.caption(
            ":material/warning: These results come from 36 synthetic profiles written and labelled by the project "
            "author. They measure agreement with those labels, not how well careers suit real learners."
        )
