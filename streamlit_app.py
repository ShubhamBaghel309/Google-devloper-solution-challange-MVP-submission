import streamlit as st
import io
import os
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Import our AssignmentChecker
from AssignmentChecker import AssignmentChecker

# Import plagiarism detection
from assistant.core.plagiarism import calculate_plagiarism, analyze_ai_content, extract_text_from_docx, read_text_file

# Load environment variables
load_dotenv()

# Setup logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AssignmentChecker with vector database directly in Streamlit
checker = AssignmentChecker(vector_db_dir="./vector_db")

# Page configuration
st.set_page_config(
    page_title="AI Teacher Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #1565C0;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .result-header {
        font-size: 1.8rem;
        color: #1565C0;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .grade-display {
        font-size: 1.5rem;
        background-color: #f0f7ff;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #1E88E5;
        margin-bottom: 1rem;
    }
    .feedback-box {
        background-color: #f5f5f5;
        padding: 1.5rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .analysis-box {
        background-color: #f0f7ff;
        padding: 1.5rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .status-box {
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 1rem;
        text-align: center;
    }
    .status-online {
        background-color: #c8e6c9;
        color: #2e7d32;
    }
    .status-offline {
        background-color: #ffcdd2;
        color: #c62828;
    }
    .plagiarism-high {
        background-color: #ffcdd2;
        color: #c62828;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .plagiarism-medium {
        background-color: #fff9c4;
        color: #ff6f00;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .plagiarism-low {
        background-color: #c8e6c9;
        color: #2e7d32;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .ai-warning {
        background-color: #ffcdd2;
        color: #c62828;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .step-container {
        border-left: 2px solid #1E88E5;
        padding-left: 20px;
        margin-bottom: 20px;
    }
    .step-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 10px;
    }
    .step-content {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Define our backend-like functions directly in Streamlit

class PlagiarismResult:
    def __init__(self, score: float, ai_generated: bool, ai_analysis: Dict[str, Any], similarity_scores: List[float] = []):
        self.score = score
        self.ai_generated = ai_generated
        self.ai_analysis = ai_analysis
        self.similarity_scores = similarity_scores

class AssignmentResponse:
    def __init__(self, student_name: str, grade: str, feedback: str, analysis: Optional[str] = None, 
                 document_id: Optional[str] = None, file_id: Optional[str] = None, 
                 plagiarism: Optional[PlagiarismResult] = None, success: bool = True):
        self.student_name = student_name
        self.grade = grade
        self.feedback = feedback
        self.analysis = analysis
        self.document_id = document_id
        self.file_id = file_id
        self.plagiarism = plagiarism
        self.success = success

def check_text_assignment(student_name: str, question: str, answer: str, reference_material: str = ""):
    """
    Check a text-based assignment submission.
    """
    logger.info(f"Checking text assignment for student: {student_name}")
    
    try:
        # Step 1: Check for plagiarism and AI-generated content
        answer_text = answer
        
        # Create knowledge base from reference material if available
        knowledge_base_texts = []
        if reference_material:
            knowledge_base_texts.append(reference_material)
        
        # Get AI content analysis first (includes perplexity and burstiness)
        ai_analysis = analyze_ai_content(answer_text)
        ai_result_text = ai_analysis['result']
        
        # Now calculate plagiarism score (which also uses perplexity)
        plagiarism_score, similarity_scores = calculate_plagiarism(answer_text, knowledge_base_texts)
        
        # More aggressive AI detection logic - use OR instead of AND
        # Detect AI content if:
        # 1. The text pattern analysis suggests AI-generated content OR
        # 2. The statistical score is above our lowered threshold of 20%
        is_ai_generated = "AI Generated" in ai_result_text or plagiarism_score > 20
        
        # Log more detailed detection info
        logger.info(f"Detailed AI detection - Score: {plagiarism_score:.2f}%, AI result: {ai_result_text}, Final decision: {is_ai_generated}")
        
        # Create plagiarism result
        plagiarism_result = PlagiarismResult(
            score=plagiarism_score,
            ai_generated=is_ai_generated,
            ai_analysis=ai_analysis,
            similarity_scores=similarity_scores
        )
        
        logger.info(f"Plagiarism score: {plagiarism_score:.2f}%, AI-generated: {is_ai_generated}")
        
        # Step 2: Only proceed with assignment checking if not flagged as AI-generated with high plagiarism
        if is_ai_generated and plagiarism_score > 50:  # Lowered from 60 to catch more AI content
            # For highly suspicious content, return early with a warning
            return AssignmentResponse(
                student_name=student_name,
                grade="Failed",
                feedback="This submission appears to be generated by AI tools or contains significant plagiarism. Our analysis indicates unusual language patterns. Please submit original work.",
                analysis="Automatic grading skipped due to academic integrity concerns. The text demonstrates unusual perplexity and burstiness patterns consistent with AI-generated text.",
                plagiarism=plagiarism_result,
                success=False
            )
        
        # Step 3: Proceed with normal assignment checking
        result = checker.check_assignment(
            question=question,
            student_answer=answer,
            student_name=student_name,
            reference_material=reference_material
        )
        
        # Step 4: Return combined results
        return AssignmentResponse(
            student_name=student_name,
            grade=result["grade"],
            feedback=result["feedback"],
            analysis=result.get("analysis", ""),
            document_id=result.get("document_id", ""),
            plagiarism=plagiarism_result,
            success=result.get("success", True)
        )
    
    except Exception as e:
        logger.error(f"Error checking assignment: {str(e)}")
        st.error(f"Error checking assignment: {str(e)}")
        return None

def check_pdf_assignment(student_name: str, assignment_prompt: str, pdf_file, reference_material: str = ""):
    """
    Check an assignment submitted as a PDF file.
    """
    if not pdf_file.name.endswith('.pdf'):
        st.error("File must be a PDF")
        return None
    
    logger.info(f"Checking PDF assignment for student: {student_name}")
    
    try:
        # Step 1: Process the PDF file
        file_contents = pdf_file.read()
        file_bytes = io.BytesIO(file_contents)
        
        # Extract text for plagiarism check
        from PyPDF2 import PdfReader
        reader = PdfReader(file_bytes)
        extracted_text = ""
        for page in reader.pages:
            extracted_text += page.extract_text()
        
        # Reset file pointer for assignment checker
        file_bytes.seek(0)
        
        # Step 2: Check for plagiarism and AI-generated content
        knowledge_base_texts = []
        if reference_material:
            knowledge_base_texts.append(reference_material)
        
        # Get AI content analysis first (includes perplexity and burstiness)
        ai_analysis = analyze_ai_content(extracted_text)
        ai_result_text = ai_analysis['result']
        
        # Now calculate plagiarism score (which also uses perplexity)
        plagiarism_score, similarity_scores = calculate_plagiarism(extracted_text, knowledge_base_texts)
        
        # More aggressive AI detection logic - use OR instead of AND
        # Detect AI content if:
        # 1. The text pattern analysis suggests AI-generated content OR
        # 2. The statistical score is above our lowered threshold of 20%
        is_ai_generated = "AI Generated" in ai_result_text or plagiarism_score > 20
        
        # Log more detailed detection info
        logger.info(f"Detailed AI detection - Score: {plagiarism_score:.2f}%, AI result: {ai_result_text}, Final decision: {is_ai_generated}")
        
        # Create plagiarism result
        plagiarism_result = PlagiarismResult(
            score=plagiarism_score,
            ai_generated=is_ai_generated,
            ai_analysis=ai_analysis,
            similarity_scores=similarity_scores
        )
        
        logger.info(f"Plagiarism score: {plagiarism_score:.2f}%, AI-generated: {is_ai_generated}")
        
        # Step 3: Only proceed with assignment checking if not flagged as AI-generated with high plagiarism
        if is_ai_generated and plagiarism_score > 50:  # Lowered from 60 to catch more AI content
            # For highly suspicious content, return early with a warning
            return AssignmentResponse(
                student_name=student_name,
                grade="Failed",
                feedback="This submission appears to be generated by AI tools or contains significant plagiarism. Our analysis indicates unusual language patterns. Please submit original work.",
                analysis="Automatic grading skipped due to academic integrity concerns. The text demonstrates unusual perplexity and burstiness patterns consistent with AI-generated text.",
                plagiarism=plagiarism_result,
                success=False
            )
        
        # Step 4: Proceed with normal assignment checking
        result = checker.check_pdf_assignment(
            pdf_file=file_bytes,
            assignment_prompt=assignment_prompt,
            student_name=student_name,
            reference_material=reference_material
        )
        
        # Step 5: Return combined results
        return AssignmentResponse(
            student_name=student_name,
            grade=result["grade"],
            feedback=result["feedback"],
            analysis=result.get("analysis", ""),
            document_id=result.get("document_id", ""),
            file_id=result.get("file_id", ""),
            plagiarism=plagiarism_result,
            success=result.get("success", True)
        )
    
    except Exception as e:
        logger.error(f"Error checking PDF assignment: {str(e)}")
        st.error(f"Error checking PDF assignment: {str(e)}")
        return None

def display_progress(title, current_step, total_steps=3):
    """Display a simplified progress indicator for the assignment checking process."""
    # Create a progress bar
    progress_bar = st.progress(0)
    
    # Update progress bar
    progress_value = current_step / total_steps
    progress_bar.progress(progress_value)
    
    # Show status message with better visibility
    if current_step == 0:
        st.markdown("""
        <div style="background-color: #e3f2fd; color: #0d47a1; padding: 10px; border-radius: 5px; border-left: 5px solid #1976d2; margin-bottom: 10px;">
            <span style="font-weight: bold;">Starting:</span> Processing assignment submission...
        </div>
        """, unsafe_allow_html=True)
    elif current_step == 1:
        st.markdown("""
        <div style="background-color: #e3f2fd; color: #0d47a1; padding: 10px; border-radius: 5px; border-left: 5px solid #1976d2; margin-bottom: 10px;">
            <span style="font-weight: bold;">Step 1:</span> Checking for plagiarism and AI-generated content...
        </div>
        """, unsafe_allow_html=True)
    elif current_step == 2:
        st.markdown("""
        <div style="background-color: #e8f5e9; color: #1b5e20; padding: 10px; border-radius: 5px; border-left: 5px solid #43a047; margin-bottom: 10px;">
            <span style="font-weight: bold;">Step 2:</span> Analyzing and grading assignment...
        </div>
        """, unsafe_allow_html=True)
    elif current_step == 3:
        st.markdown("""
        <div style="background-color: #e8f5e9; color: #1b5e20; padding: 10px; border-radius: 5px; border-left: 5px solid #43a047; margin-bottom: 10px; font-weight: bold;">
            Assignment check complete! ✓
        </div>
        """, unsafe_allow_html=True)

def display_plagiarism_results(plagiarism_data):
    """Display plagiarism detection and AI content analysis results."""
    if not plagiarism_data:
        return
    
    # Extract metrics from the data
    score = plagiarism_data.score
    is_ai_generated = plagiarism_data.ai_generated
    ai_analysis = plagiarism_data.ai_analysis
    result_text = ai_analysis.get("result", "Unknown")
    perplexity = ai_analysis.get("perplexity", 0)
    
    # More aggressive detection in the UI - show warning based on perplexity or score
    show_ai_warning = is_ai_generated or score > 20 or "AI Generated" in result_text
    
    # Set display styles based on the score - lower thresholds to match backend
    if score > 50:  # Lowered from 60 to match more sensitive backend
        bg_color = "#ffcdd2"  # Light red
        text_color = "#c62828"  # Dark red
        ai_text = "High likelihood of AI-generated content"
    elif score > 20:  # Lowered from 30 to be more sensitive
        bg_color = "#fff9c4"  # Light yellow
        text_color = "#ff6f00"  # Dark orange
        ai_text = "Medium likelihood of AI-generated content"
    else:
        bg_color = "#c8e6c9"  # Light green
        text_color = "#2e7d32"  # Dark green
        ai_text = "Low likelihood of AI-generated content"
        # Only add "likely original work" if not AI-generated and score is very low
        if not is_ai_generated and score < 10 and "Human" in result_text:
            ai_text += " - likely original work"
    
    # Display AI generation warning based on the updated logic
    if show_ai_warning:
        warning_text = "This submission contains AI-generated content!"
        # Add explanation based on different detection criteria
        if score <= 20 and is_ai_generated:
            warning_text += " (Detected based on text patterns rather than statistical measures)"
        elif "High Confidence" in result_text:
            warning_text += " (High confidence detection)"
            
        st.markdown(f"""
        <div style="background-color: #ffcdd2; color: #c62828; padding: 1rem; border-radius: 5px; margin-bottom: 1rem; font-weight: bold;">
            <span>⚠️ {warning_text}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Display AI detection score
    st.markdown(f"""
    <div style="background-color: {bg_color}; color: {text_color}; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
        <strong>AI Content Score:</strong> {score:.2f}% - {ai_text}
    </div>
    """, unsafe_allow_html=True)
    
    # Add explanation of how the score is calculated
    with st.expander("How is AI content detected?"):
        st.markdown("""
        Our system uses multiple detection techniques:
        
        1. **Statistical analysis**: Measures text perplexity and burstiness patterns that differ between human and AI writing
        2. **Pattern recognition**: Identifies language patterns typical of large language models
        3. **Comparative analysis**: Evaluates consistency against reference materials
        
        The final score is a composite of these factors, with higher scores indicating a higher probability of AI-generated content.
        """)
        
        # Show the specific values that contributed to the decision
        st.markdown("### Detection Values")
        st.markdown(f"- **Perplexity**: {perplexity:.2f}")
        st.markdown(f"- **Pattern Analysis Result**: {result_text}")
        st.markdown(f"- **Final Detection**: {'AI-Generated' if is_ai_generated else 'Likely Human'}")

def text_assignment_tab():
    """UI for submitting text-based assignments"""
    st.markdown("<h2 class='sub-header'>Text Assignment Checker</h2>", unsafe_allow_html=True)
    
    # Create form for assignment submission
    with st.form(key="text_assignment_form"):
        student_name = st.text_input("Student Name", placeholder="Enter your full name")
        
        # Assignment question/prompt
        question = st.text_area(
            "Assignment Question/Prompt", 
            placeholder="Enter the assignment question or instructions here",
            height=100
        )
        
        # Student's answer
        answer = st.text_area(
            "Your Answer", 
            placeholder="Enter your complete answer here",
            height=300
        )
        
        # Reference material (optional)
        reference_material = st.text_area(
            "Reference Material (Optional)", 
            placeholder="Enter any reference material, lecture notes, or textbook content to compare against",
            height=150
        )
        
        submit_button = st.form_submit_button("Submit Assignment")
    
    # Process the submission when button is clicked
    if submit_button:
        if not student_name or not question or not answer:
            st.error("Please fill in all required fields (Student Name, Question, and Answer)")
            return
        
        # Show progress indicator
        display_progress("Processing Assignment", 0)
        
        # Process submission
        with st.spinner("Processing your assignment..."):
            # Step 1: Check for plagiarism
            time.sleep(1)  # Simulated delay
            display_progress("Checking Plagiarism", 1)
            
            # Step 2: Grade assignment
            time.sleep(1)  # Simulated delay
            display_progress("Grading Assignment", 2)
            
            # Call backend function directly
            result = check_text_assignment(
                student_name=student_name,
                question=question,
                answer=answer,
                reference_material=reference_material
            )
            
            # Step 3: Complete and show results
            display_progress("Completed", 3)
            
            if result:
                display_results(result)

def pdf_assignment_tab():
    """UI for submitting PDF assignments"""
    st.markdown("<h2 class='sub-header'>PDF Assignment Checker</h2>", unsafe_allow_html=True)
    
    # Create form for PDF submission
    with st.form(key="pdf_assignment_form"):
        student_name = st.text_input("Student Name", placeholder="Enter your full name")
        
        # Assignment prompt
        assignment_prompt = st.text_area(
            "Assignment Question/Prompt", 
            placeholder="Enter the assignment question or instructions here",
            height=100
        )
        
        # PDF file upload
        pdf_file = st.file_uploader("Upload Assignment PDF", type=["pdf"])
        
        # Reference material (optional)
        reference_material = st.text_area(
            "Reference Material (Optional)", 
            placeholder="Enter any reference material, lecture notes, or textbook content to compare against",
            height=150
        )
        
        submit_button = st.form_submit_button("Submit Assignment")
    
    # Process the submission when button is clicked
    if submit_button:
        if not student_name or not assignment_prompt or not pdf_file:
            st.error("Please fill in all required fields (Student Name, Assignment Prompt, and PDF file)")
            return
        
        # Show progress indicator
        display_progress("Processing PDF Assignment", 0)
        
        # Process submission
        with st.spinner("Processing your PDF assignment..."):
            # Step 1: Check for plagiarism
            time.sleep(1)  # Simulated delay
            display_progress("Checking Plagiarism", 1)
            
            # Step 2: Grade assignment
            time.sleep(1)  # Simulated delay
            display_progress("Grading Assignment", 2)
            
            # Call backend function directly
            result = check_pdf_assignment(
                student_name=student_name,
                assignment_prompt=assignment_prompt,
                pdf_file=pdf_file,
                reference_material=reference_material
            )
            
            # Step 3: Complete and show results
            display_progress("Completed", 3)
            
            if result:
                display_results(result)

def display_results(result):
    """Display the assignment checking results"""
    st.markdown("<h2 class='result-header'>Assignment Results</h2>", unsafe_allow_html=True)
    
    # First show the plagiarism check results
    st.markdown("<h3>Plagiarism & AI Content Analysis</h3>", unsafe_allow_html=True)
    display_plagiarism_results(result.plagiarism)
    
    # Then show the grade in a prominent way
    st.markdown("<h3>Grade</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="grade-display">
        {result.grade}
    </div>
    """, unsafe_allow_html=True)
    
    # Show feedback with improved formatting
    st.markdown("<h3>Feedback</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="feedback-box">
        {result.feedback}
    </div>
    """, unsafe_allow_html=True)
    
    # Show detailed analysis in an expander
    if result.analysis:
        with st.expander("Detailed Analysis"):
            st.markdown(f"""
            <div class="analysis-box">
                {result.analysis}
            </div>
            """, unsafe_allow_html=True)
    
    # Add download button for the results as JSON
    if st.button("Download Results"):
        # Convert result to dict for JSON export
        result_data = {
            "student_name": result.student_name,
            "grade": result.grade,
            "feedback": result.feedback,
            "analysis": result.analysis,
            "plagiarism_score": result.plagiarism.score if result.plagiarism else 0,
            "ai_generated": result.plagiarism.ai_generated if result.plagiarism else False,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # Convert to JSON
        json_result = json.dumps(result_data, indent=2)
        # Create a download button
        st.download_button(
            label="Download Results as JSON",
            data=json_result,
            file_name=f"assignment_result_{result.student_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def main():
    # Display header
    st.markdown("<h1 class='main-header'>AI Teacher Assistant</h1>", unsafe_allow_html=True)
    
    # Add descriptive text
    st.markdown("""
    This tool helps teachers grade assignments and check for plagiarism or AI-generated content.
    Submit either a text-based assignment or upload a PDF document to get started.
    """)
    
    # Sidebar information
    with st.sidebar:
        st.markdown("## About")
        st.markdown("""
        **AI Teacher Assistant**
        
        This application uses advanced AI to:
        - Grade student assignments
        - Detect plagiarism
        - Identify AI-generated content
        - Provide detailed feedback
        
        No separate backend required - all processing happens within Streamlit!
        """)
        
        # Show environment status
        st.markdown("### Environment Status")
        
        # Always show as online since everything is integrated
        st.markdown("""
        <div class="status-box status-online">
            Status: ACTIVE
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Important Notes")
        st.markdown("""
        - Processing times vary based on assignment length
        - Your data privacy is protected
        - For educational use only
        """)
    
    # Create tabs for different submission types
    tab1, tab2 = st.tabs(["Text Assignment", "PDF Assignment"])
    
    with tab1:
        text_assignment_tab()
    
    with tab2:
        pdf_assignment_tab()

if __name__ == "__main__":
    main() 