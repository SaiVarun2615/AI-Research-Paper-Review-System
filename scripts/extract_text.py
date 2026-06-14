# scripts/extract_text.py

import fitz
import json
import re
from pathlib import Path
from pdf2image import convert_from_path
import pytesseract
from collections import Counter

pytesseract.pytesseract.tesseract_cmd = r"D:\Program Files\Tesseract-OCR\tesseract.exe"

ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = ROOT / "research" / "pdfs"
OUT_DIR = ROOT / "research" / "extracted_text"

OUT_DIR.mkdir(exist_ok=True)

def is_text_meaningful(text: str) -> bool:
    """Check if extracted text has sufficient content"""
    letters = re.findall(r"[A-Za-z]", text)
    return len(letters) > 500

def extract_title_from_pdf(pdf_path):
    """Extract title from PDF metadata or first page"""
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        
        # Try to get title from metadata
        title = metadata.get('title', '')
        if title and len(title.strip()) > 5:
            return title.strip()
        
        # Fallback: get first substantial text from first page
        first_page = doc[0]
        text = first_page.get_text("text")
        
        # Look for title-like patterns (usually at the top, larger font, etc.)
        lines = text.split('\n')[:10]  # Check first 10 lines
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 100 and not line.lower().startswith(('abstract', 'introduction', 'keywords')):
                return line
        
        return pdf_path.stem
    except:
        return pdf_path.stem

def extract_year_from_pdf(pdf_path):
    """Extract publication year from PDF or filename"""
    try:
        doc = fitz.open(pdf_path)
        metadata = doc.metadata
        
        # Try to get year from metadata
        creation_date = metadata.get('creationDate', '')
        if creation_date:
            year_match = re.search(r'(\d{4})', creation_date)
            if year_match:
                return int(year_match.group(1))
        
        # Try to extract from filename
        filename = pdf_path.stem
        year_match = re.search(r'(\d{4})', filename)
        if year_match:
            return int(year_match.group(1))
        
        return 2024  # Default fallback
    except:
        return 2024

def extract_text_from_pdf(pdf_path):
    """Extract full text from PDF with OCR fallback"""
    print(f"📄 Processing {pdf_path.name}")
    
    try:
        doc = fitz.open(pdf_path)
        text = ""

        # Primary extraction using PyMuPDF
        for page_num, page in enumerate(doc):
            page_text = page.get_text("text")
            text += page_text + "\n"
        
        # Check if text is meaningful
        if is_text_meaningful(text):
            char_count = len(text)
            print(f"✅ PyMuPDF extraction successful: {char_count} characters")
            return text.strip(), char_count
        else:
            print("⚠️ Low-quality text → Using OCR fallback")
            text = ""
            
            # OCR fallback
            images = convert_from_path(pdf_path)
            for img in images:
                ocr_text = pytesseract.image_to_string(img)
                text += ocr_text + "\n"
            
            char_count = len(text)
            print(f"✅ OCR extraction completed: {char_count} characters")
            return text.strip(), char_count
            
    except Exception as e:
        print(f"❌ Error processing {pdf_path.name}: {e}")
        return "", 0

def extract_paper_id(pdf_path):
    """Generate unique paper ID from path"""
    return pdf_path.stem.replace(' ', '_').lower()

def main():
    """Main extraction function"""
    print("� Starting PDF text extraction...")
    
    extracted_papers = []
    skipped_files = []
    
    for pdf_path in PDF_DIR.rglob("*.pdf"):
        try:
            # Extract text and metadata
            full_text, char_count = extract_text_from_pdf(pdf_path)
            
            # Skip very short documents
            if char_count < 500:
                print(f"⚠️ Skipping {pdf_path.name}: Too short ({char_count} chars)")
                skipped_files.append(pdf_path.name)
                continue
            
            # Extract metadata
            title = extract_title_from_pdf(pdf_path)
            year = extract_year_from_pdf(pdf_path)
            paper_id = extract_paper_id(pdf_path)
            
            # Create structured data
            paper_data = {
                "paper_id": paper_id,
                "title": title,
                "year": year,
                "text": full_text,
                "char_count": char_count,
                "source_file": str(pdf_path.relative_to(ROOT))
            }
            
            # Save individual paper JSON
            out_file = OUT_DIR / f"{paper_id}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(paper_data, f, indent=2, ensure_ascii=False)
            
            extracted_papers.append(paper_data)
            print(f"✅ Saved: {paper_id}.json ({char_count} chars)")
            
        except Exception as e:
            print(f"❌ Failed to process {pdf_path.name}: {e}")
            skipped_files.append(pdf_path.name)
    
    # Save summary
    summary = {
        "total_processed": len(extracted_papers),
        "skipped_files": skipped_files,
        "total_characters": sum(p["char_count"] for p in extracted_papers),
        "papers": extracted_papers
    }
    
    summary_file = OUT_DIR / "extraction_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Extraction Summary:")
    print(f"   ✅ Successfully processed: {len(extracted_papers)} papers")
    print(f"   ⚠️ Skipped files: {len(skipped_files)}")
    print(f"   📝 Total characters extracted: {summary['total_characters']:,}")
    print(f"   📁 Output saved to: {OUT_DIR}")

if __name__ == "__main__":
    main()
