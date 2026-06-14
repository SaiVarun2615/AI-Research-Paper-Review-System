import gradio as gr
import time
import json
import shutil
from pathlib import Path
from quality_check import run_quality_checks
from revision_suggestions import suggest_revisions
from paper_fetcher import fetch_from_queries
from pdf_export import build_pdf
from pipeline_runner import run_full_pipeline
from statistics_engine import save_statistics

ROOT = Path(__file__).parent.parent
DRAFTS_DIR = ROOT / "research" / "drafts"
PDF_DIR = ROOT / "research" / "pdfs"
QUERIES_FILE = ROOT / "queries.txt"

# -------------------------------
# PDF Viewer Functions
# -------------------------------
def get_all_pdfs():
    """Get all PDF files from research/pdfs/ recursively"""
    try:
        pdf_files = []
        for pdf_path in PDF_DIR.rglob("*.pdf"):
            # Create relative path for display
            relative_path = pdf_path.relative_to(ROOT)
            pdf_files.append(str(relative_path))
        
        # Sort files for consistent ordering
        pdf_files.sort()
        
        if pdf_files:
            return gr.Dropdown(choices=pdf_files, value=pdf_files[0] if pdf_files else None)
        else:
            return gr.Dropdown(choices=[], value=None)
    except Exception as e:
        print(f"Error getting PDFs: {e}")
        return gr.Dropdown(choices=[], value=None)

def load_selected_pdf(relative_path):
    """Load selected PDF for preview using Gradio file component"""
    if not relative_path:
        return gr.HTML("<div style='padding:20px;text-align:center;color:#666;'>No PDF selected</div>")
    
    try:
        # Convert relative path to absolute path
        full_path = ROOT / relative_path
        if full_path.exists() and full_path.suffix.lower() == '.pdf':
            # Create HTML with file information and download option
            file_size = full_path.stat().st_size
            
            # Convert file size to human readable format
            if file_size < 1024:
                size_str = f"{file_size} bytes"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size/1024:.1f} KB"
            else:
                size_str = f"{file_size/(1024*1024):.1f} MB"
            
            pdf_html = f"""
            <div style="padding:20px;border:2px solid #007bff;border-radius:10px;background:#f8f9ff;">
                <div style="text-align:center;margin-bottom:20px;">
                    <h3 style="color:#007bff;margin:0;">📄 PDF Document Loaded</h3>
                </div>
                
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:15px;margin-bottom:20px;">
                    <div style="padding:10px;background:#e9ecef;border-radius:5px;">
                        <strong>📁 File:</strong><br>
                        <span style="font-family:monospace;color:#495057;">{relative_path}</span>
                    </div>
                    <div style="padding:10px;background:#e9ecef;border-radius:5px;">
                        <strong>💾 Size:</strong><br>
                        <span style="color:#495057;">{size_str}</span>
                    </div>
                </div>
                
                <div style="padding:15px;background:#d1ecf1;border:1px solid #bee5eb;border-radius:5px;margin-bottom:20px;">
                    <strong>📋 Document Information:</strong><br>
                    • Research paper from your literature review<br>
                    • Contains academic content and findings<br>
                    • Part of your automated research corpus<br>
                    • Ready for detailed analysis
                </div>
                
                <div style="padding:15px;background:#fff3cd;border:1px solid #ffeaa7;border-radius:5px;margin-bottom:20px;">
                    <strong>🔍 Next Steps:</strong><br>
                    1. Use the file component below to download<br>
                    2. Open in your preferred PDF reader<br>
                    3. Review content for your research analysis<br>
                    4. Cross-reference with generated findings
                </div>
                
                <div style="text-align:center;padding:15px;background:#e7f3ff;border-radius:5px;">
                    <strong style="color:#007bff;">📂 Download Ready</strong><br>
                    <span style="color:#6c757d;">Use the file component below to access this PDF</span>
                </div>
            </div>
            """
            return gr.HTML(pdf_html)
        else:
            return gr.HTML("<div style='padding:20px;text-align:center;color:#dc3545;'>❌ File not found or not a PDF</div>")
    except Exception as e:
        return gr.HTML(f"<div style='padding:20px;text-align:center;color:#dc3545;'>❌ Error loading PDF: {str(e)}</div>")

