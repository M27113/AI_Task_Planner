import streamlit as st
from datetime import datetime
from fpdf import FPDF
import re

from planner import extract_location, generate_plan
from db import init_db, save_plan, fetch_plans, clean_plan_output

# ------------------ Setup ------------------
st.set_page_config(page_title="AI Task Planner", page_icon="📝", layout="wide")
st.title("📝 AI Task Planner")

# Initialize DB
init_db()

# ------------------ Helpers ------------------
def sanitize_text(text: str) -> str:
    """Remove unsupported characters including emojis, symbols, fancy quotes."""
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Keep only ASCII
    return text.encode("latin-1", errors="ignore").decode("latin-1")

def break_long_words(text: str, max_len: int = 40) -> str:
    """Insert spaces in very long words to prevent horizontal space errors in PDF."""
    return re.sub(r'(\S{' + str(max_len) + r'})', r'\1 ', text)

def create_report_pdf(goal: str, plan_text: str) -> bytes:
    """Create a PDF report with proper alignment and no cutting off."""
    pdf = FPDF()
    pdf.add_page()
    page_width = pdf.w - 2 * pdf.l_margin

    # Sanitize texts
    goal = sanitize_text(goal)
    plan_text = sanitize_text(plan_text)

    # ---------- PDF Title & Goal ----------
    pdf.set_font("Arial", "B", 20)
    pdf.multi_cell(page_width, 12, "AI Task Planner", align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "B", 16)
    pdf.multi_cell(page_width, 12, f"GOAL: {goal}", align="C")
    pdf.ln(10)

    # ---------- Plan Content ----------
    for line in plan_text.split("\n"):
        line_clean = sanitize_text(line.strip())
        line_clean = break_long_words(line_clean, max_len=40)
        line_clean = re.sub(r'^[^\w\d]*', '', line_clean)  # Remove leading symbols/emojis

        # Reset X to left margin
        pdf.set_x(pdf.l_margin)

        # Day headers
        if re.match(r"^Day \d+", line_clean):
            pdf.ln(2)
            pdf.set_font("Arial", "B", 14)
            pdf.set_fill_color(220, 220, 220)
            pdf.multi_cell(page_width, 10, line_clean, fill=True)
            pdf.ln(2)
            continue

        # Subheaders (Morning/Afternoon/Evening/Any header starting with "Actionable")
        elif line_clean.lower() in ["morning", "afternoon", "evening"] or line_clean.lower().startswith("actionable"):
            pdf.ln(1)
            pdf.set_font("Arial", "B", 12)
            pdf.set_fill_color(245, 245, 245)
            pdf.multi_cell(page_width, 8, line_clean, fill=True)
            pdf.ln(1)
            continue

        # Numbered lists
        elif re.match(r"^\d+\.", line_clean):
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(page_width, 8, line_clean)
            continue

        # Bullets
        elif line_clean.startswith("- "):
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(page_width, 8, "-- " + line_clean[2:])
            continue

        # Normal text
        else:
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(page_width, 8, line_clean)

    pdf.ln(2)
    return bytes(pdf.output(dest="S"))

# ------------------ New Goal ------------------
st.header("🎯 Enter a New Goal")
goal_input = st.text_area(
    "Your Goal:", 
    height=80, 
    placeholder="e.g., Plan a 3-day trip to Jaipur with cultural highlights and good food"
)


if st.button("Generate Plan"):
    if not goal_input.strip():
        st.warning("Please enter a goal first!")
    else:
        with st.spinner("Generating plan... ✨📝✨"):
            plan_text = generate_plan(goal_input)
            plan_text = clean_plan_output(plan_text)  # Clean plan before saving/PDF
            created_at = datetime.now().isoformat()
            save_plan(goal_input, plan_text, created_at)

            # ---------- Streamlit Display ----------
            st.markdown(f"## GOAL: {goal_input}", unsafe_allow_html=True)
            st.markdown(plan_text, unsafe_allow_html=True)
            # Optional note if weather included
            if extract_location(goal_input):
                st.caption("⚡ Weather info included for detected location.")
            # PDF download
            pdf_bytes = create_report_pdf(goal_input, plan_text)
            st.download_button(
                label="📄 Download PDF",
                data=pdf_bytes,
                file_name="task_plan.pdf",
                mime="application/pdf"
            )

# ------------------ Past Plans ------------------
st.header("📚 Past Plans")
past_plans = fetch_plans()
if not past_plans:
    st.info("No past plans found.")
else:
    for pid, goal, plan_text, created_at in past_plans:
        with st.expander(f"{goal} (Created: {created_at[:19]})"):
            st.markdown(plan_text, unsafe_allow_html=True)
            pdf_bytes = create_report_pdf(goal, plan_text)
            st.download_button(
                label=f"📄 Download PDF",
                data=pdf_bytes,
                file_name=f"task_plan_{pid}.pdf",
                mime="application/pdf"
            )
