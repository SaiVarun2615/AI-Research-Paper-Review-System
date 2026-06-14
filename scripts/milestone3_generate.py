from pathlib import Path
import json

ROOT = Path(__file__).parent.parent
DRAFTS = ROOT / "research" / "drafts"
PAPERS_FILE = ROOT / "research" / "papers.json"

def load_papers_metadata():
    """Load papers metadata from papers.json"""
    try:
        with open(PAPERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def format_author_name(name):
    """Format author name as 'Last, F.'"""
    if not name or not isinstance(name, str):
        return "Unknown Author"
    
    name_parts = name.strip().split()
    if len(name_parts) >= 2:
        last_name = name_parts[-1]
        first_initial = name_parts[0][0].upper() + "."
        # Handle middle initials if present
        if len(name_parts) > 2:
            middle_initials = " ".join([part[0].upper() + "." for part in name_parts[1:-1]])
            return f"{last_name}, {first_initial} {middle_initials}"
        else:
            return f"{last_name}, {first_initial}"
    else:
        return name

def generate_real_apa_references():
    """Generate real APA references from papers.json metadata"""
    papers_data = load_papers_metadata()
    references = []
    
    if not papers_data:
        print("⚠️ No papers data found in papers.json")
        return ["No references available - no papers data found."]
    
    for category, papers in papers_data.items():
        for paper in papers:
            try:
                # Extract paper information
                title = paper.get('title', 'Unknown Title')
                authors = paper.get('authors', [])
                year = paper.get('year', 'n.d.')
                url = paper.get('url', '')
                
                # Format authors (max 3 as per requirements)
                formatted_authors = []
                for i, author in enumerate(authors[:3]):  # Max 3 authors
                    if isinstance(author, dict):
                        author_name = author.get('name', '')
                    else:
                        author_name = str(author)
                    
                    formatted_author = format_author_name(author_name)
                    if formatted_author and formatted_author != "Unknown Author":
                        formatted_authors.append(formatted_author)
                
                # Handle author formatting
                if not formatted_authors:
                    author_text = "Unknown Author"
                elif len(formatted_authors) == 1:
                    author_text = formatted_authors[0]
                elif len(formatted_authors) == 2:
                    author_text = f"{formatted_authors[0]}, & {formatted_authors[1]}"
                else:
                    author_text = f"{formatted_authors[0]}, {formatted_authors[1]}, & {formatted_authors[2]}"
                
                # Format year
                if year and year != 'n.d.':
                    year_text = f"({year})"
                else:
                    year_text = "(n.d.)"
                
                # Clean title
                title_text = title.strip()
                if title_text.endswith('.'):
                    title_text = title_text[:-1]  # Remove trailing period
                
                # Build APA reference
                if url and url.strip():
                    reference = f"{author_text} {year_text}. {title_text}. Retrieved from {url}"
                else:
                    reference = f"{author_text} {year_text}. {title_text}."
                
                references.append(reference)
                print(f"✅ Generated reference: {reference[:50]}...")
                
            except Exception as e:
                print(f"⚠️ Error processing paper: {e}")
                continue
    
    # Sort references alphabetically by author
    references.sort()
    
    print(f"📚 Generated {len(references)} real APA references")
    return references


# ===============================
# Custom Academic Styles
# ===============================
def create_custom_styles():
    styles = getSampleStyleSheet()

    # Title
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Title'],
        fontSize=20,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=darkblue,
        fontName='Helvetica-Bold'
    ))

    # Section Header
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=18,
        alignment=TA_LEFT,
        textColor=black,
        fontName='Helvetica-Bold'
    ))

    # Abstract Style
    styles.add(ParagraphStyle(
        name='CustomAbstract',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leftIndent=20,
        rightIndent=20,
        fontName='Times-Roman'
    ))

    # Body Style (renamed to avoid conflict)
    styles.add(ParagraphStyle(
        name='CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leftIndent=20,
        rightIndent=20,
        fontName='Times-Roman'
    ))

    # References Style
    styles.add(ParagraphStyle(
        name='CustomReferences',
        parent=styles['Normal'],
        fontSize=10,
        leading=13,
        spaceAfter=6,
        alignment=TA_LEFT,
        leftIndent=25,
        rightIndent=20,
        fontName='Times-Roman'
    ))

    return styles


