def classify_theme_type(theme, context=None):
    """
    [STEP-H-3] Classifies a theme into EXPANSION or CONSTRAINT.
    """
    keywords_constraint = ["constraint", "bottleneck", "shortage", "limit", "capacity", "stress", "exhaustion"]
    keywords_expansion = ["growth", "expansion", "boom", "demand surge", "adoption", "acceleration"]

    context_text = ""
    if context:
        if isinstance(context, dict):
            context_text = str(context.get("mechanism", "")) + " " + str(context.get("trigger", ""))
        else:
            context_text = str(context)

    text = (theme + " " + context_text).lower()

    if any(k in text for k in keywords_constraint):
        return "CONSTRAINT"

    if any(k in text for k in keywords_expansion):
        return "EXPANSION"

    return "EXPANSION"  # Default to expansion
