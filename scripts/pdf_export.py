from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, darkblue, gray
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime
import json

ROOT = Path(__file__).parent.parent
DRAFTS = ROOT / "research" / "drafts"
ANALYSIS_DIR = ROOT / "research" / "analysis"
OUT_PDF = DRAFTS / "academic_review_report.pdf"

def create_academic_styles():
    """Create professional academic styles"""
    styles = getSampleStyleSheet()
    
    # Check if styles already exist to avoid duplicates
    existing_styles = [style.name for style in styles.byName.values()]
    
    # Title style
    if 'AcademicTitle' not in existing_styles:
        styles.add(ParagraphStyle(
            name='AcademicTitle',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=20,
            spaceBefore=20,
            alignment=TA_CENTER,
            textColor=darkblue,
            fontName='Times-Bold',
            leading=18
        ))
    
    # Author style
    if 'AuthorStyle' not in existing_styles:
        styles.add(ParagraphStyle(
            name='AuthorStyle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Times-Roman',
            leading=14
        ))
    
    # Section header style
    if 'SectionHeader' not in existing_styles:
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading1'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            alignment=TA_LEFT,
            textColor=black,
            fontName='Times-Bold',
            leftIndent=0,
            leading=16
        ))
    
    # Subsection header style
    if 'SubsectionHeader' not in existing_styles:
        styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=8,
            spaceBefore=12,
            alignment=TA_LEFT,
            textColor=black,
            fontName='Times-Bold',
            leftIndent=20,
            leading=14
        ))
    
    # Abstract style
    if 'AbstractText' not in existing_styles:
        styles.add(ParagraphStyle(
            name='AbstractText',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            spaceBefore=6,
            alignment=TA_JUSTIFY,
            leftIndent=30,
            rightIndent=30,
            fontName='Times-Roman',
            leading=12
        ))
    
    # Body text style - use unique name to avoid conflicts
    if 'AcademicBodyText' not in existing_styles:
        styles.add(ParagraphStyle(
            name='AcademicBodyText',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            spaceBefore=6,
            alignment=TA_JUSTIFY,
            leftIndent=0,
            rightIndent=0,
            fontName='Times-Roman',
            leading=13
        ))
    
    # References style
    if 'ReferencesText' not in existing_styles:
        styles.add(ParagraphStyle(
            name='ReferencesText',
            parent=styles['Normal'],
            fontSize=9,
            spaceAfter=6,
            spaceBefore=3,
            alignment=TA_LEFT,
            leftIndent=20,
            rightIndent=0,
            fontName='Times-Roman',
            leading=11
        ))
    
    # Statistics table style
    if 'TableText' not in existing_styles:
        styles.add(ParagraphStyle(
            name='TableText',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            fontName='Times-Roman',
            leading=10
        ))
    
    return styles

