
import importlib
import inspect
import io
import sys
from typing import Callable, Dict, List, Optional

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ------------------------------
# Page config & styling
# ------------------------------
st.set_page_config(
    page_title="World Bank Green Bonds — Main Findings",
    page_icon="🌍",
    layout="wide"
)

st.title("World Bank Green Bonds — Main Findings Dashboard")
st.caption("EE 105 Group Project | Interactive summary of Sections 8, 9, and 10")

st.markdown(
    \"\"\"
This dashboard distills the **main findings** from our case study on the World Bank's **Green Bonds**,
highlighting data trends (Section 8), case-study impacts (Section 9), and **policy implications** (Section 10).
Use the sidebar to tweak filters or upload your own CSVs to replicate figures.
\"\"\"
)

# ------------------------------
# Helper utilities
# ------------------------------
def try_import_project_module(mod_name: str = "ee_105_group_project"):
    \"\"\"Try to import the student's project module. Return module or None.\"\"\"
    try:
        mod = importlib.import_module(mod_name)
        return mod
    except Exception as e:
        st.info(f"ℹ️ Could not import `{mod_name}` automatically. Using built-in demo plots.\\n\\n**Reason:** {e}")
        return None

def find_plot_functions(mod, section_prefix: str) -> List[Callable]:
    \"\"\"Return a list of callables in `mod` whose names start with `section_prefix` or 'plot_' with section in name.\"\"\"
    fns: List[Callable] = []
    if mod is None:
        return fns
    for name, obj in inspect.getmembers(mod, inspect.isfunction):
        lower = name.lower()
        if lower.startswith(section_prefix) or (lower.startswith("plot") and section_prefix in lower):
            # ensure it takes 0 or 1 kwargs (we'll call without args)
            try:
                sig = inspect.signature(obj)
                fns.append(obj)
            except Exception:
                pass
    return fns

def run_and_capture_plot(fn: Callable):
    \"\"\"Run a plotting function and render the figure. We try both returning a fig or drawing on plt.\"\"\"
    try:
        out = fn()
        if hasattr(out, "savefig"):  # looks like a Matplotlib Figure
            st.pyplot(out)
            return
        # If function returns Axes or None, fallback to current figure
        fig = plt.gcf()
        st.pyplot(fig)
    except TypeError:
        # Try calling with no args even if signature disagrees
        try:
            out = fn  # if it's already a figure
            if hasattr(out, "savefig"):
                st.pyplot(out)
                return
        except Exception:
            st.warning(f"Could not render function `{getattr(fn,'__name__','<unknown>')}` due to signature mismatch.")
    except Exception as e:
        st.warning(f"⚠️ Error when running `{getattr(fn,'__name__','<unknown>')}`: {e}")

def demo_line_chart(df: Optional[pd.DataFrame] = None, x="Year", y="Value", title="Demo Trend"):
    if df is None:
        df = pd.DataFrame({
            x: list(range(2010, 2025)),
            y: [v * 1.0 for v in range(15)]
        })
    fig, ax = plt.subplots()
    ax.plot(df[x], df[y])
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    st.pyplot(fig)

# ------------------------------
# Sidebar controls
# ------------------------------
with st.sidebar:
    st.header("Controls")
    st.markdown("Adjust inputs or upload CSVs to regenerate figures.")
    uploaded_8 = st.file_uploader("Upload CSV for Section 8 (optional)", type=["csv"], key="s8_csv")
    uploaded_9 = st.file_uploader("Upload CSV for Section 9 (optional)", type=["csv"], key="s9_csv")
    default_region = st.selectbox("Region (for captions)", ["Global", "OECD", "Developing Economies", "World Bank IBRD/IDA"])
    show_notes = st.checkbox("Show verbose notes", value=False)

# ------------------------------
# Module detection & function mapping
# ------------------------------
project_mod = try_import_project_module()

section8_functions = find_plot_functions(project_mod, "section8")
section9_functions = find_plot_functions(project_mod, "section9")
# Also support explicit names like plot_section8_graph1, etc.
if project_mod is not None and not section8_functions:
    for name in ["plot_section8_graph1","plot_section8_graph2","plot_section8","plot_s8"]:
        fn = getattr(project_mod, name, None)
        if callable(fn):
            section8_functions.append(fn)

if project_mod is not None and not section9_functions:
    for name in ["plot_section9_graph1","plot_section9_graph2","plot_section9","plot_s9"]:
        fn = getattr(project_mod, name, None)
        if callable(fn):
            section9_functions.append(fn)