def get_pdf_file(relative_path):
    """Return the actual file for Gradio file component"""
    if not relative_path:
        return None
    
    try:
        full_path = ROOT / relative_path
        if full_path.exists() and full_path.suffix.lower() == '.pdf':
            return str(full_path)
        else:
            return None
    except Exception as e:
        print(f"Error getting PDF file: {e}")
        return None

def refresh_pdf_list():
    """Refresh the PDF list after fetching new papers"""
    return get_all_pdfs()

# -------------------------------
# Helpers
# -------------------------------
def load_text(name):
    path = DRAFTS_DIR / name
    return path.read_text(encoding="utf-8") if path.exists() else ""

def save_queries(user_queries):
    QUERIES_FILE.write_text(user_queries.strip() + "\n", encoding="utf-8")
    return "✅ Queries saved successfully"

def reset_system():
    """Reset system by clearing old research data while preserving project structure"""
    try:
        import shutil
        
        print("🧹 Starting system reset...")
        
        # 1. Clear generated research data
        files_to_delete = [
            ROOT / "research" / "papers.json",
            ROOT / "research" / "analysis" / "key_findings.json",
            ROOT / "research" / "drafts" / "final_report.pdf"
        ]
        
        # Delete specific files
        for file_path in files_to_delete:
            if file_path.exists():
                try:
                    file_path.unlink()
                    print(f"✅ Deleted: {file_path.name}")
                except Exception as e:
                    print(f"⚠️ Could not delete {file_path.name}: {e}")
        
        # 2. Clear draft text files
        draft_files = list((ROOT / "research" / "drafts").glob("*.txt"))
        for draft_file in draft_files:
            try:
                draft_file.unlink()
                print(f"✅ Deleted draft: {draft_file.name}")
            except Exception as e:
                print(f"⚠️ Could not delete draft {draft_file.name}: {e}")
        
        # 3. Clear analysis files
        analysis_files = list((ROOT / "research" / "analysis").glob("*.json"))
        for analysis_file in analysis_files:
            try:
                analysis_file.unlink()
                print(f"✅ Deleted analysis: {analysis_file.name}")
            except Exception as e:
                print(f"⚠️ Could not delete analysis {analysis_file.name}: {e}")
        
        # 4. Clear extracted text files
        extracted_files = list((ROOT / "research" / "extracted_text").glob("*.json"))
        for extracted_file in extracted_files:
            try:
                extracted_file.unlink()
                print(f"✅ Deleted extracted: {extracted_file.name}")
            except Exception as e:
                print(f"⚠️ Could not delete extracted {extracted_file.name}: {e}")
        
        # 5. Clear all PDFs and subfolders
        pdfs_dir = ROOT / "research" / "pdfs"
        if pdfs_dir.exists():
            try:
                shutil.rmtree(pdfs_dir)
                print(f"✅ Cleared PDFs directory: {pdfs_dir}")
            except Exception as e:
                print(f"⚠️ Could not clear PDFs directory: {e}")
        
        # 6. Recreate empty folders if missing
        folders_to_create = [
            ROOT / "research" / "pdfs",
            ROOT / "research" / "analysis",
            ROOT / "research" / "drafts",
            ROOT / "research" / "extracted_text"
        ]
        
        for folder_path in folders_to_create:
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Ensured folder exists: {folder_path}")
        
        # 7. Recreate empty data files to prevent pipeline crashes
        empty_papers = {}
        with open(ROOT / "research" / "papers.json", "w", encoding="utf-8") as f:
            json.dump(empty_papers, f, indent=2)
        print("✅ Recreated empty papers.json")
        
        empty_findings = []
        with open(ROOT / "research" / "analysis" / "key_findings.json", "w", encoding="utf-8") as f:
            json.dump(empty_findings, f, indent=2)
        print("✅ Recreated empty key_findings.json")
        
        print("🧹 System reset completed successfully!")
        
        # Return simple success message for fetch_status
        return "✅ System reset successfully. Ready for new query."
        
    except Exception as e:
        print(f"❌ Reset failed: {e}")
        return f"❌ Reset failed: {str(e)}"

