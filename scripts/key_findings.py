# scripts/key_findings.py

import json
import re
from pathlib import Path
from collections import Counter
import string

ROOT = Path(__file__).resolve().parent.parent
IN_DIR = ROOT / "research" / "extracted_text"
OUT_DIR = ROOT / "research" / "analysis"

OUT_DIR.mkdir(exist_ok=True)

def clean_text(text):
    """Clean and normalize text for analysis"""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove punctuation except for important ones
    text = text.translate(str.maketrans('', '', string.punctuation.replace('-', '').replace('_', '')))
    return text.lower().strip()

def extract_keywords(text, top_n=5):
    """Extract top keywords using frequency analysis"""
    # Common academic stop words to filter out
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'being', 'have', 'has',
        'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both',
        'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own',
        'same', 'so', 'than', 'too', 'very', 'just', 'now', 'also', 'paper', 'study',
        'research', 'analysis', 'method', 'approach', 'result', 'conclusion', 'introduction',
        'abstract', 'figure', 'table', 'section', 'chapter', 'article', 'journal', 'proceedings'
    }
    
    # Clean and tokenize
    cleaned_text = clean_text(text)
    words = cleaned_text.split()
    
    # Filter stop words and short words
    filtered_words = [
        word for word in words 
        if len(word) > 3 and word not in stop_words and word.isalpha()
    ]
    
    # Count frequency
    word_freq = Counter(filtered_words)
    
    # Get top keywords
    top_keywords = word_freq.most_common(top_n)
    return [keyword for keyword, count in top_keywords]

def extract_meaningful_sentences(text, top_n=5):
    """Extract the longest, most meaningful sentences"""
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    
    # Clean and filter sentences
    meaningful_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        
        # Filter criteria
        if (len(sentence) > 50 and  # Minimum length
            len(sentence) < 300 and  # Maximum length
            not sentence.lower().startswith(('abstract', 'introduction', 'conclusion', 'references')) and
            not any(word in sentence.lower() for word in ['figure', 'table', 'http', 'www', 'email'])):
            
            meaningful_sentences.append(sentence)
    
    # Sort by length (longer sentences often contain more substance)
    meaningful_sentences.sort(key=len, reverse=True)
    
    return meaningful_sentences[:top_n]

def extract_authors_from_papers_json(paper_title):
    """Extract authors from papers.json if available"""
    try:
        papers_file = ROOT / "research" / "papers.json"
        if papers_file.exists():
            with open(papers_file, 'r', encoding='utf-8') as f:
                papers_data = json.load(f)
            
            # Search through all categories
            for category, papers in papers_data.items():
                for paper in papers:
                    if paper.get('title', '').lower() == paper_title.lower():
                        return paper.get('authors', [])
    except:
        pass
    return []

def calculate_word_count(text):
    """Calculate accurate word count"""
    words = text.split()
    return len(words)

def main():
    """Main key findings extraction function"""
    print("🔍 Starting key findings extraction...")
    
    findings = []
    processed_papers = 0
    skipped_papers = 0
    
    for file_path in IN_DIR.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract text and metadata
            full_text = data.get('text', '')
            title = data.get('title', file_path.stem)
            year = data.get('year', 2024)
            paper_id = data.get('paper_id', file_path.stem)
            
            if not full_text or len(full_text.strip()) < 100:
                print(f"⚠️ Skipping {file_path.name}: Empty or too short text")
                skipped_papers += 1
                continue
            
            # Extract keywords
            keywords = extract_keywords(full_text, top_n=5)
            
            # Extract meaningful sentences
            key_sentences = extract_meaningful_sentences(full_text, top_n=5)
            
            # Extract authors if available
            authors = extract_authors_from_papers_json(title)
            
            # Calculate word count
            word_count = calculate_word_count(full_text)
            
            # Create structured findings
            paper_findings = {
                "paper_id": paper_id,
                "title": title,
                "year": year,
                "authors": authors,
                "keywords": keywords,
                "key_findings": key_sentences,
                "word_count": word_count,
                "char_count": len(full_text),
                "source_file": str(file_path.relative_to(ROOT))
            }
            
            findings.append(paper_findings)
            processed_papers += 1
            
            print(f"✅ Processed: {title[:50]}... ({len(keywords)} keywords, {len(key_sentences)} findings)")
            
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")
            skipped_papers += 1
    
    # Save findings
    output_file = OUT_DIR / "key_findings.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(findings, f, indent=2, ensure_ascii=False)
    
    # Generate summary statistics
    total_words = sum(paper['word_count'] for paper in findings)
    total_chars = sum(paper['char_count'] for paper in findings)
    all_keywords = []
    for paper in findings:
        all_keywords.extend(paper['keywords'])
    keyword_freq = Counter(all_keywords)
    
    summary = {
        "total_papers": processed_papers,
        "skipped_papers": skipped_papers,
        "total_words": total_words,
        "total_characters": total_chars,
        "average_words_per_paper": total_words / processed_papers if processed_papers > 0 else 0,
        "top_keywords_overall": keyword_freq.most_common(10),
        "papers": findings
    }
    
    summary_file = OUT_DIR / "findings_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Key Findings Summary:")
    print(f"   ✅ Successfully processed: {processed_papers} papers")
    print(f"   ⚠️ Skipped papers: {skipped_papers}")
    print(f"   📝 Total words extracted: {total_words:,}")
    print(f"   🔤 Total unique keywords: {len(keyword_freq)}")
    print(f"   📁 Output saved to: {OUT_DIR}")

if __name__ == "__main__":
    main()
