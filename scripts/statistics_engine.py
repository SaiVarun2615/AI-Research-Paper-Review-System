# scripts/statistics_engine.py

import json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
ANALYSIS_DIR = ROOT / "research" / "analysis"
PAPERS_FILE = ROOT / "research" / "papers.json"

def load_key_findings():
    """Load key findings from analysis"""
    try:
        with open(ANALYSIS_DIR / "key_findings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def load_papers_metadata():
    """Load papers metadata from papers.json"""
    try:
        with open(PAPERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def compute_comprehensive_statistics():
    """Compute comprehensive statistics from extracted data"""
    print("📊 Computing comprehensive statistics...")
    
    # Load data
    findings = load_key_findings()
    papers_metadata = load_papers_metadata()
    
    if not findings:
        print("⚠️ No findings data available")
        return {}
    
    # Basic counts
    total_papers = len(findings)
    total_words = sum(paper.get('word_count', 0) for paper in findings)
    total_characters = sum(paper.get('char_count', 0) for paper in findings)
    
    # Year statistics
    years = [paper.get('year', 2024) for paper in findings]
    average_year = sum(years) / len(years) if years else 2024
    year_distribution = Counter(years)
    
    # Keyword analysis
    all_keywords = []
    for paper in findings:
        keywords = paper.get('keywords', [])
        all_keywords.extend(keywords)
    
    keyword_freq = Counter(all_keywords)
    most_common_keyword = keyword_freq.most_common(1)[0] if keyword_freq else ("None", 0)
    top_5_keywords = keyword_freq.most_common(5)
    
    # Author statistics
    all_authors = []
    for paper in findings:
        authors = paper.get('authors', [])
        for author in authors:
            if isinstance(author, dict):
                author_name = author.get('name', '')
            else:
                author_name = str(author)
            if author_name:
                all_authors.append(author_name)
    
    author_freq = Counter(all_authors)
    top_authors = author_freq.most_common(5)
    
    # Paper length statistics
    word_counts = [paper.get('word_count', 0) for paper in findings]
    avg_words_per_paper = sum(word_counts) / len(word_counts) if word_counts else 0
    max_words = max(word_counts) if word_counts else 0
    min_words = min(word_counts) if word_counts else 0
    
    # Generate publication trend
    sorted_years = sorted(year_distribution.items())
    publication_trend = [{"year": year, "count": count} for year, count in sorted_years]
    
    # Theme extraction based on keyword clustering
    themes = extract_themes_from_keywords(findings)
    
    # Quality metrics
    papers_with_keywords = sum(1 for paper in findings if paper.get('keywords'))
    papers_with_findings = sum(1 for paper in findings if paper.get('key_findings'))
    papers_with_authors = sum(1 for paper in findings if paper.get('authors'))
    
    statistics = {
        "overview": {
            "total_papers_analyzed": total_papers,
            "average_publication_year": round(average_year, 1),
            "most_common_keyword": most_common_keyword[0],
            "most_common_keyword_count": most_common_keyword[1],
            "total_words_corpus": total_words,
            "total_characters_corpus": total_characters,
            "average_words_per_paper": round(avg_words_per_paper, 1),
            "max_words_in_paper": max_words,
            "min_words_in_paper": min_words
        },
        "keywords": {
            "top_5_keywords": top_5_keywords,
            "total_unique_keywords": len(keyword_freq),
            "papers_with_keywords": papers_with_keywords,
            "keyword_coverage": round(papers_with_keywords / total_papers * 100, 1) if total_papers > 0 else 0
        },
        "authors": {
            "total_unique_authors": len(author_freq),
            "top_5_authors": top_authors,
            "papers_with_authors": papers_with_authors,
            "author_coverage": round(papers_with_authors / total_papers * 100, 1) if total_papers > 0 else 0
        },
        "publication_trend": publication_trend,
        "themes": themes,
        "quality_metrics": {
            "papers_with_keywords": papers_with_keywords,
            "papers_with_findings": papers_with_findings,
            "papers_with_authors": papers_with_authors,
            "data_completeness": round((papers_with_keywords + papers_with_findings + papers_with_authors) / (total_papers * 3) * 100, 1)
        },
        "year_distribution": dict(year_distribution)
    }
    
    return statistics

def extract_themes_from_keywords(findings):
    """Extract themes by clustering keywords"""
    # Theme keyword mappings
    theme_keywords = {
        "Machine Learning": ["machine", "learning", "algorithm", "model", "neural", "deep", "ai", "artificial", "intelligence"],
        "Security": ["security", "privacy", "encryption", "authentication", "attack", "vulnerability", "protection"],
        "Blockchain": ["blockchain", "bitcoin", "cryptocurrency", "distributed", "ledger", "smart", "contract"],
        "Data Science": ["data", "analytics", "mining", "big", "visualization", "statistics", "analysis"],
        "Cloud Computing": ["cloud", "computing", "virtualization", "container", "microservice", "serverless"],
        "Internet of Things": ["iot", "sensor", "device", "embedded", "wireless", "rfid", "smart"],
        "Software Engineering": ["software", "development", "testing", "quality", "maintenance", "agile", "devops"],
        "Network Systems": ["network", "protocol", "routing", "topology", "bandwidth", "latency", "packet"],
        "Human-Computer Interaction": ["user", "interface", "interaction", "ux", "design", "usability", "experience"],
        "Performance Optimization": ["performance", "optimization", "efficiency", "speed", "throughput", "scalability"]
    }
    
    theme_counts = defaultdict(int)
    theme_papers = defaultdict(list)
    
    for paper in findings:
        paper_keywords = [kw.lower() for kw in paper.get('keywords', [])]
        paper_themes = set()
        
        for theme, theme_words in theme_keywords.items():
            if any(theme_word in ' '.join(paper_keywords) for theme_word in theme_words):
                paper_themes.add(theme)
        
        # If no theme matches, try to assign based on individual keywords
        if not paper_themes:
            for keyword in paper_keywords:
                for theme, theme_words in theme_keywords.items():
                    if any(theme_word in keyword for theme_word in theme_words):
                        paper_themes.add(theme)
                        break
        
        # Count themes
        for theme in paper_themes:
            theme_counts[theme] += 1
            theme_papers[theme].append(paper.get('title', 'Unknown'))
    
    # Sort themes by count
    sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
    
    themes = []
    for theme_name, count in sorted_themes:
        themes.append({
            "name": theme_name,
            "count": count,
            "percentage": round(count / len(findings) * 100, 1) if findings else 0,
            "sample_papers": theme_papers[theme_name][:3]  # First 3 papers as examples
        })
    
    return themes

def generate_statistics_summary_text(statistics):
    """Generate human-readable summary of statistics"""
    if not statistics:
        return "No statistics available."
    
    overview = statistics.get('overview', {})
    keywords = statistics.get('keywords', {})
    themes = statistics.get('themes', [])
    
    summary = f"""This systematic literature review analyzed {overview.get('total_papers_analyzed', 0)} research papers published between {min(statistics.get('year_distribution', {}).keys())} and {max(statistics.get('year_distribution', {}).keys())}. The corpus contains {overview.get('total_words_corpus', 0):,} words with an average of {overview.get('average_words_per_paper', 0):.1f} words per paper.

The most prominent keyword in the literature is "{overview.get('most_common_keyword', 'N/A')}" appearing {overview.get('most_common_keyword_count', 0)} times across the analyzed papers. The top five keywords overall are: {', '.join([f"{kw} ({count})" for kw, count in keywords.get('top_5_keywords', [])])}.

Thematic analysis reveals {len(themes)} major research themes. The dominant theme is "{themes[0]['name'] if themes else 'N/A'}" appearing in {themes[0]['count'] if themes else 0} papers ({themes[0]['percentage'] if themes else 0}% of the corpus). Other significant themes include {', '.join([f"{theme['name']} ({theme['count']})" for theme in themes[1:4]])}.

The average publication year is {overview.get('average_publication_year', 0):.1f}, indicating relatively recent research activity in this domain. The data completeness score is {statistics.get('quality_metrics', {}).get('data_completeness', 0):.1f}%, suggesting high-quality extraction and analysis."""
    
    return summary

def save_statistics():
    """Save comprehensive statistics to file"""
    statistics = compute_comprehensive_statistics()
    
    if statistics:
        # Save detailed statistics
        stats_file = ANALYSIS_DIR / "comprehensive_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(statistics, f, indent=2, ensure_ascii=False)
        
        # Save summary text
        summary_text = generate_statistics_summary_text(statistics)
        summary_file = ANALYSIS_DIR / "statistics_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        
        print(f"✅ Statistics saved to {ANALYSIS_DIR}")
        return statistics
    else:
        print("❌ No statistics to save")
        return {}

if __name__ == "__main__":
    stats = save_statistics()
    if stats:
        print("\n📈 Quick Statistics Overview:")
        overview = stats.get('overview', {})
        print(f"   Papers analyzed: {overview.get('total_papers_analyzed', 0)}")
        print(f"   Average year: {overview.get('average_publication_year', 0):.1f}")
        print(f"   Total words: {overview.get('total_words_corpus', 0):,}")
        print(f"   Top keyword: {overview.get('most_common_keyword', 'N/A')}")