def load_statistics_display():
    """Load statistics for UI display"""
    try:
        from statistics_engine import compute_comprehensive_statistics
        stats = compute_comprehensive_statistics()
        
        if stats:
            overview = stats.get('overview', {})
            keywords = stats.get('keywords', {})
            
            return {
                "papers_analyzed": overview.get('total_papers_analyzed', 0),
                "avg_year": f"{overview.get('average_publication_year', 0):.1f}",
                "top_keyword": f"{overview.get('most_common_keyword', 'N/A')} ({overview.get('most_common_keyword_count', 0)})",
                "total_words": f"{overview.get('total_words_corpus', 0):,}",
                "unique_keywords": keywords.get('total_unique_keywords', 0),
                "data_completeness": f"{stats.get('quality_metrics', {}).get('data_completeness', 0):.1f}%"
            }
        else:
            return {
                "papers_analyzed": 0,
                "avg_year": "N/A",
                "top_keyword": "N/A",
                "total_words": "0",
                "unique_keywords": 0,
                "data_completeness": "0%"
            }
    except Exception as e:
        return {
            "papers_analyzed": 0,
            "avg_year": "Error",
            "top_keyword": str(e),
            "total_words": "0",
            "unique_keywords": 0,
            "data_completeness": "0%"
        }

def fetch_papers_with_progress(user_queries):
    """Fetch papers with progress indication"""
    try:
        yield ("🔄 Fetching papers...", gr.update(visible=True), gr.update(visible=False))
        time.sleep(0.5)  # Brief pause for UI update
        
        msg = fetch_from_queries(user_queries)
        yield (f"🟢 {msg}", gr.update(visible=False), gr.update(visible=True))
    except Exception as e:
        yield (f"🔴 Fetch failed: {e}", gr.update(visible=False), gr.update(visible=True))

def regenerate_drafts_with_progress():
    """Regenerate drafts with full pipeline and progress indication"""
    try:
        yield ("🔄 Running full pipeline...", gr.update(visible=True), gr.update(visible=False))
        time.sleep(0.5)
        
        # Run the complete pipeline
        msg = run_full_pipeline()
        yield (f"🟢 {msg}", gr.update(visible=False), gr.update(visible=True))
    except Exception as e:
        yield (f"🔴 Pipeline failed: {e}", gr.update(visible=False), gr.update(visible=True))

def export_pdf_with_status():
    """Export PDF with status feedback"""
    try:
        path = build_pdf()
        return str(path), "✅ Academic PDF generated successfully"
    except Exception as e:
        return None, f"🔴 PDF export failed: {e}"

def review_pipeline_with_status():
    """Review pipeline with comprehensive output"""
    try:
        quality = run_quality_checks()
        suggestions = suggest_revisions(quality)

        quality_text = "\n".join(f"• {k}: {v}" for k, v in quality.items())
        suggestions_text = "\n".join(suggestions)

        # Simple KPIs
        def wc(name):
            t = load_text(name)
            return len(t.split()) if t else 0

        kpis = {
            "Abstract words": wc("abstract.txt"),
            "Methods words": wc("methods.txt"),
            "Results words": wc("results.txt"),
            "Discussion words": wc("discussion.txt"),
            "References entries": load_text("references.txt").count("\n") + (1 if load_text("references.txt") else 0),
        }
        kpi_text = " | ".join([f"{k}: {v}" for k, v in kpis.items()])
        
        return quality_text, suggestions_text, kpi_text, "✅ Review completed"
    except Exception as e:
        return "", "", "", f"🔴 Review failed: {e}"

def refresh_drafts():
    """Refresh all draft content"""
    return {
        abstract: load_text("abstract.txt"),
        introduction: load_text("introduction.txt"),
        methods: load_text("methods.txt"),
        results: load_text("results.txt"),
        discussion: load_text("discussion.txt"),
        references: load_text("references.txt")
    }

