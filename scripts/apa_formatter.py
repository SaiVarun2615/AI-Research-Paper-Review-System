def format_apa_from_metadata(title, authors, year, url):
    """
    Format reference in proper APA 7 style: AuthorLast, F. M., & AuthorLast, F. M. (Year). Title. Retrieved from URL
    
    Args:
        title: Paper title (string)
        authors: List of author dictionaries with 'name' field or list of strings
        year: Publication year (string, int, or None)
        url: Paper URL (string)
    """
    # Format authors according to APA 7 guidelines
    if not authors:
        author_text = title if title else "Unknown Author"
    else:
        formatted_authors = []
        
        for i, author in enumerate(authors):
            # Handle different author formats
            if isinstance(author, dict):
                name = author.get('name', '').strip()
            else:
                name = str(author).strip()
            
            if not name:
                continue
            
            # Split name into parts
            name_parts = name.split()
            if len(name_parts) >= 2:
                last_name = name_parts[-1]
                # Format initials with periods
                initials = ". ".join([part[0].upper() + "." for part in name_parts[:-1]])
                formatted_authors.append(f"{last_name}, {initials}")
            else:
                # Single name, use as is
                formatted_authors.append(name)
        
        # Apply APA 7 author formatting rules
        if formatted_authors:
            if len(formatted_authors) == 1:
                author_text = formatted_authors[0]
            elif len(formatted_authors) == 2:
                author_text = f"{formatted_authors[0]}, & {formatted_authors[1]}"
            elif len(formatted_authors) <= 20:
                # List all authors up to 20
                author_text = ", ".join(formatted_authors[:-1]) + f", & {formatted_authors[-1]}"
            else:
                # More than 20 authors - list first 19, ..., last
                author_text = ", ".join(formatted_authors[:19]) + f", ... & {formatted_authors[-1]}"
        else:
            author_text = title if title else "Unknown Author"
    
    # Format year
    if not year:
        year_text = "n.d."
    else:
        year_text = str(year)
    
    # Clean and format title
    if title:
        title_text = title.strip()
        # Remove any extra whitespace and ensure proper capitalization
        title_text = " ".join(title_text.split())
        # Title case for APA (first word and proper nouns capitalized)
        title_text = title_text[0].upper() + title_text[1:] if title_text else ""
    else:
        title_text = "Unknown Title"
    
    # Format source and retrieval information
    if url and url.strip():
        # Extract domain for source if possible
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace("www.", "")
            if domain:
                source = domain
                citation = f"{author_text} ({year_text}). {title_text}. Retrieved from {url}"
            else:
                citation = f"{author_text} ({year_text}). {title_text}. Retrieved from {url}"
        except:
            citation = f"{author_text} ({year_text}). {title_text}. Retrieved from {url}"
    else:
        citation = f"{author_text} ({year_text}). {title_text}."
    
    return citation

def format_apa_citation(authors, year, in_text=False):
    """
    Format in-text citation in APA style
    
    Args:
        authors: List of author dictionaries or strings
        year: Publication year
        in_text: Whether this is an in-text citation (parenthetical vs narrative)
    """
    if not authors:
        return f"(n.d.)"
    
    # Get first author's last name for in-text citation
    first_author = authors[0]
    if isinstance(first_author, dict):
        name = first_author.get('name', '').strip()
    else:
        name = str(first_author).strip()
    
    if not name:
        return "(n.d.)"
    
    # Extract last name
    name_parts = name.split()
    last_name = name_parts[-1] if name_parts else name
    
    # Format year
    year_text = str(year) if year else "n.d."
    
    if len(authors) == 1:
        if in_text:
            return f"{last_name} ({year_text})"
        else:
            return f"({last_name}, {year_text})"
    elif len(authors) == 2:
        second_author = authors[1]
        if isinstance(second_author, dict):
            second_name = second_author.get('name', '').strip()
        else:
            second_name = str(second_author).strip()
        
        second_parts = second_name.split()
        second_last = second_parts[-1] if second_parts else second_name
        
        if in_text:
            return f"{last_name} and {second_last} ({year_text})"
        else:
            return f"({last_name} and {second_last}, {year_text})"
    else:
        # Three or more authors
        if in_text:
            return f"{last_name} et al. ({year_text})"
        else:
            return f"({last_name} et al., {year_text})"

def generate_reference_list(papers_data):
    """
    Generate complete reference list from papers.json data
    
    Args:
        papers_data: Dictionary from papers.json with categories and papers
    """
    references = []
    
    for category, papers in papers_data.items():
        for paper in papers:
            title = paper.get('title', '')
            authors = paper.get('authors', [])
            year = paper.get('year')
            url = paper.get('url', '')
            
            if title:  # Only include papers with titles
                reference = format_apa_from_metadata(title, authors, year, url)
                references.append(reference)
    
    # Sort references alphabetically by author
    references.sort()
    
    return references

def validate_apa_format(reference):
    """
    Basic validation of APA format
    """
    checks = {
        'has_authors': bool(reference and not reference.startswith('(')),
        'has_year': '(19' in reference or '(20' in reference or '(n.d.)' in reference,
        'has_title': bool(reference and '.' in reference),
        'has_retrieval': 'retrieved from' in reference.lower() or reference.endswith('.')
    }
    
    return all(checks.values()), checks
