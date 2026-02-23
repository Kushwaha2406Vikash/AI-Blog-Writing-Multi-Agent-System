from __future__ import annotations
from typing import List,Optional  
from datetime import date,datetime,timedelta 
from langchain_core.messages import HumanMessage,SystemMessage 
from core.state import State 
from schemas.EvidenceSchema import EvidenceItem,EvidencePack 
import re 
from langchain_tavily import TavilySearch 
from core.llm import get_llm 
from langsmith  import traceable

llm = get_llm()




 #-----------------------------
# 4) Research (Tavily)
# -----------------------------
"""
@traceable(name="Tavily_Node")
def _tavily_search(query: str, max_results: int = 5) -> List[dict]:

    Uses TavilySearch if installed and TAVILY_API_KEY is set.
    Returns list of dict with common fields. Note: published date is often missing.
    
    tool = TavilySearch(max_results=max_results)
    results = tool.invoke({"query": query})
    print("Query Result")
    print(results)

    normalized: List[dict] = []
    for r in results or []:
        normalized.append(
            {
                "title": r.get("Title") or "",
                "url": r.get("url") or "",
                "snippet": r.get("Content") or r.get("snippet") or "",
                "published_at": r.get("published_date") or r.get("published_at"),
                "source": r.get("source"),
            }
        )
    return normalized
"""
@traceable(name="Tavily_Node")
def _tavily_search(query: str, max_results=5):
    tool = TavilySearch(max_results=max_results)
    response = tool.invoke({"query": query})

    raw = response.get("results", [])
    normalized = []

    for r in raw:
        if isinstance(r, dict):
            normalized.append({
                "title": r.get("title",""),
                "url": r.get("url",""),
                "snippet": r.get("content",""),
            })
        else:
            normalized.append({"title":"","url":"","snippet":str(r)})

    return normalized


def _iso_to_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    try:
        return date.fromisoformat(s[:10])
    except Exception:
        return None


RESEARCH_SYSTEM = """You are a research synthesizer for technical writing.

Given raw web search results, produce a deduplicated list of EvidenceItem objects.

Rules:
- Only include items with a non-empty url.
- Prefer relevant + authoritative sources (company blogs, docs, reputable outlets).
- Extract/normalize published_at as ISO (YYYY-MM-DD) if you can infer it from title/snippet.
  If you can't infer a date reliably, set published_at=null (do NOT guess).
- Keep snippets short.
- Deduplicate by URL.
"""
@traceable(name="Research_Node")
def research_node(state: State) -> dict:
    queries = (state.get("queries", []) or [])[:10]
    max_results = 6

    raw_results: List[dict] = []
    for q in queries:
        raw_results.extend(_tavily_search(q, max_results=max_results))

    if not raw_results:
        return {"evidence": []}

    extractor = llm.with_structured_output(EvidencePack)
    pack = extractor.invoke(
        [
            SystemMessage(content=RESEARCH_SYSTEM),
            HumanMessage(
                content=(
                    f"As-of date: {state['as_of']}\n"
                    f"Recency days: {state['recency_days']}\n\n"
                    f"Raw results:\n{raw_results}"
                )
            ),
        ]
    )

    # Deduplicate by URL
    dedup = {}
    for e in pack.evidence:
        if e.url:
            dedup[e.url] = e
    evidence = list(dedup.values())

    # HARD RECENCY FILTER for open_book weekly roundup:
    # keep only items with a parseable ISO date and within the window.
    mode = state.get("mode", "closed_book")
    if mode == "open_book":
        as_of = date.fromisoformat(state["as_of"])
        cutoff = as_of - timedelta(days=int(state["recency_days"]))
        fresh: List[EvidenceItem] = []
        for e in evidence:
            d = _iso_to_date(e.published_at)
            if d and d >= cutoff:
                fresh.append(e)
        evidence = fresh

    return {"evidence": evidence}