def refresh_statistics():
    """Refresh statistics display"""
    try:
        from statistics_engine import compute_comprehensive_statistics
        stats = compute_comprehensive_statistics()
        
        if stats:
            overview = stats.get('overview', {})
            keywords = stats.get('keywords', {})
            
            # Return 4 separate values as expected by the UI
            return (
                overview.get('total_papers_analyzed', 0),
                f"{overview.get('average_publication_year', 0):.1f}",
                f"{overview.get('total_words_corpus', 0):,}",
                keywords.get('total_unique_keywords', 0)
            )
        else:
            return (0, "N/A", "0", 0)
    except Exception as e:
        return (0, f"Error: {e}", "0", 0)

# -------------------------------
# Custom CSS
# -------------------------------
custom_css = """
.gradio-container {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 20px;
}

.tab-nav {
    background: #f8f9fa;
    border-bottom: 2px solid #dee2e6;
}

.status-success {
    color: #28a745;
    font-weight: 600;
}

.status-error {
    color: #dc3545;
    font-weight: 600;
}

.status-loading {
    color: #007bff;
    font-weight: 600;
}

.kpi-bar {
    background: #e9ecef;
    padding: 10px;
    border-radius: 5px;
    font-family: monospace;
    margin: 10px 0;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin: 15px 0;
}

.stat-card {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #007bff;
}

.stat-value {
    font-size: 1.2em;
    font-weight: bold;
    color: #007bff;
}

.stat-label {
    font-size: 0.9em;
    color: #6c757d;
    margin-top: 5px;
}

.draft-section {
    border: 1px solid #dee2e6;
    border-radius: 5px;
    padding: 15px;
    margin: 10px 0;
    background: white;
}

.section-title {
    font-weight: 600;
    color: #495057;
    margin-bottom: 10px;
    border-bottom: 1px solid #dee2e6;
    padding-bottom: 5px;
}

.footer {
    text-align: center;
    color: #6c757d;
    font-size: 0.9em;
    margin-top: 30px;
    padding: 20px;
    border-top: 1px solid #dee2e6;
}
"""

