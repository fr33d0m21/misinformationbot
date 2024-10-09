# MisinformationBot: No More Lies

![MisinformationBot](https://github.com/fr33d0m21/misinformationbot/blob/main/assets/logo.png)

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [How It Works](#how-it-works)
- [Installation Guide](#installation-guide)
  - [Prerequisites](#prerequisites)
  - [Steps](#steps)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Software Flow](#software-flow)
- [Important Notes](#important-notes)
- [Contributing](#contributing)
- [License](#license)

## Introduction

**MisinformationBot: No More Lies** is a robotic detective designed to help you determine the veracity of the information you encounter. Whether it's an article, a social media post, or a news report, MisinformationBot excels at identifying fake news and fostering critical thinking about the information you consume.

## Features

- **Clarifies Claims:** Rewords confusing statements and examines them from multiple perspectives.
- **Detective-Like Investigation:** Develops a strategic plan to uncover the truth behind claims.
- **Decomposition:** Breaks down complex claims into manageable, verifiable parts.
- **Question Generation:** Forms insightful questions to guide research.
- **Research Capability:** Utilizes reliable government sources and advanced tools to gather information.
- **Analysis:** Evaluates research findings to support or refute claims.
- **Argument Identification:** Recognizes and assesses key arguments for and against claims.
- **Comprehensive Reporting:** Compiles findings into detailed, unbiased reports.
- **Visualization:** Creates timelines and charts for better understanding.
- **Feedback & Explanation:** Provides clear, understandable explanations and suggestions.
- **Interactive Q&A:** Answers follow-up questions based on gathered data.

## How It Works

MisinformationBot employs a multi-agent architecture, where each agent specializes in a specific task. These agents collaborate to analyze and verify claims using advanced language processing and research methodologies.

## Installation Guide

### Prerequisites

Before installing MisinformationBot, ensure you have the following:

- **Python:** Version 3.9 or higher. Download it from [python.org](https://www.python.org/).
- **API Accounts & Keys:**
  - **OpenAI:** [OpenAI Platform](https://platform.openai.com/)
  - **Tavily:** [Tavily](https://www.tavily.com/)
  - **Data.gov:** [Data.gov API](https://api.data.gov/) (Free API key available)

### Steps

1. **Clone the Repository:**

   Open your terminal or command prompt and run:

   ```bash
   git clone https://github.com/fr33d0m21/misinformationbot.git
   ```

   Navigate to the project directory:

   ```bash
   cd misinformationbot
   ```

2. **Install Required Libraries:**

   Install the necessary Python packages using pip:

   ```bash
   pip install -r requirements.txt
   ```

   Alternatively, install packages individually:

   ```bash
   pip install fastapi uvicorn python-multipart redis tiktoken python-dotenv openai tavily-python requests beautifulsoup4 matplotlib govinfo pydantic united-states-congress-python-api python-usda
   ```

3. **Set Up API Keys:**

   Create a `.env` file in the `misinformationbot` directory:

   ```bash
   touch .env
   ```

   Open the `.env` file with a text editor and add your API keys:

   ```env
   OPENAI_API_KEY=your_openai_api_key
   TAVILY_API_KEY=your_tavily_api_key
   DATAGOV_API_KEY=your_datagov_api_key
   ```

4. **(Optional) Install Redis for Follow-Up Questions:**

   - **Download Redis:** [Redis Download](https://redis.io/)
   - **Install Redis:** Follow the instructions specific to your operating system.
   
   Once Redis is running, add the following lines to your `.env` file:

   ```env
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```

5. **Run the Bot:**

   In your terminal, start the MisinformationBot server:

   ```bash
   uvicorn main:app --reload
   ```

   Open a second terminal and start the HTTP server:

   ```bash
   python -m http.server 8001
   ```

6. **Access the User Interface:**

   Open your web browser and navigate to [http://127.0.0.1:8000/](http://127.0.0.1:8000/). You should see the MisinformationBot interface ready for use.

## Usage

Once installed and running:

1. **Enter a Claim:** Input any statement or claim you want to verify.
2. **Analysis Process:** MisinformationBot will:
   - Clarify and decompose the claim.
   - Generate and answer relevant questions.
   - Research using reliable sources.
   - Analyze and identify supporting or contradicting arguments.
   - Compile a comprehensive, unbiased report.
   - Provide visual aids and clear explanations.
3. **Review the Report:** Understand the truthfulness of the claim through detailed analysis and visualizations.
4. **Ask Follow-Up Questions:** Engage with the bot for deeper insights or clarifications.

## Project Structure

```
misinformationbot/
├── agents/
│   ├── chain_of_thought_agent.py          # Creates understanding and reasoning for user questions
│   ├── claim_decomposition_agent.py       # Breaks logic into manageable, cross-domain questions
│   ├── question_generation_agent.py       # Generates research questions based on decomposed claims
│   ├── research_agent.py                  # Conducts research for generated questions
│   ├── analyst_agent.py                   # Analyzes collected information and extracts key points
│   ├── argumentation_mining_agent.py      # Identifies and analyzes supporting and opposing arguments
│   ├── drafter_agent.py                   # Writes the initial report based on analysis
│   ├── compliance_agent.py                # Checks report accuracy and logical consistency
│   ├── data_visualization_reporting_agent.py # Creates visual reports summarizing findings
│   ├── user_feedback_explanation_agent.py # Provides clear explanations and feedback to users
│   └── followup_agent.py                  # Handles user follow-up questions and additional research
└── main.py                                # Entry point of the application
```

## Software Flow

MisinformationBot follows a structured flow to analyze and verify claims:

1. **User Input:** 
   - User submits a claim via the web interface.
   
2. **Clarification Agent:** 
   - Rephrases the claim for clarity and neutrality.
   - Generates arguments for and against the claim.

3. **Cognitive Reasoning Agent:** 
   - Develops a structured thought process incorporating various reasoning methods.

4. **Claim Decomposition Agent:** 
   - Breaks down the claim into smaller, verifiable sub-claims.

5. **Question Generation Agent:** 
   - Creates research questions for each sub-claim.

6. **Research Agent:** 
   - Conducts research using Tavily and Data.gov APIs.

7. **Analyst Agent:** 
   - Evaluates research data to assess the claim's truthfulness.

8. **Argumentation Mining Agent:** 
   - Analyzes the strength and weaknesses of arguments from research data.

9. **Drafter Agent:** 
   - Compiles a comprehensive report summarizing the analysis.

10. **Objectivity Agent:** 
    - Reviews the draft report for bias and objectivity.

11. **Data Visualization & Reporting Agent:** 
    - Generates visualizations to represent findings.

12. **User Feedback & Explanation Agent:** 
    - Provides a final summary and user-friendly explanations.

13. **Follow-up Agent (Optional):** 
    - Addresses additional user questions using stored data and further research.

## Important Notes

- **Reliability:** MisinformationBot relies on available data and current technology limitations. It may not always be perfect.
- **Bias:** There might be inherent biases based on the tools and data sources used.
- **Research Quality:** The accuracy of the analysis depends on the quality and availability of information.
- **Usage Caution:** This tool is intended for educational and exploratory purposes. Do not use it as the sole source of information for critical decisions. Always verify information through multiple sources.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the Repository**
2. **Create a New Branch:** `git checkout -b feature/YourFeature`
3. **Commit Your Changes:** `git commit -m 'Add some feature'`
4. **Push to the Branch:** `git push origin feature/YourFeature`
5. **Open a Pull Request**

Please ensure your code follows the project's coding standards and includes appropriate documentation.

## License

This project is licensed under the [MIT License](LICENSE).

---

*Disclaimer: MisinformationBot is a tool designed to assist in identifying misinformation. It should not be solely relied upon for making important decisions. Always consult multiple sources and use critical thinking when evaluating information.*