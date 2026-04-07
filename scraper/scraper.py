"""
SHL Product Catalog Scraper
Scrapes Individual Test Solutions from SHL's product catalog
"""

import json
import os
import re
import time
import warnings
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag
from tqdm import tqdm

warnings.filterwarnings("ignore")

# Test type code mapping
TEST_TYPE_MAP = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competency Assessment",
    "D": "Development & 360",
    "E": "Assessment Center Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulation",
}


def parse_test_type_codes(code_str: str) -> List[str]:
    """Convert test type code string like 'ABKP' into descriptive list."""
    if not code_str or code_str in ("Type not specified", "Not found"):
        return ["Unknown"]
    types = []
    for char in code_str.strip().upper():
        if char in TEST_TYPE_MAP:
            mapped = TEST_TYPE_MAP[char]
            if mapped not in types:
                types.append(mapped)
    return types if types else ["Unknown"]


def parse_duration(duration_str: str) -> Optional[int]:
    """Extract integer minutes from duration string."""
    if not duration_str or duration_str == "Duration not specified":
        return None
    numbers = re.findall(r"\d+", str(duration_str))
    if numbers:
        return int(numbers[0])
    return None


def normalize_yes_no(value: str) -> str:
    """Convert emoji indicators to Yes/No strings."""
    value = str(value).strip()
    if "\U0001f7e2" in value or "green" in value.lower() or "yes" in value.lower():
        return "Yes"
    elif "\U0001f534" in value or "red" in value.lower() or "no" in value.lower():
        return "No"
    return "No"


def scrape_shl_catalog(output_path: str = "data/scraped_data.json") -> List[Dict]:
    """
    Scrape the SHL product catalog for Individual Test Solutions.
    
    Returns list of assessment dictionaries with standardized fields.
    """
    BASE_URL = "https://www.shl.com"
    
    # All 32 paginated catalog URLs for type=1 (Individual Test Solutions)
    CATALOG_URLS = [
        "https://www.shl.com/solutions/products/product-catalog/",
    ] + [
        f"https://www.shl.com/solutions/products/product-catalog/?start={i}&type=1&type=1"
        for i in range(12, 384, 12)
    ]
    
    assessments = []
    seen_urls = set()
    
    for tab_num, catalog_url in enumerate(CATALOG_URLS, 1):
        try:
            print(f"\n--- Fetching Page {tab_num}/{len(CATALOG_URLS)} ---")
            catalog_response = requests.get(
                catalog_url,
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15,
            )
            catalog_response.raise_for_status()
            catalog_soup = BeautifulSoup(catalog_response.text, "html.parser")
            
            rows = catalog_soup.select("table tr")[1:]  # Skip header
            print(f"  Found {len(rows)} entries on page {tab_num}")
            
            for i, row in enumerate(rows, 1):
                cols = row.select("td")
                if not cols:
                    continue
                
                link = cols[0].find("a")
                if not link:
                    continue
                
                # Build assessment URL
                assessment_url = urljoin(BASE_URL, link["href"].strip())
                if "solutions/products/product-catalog/solutions/products" in assessment_url:
                    assessment_url = assessment_url.replace(
                        "solutions/products/product-catalog/solutions/products",
                        "solutions/products",
                    )
                
                # Skip duplicates
                if assessment_url in seen_urls:
                    continue
                seen_urls.add(assessment_url)
                
                # Check adaptive support from catalog table
                adaptive_support = "No"
                if len(cols) >= 3:
                    cell_html = str(cols[2]) if len(cols) > 2 else ""
                    if "green" in cell_html.lower() or "\U0001f7e2" in cell_html:
                        adaptive_support = "Yes"
                
                # Check remote support from catalog table
                remote_support = "Yes"  # Default for SHL
                if len(cols) >= 4:
                    cell_html = str(cols[3]) if len(cols) > 3 else ""
                    if "red" in cell_html.lower() or "\U0001f534" in cell_html:
                        remote_support = "No"
                
                try:
                    # Fetch individual assessment page
                    resp = requests.get(
                        assessment_url,
                        headers={"User-Agent": "Mozilla/5.0"},
                        timeout=10,
                    )
                    soup = BeautifulSoup(resp.text, "html.parser")
                    
                    # Extract description
                    description = _extract_description(soup)
                    
                    # Extract duration
                    duration_str = _extract_field(soup, ["assessment length", "duration"])
                    duration = parse_duration(duration_str)
                    
                    # Extract test type
                    test_type_raw = _extract_test_type(soup)
                    test_type = parse_test_type_codes(test_type_raw)
                    
                    assessment = {
                        "name": link.get_text(strip=True),
                        "url": assessment_url,
                        "description": description or "Description unavailable",
                        "duration": duration,
                        "adaptive_support": adaptive_support,
                        "remote_support": remote_support,
                        "test_type": test_type,
                    }
                    
                    assessments.append(assessment)
                    time.sleep(1.0)
                    
                except Exception as e:
                    print(f"  Warning: Failed to scrape {assessment_url}: {e}")
                    assessments.append({
                        "name": link.get_text(strip=True),
                        "url": assessment_url,
                        "description": "Description unavailable",
                        "duration": None,
                        "adaptive_support": adaptive_support,
                        "remote_support": remote_support,
                        "test_type": ["Unknown"],
                    })
            
            time.sleep(1.5)
            
        except Exception as e:
            print(f"  Error on page {tab_num}: {e}")
            continue
    
    print(f"\nTotal scraped: {len(assessments)} unique assessments")
    
    # Save to JSON
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(assessments, f, indent=2, ensure_ascii=False)
    
    print(f"Saved to {output_path}")
    return assessments


