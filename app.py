import streamlit as st
import pandas as pd
import altair as alt
from google import genai
from gmail_service import send_ai_insights_email

# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

DATA_FILE = "data/IBM_i_Incident_Data.xlsx"
PROMPT_FILE = "prompts/ai_insights_prompt.md"
CSS_FILE = "styles/app_styles.css"

# --------------------------------------------------
# GEMINI AI CONFIGURATION
# --------------------------------------------------

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

client = genai.Client(
    api_key=GEMINI_API_KEY
)

# --------------------------------------------------
# GEMINI AI OPERATIONAL INSIGHT FUNCTION
# --------------------------------------------------

def generate_ai_insights(findings):

    try:

        prompt_template = load_ai_prompt()

        prompt = f"""
{prompt_template}

# VALIDATED FINDINGS

{findings}
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
        )

        return response.text

    except FileNotFoundError:

        raise RuntimeError(
            "AI prompt file could not be found. "
            "Please check the PROMPT_FILE configuration."
        )

    except Exception as e:

        raise RuntimeError(
            f"Unable to generate AI operational insights: {str(e)}"
        )

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="IBM i Incident Insight & Response Assistant",
    page_icon="🖥️",
    layout="wide"
)

# --------------------------------------------------
# APPLICATION TITLE
# --------------------------------------------------

st.markdown(
"""<div style="text-align: center; padding: 10px 0 20px 0;">
<h1>🖥️ IBM i Incident Insight &amp; Response Assistant</h1>
<h3>AI-Assisted Operational Incident Analysis</h3>
<p style="font-size: 16px;">
This prototype analyses synthetic IBM i operational incident data to identify
patterns, calculate key performance indicators, and generate advisory insights
to support human decision-making.
</p>
</div>
""",
unsafe_allow_html=True
)

st.info("""
⚠️ Responsible AI Notice:
AI-generated insights in this application are advisory only.
Final operational decisions must be reviewed by an authorised IBM i support professional.
""")

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_excel(DATA_FILE)
    return df

# --------------------------------------------------
# DATA VALIDATION
# --------------------------------------------------

REQUIRED_COLUMNS = [
    "incident_id",
    "timestamp",
    "system_name",
    "subsystem",
    "alert_category",
    "message_id",
    "severity",
    "description",
    "resolution_status",
    "resolution_duration_minutes",
    "business_impact",
    "affected_users",
    "assigned_team"
]

def validate_data(df):

    validation_results = {}

    # Check for missing required columns
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    validation_results["missing_columns"] = missing_columns

    # Check for missing values
    validation_results["missing_values"] = int(
        df.isnull().sum().sum()
    )

    # Check for duplicate Incident IDs
    if "incident_id" in df.columns:

        validation_results["duplicate_incident_ids"] = int(
            df["incident_id"].duplicated().sum()
        )

    else:

        validation_results["duplicate_incident_ids"] = None

    return validation_results

def load_ai_prompt():

    with open(
        PROMPT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        prompt_template = file.read()

        return prompt_template

def load_css():

    with open(
        CSS_FILE,
        "r"
    ) as file:

        st.markdown(
            f"<style>{file.read()}</style>",
            unsafe_allow_html=True
        )

try:

    load_css()
    # Load data
    df = load_data()

    # Convert data types
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df["resolution_duration_minutes"] = pd.to_numeric(df["resolution_duration_minutes"],errors="coerce")
    df["affected_users"] = pd.to_numeric(df["affected_users"],errors="coerce")

    # Validate dataset
    validation_results = validate_data(df)

    # Show validation confirmation
    st.success("Incident dataset loaded successfully.")
    st.success("Dataset validation completed.")

    with st.expander("🔍 View Data Validation Results"):

        # Required columns validation
        if len(validation_results["missing_columns"]) == 0:
            st.success("✅ All required columns are present.")
        else:
            st.error(
                f"❌ Missing required columns: "
                f"{', '.join(validation_results['missing_columns'])}"
            )

        # Missing values validation
        if validation_results["missing_values"] == 0:
            st.success("✅ No missing values found.")
        else:
            st.warning(
                f"⚠️ Missing values found: "
                f"{validation_results['missing_values']}"
            )

        # Duplicate Incident IDs validation
        if validation_results["duplicate_incident_ids"] is None:

            st.warning(
                "⚠️ Duplicate Incident ID validation could not be performed "
                "because the incident_id column is missing."
            )

        elif validation_results["duplicate_incident_ids"] == 0:

            st.success(
                "✅ No duplicate Incident IDs found."
            )
        else:

            st.warning(
                f"⚠️ Duplicate Incident IDs found: "
                f"{validation_results['duplicate_incident_ids']}"
            )
    # --------------------------------------------------
    # APPLICATION NAVIGATION
    # --------------------------------------------------

    tab_dashboard, tab_data, tab_ai = st.tabs(
        [
            "📊 Dashboard",
            "📋 Incident Data",
            "🤖 AI Insights"
        ]
    )


    # --------------------------------------------------
    # KPI CALCULATIONS
    # --------------------------------------------------

    total_incidents = len(df)

    critical_high_incidents = len(df[df["severity"].isin(["Critical", "High"])])
    open_incidents = len(df[df["resolution_status"] != "Resolved"])
    resolved_incidents = df[df["resolution_status"] == "Resolved"]
    average_resolution_time = (resolved_incidents["resolution_duration_minutes"].dropna().mean())
    total_affected_users = int(df["affected_users"].sum())    

    # --------------------------------------------------
    # KEY OPERATIONAL FINDINGS
    # --------------------------------------------------

    # Most frequent alert category
    most_frequent_category = (
        df["alert_category"]
        .value_counts()
        .idxmax()
    )

    most_frequent_category_count = int(
        df["alert_category"]
        .value_counts()
        .max()
    )


    # System with the highest number of incidents
    highest_incident_system = (
        df["system_name"]
        .value_counts()
        .idxmax()
    )

    highest_incident_system_count = int(
        df["system_name"]
        .value_counts()
        .max()
    )


    # Alert category with longest average resolution time
    longest_resolution_category = (
        resolved_incidents
        .groupby("alert_category")[
            "resolution_duration_minutes"
        ]
        .mean()
        .idxmax()
    )

    longest_resolution_time = (
        resolved_incidents
        .groupby("alert_category")[
            "resolution_duration_minutes"
        ]
        .mean()
        .max()
    )


    # Peak incident day
    daily_incident_counts = (
        df.groupby(
            df["timestamp"].dt.date
        )
        .size()
    )

    peak_incident_day = (
        daily_incident_counts.idxmax()
    )

    peak_incident_count = int(
        daily_incident_counts.max()
    )


    # Critical incidents
    critical_incident_count = int(
        len(
            df[
                df["severity"] == "Critical"
            ]
        )
    )

    critical_incident_percentage = (
        critical_incident_count
        / total_incidents
        * 100
    )

    # --------------------------------------------------
    # INCIDENT OVERVIEW - CORE KPIs
    # --------------------------------------------------
    with tab_dashboard:
        st.header("📊 Incident Overview")
        st.caption(
                    "A high-level operational snapshot of incident volume, severity, backlog, resolution performance," 
                    "and business impact, calculated directly from the validated incident dataset."
        )

        # KPI cards
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            with st.container(border=True):
                st.metric(
                    label="📊 Total Incidents",
                    value=f"{total_incidents:,}"
                )


        with col2:
            with st.container(border=True):
                st.metric(
                    label="🚨 Critical + High Incidents",
                    value=f"{critical_high_incidents:,}"
                )

        with col3:
            with st.container(border=True):
                st.metric(
                    label="📂 Open Incident Backlog",
                    value=f"{open_incidents:,}"
                )

        with col4:
            with st.container(border=True):
                st.metric(
                    label="⏱️ Avg Resolution Time",
                    value=f"{average_resolution_time:.1f} min"
                )

        with col5:
            with st.container(border=True):
                st.metric(
                    label="👥 Total Affected Users",
                    value=f"{total_affected_users:,}"
                )

        with st.expander("ℹ️ KPI Definitions"):
            st.markdown("""
            - **Total Incidents:** Total number of incidents in the dataset.
            - **Critical + High:** Number of incidents classified as Critical or High severity.
            - **Open Backlog:** Incidents not yet marked as Resolved.
            - **Average Resolution Time:** Average resolution duration for resolved incidents.
            - **Affected Users:** Total number of users affected across all incidents.
            """)

    # --------------------------------------------------
    # INCIDENT PATTERN ANALYSIS
    # --------------------------------------------------

        st.header("📈 Incident Pattern Analysis")

        st.caption(
                    "The charts below highlight incident distribution, system impact, "
                    "resolution performance, and incident activity trends based on the "
                    "validated incident dataset."
        )

    # ==================================================
    # PREPARE DATA FOR CHARTS
    # ==================================================

    # Chart 1 - Incidents by Severity
        severity_counts = (
            df["severity"]
            .value_counts()
            .reindex(["Critical", "High", "Medium", "Low"])
            .fillna(0)
        )

        severity_df = severity_counts.reset_index()
        severity_df.columns = ["Severity", "Incident Count"]


        # Chart 2 - Incidents by Alert Category
        category_counts = (
            df["alert_category"]
            .value_counts()
            .sort_values(ascending=False)
        )

        category_df = category_counts.reset_index()
        category_df.columns = ["Alert Category", "Incident Count"]


        # Chart 3 - Incidents by System
        system_counts = (
            df["system_name"]
            .value_counts()
            .sort_values(ascending=False)
        )

        system_df = system_counts.reset_index()
        system_df.columns = ["System", "Incident Count"]


        # Chart 4 - Daily Incident Trend
        daily_incidents = (
            df.groupby(df["timestamp"].dt.date)
            .size()
            .reset_index(name="incident_count")
        )

        daily_incidents.columns = [
            "Date",
            "Incident Count"
        ]


        # Chart 5 - Average Resolution Time
        average_resolution_by_category = (
            resolved_incidents
            .groupby("alert_category")[
                "resolution_duration_minutes"
            ]
            .mean()
            .sort_values(ascending=False)
        )

        resolution_df = (
            average_resolution_by_category
            .reset_index()
        )

        resolution_df.columns = [
            "Alert Category",
            "Average Resolution Time (Minutes)"
        ]

    # ==================================================
    # CREATE CHARTS
    # ==================================================

    # Chart 1 - Severity
        severity_chart = (
            alt.Chart(severity_df)
            .mark_bar(size=45)
            .encode(
                x=alt.X(
                    "Severity:N",
                    sort=["Critical", "High", "Medium", "Low"],
                    axis=alt.Axis(
                        title=None,
                        labelAngle=0
                    )
                ),
                y=alt.Y(
                    "Incident Count:Q",
                    title="Incident Count"
                ),
                color=alt.Color(
                    "Severity:N",
                    legend=None
                ),
                tooltip=[
                    alt.Tooltip("Severity:N"),
                    alt.Tooltip("Incident Count:Q")
                ]
            )
            .properties(
                height=220
            )
        )


        # Chart 2 - Alert Category
        category_chart = (
            alt.Chart(category_df)
            .mark_bar(size=40)
            .encode(
                x=alt.X(
                    "Alert Category:N",
                    sort="-y",
                    axis=alt.Axis(
                        title=None,
                        labelAngle=-35
                    )
                ),
                y=alt.Y(
                    "Incident Count:Q",
                    title="Incident Count"
                ),
                color=alt.Color(
                    "Alert Category:N",
                    legend=None
                ),
                tooltip=[
                    alt.Tooltip("Alert Category:N"),
                    alt.Tooltip("Incident Count:Q")
                ]
            )
            .properties(
                height=220
            )
        )


        # Chart 3 - System
        system_chart = (
            alt.Chart(system_df)
            .mark_bar(size=55)
            .encode(
                x=alt.X(
                    "System:N",
                    sort="-y",
                    axis=alt.Axis(
                        title=None,
                        labelAngle=-20
                    )
                ),
                y=alt.Y(
                    "Incident Count:Q",
                    title="Incident Count"
                ),
                color=alt.Color(
                    "System:N",
                    legend=None
                ),
                tooltip=[
                    alt.Tooltip("System:N"),
                    alt.Tooltip("Incident Count:Q")
                ]
            )
            .properties(
                height=220
            )
        )


        # Chart 4 - Daily Incident Trend
        trend_chart = (
            alt.Chart(daily_incidents)
            .mark_line(
                point=True
            )
            .encode(
                x=alt.X(
                    "Date:T",
                    title="Date"
                ),
                y=alt.Y(
                    "Incident Count:Q",
                    title="Incident Count"
                ),
                tooltip=[
                    alt.Tooltip(
                        "Date:T",
                        format="%d %b %Y"
                    ),
                    alt.Tooltip("Incident Count:Q")
                ]
            )
            .properties(
                height=250
            )
        )


        # Chart 5 - Resolution Time
        resolution_chart = (
            alt.Chart(resolution_df)
            .mark_bar(size=40)
            .encode(
                x=alt.X(
                    "Alert Category:N",
                    sort="-y",
                    axis=alt.Axis(
                        title=None,
                        labelAngle=-35
                    )
                ),
                y=alt.Y(
                    "Average Resolution Time (Minutes):Q",
                    title="Resolution Time (Min)"
                ),
                color=alt.Color(
                    "Alert Category:N",
                    legend=None
                ),
                tooltip=[
                    alt.Tooltip("Alert Category:N"),
                    alt.Tooltip(
                        "Average Resolution Time (Minutes):Q",
                        format=".1f"
                    )
                ]
            )
            .properties(
                height=250
            )
        )

    # ==================================================
    # DISPLAY CHARTS ON DASHBOARD
    # ==================================================

        st.divider()

        # ------------------------------
        # FIRST ROW
        # ------------------------------

        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):

                st.markdown(
                    "<h4 style='text-align: center;'>"
                    "Incidents by Severity"
                    "</h4>",
                    unsafe_allow_html=True
                )

                st.altair_chart(
                    severity_chart,
                    use_container_width=True
                )


        with col2:
            with st.container(border=True):

                st.markdown(
                    "<h4 style='text-align: center;'>"
                    "Incidents by Alert Category"
                    "</h4>",
                    unsafe_allow_html=True
                )

                st.altair_chart(
                    category_chart,
                    use_container_width=True
                )


        # ------------------------------
        # SECOND ROW
        # ------------------------------

        col3, col4 = st.columns(2)

        with col3:
            with st.container(border=True):

                st.markdown(
                    "<h4 style='text-align: center;'>"
                    "Incidents by System"
                    "</h4>",
                    unsafe_allow_html=True
                )

                st.altair_chart(
                    system_chart,
                    use_container_width=True
                )


        with col4:
            with st.container(border=True):

                st.markdown(
                    "<h4 style='text-align: center;'>"
                    "Average Resolution Time"
                    "</h4>",
                    unsafe_allow_html=True
                )

                st.altair_chart(
                    resolution_chart,
                    use_container_width=True
                )


        # ------------------------------
        # THIRD ROW - FULL WIDTH
        # ------------------------------

        with st.container(border=True):

            st.markdown(
                "<h4 style='text-align: center;'>"
                "Daily Incident Trend"
                "</h4>",
                unsafe_allow_html=True
            )

            st.altair_chart(
                trend_chart,
                use_container_width=True
            )

        with st.expander("📖 Chart Guide"):

            st.markdown(
                """
                - **Incidents by Severity:** Shows the distribution of incidents
                across severity levels.

                - **Incidents by Alert Category:** Shows which operational alert
                categories occur most frequently.

                - **Incidents by System:** Shows incident volume across IBM i systems.

                - **Average Resolution Time:** Shows the average time required to
                resolve incidents by alert category.

                - **Daily Incident Trend:** Shows how incident volume changes over time.
                """
            )

        # --------------------------------------------------
        # KEY OPERATIONAL FINDINGS
        # --------------------------------------------------

        st.header("🔎 Key Operational Findings")

        st.caption(
            "The findings below are calculated directly from the "
            "validated incident dataset using deterministic Python logic."
        )

        st.divider()


        # ==================================================
        # FIRST ROW
        # ==================================================

        col1, col2 = st.columns(2)

        with col1:
            with st.container(border=True):

                st.subheader("📊 Alert Pattern")

                st.markdown(
                    f"**Most Frequent Alert Category:** {most_frequent_category}"
                )

                st.markdown(
                    f"**Incident Volume:** {most_frequent_category_count} incidents"
                )


        with col2:
            with st.container(border=True):

                st.subheader("🖥️ System Impact")

                st.markdown(
                    f"**Highest Incident Volume:** {highest_incident_system}"
                )

                st.markdown(
                    f"**Incident Count:** {highest_incident_system_count} incidents"
                )


        # ==================================================
        # SECOND ROW
        # ==================================================

        col3, col4 = st.columns(2)

        with col3:
            with st.container(border=True):

                st.subheader("⏱️ Resolution Concern")

                st.markdown(
                    f"**Longest Average Resolution Time:** "
                    f"{longest_resolution_category}"
                )

                st.markdown(
                    f"**Average Resolution:** "
                    f"{longest_resolution_time:.1f} minutes"
                )


        with col4:
            with st.container(border=True):

                st.subheader("📅 Peak Activity")

                st.markdown(
                    f"**Peak Incident Day:** "
                    f"{peak_incident_day.strftime('%d %b %Y')}"
                )

                st.markdown(
                    f"**Incidents Recorded:** {peak_incident_count}"
                )

        # ==================================================
        # THIRD ROW
        # ==================================================

        col5, col6 = st.columns(2)

        with col5:
            with st.container(border=True):

                st.subheader("🚨 Critical Incident Risk")

                st.markdown(
                    f"**Critical Incidents:** "
                    f"{critical_incident_count}"
                )

                st.markdown(
                    f"**Percentage of Total:** "
                    f"{critical_incident_percentage:.1f}%"
                )


        with col6:
            with st.container(border=True):

                st.subheader("📂 Operational Backlog")

                st.markdown(
                    f"**Current Open Incidents:** "
                    f"{open_incidents}"
                )

                st.markdown(
                    "**Metric:** Incidents not yet marked as Resolved"
                )

    # --------------------------------------------------
    # INCIDENT DATA EXPLORER
    # --------------------------------------------------
    with tab_data:
        st.subheader("📋 Incident Data Explorer")

        st.caption(
            f"The dataset contains {len(df):,} incident records. "
            "Select how many records you want to display."
        )

        records_to_show = st.selectbox(
            "Number of records to display",
            options=[20, 50, 100, "All"],
            index=0
        )

        if records_to_show == "All":
            data_to_display = df
        else:
            data_to_display = df.head(records_to_show)

        st.dataframe(
            data_to_display,
            use_container_width=True,
            height=500
        )

    # --------------------------------------------------
    # COLUMN INFORMATION
    # --------------------------------------------------

        st.subheader("Dataset Columns")

        st.write(list(df.columns))

    # --------------------------------------------------
    # PREPARE VALIDATED FINDINGS FOR GEMINI AI
    # --------------------------------------------------

    findings_summary = f"""
    Most frequent alert category: {most_frequent_category}
    Number of incidents in this category: {most_frequent_category_count}

    System with highest incident volume: {highest_incident_system}
    Number of incidents on this system: {highest_incident_system_count}

    Alert category with longest average resolution time: {longest_resolution_category}
    Average resolution time: {longest_resolution_time:.1f} minutes

    Peak incident day: {peak_incident_day.strftime('%d %b %Y')}
    Number of incidents on peak day: {peak_incident_count}

    Critical incidents: {critical_incident_count}
    Critical incident percentage: {critical_incident_percentage:.1f}%

    Current open incident backlog: {open_incidents}
    """

    # --------------------------------------------------
    # AI-ASSISTED OPERATIONAL INSIGHTS
    # --------------------------------------------------
    with tab_ai:

        st.header("🤖 AI-Assisted Operational Insights")

        st.caption(
            "AI-Generated Insights Notice: Operational metrics and findings are "
            "calculated using Python/Pandas from the validated incident dataset. "
            "Gemini AI is used to interpret these validated findings and generate "
            "hypotheses and recommendations. AI-generated hypotheses require "
            "further operational validation and should not be treated as confirmed "
            "root causes."
        )


        # --------------------------------------------------
        # INITIALIZE SESSION STATE
        # --------------------------------------------------

        if "ai_insights" not in st.session_state:
            st.session_state.ai_insights = None


        # --------------------------------------------------
        # AI INSIGHT ACTION BUTTONS
        # --------------------------------------------------

        col_generate, col_clear = st.columns(2)
        #left_space, col_generate, col_clear, right_space = st.columns([1, 2, 2, 1])

        with col_generate:

            generate_clicked = st.button(
                "✨ Generate AI Insights",
                type="primary",
                use_container_width=True
            )


        with col_clear:

            clear_clicked = st.button(
                "🗑️ Clear Insights",
                type="secondary",
                use_container_width=True
            )


        # --------------------------------------------------
        # CLEAR AI INSIGHTS
        # --------------------------------------------------

        if clear_clicked:

            st.session_state.ai_insights = None

            st.rerun()


        # --------------------------------------------------
        # GENERATE AI INSIGHTS
        # --------------------------------------------------

        if generate_clicked:

            try:

                with st.spinner(
                    "Gemini is analyzing the operational findings..."
                ):

                    st.session_state.ai_insights = (
                        generate_ai_insights(
                            findings_summary
                        )
                    )

            except RuntimeError as e:

                st.error(
                    f"⚠️ AI insights could not be generated.\n\n{str(e)}"
                )

        # --------------------------------------------------
        # DISPLAY AI INSIGHTS
        # --------------------------------------------------

        if st.session_state.ai_insights:

            st.success(
                "AI operational insights generated successfully."
            )

            st.divider()

            st.subheader("📋 AI Operational Analysis")

            # --------------------------------------------------
            # AI INSIGHTS DISPLAY CONTAINER
            # --------------------------------------------------

            with st.container(border=True):

                st.markdown(
                    """
                    ### 🤖 AI-Generated Operational Insights

                    The following analysis is generated from validated
                    operational findings. AI-generated risks, hypotheses,
                    and recommendations require operational review and
                    validation.
                    """
                )

                st.divider()

                st.markdown(
                    st.session_state.ai_insights
                )

            st.divider()

            # --------------------------------------------------
            # DOWNLOAD AI INSIGHTS
            # --------------------------------------------------

            st.download_button(
                label="📥 Download AI Insights Report",
                data=st.session_state.ai_insights,
                file_name="IBM_i_AI_Operational_Insights.md",
                mime="text/markdown",
                use_container_width=True
            )

            # --------------------------------------------------
            # EMAIL AI INSIGHTS
            # --------------------------------------------------

            st.divider()

            st.subheader("📧 Send AI Insights via Email")

            st.caption(
                "Send the generated AI operational insights to an "
                "operations team member or stakeholder."
            )

            recipient_email = st.text_input(
                "Recipient Email Address",
                placeholder="name@example.com"
            )

            if st.button(
                "📧 Send AI Insights",
                use_container_width=True
            ):

                if not recipient_email.strip():

                    st.warning(
                        "Please enter a recipient email address."
                    )

                else:

                    try:

                        with st.spinner(
                            "Sending AI insights via Gmail..."
                        ):

                            send_ai_insights_email(
                                recipient_email.strip(),
                                st.session_state.ai_insights
                            )

                        st.success(
                            "AI operational insights sent successfully."
                        )

                    except Exception as e:

                        st.error(
                            "Unable to send the AI insights email. "
                            "Please verify the recipient email address and Gmail authorization."
                        )            

except FileNotFoundError:

    st.error(
        "Excel data file was not found. "
        "Please make sure IBM_i_Incident_Data.xlsx is inside the Project Files folder."
    )

except Exception as e:

    st.error(f"An error occurred while loading the data: {e}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Capstone Prototype | Synthetic Data Only | "
    "IBM i Incident Insight & Response Assistant"
)