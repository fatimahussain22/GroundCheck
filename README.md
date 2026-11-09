# GroundCheck — AI Hallucination Detection & Evidence Verification

GroundCheck is an AI-powered tool that evaluates whether AI-generated answers are supported by the information provided in a source document.

Built with **Python, Streamlit, and Claude Haiku 4.5**, it breaks AI responses into individual claims, checks them against source evidence, and identifies potentially unsupported information.

## Key Features

- **Hallucination Detection:** Identifies claims that are not supported by the provided source material.
- **Claim-Level Verification:** Evaluates individual statements rather than treating the entire answer as a single claim.
- **Evidence-Based Evaluation:** Provides supporting source quotes to explain verification results.
- **AI Answer Generation:** Generates answers from supplied context for evaluation.
- **Document Support:** Accepts source documents for evidence-based checking.
- **Benchmark Evaluation:** Compares verification results against labeled examples and calculates performance metrics.
- **Interactive Dashboard:** Visualizes evaluation results, claim classifications, and session activity.

## How It Works

1. **Provide Evidence:** Upload a document or paste source text.
2. **Enter an Answer:** Supply an AI-generated response or generate one using Claude.
3. **Extract Claims:** GroundCheck identifies the factual claims in the answer.
4. **Verify Evidence:** Each claim is evaluated against the provided source.
5. **Review Results:** The dashboard displays classifications, supporting quotes, and verification details.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive dashboard |
| Claude Haiku 4.5 | AI-powered answer generation and verification |
| Pandas | Benchmark data processing |
| Altair | Data visualization |
| Pytest | Automated testing |

## Getting Started

Clone the repository:

```bash
git clone https://github.com/fatimahussain22/GroundCheck.git
cd GroundCheck
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file using `.env.example` as a reference, and configure your Anthropic API key.

Run the application:

```bash
python -m streamlit run app.py
```

## Project Goal

GroundCheck explores how large language models can be used to evaluate the factual grounding of AI-generated responses. It combines **LLM-based claim verification, evidence retrieval, benchmark evaluation, and interactive visualization** into a practical AI engineering project.