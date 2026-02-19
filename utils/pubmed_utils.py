# ==========================================
# PubMed utilities (NCBI E-utilities)
# - keyword suggester per study type
# - PubMed search (esearch) and details (efetch)
# - returns abstracts + clickable PubMed URLs
# ==========================================
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import time
import xml.etree.ElementTree as ET

import requests


@dataclass
class PubMedArticle:
    pmid: str
    title: str = ""
    journal: str = ""
    year: str = ""
    authors: str = ""
    doi: str = ""
    abstract: str = ""
    url: str = ""


EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _safe_text(node: Optional[ET.Element]) -> str:
    if node is None:
        return ""
    return "".join(node.itertext()).strip()


def build_pubmed_query(study_type: str, outcome: str = "", population: str = "", extra: str = "") -> str:
    """
    Lightweight keyword suggester. Expand/override in each study page if needed.
    """
    outcome = (outcome or "").strip()
    population = (population or "").strip()
    extra = (extra or "").strip()

    base = []
    if study_type == "One-Sample Mean":
        base += ["standard deviation", "mean", "baseline", "pilot", "reference value"]
    elif study_type == "Two Independent Means":
        base += ["standard deviation", "pooled", "mean difference", "randomized trial"]
    elif study_type == "Paired Mean":
        base += ["standard deviation", "within-subject", "paired", "pre post"]
    elif study_type == "ANOVA (One-way)":
        base += ["standard deviation", "group means", "one-way ANOVA"]
    elif study_type == "One Proportion":
        base += ["prevalence", "event rate", "proportion"]
    elif study_type == "Two Proportions":
        base += ["event rate", "risk difference", "incidence"]
    elif study_type == "Correlation":
        base += ["correlation", "pearson", "r value"]
    elif study_type == "Logistic Regression":
        base += ["odds ratio", "event rate", "logistic regression", "sample size"]
    elif study_type == "Survival (Log-Rank)":
        base += ["hazard ratio", "event rate", "log-rank", "survival"]
    else:
        base += ["effect size", "standard deviation", "pilot"]

    if population:
        base.insert(0, population)
    if outcome:
        base.insert(0, outcome)
    if extra:
        base.append(extra)

    return " ".join([t for t in base if t]).strip()


def search_pubmed(query: str, retmax: int = 20, sort: str = "relevance", api_key: Optional[str] = None) -> List[str]:
    """
    Search PubMed and return list of PMIDs.

    - retmax capped at 100 for safety
    - Supports optional API key
    """

    # Safety cap
    retmax = min(int(retmax), 100)

    params = {
        "db": "pubmed",
        "term": query,
        "retmax": retmax,
        "sort": sort,
        "retmode": "json"
    }

    if api_key:
        params["api_key"] = api_key

    r = requests.get(f"{EUTILS_BASE}/esearch.fcgi", params=params, timeout=30)
    r.raise_for_status()

    data = r.json()
    return data.get("esearchresult", {}).get("idlist", []) or []
    params = {"db": "pubmed", "term": query, "retmax": int(retmax), "sort": sort, "retmode": "json"}
    if api_key:
        params["api_key"] = api_key
    r = requests.get(f"{EUTILS_BASE}/esearch.fcgi", params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("esearchresult", {}).get("idlist", []) or []


def fetch_pubmed_details(pmids: List[str], api_key: Optional[str] = None) -> List[PubMedArticle]:
    if not pmids:
        return []
    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}
    if api_key:
        params["api_key"] = api_key
    r = requests.get(f"{EUTILS_BASE}/efetch.fcgi", params=params, timeout=60)
    r.raise_for_status()

    root = ET.fromstring(r.text)
    out: List[PubMedArticle] = []

    for article in root.findall(".//PubmedArticle"):
        pmid = _safe_text(article.find(".//PMID"))
        title = _safe_text(article.find(".//ArticleTitle"))
        journal = _safe_text(article.find(".//Journal/Title"))
        year = _safe_text(article.find(".//PubDate/Year")) or _safe_text(article.find(".//PubDate/MedlineDate"))[:4]

        auth_list = []
        for a in article.findall(".//AuthorList/Author"):
            last = _safe_text(a.find("LastName"))
            fore = _safe_text(a.find("ForeName"))
            coll = _safe_text(a.find("CollectiveName"))
            if coll:
                auth_list.append(coll)
            else:
                nm = (fore + " " + last).strip()
                if nm:
                    auth_list.append(nm)
        authors = ", ".join(auth_list[:8]) + (" et al." if len(auth_list) > 8 else "")

        doi = ""
        for aid in article.findall(".//ArticleIdList/ArticleId"):
            if aid.attrib.get("IdType") == "doi":
                doi = _safe_text(aid)
                break

        abs_parts = []
        for abs_node in article.findall(".//Abstract/AbstractText"):
            label = abs_node.attrib.get("Label")
            txt = _safe_text(abs_node)
            if label and txt:
                abs_parts.append(f"{label}: {txt}")
            elif txt:
                abs_parts.append(txt)
        abstract = "\n\n".join(abs_parts)

        url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""

        out.append(PubMedArticle(
            pmid=pmid, title=title, journal=journal, year=year,
            authors=authors, doi=doi, abstract=abstract, url=url
        ))
    return out


def throttle_sleep(n_calls: int = 1, api_key: Optional[str] = None):
    # conservative throttling
    time.sleep((0.12 if api_key else 0.35) * n_calls)
