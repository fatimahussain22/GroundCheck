import pytest
from groundcheck.core import parse_evaluation, verify_quotes, classification_metrics, naive_baseline
from groundcheck.documents import extract_text

def test_parse_valid():
    r = parse_evaluation('{"label":"supported","explanation":"ok","evidence":["hello world"],"claims":[]}')
    assert r.label == "supported"

def test_parse_invalid():
    with pytest.raises(ValueError):
        parse_evaluation('{"label":"maybe","claims":[],"evidence":[]}')

def test_quote_verification():
    r = parse_evaluation('{"label":"supported","evidence":["Not in source"],"claims":[]}')
    assert verify_quotes(r, "Some other text") == ["Not in source"]

def test_metrics():
    m = classification_metrics(["unsupported", "supported", "unsupported"], ["unsupported", "unsupported", "supported"])
    assert m["tp"] == 1 and m["fp"] == 1 and m["fn"] == 1

def test_text():
    assert extract_text("a.txt", b"hello") == "hello"

def test_baseline():
    assert naive_baseline("employees receive twenty days", "employees receive twenty days").label == "supported"
