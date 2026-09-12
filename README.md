# 🖥️ IBM i Incident Insight & Response Assistant

## AI-Assisted Operational Incident Analysis

A Python and Streamlit-based prototype designed to analyse IBM i operational incident data, identify patterns, calculate key performance indicators, and generate AI-assisted operational insights.

The application combines deterministic Python/Pandas analysis with Gemini AI interpretation to support IBM i operations teams in reviewing incident patterns, operational risks, possible investigation areas, and recommended actions.

> ⚠️ **Responsible AI Notice**
>
> AI-generated insights in this application are advisory only. Operational findings and metrics are calculated from the validated dataset using deterministic Python logic. AI-generated hypotheses and recommendations require human operational review and should not be treated as confirmed root causes.

---

# 📌 Project Overview

IBM i environments generate operational information including incidents, alerts, system events, resolution records, and business impact information.

This prototype demonstrates how operational incident data can be transformed into useful management and operational insights.

---

## 🔄 Application Workflow

The application follows the workflow below:

```text
Incident Dataset
       ↓
Data Validation
       ↓
Python / Pandas Analysis
       ↓
Operational KPIs
       ↓
Incident Pattern Analysis
       ↓
Validated Operational Findings
       ↓
Gemini AI Interpretation
       ↓
Human Review
       ↓
Download or Email AI Insights

```
The AI component does not treat raw incident records as its primary source of truth. Instead, Python and Pandas first calculate validated findings from the dataset. These validated findings are then provided to Gemini AI for interpretation.

---

# ✨ Key Features

## 📊 Incident Dashboard

Provides a high-level operational overview including:

- Total incidents
- Critical and high-severity incidents
- Open incident backlog
- Average resolution time
- Total affected users

---

## 📈 Incident Pattern Analysis

Visualises operational patterns using Altair charts, including:

- Incidents by severity
- Incidents by alert category
- Incidents by system
- Average resolution time by alert category
- Daily incident trend

---

## 🔎 Key Operational Findings

Calculates validated findings directly from the incident dataset, including:

- Most frequent alert category
- System with the highest incident volume
- Alert category with the longest average resolution time
- Peak incident day
- Critical incident percentage
- Current open incident backlog

These findings are calculated using deterministic Python/Pandas logic before being provided to the AI model.

---

## 🤖 AI-Assisted Operational Insights

Gemini AI interprets the validated operational findings and generates the following sections.

### Executive Summary

A concise summary of the most important operational patterns identified in the validated findings.

### Most Important Operational Risk

The AI analysis clearly separates:

- **Observation** — a fact directly supported by the validated findings.
- **Risk** — a potential operational impact inferred from the findings.

Inferred risks are not presented as confirmed incidents or facts.

### Possible Reasons Requiring Investigation

The AI provides possible explanations and areas for further investigation.

These are treated as hypotheses only and are not presented as confirmed root causes.

### Recommended Priority Actions

Recommendations are separated into:

- **Immediate Actions**
- **Preventive Actions**

Recommendations are based on observed operational patterns and require appropriate operational validation.

---

# 🧠 Responsible AI Approach

The project follows a structured approach to reduce the risk of AI-generated assumptions being treated as operational facts.

The responsibilities are separated as follows:

| Component | Responsibility |
|---|---|
| Python / Pandas | Data processing and validated calculations |
| Dataset Validation | Required column validation, missing value checks, and duplicate Incident ID checks |
| Gemini AI | Interpretation of validated findings |
| Human Operator | Review and final operational decisions |

The AI prompt instructs the model to:

- Treat validated findings as the source of truth.
- Avoid inventing statistics, incidents, systems, or events.
- Clearly distinguish observations from inferred risks.
- Treat possible causes as hypotheses.
- Avoid claiming confirmed root causes without supporting evidence.
- Use cautious language when suggesting IBM i investigation areas.
- Explicitly state when further investigation or validation is required.

This approach ensures that AI-generated content remains advisory and supports, rather than replaces, operational decision-making.

---

# 📧 Email Integration

The application can send generated AI Operational Insights directly by email using the Gmail API.

The implementation uses:

