import re

def format_report(report):
    """
    Formats the ultrasound report to improve readability and engagement.

    Args:
        report (str): The raw ultrasound report text.

    Returns:
        str: The formatted ultrasound report.
    """

    formatted_report = f"""
    <div class="report-container">
        <h2 class="report-title">💖 Your Pregnancy Ultrasound Report 💖</h2>
    """

    # --- Positive Findings Section ---
    formatted_report += """
        <div class="report-section">
            <h3 class="section-title">🌟 Positive Findings 🌟</h3>
            <ul class="list-disc list-inside">
    """
    positive_findings_match = re.search(r"🌟 Positive Findings(.*?)📝 Notable Observations", report, re.DOTALL)
    if positive_findings_match:
        positive_findings = positive_findings_match.group(1).strip()
        positive_findings = re.sub(r'(?m)^(.*?):', r'<li><b>\1:</b>', positive_findings) # Bold the key part

        formatted_report += f"""
                {positive_findings}
            </ul>
        </div>
    """

    # --- Notable Observations Section ---
    formatted_report += """
        <div class="report-section">
            <h3 class="section-title">📝 Notable Observations 📝</h3>
            <ul class="list-decimal list-inside">
    """

    notable_observations_match = re.search(r"📝 Notable Observations(.*?)❤️ Care Recommendations", report, re.DOTALL)
    if notable_observations_match:
        notable_observations = notable_observations_match.group(1).strip()
        notable_observations = re.sub(r'(?m)^(.*?):', r'<li><b>\1:</b>', notable_observations)  # Bold the key part

        formatted_report += f"""
                {notable_observations}
            </ul>
        </div>
    """

    # --- Care Recommendations Section ---
    formatted_report += """
        <div class="report-section">
            <h3 class="section-title">❤️ Care Recommendations ❤️</h3>
            <ul class="list-disc list-inside">
    """

    care_recommendations_match = re.search(r"❤️ Care Recommendations(.*?)Let's dig a little deeper", report, re.DOTALL)
    if care_recommendations_match:
        care_recommendations = care_recommendations_match.group(1).strip()
        care_recommendations = re.sub(r'(?m)^(.*?):', r'<li><b>\1:</b>', care_recommendations) # Bold the key part

        formatted_report += f"""
                {care_recommendations}
            </ul>
        </div>
    """

    # --- Oligohydramnios Explanation Section ---
    oligohydramnios_match = re.search(r"Oligohydramnios(.*?)❤️ Care Recommendations", report, re.DOTALL)
    if oligohydramnios_match:
        oligohydramnios_text = oligohydramnios_match.group(1).strip()
        oligohydramnios_text = re.sub(r"(Patient explanation:)", r"<h4 class='patient-explanation'>\1</h4>", oligohydramnios_text)

        formatted_report += f"""
        <div class="report-section">
            <h3 class="section-title">💧 Understanding Oligohydramnios 💧</h3>
            <div class="oligohydramnios-explanation">{oligohydramnios_text}</div>
        </div>
    """

    # --- Medical Research Summary Section ---
    medical_research_match = re.search(r"📚 Medical Research Summary(.*?)Next Steps", report, re.DOTALL)
    if medical_research_match:
        medical_research = medical_research_match.group(1).strip()

        # Format the research summary with bullet points and proper spacing
        medical_research = re.sub(r"🏥 Medical Term:", r"<li><b>🏥 Medical Term:</b>", medical_research)
        medical_research = re.sub(r"📚 Research Summary:", r"<br><b>📚 Research Summary:</b>", medical_research)
        medical_research = re.sub(r"🔗 DOI Link:", r"<br><b>🔗 DOI Link:</b>", medical_research)
        medical_research = re.sub(r"💡 Patient Implications:", r"<br><b>💡 Patient Implications:</b>", medical_research)
        medical_research = re.sub(r"(?m)(.*?)(?=(<li>|$))", r"\1</li>", medical_research)  # Ensure each entry ends with </li>

        formatted_report += f"""
            <div class="report-section">
                <h3 class="section-title">📚 Medical Research Summary 📚</h3>
                <ul class="list-disc list-inside">
                    {medical_research}
                </ul>
            </div>
        """

    # --- Next Steps Section ---
    next_steps_match = re.search(r"Next Steps(.*?)💖 You're doing great, mom-to-be!", report, re.DOTALL)
    if next_steps_match:
        next_steps = next_steps_match.group(1).strip()
        next_steps = re.sub(r'(?m)^(.*?)$', r'<li>\1</li>', next_steps) #Bullet points
        formatted_report += f"""
            <div class="report-section">
                <h3 class="section-title">➡️ Next Steps ➡️</h3>
                <ul class="list-disc list-inside">
                    {next_steps}
                </ul>
            </div>
        """
    formatted_report += """
        <div class="report-section final-note">
            <p>💖 You're doing great, mom-to-be! 💖</p>
        </div>
    </div>
    """

    return formatted_report

# Example usage (assuming you have the 'report' variable from your Django view):
# formatted_report = format_report(report)
# In your Django template:
# {{ formatted_report|safe }}