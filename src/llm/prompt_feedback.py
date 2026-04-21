# src/llm/prompt_feedback.py
# Prompt Feedback Layer: Turning Failure Reasons into Instructions ( 지시서 #080 )

def build_feedback_prompt(reasons):
    """Task 4: 개선 지시 자동 생성"""
    if not reasons:
        return ""
        
    instructions = [
        "--- [SELF-REFINEMENT FEEDBACK] ---",
        "Your previous output was slightly lacking in quality. Please improve the next output as follows:"
    ]

    if "NO_NUMERICAL_EVIDENCE" in reasons:
        instructions.append("- Include concrete numerical data and specific values from the provided metrics.")

    if "WEAK_WHY_NOW" in reasons:
        instructions.append("- Strengthen the 'Why Now' section by explaining the immediate urgency and timing.")

    if "MISSING_STRUCTURE" in reasons:
        instructions.append("- Clearly explain the underlying structural cause of the market anomaly.")

    if "MISSING_FACT" in reasons:
        instructions.append("- Ensure the 'Surface Fact' clearly states the direct market observation.")

    instructions.append("PLEASE PROVIDE THE FULL JSON AGAIN WITH THESE IMPROVEMENTS.")
    instructions.append("-----------------------------------")
    
    return "\n".join(instructions)