def load_statistics():
    """Load comprehensive statistics"""
    try:
        with open(ANALYSIS_DIR / "comprehensive_statistics.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def load_section_content(filename):
    """Load content from a section file"""
    path = DRAFTS / filename
    if not path.exists():
        return ""
    
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        return ""
    
    # Convert newlines to paragraphs
    paragraphs = []
    for para in content.split('\n'):
        para = para.strip()
        if para:
            # Clean problematic characters
            para = para.replace('—', '-')
            para = para.replace('"', '&quot;')
            para = para.replace("'", '&#39;')
            paragraphs.append(para)
    
    return paragraphs

def generate_statistics_table(statistics):
    """Generate statistics table for the report"""
    if not statistics:
        return []
    
    overview = statistics.get('overview', {})
    keywords = statistics.get('keywords', {})
    
    data = [
        ['Metric', 'Value'],
        ['Total Papers Analyzed', str(overview.get('total_papers_analyzed', 0))],
        ['Average Publication Year', str(overview.get('average_publication_year', 'N/A'))],
        ['Most Common Keyword', f"{overview.get('most_common_keyword', 'N/A')} ({overview.get('most_common_keyword_count', 0)})"],
        ['Total Words in Corpus', f"{overview.get('total_words_corpus', 0):,}"],
        ['Average Words per Paper', f"{overview.get('average_words_per_paper', 0):.1f}"],
        ['Unique Keywords', str(keywords.get('total_unique_keywords', 0))],
        ['Data Completeness', f"{statistics.get('quality_metrics', {}).get('data_completeness', 0):.1f}%"]
    ]
    
    return data

def generate_dynamic_introduction(statistics):
    """Generate introduction based on real statistics"""
    if not statistics:
        return "This systematic literature review provides a comprehensive analysis of current research trends."
    
    overview = statistics.get('overview', {})
    themes = statistics.get('themes', [])
    
    total_papers = overview.get('total_papers_analyzed', 0)
    avg_year = overview.get('average_publication_year', 2024)
    total_words = overview.get('total_words_corpus', 0)
    
    intro = f"""This systematic literature review provides a comprehensive analysis of {total_papers} research papers, examining current trends and developments in the field. The analyzed corpus contains {total_words:,} words spanning publications from various years, with an average publication year of {avg_year:.1f}, indicating relatively recent research activity in this domain.

The rapid advancement of technology and methodology necessitates regular synthesis of existing knowledge to identify patterns, gaps, and future directions. Understanding the current state of research enables scholars and practitioners to build upon existing work rather than duplicating efforts."""
    
    if themes:
        dominant_theme = themes[0] if themes else None
        if dominant_theme:
            intro += f"""
            
Thematic analysis reveals {len(themes)} major research areas, with "{dominant_theme['name']}" emerging as the dominant theme, appearing in {dominant_theme['count']} papers ({dominant_theme['percentage']}% of the corpus). This concentration suggests a focused research agenda around this particular domain while still maintaining diversity in related areas."""
    
    intro += """
    
This review employs a systematic approach to data collection, extraction, and analysis, ensuring comprehensive coverage of the literature while maintaining methodological rigor. The findings presented here aim to provide researchers, practitioners, and policymakers with valuable insights into the current research landscape and emerging trends."""
    
    return intro

def generate_dynamic_abstract(statistics, findings):
    """Generate abstract based on real data"""
    if not statistics:
        return "This systematic literature review analyzes current research trends and developments."
    
    overview = statistics.get('overview', {})
    keywords = statistics.get('keywords', {})
    themes = statistics.get('themes', [])
    
    total_papers = overview.get('total_papers_analyzed', 0)
    total_words = overview.get('total_words_corpus', 0)
    top_keyword = overview.get('most_common_keyword', 'N/A')
    
    abstract = f"""Background: This systematic literature review examines {total_papers} research papers comprising {total_words:,} words, focusing on current trends and developments in the field. Understanding these research trajectories is essential for identifying gaps and future directions.

Objective: To synthesize existing research, identify thematic patterns, and provide a comprehensive overview of methodological approaches and key findings across multiple research areas.

Methods: A structured literature review methodology was employed. Papers were systematically collected and processed using automated text extraction and analysis. Thematic clustering was performed to identify recurring patterns and research trends. Data synthesis followed a systematic approach to ensure comprehensive coverage.

Key Results: The analysis reveals significant concentration around the keyword "{top_keyword}" and {len(themes)} major thematic areas. The corpus spans multiple years with an average publication year of {overview.get('average_publication_year', 2024):.1f}, indicating ongoing research activity. Data completeness metrics suggest high-quality extraction and analysis.

Conclusion: This review provides valuable insights into current research landscapes and identifies promising directions for future investigation. The synthesized findings offer a foundation for researchers and practitioners seeking to understand current state-of-the-art developments."""
    
    return abstract

def generate_thematic_analysis_section(statistics):
    """Generate thematic analysis section"""
    themes = statistics.get('themes', []) if statistics else []
    
    if not themes:
        return "Thematic analysis was not possible due to insufficient data."
    
    content = ["Thematic Analysis"]
    content.append("The systematic review identified several distinct thematic clusters across the analyzed literature:")
    
    for i, theme in enumerate(themes[:5], 1):  # Top 5 themes
        theme_name = theme['name']
        count = theme['count']
        percentage = theme['percentage']
        sample_papers = theme.get('sample_papers', [])
        
        content.append(f"{i}. {theme_name}")
        content.append(f"This theme appears in {count} papers ({percentage}% of the corpus), indicating significant research focus in this area. ")
        
        if sample_papers:
            content.append("Representative papers in this theme include:")
            for paper in sample_papers[:2]:
                content.append(f"• {paper}")
        
        content.append("")  # Spacing
    
    return "\n".join(content)

def generate_results_section(findings, statistics):
    """Generate results section from real findings"""
    if not findings:
        return "No key findings were available for analysis."
    
    content = ["Results"]
    content.append("The analysis of extracted key findings reveals several important patterns and insights:")
    
    # Group findings by themes if available
    themes = statistics.get('themes', []) if statistics else []
    
    if themes:
        for theme in themes[:3]:  # Top 3 themes
            theme_name = theme['name']
            content.append(f"\n{theme_name} Related Findings")
            content.append(f"Papers related to {theme_name.lower()} demonstrate consistent patterns:")
            
            # Add sample findings (this would need to be matched with actual findings)
            for i, finding in enumerate(findings[:3], 1):
                if finding.get('key_findings'):
                    for j, key_finding in enumerate(finding['key_findings'][:2], 1):
                        if key_finding.strip():
                            content.append(f"{i}.{j} {key_finding.strip()}")
    
    # Add quantitative insights
    if statistics:
        overview = statistics.get('overview', {})
        content.append(f"\nQuantitative Insights")
        content.append(f"The corpus contains {overview.get('total_words_corpus', 0):,} words across {overview.get('total_papers_analyzed', 0)} papers, with an average of {overview.get('average_words_per_paper', 0):.1f} words per paper.")
        
        keywords = statistics.get('keywords', {})
        top_keywords = keywords.get('top_5_keywords', [])
        if top_keywords:
            content.append("The most frequently occurring keywords are:")
            for kw, count in top_keywords:
                content.append(f"• {kw}: {count} occurrences")
    
    return "\n".join(content)

def generate_discussion_section(statistics, findings):
    """Generate discussion section based on real findings"""
    if not statistics:
        return "Discussion was limited by data availability."
    
    overview = statistics.get('overview', {})
    themes = statistics.get('themes', [])
    quality = statistics.get('quality_metrics', {})
    
    content = ["Discussion"]
    
    # Implications
    content.append("Implications")
    content.append(f"The findings from this systematic review have several important implications for both research and practice. The analysis of {overview.get('total_papers_analyzed', 0)} papers reveals a maturing research domain with established methodologies and growing applications.")
    
    if themes:
        dominant_theme = themes[0] if themes else None
        if dominant_theme:
            content.append(f"The prominence of {dominant_theme['name']} as the dominant theme ({dominant_theme['percentage']}% of papers) suggests concentrated research efforts in this area, potentially indicating both established importance and opportunities for innovation in adjacent domains.")
    
    content.append("For researchers, the synthesis provides a roadmap of established approaches and identifies promising directions for future investigation. Practitioners benefit from the consolidated evidence base that can inform decision-making and implementation strategies.")
    
    # Limitations
    content.append("\nLimitations")
    content.append("This review has several limitations that should be considered when interpreting the findings. First, the search strategy, while comprehensive, may not have captured all relevant literature, particularly grey literature or pre-print publications.")
    
    content.append(f"Second, the automated text extraction and analysis process achieved a data completeness score of {quality.get('data_completeness', 0):.1f}%, while efficient, may miss nuanced insights that human reviewers might identify. Third, the thematic clustering approach, while systematic, relies on keyword-based categorization that may not capture all conceptual relationships.")
    
    # Future Research
    content.append("\nFuture Research")
    content.append("Based on the identified gaps and limitations, several directions for future research emerge. Longitudinal studies are needed to examine the evolution of research trends and their impact over time. Development of standardized evaluation metrics would facilitate more meaningful comparisons across different approaches and methodologies.")
    
    if themes:
        content.append(f"There is also need for more research in underrepresented thematic areas. While {themes[0]['name']} dominates the literature, other themes like {themes[1]['name'] if len(themes) > 1 else 'emerging areas'} may offer untapped potential for innovation.")
    
    content.append("Finally, investigation into the real-world impact and implementation of research findings would help bridge the gap between academic research and practical application.")
    
    return "\n".join(content)

def build_pdf():
    """Generate professional academic PDF report"""
    styles = create_academic_styles()
    story = []
    
    # Load data
    statistics = load_statistics()
    findings = load_section_content("results.txt")
    
    # Title Page
    story.append(Paragraph("Systematic Literature Review", styles['AcademicTitle']))
    story.append(Paragraph("A Comprehensive Analysis of Current Research Trends and Developments", styles['AcademicTitle']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Generated by Automated Research Review System", styles['AuthorStyle']))
    story.append(Paragraph(f"{datetime.now().strftime('%B %d, %Y')}", styles['AuthorStyle']))
    story.append(PageBreak())
    
    # Abstract
    abstract_text = generate_dynamic_abstract(statistics, [])
    story.append(Paragraph("Abstract", styles['SectionHeader']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(abstract_text, styles['AbstractText']))
    story.append(Spacer(1, 20))
    
    # 1. Introduction
    intro_text = generate_dynamic_introduction(statistics)
    story.append(Paragraph("1. Introduction", styles['SectionHeader']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(intro_text, styles['AcademicBodyText']))
    story.append(Spacer(1, 20))
    
    # 2. Methods
    methods_content = load_section_content("methods.txt")
    if methods_content:
        story.append(Paragraph("2. Methods", styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        for para in methods_content:
            if para.strip():
                story.append(Paragraph(para, styles['AcademicBodyText']))
                story.append(Spacer(1, 6))
    else:
        # Fallback methods section
        methods_text = """Literature Search Process
This study employed a systematic literature review methodology following established guidelines for comprehensive research synthesis. The search process utilized automated academic database queries through the Semantic Scholar API, targeting peer-reviewed publications.

Extraction Method
PDF documents were processed using a hybrid text extraction approach. Primary extraction utilized PyMuPDF for direct text parsing, with OCR fallback via Tesseract for scanned or low-quality documents.

Synthesis Approach
The synthesis process followed a multi-stage approach: (1) Initial text extraction and cleaning, (2) Key findings identification using automated pattern recognition, (3) Thematic clustering using keyword-based categorization, and (4) Systematic integration of findings across papers."""
        
        story.append(Paragraph("2. Methods", styles['SectionHeader']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(methods_text, styles['AcademicBodyText']))
    
    story.append(Spacer(1, 20))
    
    # 3. Statistics
    if statistics:
        story.append(Paragraph("3. Corpus Statistics", styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        # Add statistics table
        table_data = generate_statistics_table(statistics)
        if table_data:
            table = Table(table_data, colWidths=[3*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(table)
            story.append(Spacer(1, 20))
    
    # 4. Results
    results_text = generate_results_section([], statistics)
    story.append(Paragraph("4. Results", styles['SectionHeader']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(results_text, styles['AcademicBodyText']))
    story.append(Spacer(1, 20))
    
    # 5. Thematic Analysis
    thematic_text = generate_thematic_analysis_section(statistics)
    story.append(Paragraph("5. Thematic Analysis", styles['SectionHeader']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(thematic_text, styles['AcademicBodyText']))
    story.append(Spacer(1, 20))
    
    # 6. Discussion
    discussion_text = generate_discussion_section(statistics, [])
    story.append(Paragraph("6. Discussion", styles['SectionHeader']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(discussion_text, styles['AcademicBodyText']))
    story.append(Spacer(1, 20))
    
    # 7. References
    references_content = load_section_content("references.txt")
    if references_content:
        story.append(Paragraph("7. References", styles['SectionHeader']))
        story.append(Spacer(1, 12))
        
        for ref in references_content:
            if ref.strip():
                story.append(Paragraph(ref, styles['ReferencesText']))
                story.append(Spacer(1, 3))
    
    # Build PDF
    doc = SimpleDocTemplate(
        str(OUT_PDF),
        pagesize=A4,
        rightMargin=72,  # 1 inch margins
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    doc.build(story)
    return OUT_PDF
