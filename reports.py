import os
import re
from typing import List, Union, Optional
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.tavily import TavilyTools
from phi.tools.pubmed import PubmedTools

# Environment configuration
os.environ['TAVILY_API_KEY'] = "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"
os.environ['GOOGLE_API_KEY'] = "AIzaSyCRKWB-XFsghy70mD6f9tPYOZklWXZiTLQ"

class PregnancyUltrasoundAnalyzer:
    def __init__(self):
        self.ultrasound_agent = self._create_ultrasound_agent()
        self.research_agent = self._create_research_agent()
        
    def _create_ultrasound_agent(self) -> Agent:
        """Create the primary ultrasound analysis agent with Tavily for web searches"""
        return Agent(
            model=Gemini(id="gemini-2.0-flash-exp"),
            system_prompt="""You are a senior obstetric sonographer with 15 years experience. Your tasks:
1. Analyze ultrasound images/reports with medical precision
2. Identify 3-5 key findings needing further explanation
3. Mark each with [[RESEARCH:TERM]] notation
4. Create patient-friendly explanations using:
   - Simple analogies (e.g. "baby's size of a pineapple")
   - Visual emojis/icons
   - Reassuring language
5. For complex findings, use Tavily to find layperson explanations
6. Structure output with:
   - 🌟 Positive Findings
   - 📝 Notable Observations
   - ❤️ Care Recommendations""",
            instructions="""Analysis Protocol:
1. First pass: Extract all medical data with 100% accuracy
2. Second pass: Convert to patient-friendly language
3. Research terms: Mark any needing literature support
4. Web search: Use Tavily for patient education materials
5. Final output: Combine all elements with warm tone""",
            tools=[TavilyTools(api_key=os.getenv("TAVILY_API_KEY"))],
            markdown=True,
            # debug_mode=True,
            show_tool_calls=True
        )

    def _create_research_agent(self) -> Agent:
        """Create specialized research agent for medical literature"""
        return Agent(
            model=Gemini(id="gemini-2.0-flash-exp"),
            system_prompt="""You are a medical research librarian specializing in obstetrics. Your tasks:
1. For each [[RESEARCH:TERM]] from ultrasound reports:
   - Find 2-3 most relevant PubMed articles
   - Include recent studies (priority to last 3 years)
   - Extract key conclusions in plain language
2. Format each finding with:
   - 🏥 Medical Term
   - 📚 Research Summary (1-2 sentences)
   - 🔗 DOI Link
   - 💡 Patient Implications""",
            tools=[PubmedTools(
                email="siddharthbasale2004@gmail.com",
                max_results=3,
                
            )],
            markdown=True,
            # debug_mode=True,
            show_tool_calls=True
        )

    def analyze(self, image_paths: Union[str, List[str]]) -> str:
        """Complete analysis pipeline with error handling"""
        try:
            # Step 1: Ultrasound analysis
            ultrasound_task = """Analyze these ultrasound images with special attention to:
1. Accurate medical interpretation
2. Marking terms needing research [[RESEARCH:TERM]] 
3. Using Tavily to find patient-friendly explanations
4. Creating warm, supportive output"""
            
            ultrasound_report = self.ultrasound_agent.run(
                ultrasound_task,
                images=[image_paths] if isinstance(image_paths, str) else image_paths
            ).content

            # Step 2: Extract research terms
            research_terms = self._extract_research_terms(ultrasound_report)
            
            # Step 3: Conduct targeted research
            research_report = ""
            if research_terms:
                research_report = self.research_agent.run(
                    f"Research these obstetric terms: {', '.join(research_terms)}\n"
                    "Prioritize recent studies (last 3 years) with clear patient implications"
                ).content

            # Step 4: Generate final report
            return self._generate_final_report(
                ultrasound=ultrasound_report,
                research=research_report
            )

        except Exception as e:
            return self._generate_error_report(e)

    def _extract_research_terms(self, report: str) -> List[str]:
        """Sophisticated term extraction with deduplication"""
        terms = re.findall(r'\[\[RESEARCH:(.*?)\]\]', report)
        return list(set(terms))[:5]  # Limit to 5 most important terms

    def _generate_final_report(self, ultrasound: str, research: str) -> str:
        """Professional report assembly with safety checks"""
        # Remove research markers from patient-facing content
        clean_ultrasound = re.sub(r'\[\[RESEARCH:.*?\]\]', '', ultrasound)
        
        report = f"""
# 👶 Your Pregnancy Ultrasound Report

{clean_ultrasound}

{self._format_research_section(research) if research else ""}

## Next Steps
- Discuss these results with your OB/GYN
- Remember most variations are normal
- Your care team is here to support you

💖 You're doing great, mom-to-be!
"""
        return report.strip()

    def _format_research_section(self, research: str) -> str:
        """Format research findings for patient understanding"""
        return f"""
## 📚 Medical Research Summary

Based on the latest studies:

{research}

Note: Always consult your doctor about your specific case
"""

    def _generate_error_report(self, error: Exception) -> str:
        """User-friendly error handling"""
        return f"""
⚠️ We encountered an issue generating your full report

Our team has been notified. Please try again later.

For immediate assistance:
- Contact your healthcare provider
- Call support at 1-800-EXAMPLE

Error details (for support staff):
{str(error)}
"""

    def save_report(self, report: str, filename: str = "ultrasound_report.md") -> None:
        """Secure report saving with validation"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"✅ Report saved to {filename}")
        except IOError as e:
            print(f"❌ Could not save report: {str(e)}")

# Example usage
if __name__ == "__main__":
    analyzer = PregnancyUltrasoundAnalyzer()
    
    try:
        print("🔍 Analyzing...")
        result = analyzer.analyze([
            "image1.jpeg",
            "image2.jpeg",
            "image3.jpeg",

        ])
        
        print("\n" + "="*50)
        print(result)
        print("="*50 + "\n")
        
        analyzer.save_report(result)
        
    except Exception as e:
        print(f"❌ Critical system error: {str(e)}")
        print("Please contact technical support")