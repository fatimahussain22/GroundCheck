# GroundCheck — Source-Grounded LLM Answer Evaluator

A small, reproducible **AI engineering portfolio experiment** for checking whether answers are supported by a source passage. Built with Python, Streamlit and the Anthropic Claude API. Includes an offline baseline and a manually labeled synthetic dataset.

> **Scope:** GroundCheck evaluates *groundedness*, not universal factual truth. It is experimental and must not be used for high-stakes decisions.

## Quick start (Windows PowerShell + VS Code)

1. Extract the ZIP and open the `GroundCheck` folder in VS Code.
2. Open **Terminal → New Terminal** and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If activation is blocked, use `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe -m streamlit run app.py` instead.

3. Copy `.env.example` to `.env`:

```powershell
Copy-Item .env.example .env
```

4. Edit `.env` in VS Code. Replace `your_api_key_here` with **your own Anthropic API key**. Choose a `CLAUDE_MODEL` ID enabled for your Anthropic account (the example may need updating). **Never commit or share `.env`.**
5. Start the app:

```powershell
streamlit run app.py
```

The terminal will display a local URL, commonly `http://localhost:8501`. Open it in your browser.

## Try it without spending API credits

- In **Check an answer**, select **Offline lexical baseline**. The default example deliberately contains a wrong leave allowance.
- In **Benchmark**, select **Offline lexical baseline (free)** and run the sample dataset.
- The offline baseline is deliberately weak: word overlap does not detect all false claims. Do not present its scores as Claude's performance.

## Try it with Claude

- In **Check an answer**, select **Claude evidence-based judge** and click **Evaluate answer**.
- Optionally select **Generate with Claude** to create a source-grounded answer before evaluating it.
- In **Benchmark**, choose **Claude judge** and start with five rows to control costs. Every row makes an API call. The app displays failures rather than silently inventing results.

**Billing:** A ChatGPT subscription does not include Anthropic API credits. Check the Anthropic Console for available balance and current model IDs. This project never needs you to paste an API key into a chat.

## Project layout

```text
GroundCheck/
  app.py                   Streamlit user interface
  groundcheck/core.py      Labels, JSON parsing, quote checks, metrics, weak baseline
  groundcheck/claude_client.py  Claude generation and judging
  groundcheck/documents.py TXT/PDF extraction and limits
  data/benchmark.csv       20 synthetic, manually labeled cases
  tests/test_core.py       Unit tests
  .env.example             Safe example configuration
  .gitignore               Excludes credentials and local files
  requirements.txt         Python dependencies
```

## Labels

- **supported** — all substantive factual claims are supported by the source, or the answer correctly refuses to invent missing information.
- **unsupported** — at least one substantive factual claim contradicts or invents information relative to the source.
- **insufficient_evidence** — the answer has no verifiable factual claim or available evidence is too limited to classify confidently, without a clear unsupported specific claim.

The judge may misapply these rules; manually inspect disagreements.

## Metrics

The benchmark treats `unsupported` as the **positive** class. It reports accuracy, precision, recall, F1, and TP/FP/FN/TN. The third class is treated as negative for these binary metrics. Failed API calls are excluded and counted separately. Do not publish scores without specifying the sample size, model, dataset, and method.

## Testing

```powershell
python -m pytest -q
```

## Security and limitations

- Only use **public or synthetic documents**. Claude calls send source passages and answers to Anthropic.
- Never upload real bank policies, private employee data, internal code, or other confidential material without explicit permission.
- Do not publish `.env`, screenshots containing secrets, or unredacted documents.
- The model judge can be biased or inaccurate. Quote matching checks presence, not logical entailment.
- Only the first 15,000 characters of text are evaluated. Text-based PDFs only; scanned PDFs require OCR.
- A 20-row synthetic dataset is not a rigorous benchmark. Expand it and add independent human labels before making performance claims.
- This prototype does not include production authentication, rate limiting, or cost quotas. Run it locally.

## Suggested next steps

1. Add 100+ diverse human-labeled examples, including difficult paraphrases and conflicting facts.
2. Compare baseline and Claude judge on exactly the same test set.
3. Analyze every false positive and false negative.
4. Record model ID, prompt version, date, and approximate API cost.
5. Publish a short, honest LinkedIn case study with **measured** results, not invented numbers.

## License

MIT — see LICENSE.
