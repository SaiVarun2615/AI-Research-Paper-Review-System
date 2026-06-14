def suggest_revisions(quality_report):
    suggestions = []

    for section, status in quality_report.items():
        if "too short" in status:
            suggestions.append(f"🔧 Expand the {section} section with more details.")
        if "missing" in status:
            suggestions.append(f"❗ Generate the {section} section.")

    if not suggestions:
        suggestions.append("✅ All sections meet basic quality requirements.")

    return suggestions