- Google OAuth 2.0 authentication
- Gmail API
- Restricted Gmail sending permissions
- Locally stored OAuth credentials and authorization tokens

The Gmail functionality is implemented separately in:

```text
gmail_service.py
```
OAuth credentials and authorization tokens are excluded from GitHub using `.gitignore`.

---

# 🏗️ Project Structure

```text
IBM-i-Incident-Insight-Response-Assistant/
│
├── app.py
├── gmail_service.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── .streamlit/
│   └── secrets.toml              # Not uploaded to GitHub
│
├── credentials/
│   ├── credentials.json          # Not uploaded to GitHub
│   └── token.json                # Not uploaded to GitHub
│
├── data/
│   └── IBM_i_Incident_Data.xlsx
│
├── prompts/
│   └── ai_insights_prompt.md
│
└── styles/
    └── app_styles.css

```
---
# 🛠️ Technology Stack

The project uses the following technologies:

- Python
- Streamlit
- Pandas
- Altair
- OpenPyXL
- Google Gemini API
- Google Gen AI SDK
- Gmail API
- Google OAuth 2.0

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone <your-repository-url>
```

## 2. Move into the Project Directory
```bash
cd IBM-i-Incident-Insight-Response-Assistant
```

## 3. Create a Virtual Environment
```bash
python -m venv venv
```

### Windows
```bash
venv\Scripts\activate
```

### macOS / Linux
```bash
source venv/bin/activate
```

## 4. Install Dependencies
```bash
pip install -r requirements.txt
```
---

# 🔑 Gemini API Configuration

The application requires a Gemini API key.

Create the following file:

```text
.streamlit/secrets.toml
```

> ⚠️ Never upload your API key to GitHub.

Add your Gemini API key:
```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```
The `.streamlit/secrets.toml` file should remain private and is excluded from Git using `.gitignore`.

---

# 📧 Gmail API Configuration

The email feature requires Gmail API and Google OAuth configuration.

To configure Gmail integration:

1. Create a Google Cloud project.
2. Enable the Gmail API.
3. Configure the Google OAuth consent screen.
4. Add the required Gmail account as a test user when using Testing mode.
5. Create an OAuth Desktop Client.
6. Download the OAuth credentials JSON file.
7. Place the credentials file at:

```text
credentials/credentials.json
```
The first time an email is sent, Google OAuth authorization will open in the browser.

After successful authorization, the application will create:

```text
`credentials/token.json`
```

The token is used for future authenticated Gmail API access.

Both files must remain private and must not be uploaded to GitHub.

---

# ▶️ Running the Application

Run the Streamlit application using:

```bash
streamlit run app.py
```
The application will then open in your web browser.

---

# 📂 Dataset

This prototype uses synthetic IBM i operational incident data for learning and demonstration purposes.
The dataset includes operational information such as:

- Incident ID
- Incident timestamp
- System name
- Subsystem
- Alert category
- Message ID
- Severity
- Incident description
- Resolution status
- Resolution duration
- Business impact
- Number of affected users
- Assigned team

> The project does not use real production IBM i operational data.

---

# 🔒 Security Considerations

The following files and folders must not be uploaded to GitHub:

```text
credentials/
.streamlit/secrets.toml
```

These locations may contain sensitive information including:

- Google OAuth client credentials
- OAuth authorization tokens
- Gemini API keys

The project's `.gitignore` file is configured to exclude these files from Git.

---

# 🎯 Future Improvements

Possible future enhancements include:

- DB2 for i integration
- Direct integration with IBM i operational data sources
- Automated incident report generation
- Scheduled insight generation
- Email distribution lists
- Historical incident trend comparison
- Configurable alert thresholds
- Role-based access
- Additional AI models
- IBM i services integration
- Enhanced operational dashboards

---

# 👨‍💻 Author

**Aneak Dongre**

IBM i / AS400 Systems Support | Python | Data Analysis | AI-Assisted Operations

---

# 📜 Disclaimer

This project is a prototype created for learning and demonstration purposes.

The application uses synthetic operational incident data and AI-assisted interpretation.

AI-generated insights, risks, hypotheses, and recommendations are advisory only. They should not be treated as confirmed operational facts, confirmed root causes, or production solutions without appropriate human review and technical validation.