# ------------------------------
# Section 8 — Data Analysis & Key Trends
# ------------------------------
st.markdown("## Section 8 — Data Analysis & Key Trends")
st.write("Trends in **green bond issuance**, **capital mobilization**, and **climate outcome metrics**.")

if uploaded_8 is not None:
    try:
        df8 = pd.read_csv(uploaded_8)
        st.dataframe(df8.head(20), use_container_width=True)
        demo_line_chart(df8, x=df8.columns[0], y=df8.columns[1], title="Section 8 — Uploaded Data Trend")
    except Exception as e:
        st.error(f"Could not parse Section 8 CSV: {e}")

if section8_functions:
    st.info("Using plotting functions detected in your project module for Section 8.")
    for fn in section8_functions:
        st.markdown(f"**Figure:** `{fn.__name__}`")
        run_and_capture_plot(fn)
else:
    st.warning("No Section 8 plotting functions detected in `ee_105_group_project.py`. Showing demo chart instead.")
    demo_line_chart(title="Section 8 — Demo Trend (Green Bond Issuance)")

st.markdown(
    f\"\"\"
**Interpretation (Section 8):**  
• Green bond issuance has shown sustained growth, signaling stronger investor appetite for climate finance.  
• Real-economy indicators suggest incremental links between financing volumes and **project outcomes** (e.g., renewables capacity, energy efficiency).  
• Regional view: **{default_region}** shows differing uptake based on policy frameworks and market depth.
\"\"\"
)

# ------------------------------
# Section 9 — Case Studies & Impact Evaluation
# ------------------------------
st.markdown("## Section 9 — Case Studies & Impact Evaluation")
st.write("Comparative evidence on **emissions**, **resilience**, and **social spillovers** across projects/countries.")

if uploaded_9 is not None:
    try:
        df9 = pd.read_csv(uploaded_9)
        st.dataframe(df9.head(20), use_container_width=True)
        demo_line_chart(df9, x=df9.columns[0], y=df9.columns[1], title="Section 9 — Uploaded Data Trend")
    except Exception as e:
        st.error(f"Could not parse Section 9 CSV: {e}")

if section9_functions:
    st.info("Using plotting functions detected in your project module for Section 9.")
    for fn in section9_functions:
        st.markdown(f"**Figure:** `{fn.__name__}`")
        run_and_capture_plot(fn)
else:
    st.warning("No Section 9 plotting functions detected in `ee_105_group_project.py`. Showing demo chart instead.")
    demo_line_chart(title="Section 9 — Demo Impact Comparison")

st.markdown(
    f\"\"\"
**Interpretation (Section 9):**  
• Projects financed by green bonds show **measurable environmental benefits** when coupled with robust monitoring and reporting.  
• **Co-benefits** (jobs, public health, energy access) appear stronger in **{default_region}** when governance capacity is higher.  
• Impact heterogeneity underscores the need for transparent **use-of-proceeds** and standardized metrics.
\"\"\"
)

# ------------------------------
# Section 10 — Policy Implications & Significance
# ------------------------------
st.markdown("## Section 10 — Policy Implications & Significance")
st.success(
    \"\"\"
- **Scale & Standardize:** Clear taxonomies and verification standards reduce greenwashing and lower issuance costs.
- **De-risking:** Blended finance (guarantees, first-loss tranches) can crowd in private capital in emerging markets.
- **Disclosure:** Comparable KPIs (emissions avoided, MW installed, households served) enable outcome-based evaluation.
- **Local Capacity:** Strengthen project pipeline (PPPs, technical assistance) to translate proceeds into **real outcomes**.
- **Just Transition:** Prioritize co-benefits (health, jobs) and community safeguards to ensure equitable distribution.
\"\"\"
)

with st.expander("📌 Key Takeaways (One-slide Summary)"):
    st.markdown(
        \"\"\"
1. **Green bonds mobilize climate capital** at scale, with growth linked to policy clarity and investor confidence.  
2. **Outcomes improve with accountability:** strong MRV, standardized KPIs, and independent verification.  
3. **Policy levers** (taxonomies, de-risking, disclosure) are pivotal to expand adoption, especially in developing regions.  
4. **Social co-benefits** make green bonds a compelling public narrative beyond carbon metrics.
\"\"\"
    )

# ------------------------------
# Footer
# ------------------------------
st.markdown("---")
st.caption("Created with Streamlit • Swap in your own figures by defining functions in `ee_105_group_project.py` (e.g., `plot_section8_graph1`) or uploading CSVs from the sidebar.")