def _extract_description(soup: BeautifulSoup) -> str:
    """Extract assessment description using multiple strategies."""
    # Strategy 1: Find heading labeled 'Description'
    heading = soup.find(
        lambda tag: tag.name in ["h1", "h2", "h3", "h4"]
        and tag.get_text(strip=True).lower() == "description"
    )
    if heading:
        parts = []
        elem = heading.find_next()
        while elem and elem.name == "p":
            parts.append(elem.get_text(" ", strip=True))
            elem = elem.find_next()
        if parts:
            return " ".join(parts)
    
    # Strategy 2: Container with description class/id
    for selector in ["#Description", ".Description", ".product-description"]:
        container = soup.select_one(selector)
        if container:
            paragraphs = container.find_all("p")
            text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)
            if text:
                return text
    
    # Strategy 3: Keywords in paragraphs
    keywords = ["entry-level", "position", "candidate", "assessment", "measure", "skill", "solution"]
    for p in soup.find_all("p"):
        text = p.get_text(" ", strip=True)
        if any(kw in text.lower() for kw in keywords) and len(text) > 50:
            # Filter out navigation text
            if not any(nav in text for nav in ["Contact", "Practice Tests", "Login"]):
                return text
    
    return ""


def _extract_field(soup: BeautifulSoup, field_names: List[str]) -> str:
    """Extract a field value by searching for headings matching field names."""
    for heading in soup.find_all(["h2", "h3", "h4"]):
        heading_text = heading.get_text(strip=True).lower()
        if any(name in heading_text for name in field_names):
            sibling = heading.find_next_sibling()
            if sibling:
                return sibling.get_text(strip=True)
    return ""


def _extract_test_type(soup: BeautifulSoup) -> str:
    """Extract test type code from assessment page."""
    element = soup.find(string=lambda x: "Test Type:" in x if x else False)
    if element:
        container = element.parent.find_next("span") or element.find_next_sibling()
        if container:
            return container.get_text(strip=True)
    return ""


def convert_existing_data(
    input_path: str = "data/shl_assessments_complete.json",
    output_path: str = "data/scraped_data.json",
) -> List[Dict]:
    """
    Convert existing scraped data to the new standardized format.
    Used when we already have scraped data and don't need to re-scrape.
    """
    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)
    
    converted = []
    seen_urls = set()
    
    for item in raw_data:
        url = item.get("url", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        
        # Parse duration
        duration = parse_duration(item.get("duration", ""))
        
        # Parse test type codes
        test_type_raw = item.get("test_type", "")
        test_type = parse_test_type_codes(test_type_raw)
        
        # Normalize adaptive/remote support
        adaptive = normalize_yes_no(item.get("adaptive/irt_support", "No"))
        remote = normalize_yes_no(item.get("remote_testing", "Yes"))
        
        # Clean description
        description = item.get("description", "Description unavailable")
        for unwanted in ["Contact", "Practice Tests", "Support", "Login", "Buy Online", "Book a Demo"]:
            description = description.replace(unwanted, "")
        description = description.strip()
        
        converted.append({
            "name": item.get("name", "Unknown"),
            "url": url,
            "description": description if description else "Description unavailable",
            "duration": duration,
            "adaptive_support": adaptive,
            "remote_support": remote,
            "test_type": test_type,
        })
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(converted, f, indent=2, ensure_ascii=False)
    
    print(f"Converted {len(converted)} assessments to standardized format")
    print(f"Saved to {output_path}")
    return converted


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--convert":
        convert_existing_data()
    else:
        scrape_shl_catalog()