# ===============================
# Load Section Content
# ===============================
def load_section_content(filename):
    path = DRAFTS / filename
    if not path.exists():
        return []

    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return []

    paragraphs = []
    for para in content.split("\n"):
        para = para.strip()
        if para:
            para = para.replace("—", "-")
            para = para.replace("&", "&amp;")
            para = para.replace("<", "&lt;")
            para = para.replace(">", "&gt;")
            paragraphs.append(para)

    return paragraphs


def run():
    """Generate real APA references and complete the milestone"""
    try:
        print("🔍 Generating real APA references from papers.json...")
        
        # Generate real APA references
        references = generate_real_apa_references()
        
        # Save references to file
        references_file = DRAFTS / "references.txt"
        with open(references_file, "w", encoding="utf-8") as f:
            f.write("\n\n".join(references))
        
        print(f"✅ Generated {len(references)} real APA references")
        print(f"📁 Saved to: {references_file}")
        
        # Show sample of generated references
        if references:
            print("\n📖 Sample references:")
            for i, ref in enumerate(references[:3], 1):
                print(f"   {i}. {ref}")
            if len(references) > 3:
                print(f"   ... and {len(references) - 3} more")
        
        return f"Real APA references generated successfully: {len(references)} entries"
        
    except Exception as e:
        print(f"❌ Error generating references: {e}")
        return f"Error: {e}"


# ===============================
# Build Final Academic PDF
# ===============================
def build_pdf():
    styles = create_custom_styles()
    story = []

    # Title Page
    story.append(Paragraph("Systematic Literature Review", styles['CustomTitle']))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph(
        "An Automated Analysis of Current Research Trends",
        styles['CustomBody']
    ))
    story.append(Spacer(1, 0.5 * inch))

    story.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%B %d, %Y')}",
        styles['CustomBody']
    ))
    story.append(PageBreak())

    # Abstract
    abstract = load_section_content("abstract.txt")
    if abstract:
        story.append(Paragraph("Abstract", styles['SectionHeader']))
        story.append(Spacer(1, 12))

        abstract_text = " ".join(abstract)
        story.append(Paragraph(abstract_text, styles['CustomAbstract']))
        story.append(Spacer(1, 20))

    # Introduction
    story.append(Paragraph("1. Introduction", styles['SectionHeader']))
    story.append(Spacer(1, 12))

    intro_text = (
        "This systematic literature review provides a comprehensive analysis "
        "of current research trends and developments. The rapid advancement "
        "of methodologies and technologies necessitates structured synthesis "
        "to identify patterns, research gaps, and future opportunities."
    )

    story.append(Paragraph(intro_text, styles['CustomBody']))
    story.append(Spacer(1, 20))

    # Methods
    methods = load_section_content("methods.txt")
    if methods:
        story.append(Paragraph("2. Methods", styles['SectionHeader']))
        story.append(Spacer(1, 12))
        for para in methods:
            story.append(Paragraph(para, styles['CustomBody']))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 20))

    # Results
    results = load_section_content("results.txt")
    if results:
        story.append(Paragraph("3. Results", styles['SectionHeader']))
        story.append(Spacer(1, 12))
        for para in results:
            story.append(Paragraph(para, styles['CustomBody']))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 20))

    # Discussion
    discussion = load_section_content("discussion.txt")
    if discussion:
        story.append(Paragraph("4. Discussion", styles['SectionHeader']))
        story.append(Spacer(1, 12))
        for para in discussion:
            story.append(Paragraph(para, styles['CustomBody']))
            story.append(Spacer(1, 6))
        story.append(Spacer(1, 20))

    # References
    references = load_section_content("references.txt")
    if references:
        story.append(Paragraph("5. References", styles['SectionHeader']))
        story.append(Spacer(1, 12))
        for ref in references:
            story.append(Paragraph(ref, styles['CustomReferences']))
            story.append(Spacer(1, 4))

    # Build document
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    doc.build(story)
    return OUT_PDF


if __name__ == "__main__":
    run()