# -------------------------------
# UI Components
# -------------------------------
with gr.Blocks(title="Automated Research Review System") as demo:
    
    # Header
    gr.HTML("""
    <div class="main-header">
        <h1>🚀 Automated Research Review System</h1>
        <p>Professional Academic Literature Review • Real Data Analysis • Portfolio-Quality Reports</p>
    </div>
    """)
    
    # Status bar
    with gr.Row():
        status_display = gr.Markdown("🟢 System Ready", elem_classes=["status-success"])
    
    with gr.Tabs() as tabs:
        
        # Tab 1: Query & Fetch
        with gr.TabItem("🔍 Query & Fetch", elem_classes=["tab-nav"]):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Research Queries")
                    query_box = gr.Textbox(
                        placeholder="Enter one query per line",
                        lines=8,
                        value=QUERIES_FILE.read_text(encoding="utf-8") if QUERIES_FILE.exists() else "",
                        label="Search Queries"
                    )
                    
                    with gr.Row():
                        save_query_btn = gr.Button("💾 Save Queries", variant="secondary")
                        fetch_btn = gr.Button("🔎 Fetch Papers", variant="primary")
                        reset_btn = gr.Button("🧹 Reset System", variant="secondary")
                    
                    fetch_status = gr.Markdown("", elem_classes=["status-loading"])
                    fetch_progress = gr.HTML(visible=False)
                    
                    save_query_btn.click(
                        save_queries,
                        inputs=query_box,
                        outputs=fetch_status
                    )
                    
                    fetch_btn.click(
                        fetch_papers_with_progress,
                        inputs=query_box,
                        outputs=[fetch_status, fetch_progress, fetch_status]
                    )
                    
                    reset_btn.click(
                        reset_system,
                        outputs=fetch_status
                    )
                
                with gr.Column(scale=1):
                    gr.Markdown("### Pipeline Control")
                    regen_btn = gr.Button("🔄 Run Full Pipeline", variant="primary", size="lg")
                    regen_status = gr.Markdown("", elem_classes=["status-loading"])
                    regen_progress = gr.HTML(visible=False)
                    
                    regen_btn.click(
                        regenerate_drafts_with_progress,
                        outputs=[regen_status, regen_progress, regen_status]
                    )
                    
                    gr.Markdown("""
                    <div style="padding:15px;border:1px dashed #ced4da;border-radius:8px;background:#f8f9fa">
                        <strong>💡 Pipeline:</strong> Extract → Analyze → Statistics → Draft → References
                    </div>
                    """)
        
        # Tab 2: Statistics & Analysis
        with gr.TabItem("📊 Statistics & Analysis", elem_classes=["tab-nav"]):
            with gr.Row():
                refresh_stats_btn = gr.Button("🔄 Refresh Statistics", variant="secondary", size="sm")
            
            # Statistics Display Grid
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Corpus Overview")
                    stats_display = load_statistics_display()
                    
                    with gr.Row():
                        papers_stat = gr.Number(
                            label="Papers Analyzed", 
                            value=stats_display["papers_analyzed"],
                            interactive=False
                        )
                        avg_year_stat = gr.Number(
                            label="Average Publication Year", 
                            value=float(stats_display["avg_year"]) if stats_display["avg_year"] != "N/A" else 0,
                            interactive=False
                        )
                    
                    with gr.Row():
                        words_stat = gr.Number(
                            label="Total Words", 
                            value=int(stats_display["total_words"].replace(',', '')) if stats_display["total_words"] != "0" else 0,
                            interactive=False
                        )
                        keywords_stat = gr.Number(
                            label="Unique Keywords", 
                            value=stats_display["unique_keywords"],
                            interactive=False
                        )
                
                with gr.Column():
                    gr.Markdown("### Key Metrics")
                    gr.Markdown(f"""
                    **Most Common Keyword:** {stats_display["top_keyword"]}
                    
                    **Data Completeness:** {stats_display["data_completeness"]}
                    """)
                    
                    gr.Markdown("""
                    ### Quality Indicators
                    - ✅ Real keyword extraction
                    - ✅ Meaningful sentence analysis
                    - ✅ Thematic clustering
                    - ✅ Statistical validation
                    - ✅ No placeholder data
                    """)
            
            refresh_stats_btn.click(
                refresh_statistics,
                outputs=[papers_stat, avg_year_stat, words_stat, keywords_stat]
            )
        
        # Tab 3: Draft Review
        with gr.TabItem("📝 Draft Review", elem_classes=["tab-nav"]):
            with gr.Row():
                refresh_btn = gr.Button("🔄 Refresh Drafts", variant="secondary", size="sm")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Abstract", elem_classes=["section-title"])
                    abstract = gr.Textbox(
                        load_text("abstract.txt"), 
                        lines=6, 
                        show_label=False,
                        elem_classes=["draft-section"]
                    )
                    
                    gr.Markdown("### Introduction", elem_classes=["section-title"])
                    introduction = gr.Textbox(
                        load_text("introduction.txt"), 
                        lines=6, 
                        show_label=False,
                        elem_classes=["draft-section"]
                    )
                    
                    gr.Markdown("### Methods", elem_classes=["section-title"])
                    methods = gr.Textbox(
                        load_text("methods.txt"), 
                        lines=6, 
                        show_label=False,
                        elem_classes=["draft-section"]
                    )
                
                with gr.Column():
                    gr.Markdown("### Results", elem_classes=["section-title"])
                    results = gr.Textbox(
                        load_text("results.txt"), 
                        lines=8, 
                        show_label=False,
                        elem_classes=["draft-section"]
                    )
                    
                    gr.Markdown("### Discussion", elem_classes=["section-title"])
                    discussion = gr.Textbox(
                        load_text("discussion.txt"), 
                        lines=6, 
                        show_label=False,
                        elem_classes=["draft-section"]
                    )
            
            gr.Markdown("### References", elem_classes=["section-title"])
            references = gr.Textbox(
                load_text("references.txt"), 
                lines=6, 
                show_label=False,
                elem_classes=["draft-section"]
            )
            
            refresh_btn.click(
                refresh_drafts,
                outputs=[abstract, introduction, methods, results, discussion, references]
            )
        
        # Tab 4: Quality & Revision
        with gr.TabItem("✅ Quality & Revision", elem_classes=["tab-nav"]):
            critique_btn = gr.Button("🔁 Analyze Quality & Suggest Revisions", variant="primary", size="lg")
            
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Quality Evaluation", elem_classes=["section-title"])
                    quality_box = gr.Textbox(
                        lines=8, 
                        show_label=False,
                        placeholder="Quality metrics will appear here..."
                    )
                
                with gr.Column():
                    gr.Markdown("### Revision Suggestions", elem_classes=["section-title"])
                    suggestions_box = gr.Textbox(
                        lines=8, 
                        show_label=False,
                        placeholder="Revision suggestions will appear here..."
                    )
            
            kpi_bar = gr.Markdown("KPIs will appear after analysis", elem_classes=["kpi-bar"])
            review_status = gr.Markdown("")
            
            critique_btn.click(
                review_pipeline_with_status,
                outputs=[quality_box, suggestions_box, kpi_bar, review_status]
            )
        
        # Tab 5: Paper Viewer
        with gr.TabItem("📄 Paper Viewer", elem_classes=["tab-nav"]):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Downloaded Research Papers")
                    gr.Markdown("Select a PDF to preview inline in your browser.")
                    
                    with gr.Row():
                        refresh_pdfs_btn = gr.Button("🔄 Refresh List", variant="secondary", size="sm")
                    
                    # Create a new PDF dropdown for this tab
                    pdf_viewer_dropdown = gr.Dropdown(
                        label="Available PDFs",
                        choices=[],
                        value=None,
                        interactive=True
                    )
                    
                    load_pdf_btn = gr.Button("📖 Load PDF", variant="primary")
                    
                    gr.Markdown("""
                    <div style="padding:15px;border:1px dashed #ced4da;border-radius:8px;background:#f8f9fa">
                        <strong>💡 Tip:</strong> PDFs are organized by research category. Use the dropdown to select and preview any downloaded paper.
                    </div>
                    """)
                
                with gr.Column(scale=2):
                    gr.Markdown("### PDF Preview & Download")
                    pdf_viewer = gr.HTML(
                        value="<div style='padding:20px;text-align:center;color:#666;'>Select a PDF from the dropdown and click 'Load PDF' to preview</div>",
                        visible=True
                    )
                    
                    # Add file component for actual PDF download
                    pdf_file_component = gr.File(
                        label="📂 Download PDF",
                        file_types=[".pdf"],
                        visible=False
                    )
            
            # Event handlers for this tab
            load_pdf_btn.click(
                fn=lambda path: (
                    load_selected_pdf(path), 
                    gr.File(value=get_pdf_file(path), visible=True) if get_pdf_file(path) else gr.File(visible=False)
                ),
                inputs=pdf_viewer_dropdown,
                outputs=[pdf_viewer, pdf_file_component]
            )
            
            refresh_pdfs_btn.click(
                refresh_pdf_list,
                outputs=pdf_viewer_dropdown
            )
            
            # Initialize PDF list on load
            demo.load(
                refresh_pdf_list,
                outputs=pdf_viewer_dropdown
            )
        
        # Tab 6: Export Report
        with gr.TabItem("📄 Export Report", elem_classes=["tab-nav"]):
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("""
                    ### Export Academic Report
                    
                    Generate a comprehensive academic PDF with real data:
                    - Professional title page with metadata
                    - Dynamic abstract from real statistics
                    - Introduction based on actual themes
                    - Methods describing the real pipeline
                    - Results from real key findings
                    - Thematic analysis with actual counts
                    - Discussion based on real implications
                    - Proper APA 7 formatted references
                    - Statistics table with real metrics
                    - No placeholder or generic content
                    """)
                    
                    export_btn = gr.Button("📄 Generate Academic PDF", variant="primary", size="lg")
                    export_status = gr.Markdown("")
                
                with gr.Column(scale=1):
                    pdf_file = gr.File(label="Download Academic Report")
            
            export_btn.click(
                export_pdf_with_status,
                outputs=[pdf_file, export_status]
            )
    
    # Footer
    gr.HTML("""
    <div class="footer">
        <strong>Professional Academic Research Review System</strong><br/>
        Technology: Python • Real Data Analysis • APA 7 Formatting<br/>
        Features: Dynamic Content Generation • Statistical Validation • Portfolio Quality
    </div>
    """)

# Launch application
if __name__ == "__main__":
    demo.launch(share=True, server_name="0.0.0.0", server_port=7863, css=custom_css)
