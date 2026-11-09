"""GroundCheck — premium dark analytics interface. Run: python -m streamlit run app.py"""
from __future__ import annotations
import os
from pathlib import Path
import pandas as pd
import streamlit as st
import altair as alt
from dotenv import load_dotenv
from groundcheck.core import naive_baseline, verify_quotes, classification_metrics
from groundcheck.claude_client import evaluate_answer, generate_answer
from groundcheck.documents import extract_text

ROOT = Path(__file__).parent
load_dotenv(ROOT / '.env')
st.set_page_config(page_title='GroundCheck | AI Reliability Studio', page_icon='◈', layout='wide', initial_sidebar_state='expanded')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root {color-scheme:dark}
html,body,[class*="css"],.stApp {font-family:'DM Sans',sans-serif;color:#e9e9f7}
.stApp {background:radial-gradient(ellipse 70% 45% at 82% -10%,#25183c 0%,transparent 70%),#0c0b17}
.block-container {max-width:1500px;padding:2.1rem 2.8rem 5rem}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif!important;letter-spacing:-.04em!important;color:#f5f3ff!important}
h1 {font-size:2.65rem!important} h2 {font-size:1.5rem!important} h3 {font-size:1.15rem!important}
p, label, .stMarkdown {color:#c3bfd7}
[data-testid="stSidebar"] {background:#121020;border-right:1px solid #28243b}
[data-testid="stSidebar"] .block-container {padding:1.3rem 1rem}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {color:#bdb8d2}
[data-testid="stSidebar"] [role="radiogroup"] {gap:.15rem}
[data-testid="stSidebar"] [data-testid="stRadio"] label {padding:10px 12px;border-radius:10px;background:transparent}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {background:#32254d}
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {color:#fff;font-weight:700}
[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stWidgetLabel"] {display:none}
[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"]>label>div:first-child {display:none}
[data-testid="stHeader"] {background:transparent}
[data-testid="stToolbar"] {visibility:hidden}
.stButton>button,.stDownloadButton>button {border:1px solid #493c65;border-radius:11px;background:#221c34;color:#f3edff;font-weight:700;min-height:42px}
.stButton>button:hover,.stDownloadButton>button:hover {border-color:#aa79ff;color:white;background:#34264e}
.stButton>button[kind="primary"] {border:0;background:linear-gradient(110deg,#ae65fa,#755bf3);color:#fff;box-shadow:0 8px 24px #8b55ef33}
.stTextArea textarea,.stTextInput input,[data-baseweb="select"]>div {background:#191626!important;color:#f4f0ff!important;border:1px solid #36304a!important;border-radius:11px!important}
.stTextArea textarea:focus,.stTextInput input:focus {border-color:#b477ff!important}
[data-testid="stFileUploader"] {background:#181525;border:1px dashed #56476e;border-radius:13px;padding:10px}
[data-testid="stDataFrame"], [data-testid="stCode"] {border:1px solid #342c47;border-radius:12px;overflow:hidden}
[data-testid="stMetric"] {background:#1b172b;border:1px solid #332a4a;border-radius:15px;padding:18px}
[data-testid="stMetricValue"] {color:#f8f4ff}
[data-testid="stMetricLabel"] {color:#b8adc9}
[data-testid="stAlert"] {border-radius:12px}
hr {border-color:#332b45}
.gc-top {display:flex;justify-content:space-between;align-items:center;margin-bottom:26px;gap:12px}
.gc-kicker {color:#ad9cc9;font-size:11px;font-weight:800;letter-spacing:2px;text-transform:uppercase}
.gc-chip {display:inline-block;background:#241d37;border:1px solid #49345f;border-radius:50px;color:#d9c2fc;padding:7px 12px;font-size:11px;font-weight:700}
.gc-hero {background:linear-gradient(115deg,#25183b 0%,#36234d 52%,#492c68 100%);border:1px solid #654483;border-radius:20px;padding:32px 36px;margin-bottom:24px;position:relative;overflow:hidden}
.gc-hero:after {content:'◈';position:absolute;right:35px;top:-60px;font-size:240px;color:#ffffff0a;pointer-events:none}
.gc-hero h1 {margin:6px 0 9px!important;font-size:2.6rem!important}
.gc-hero p {max-width:680px;line-height:1.65;color:#d7c9e8}
.gc-panel {background:#191525;border:1px solid #342c47;border-radius:16px;padding:21px;margin-bottom:15px}
.gc-panel-title {font-size:13px;color:#e8e0f6;font-weight:800;letter-spacing:.15px;margin-bottom:12px}
.gc-stat {background:linear-gradient(140deg,#20192f,#191526);border:1px solid #3a2c50;border-radius:16px;padding:19px 20px;min-height:116px}
.gc-stat-label {font-size:11px;color:#a99cbc;font-weight:700;text-transform:uppercase;letter-spacing:1px}
.gc-stat-num {font:700 31px 'Space Grotesk',sans-serif;color:#fff;margin:8px 0 2px}
.gc-stat-sub {font-size:11px;color:#a79cb9}
.gc-pill {display:inline-block;border-radius:8px;padding:7px 12px;font-size:12px;font-weight:800}
.gc-supported {background:#153d37;color:#7de1bf}
.gc-unsupported {background:#482338;color:#ff9bb7}
.gc-insufficient_evidence {background:#40321e;color:#f8ce84}
.gc-brand {font:700 26px 'Space Grotesk',sans-serif;color:#f8f2ff;letter-spacing:-1px;margin:4px 0 5px}
.gc-brand span {color:#bd7fff}
.gc-sub {color:#978ba9;font-size:11px;letter-spacing:1.4px;text-transform:uppercase}
.gc-divider {height:1px;background:#30283f;margin:19px 0}
.gc-note {color:#a69cb9;font-size:12px;line-height:1.6}
</style>''',unsafe_allow_html=True)

api_ready = bool(os.getenv('ANTHROPIC_API_KEY') and os.getenv('ANTHROPIC_API_KEY') != 'your_api_key_here')
model = os.getenv('CLAUDE_MODEL','Not configured')

with st.sidebar:
    st.markdown('<div class="gc-brand">◈ Ground<span>Check</span></div><div class="gc-sub">AI RELIABILITY STUDIO</div><div class="gc-divider"></div>',unsafe_allow_html=True)
    page = st.radio('Navigation', ['◫  Overview','◇  Answer Lab','▥  Benchmark','◎  Evidence Explorer','◷  Experiments','⚙  Settings'],label_visibility='collapsed')
    st.markdown('<div class="gc-divider"></div><div class="gc-sub">WORKSPACE STATUS</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="gc-panel" style="margin-top:12px;padding:13px"><div style="color:{"#7de1bf" if api_ready else "#ffb5b5"};font-weight:700;font-size:12px">● {"Claude connected" if api_ready else "API not configured"}</div><div class="gc-note" style="margin-top:6px">{model}</div></div>',unsafe_allow_html=True)
    st.caption('GroundCheck · Local workspace')

st.markdown(f'<div class="gc-top"><div class="gc-kicker">WORKSPACE / {page.split("  ",1)[-1].upper()}</div><div class="gc-chip">◉ &nbsp; {"API READY" if api_ready else "OFFLINE MODE"}</div></div>',unsafe_allow_html=True)

if 'check_history' not in st.session_state: st.session_state.check_history=[]
if 'last_result' not in st.session_state: st.session_state.last_result=None
history = st.session_state.check_history
bench = st.session_state.get('benchmark_results')

def panel(title, body):
    st.markdown(f'<div class="gc-panel"><div class="gc-panel-title">{title}</div><div class="gc-note">{body}</div></div>',unsafe_allow_html=True)

def stat(label, value, sub):
    st.markdown(f'<div class="gc-stat"><div class="gc-stat-label">{label}</div><div class="gc-stat-num">{value}</div><div class="gc-stat-sub">{sub}</div></div>',unsafe_allow_html=True)

def show_result(result, source):
    label=result.label
    safe_label=label if label in ('supported','unsupported','insufficient_evidence') else 'insufficient_evidence'
    st.markdown(f'<div class="gc-panel"><div class="gc-panel-title">EVALUATION OUTCOME</div><span class="gc-pill gc-{safe_label}">{label.replace("_"," ").upper()}</span></div>',unsafe_allow_html=True)
    st.write(result.explanation)
    if result.evidence:
        st.markdown('#### Supporting evidence')
        for q in result.evidence: st.code(q,language=None)
    if result.claims:
        st.markdown('#### Claim-level analysis')
        st.dataframe(pd.DataFrame(result.claims),use_container_width=True,hide_index=True)
    invalid=verify_quotes(result,source)
    if invalid: st.error('Evidence quote verification failed. Treat this evaluation as unverified.')

if page.startswith('◫'):
    st.markdown('''<div class="gc-hero"><div class="gc-kicker" style="color:#d1b4ff">INTELLIGENCE OVERVIEW</div><h1>Trust is measurable.</h1><p>Inspect generated answers, trace claims back to evidence, and measure model reliability from one focused workspace.</p><span class="gc-chip">◈ &nbsp; Source-grounded evaluation</span></div>''',unsafe_allow_html=True)
    completed=len(history)
    supported=sum(h['label']=='supported' for h in history)
    unsupported=sum(h['label']=='unsupported' for h in history)
    c1,c2,c3,c4=st.columns(4)
    with c1: stat('Answers checked',str(completed),'Current browser session')
    with c2: stat('Supported',str(supported),'Source-backed claims')
    with c3: stat('Unsupported',str(unsupported),'Flagged inconsistencies')
    with c4:
        if bench is not None and len(bench.dropna(subset=['predicted'])):
            valid=bench.dropna(subset=['predicted']); score=classification_metrics(valid.gold.tolist(),valid.predicted.tolist())['accuracy']; stat('Benchmark accuracy',f'{score:.0%}',f'{len(valid)} completed samples')
        else: stat('Benchmark accuracy','—','Run a benchmark to populate')
    left,right=st.columns([1.65,1],gap='large')
    with left:
        st.markdown('### Evaluation activity')
        if history:
            chart=pd.DataFrame(history).assign(run=lambda d:range(1,len(d)+1))
            counts=chart.groupby(['run','label']).size().reset_index(name='count')
            st.altair_chart(alt.Chart(counts).mark_bar(cornerRadiusTopLeft=4,cornerRadiusTopRight=4).encode(x=alt.X('run:O',title='Check number'),y=alt.Y('count:Q',title='Checks'),color=alt.Color('label:N',scale=alt.Scale(domain=['supported','unsupported','insufficient_evidence'],range=['#7de1bf','#ff83ac','#efc67a']),legend=alt.Legend(title=None))).properties(height=260).configure_view(strokeOpacity=0),use_container_width=True)
        else:
            panel('AWAITING FIRST EVALUATION','Run an answer check in Answer Lab to populate real activity data. No sample results are being presented as actual measurements.')
    with right:
        st.markdown('### Claim distribution')
        if history:
            dist=pd.DataFrame(history).groupby('label').size().reset_index(name='count')
            st.altair_chart(alt.Chart(dist).mark_arc(innerRadius=65,outerRadius=105).encode(theta='count:Q',color=alt.Color('label:N',scale=alt.Scale(domain=['supported','unsupported','insufficient_evidence'],range=['#7de1bf','#ff83ac','#efc67a']),legend=alt.Legend(title=None))).properties(height=260),use_container_width=True)
        else: panel('NO DATA YET','The chart will appear after your first check.')
    st.markdown('### Recent evaluations')
    if history: st.dataframe(pd.DataFrame(history[::-1]),use_container_width=True,hide_index=True)
    else: panel('READY WHEN YOU ARE','Navigate to Answer Lab to evaluate your first answer.')

elif page.startswith('◇'):
    st.markdown('''<div class="gc-hero"><div class="gc-kicker" style="color:#d1b4ff">EVIDENCE WORKSPACE</div><h1>Answer Lab</h1><p>Challenge an answer with a source passage. Get a verdict, evidence quotes, and claim-level analysis.</p></div>''',unsafe_allow_html=True)
    left,right=st.columns([1.12,.88],gap='large')
    with left:
        st.markdown('### 01 / Source material')
        upload=st.file_uploader('Upload TXT or text-based PDF (max 5 MB)',type=['txt','pdf'])
        default_source='Employees receive 20 days of annual leave per year. Remote work requires manager approval.'
        if upload:
            try: source_default=extract_text(upload.name,upload.getvalue())
            except Exception as exc: st.error(f'Document could not be read: {exc}');source_default=default_source
        else: source_default=default_source
        source=st.text_area('Source passage',value=source_default,height=210)
        question=st.text_input('Question','How many days of annual leave are offered?')
    with right:
        st.markdown('### 02 / Answer to verify')
        mode=st.radio('Answer mode',['Write or paste an answer','Generate with Claude'])
        if mode=='Generate with Claude':
            if st.button('Generate answer with Claude'):
                try:
                    with st.spinner('Generating answer...'): st.session_state.generated_answer=generate_answer(source[:15000],question)
                except Exception as exc: st.error(f'Generation failed: {exc}')
            answer=st.text_area('Generated answer (editable)',value=st.session_state.get('generated_answer',''),height=130)
        else: answer=st.text_area('Answer to evaluate','Employees receive 25 days of annual leave.',height=130)
        judge=st.radio('Evaluation method',['Claude evidence-based judge','Offline lexical baseline'])
        evaluate=st.button('◈  Evaluate answer',type='primary',use_container_width=True)
    if evaluate:
        if not all(x.strip() for x in (source,question,answer)): st.error('Source, question, and answer are required.')
        else:
            try:
                with st.spinner('Evaluating claims against evidence...'):
                    result=evaluate_answer(source[:15000],question,answer) if judge.startswith('Claude') else naive_baseline(source,answer)
                st.session_state.last_result=(result,source)
                st.session_state.check_history.append({'question':question[:110],'label':result.label,'method':judge,'answer':answer[:140]})
            except Exception as exc: st.error(f'Evaluation failed: {exc}')
    if st.session_state.last_result:
        st.markdown('### 03 / Verification report')
        show_result(*st.session_state.last_result)
        if judge.startswith('Offline'): st.info('The offline baseline only checks word overlap. It cannot establish factual correctness.')

elif page.startswith('▥'):
    st.markdown('''<div class="gc-hero"><div class="gc-kicker" style="color:#d1b4ff">MEASURE PERFORMANCE</div><h1>Benchmark</h1><p>Compare model predictions with manually labeled examples and inspect the resulting errors.</p></div>''',unsafe_allow_html=True)
    df=pd.read_csv(ROOT/'data'/'benchmark.csv')
    st.markdown('### Evaluation setup')
    st.caption('Included dataset: 20 synthetic, manually labeled examples. This is a demonstration dataset, not a representative real-world benchmark.')
    method=st.radio('Method',['Offline lexical baseline (free)','Claude judge (API charges)'],horizontal=True)
    max_rows=st.slider('Number of samples',5,len(df),10,1)
    if st.button('◈  Run benchmark',type='primary'):
        rows=[];progress=st.progress(0)
        for i,(_,row) in enumerate(df.head(max_rows).iterrows()):
            try:
                result=evaluate_answer(row.source,row.question,row.answer) if method.startswith('Claude') else naive_baseline(row.source,row.answer)
                invalid=verify_quotes(result,row.source)
                predicted=result.label if not invalid else 'insufficient_evidence'
                rows.append({'id':row.id,'gold':row.gold_label,'predicted':predicted,'correct':row.gold_label==predicted,'quote_warning':bool(invalid),'error':''})
            except Exception as exc:
                rows.append({'id':row.id,'gold':row.gold_label,'predicted':None,'correct':False,'quote_warning':False,'error':str(exc)})
            progress.progress((i+1)/max_rows)
        st.session_state.benchmark_results=pd.DataFrame(rows)
    results=st.session_state.get('benchmark_results')
    if results is not None:
        valid=results.dropna(subset=['predicted'])
        if len(valid):
            metrics=classification_metrics(valid.gold.tolist(),valid.predicted.tolist())
            a,b,c,d=st.columns(4)
            for col,key in zip([a,b,c,d],['accuracy','precision','recall','f1']):
                with col: stat(key.upper(),f'{metrics[key]:.0%}',f'{len(valid)} completed samples')
            st.markdown('### Error breakdown')
            errors=pd.DataFrame([{'Outcome':'True positive','Count':metrics['tp']},{'Outcome':'False positive','Count':metrics['fp']},{'Outcome':'False negative','Count':metrics['fn']},{'Outcome':'True negative','Count':metrics['tn']}])
            st.altair_chart(alt.Chart(errors).mark_bar(cornerRadiusEnd=5).encode(x=alt.X('Count:Q'),y=alt.Y('Outcome:N',sort=None),color=alt.Color('Outcome:N',scale=alt.Scale(range=['#a56cf6','#ff8db4','#f6c87e','#6ad4c1']),legend=None)).properties(height=220),use_container_width=True)
            st.caption(f'Positive class: unsupported. {len(results)-len(valid)} failed API calls excluded from metrics.')
        st.dataframe(results,use_container_width=True,hide_index=True)
        st.download_button('Download benchmark CSV',results.to_csv(index=False).encode(),'groundcheck_results.csv','text/csv')
    with st.expander('View labeled dataset'): st.dataframe(df,use_container_width=True,hide_index=True)

elif page.startswith('◎'):
    st.markdown('''<div class="gc-hero"><div class="gc-kicker" style="color:#d1b4ff">TRACE THE EVIDENCE</div><h1>Evidence Explorer</h1><p>Inspect the latest verification outcome and trace individual claims to their source passages.</p></div>''',unsafe_allow_html=True)
    if st.session_state.last_result:
        result,source=st.session_state.last_result
        left,right=st.columns([1,1],gap='large')
        with left:
            st.markdown('### Original source')
            st.text_area('Source snapshot',source,height=320,disabled=True)
        with right:
            st.markdown('### Claim verification')
            show_result(result,source)
    else: panel('NO VERIFICATION SELECTED','Run a check in Answer Lab to see its evidence here. This page uses real session results, not fabricated data.')

elif page.startswith('◷'):
    st.markdown('''<div class="gc-hero"><div class="gc-kicker" style="color:#d1b4ff">EXPERIMENTAL WORKSPACE</div><h1>Experiments</h1><p>Explore upcoming research capabilities. Preview components below are UI concepts, not completed experiments.</p><span class="gc-chip">DESIGN PREVIEW · NOT IMPLEMENTED</span></div>''',unsafe_allow_html=True)
    a,b=st.columns(2,gap='large')
    with a:
        panel('MODEL COMPARISON · PLANNED','Compare groundedness judgments across multiple LLMs and investigate disagreements. No comparison results have been collected.')
        st.selectbox('Comparison model (preview only)',['Claude Haiku 4.5','Claude Sonnet (planned)','Another model (planned)'],disabled=True)
    with b:
        panel('PROMPT ROBUSTNESS · PLANNED','Measure how verification changes under paraphrases, contradictory evidence, and missing context. Not yet implemented.')
        st.selectbox('Test suite (preview only)',['Contradiction stress test','Paraphrase challenge','Missing-evidence challenge'],disabled=True)
    st.markdown('### Research roadmap')
    st.dataframe(pd.DataFrame([{'Experiment':'Cross-model agreement','Status':'Planned','Data':'Not collected'},{'Experiment':'Prompt robustness','Status':'Planned','Data':'Not collected'},{'Experiment':'Real-world labeled dataset','Status':'Planned','Data':'Not collected'}]),use_container_width=True,hide_index=True)

else:
    st.markdown('''<div class="gc-hero"><div class="gc-kicker" style="color:#d1b4ff">WORKSPACE CONFIGURATION</div><h1>Settings & methodology</h1><p>Review connection status, data handling, and evaluation limitations.</p></div>''',unsafe_allow_html=True)
    a,b=st.columns(2,gap='large')
    with a:
        panel('API CONNECTION',f'Claude API configured: {"Yes" if api_ready else "No"}. Model: {model}. The API key is never displayed.')
    with b: panel('DATA HANDLING','Only use public or synthetic documents. Text and questions are transmitted to Anthropic when using Claude. API calls may incur charges.')
    st.markdown('### What GroundCheck measures')
    st.write('GroundCheck estimates source-groundedness: whether claims in an answer are supported by supplied text. It does not independently establish that the source is true.')
    st.markdown('### Limitations')
    st.markdown('''- A Claude judge may be wrong or biased, especially when evaluating Claude-generated answers.
- Verbatim evidence quotes are checked for presence, not for logical entailment.
- The synthetic benchmark is small and cannot establish real-world reliability.
- The offline baseline is lexical overlap only and misses paraphrases and contradictions.
- Documents are truncated to 15,000 characters; scanned PDFs are unsupported.
- Source text can contain prompt-injection attempts.
- API calls may cost money and send user-provided text to Anthropic.''')
