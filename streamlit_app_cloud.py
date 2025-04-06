import streamlit as st
import io
import time
from datetime import datetime
import json

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
</style>
""", unsafe_allow_html=True)

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
            time.sleep(2)  # Simulated delay
            display_progress("Grading Assignment", 2)
            
            # Step 3: Complete and show results
            time.sleep(1)  # Simulated delay
            display_progress("Completed", 3)
            
            # Display demo results
            display_demo_results(student_name, question, answer)

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
            time.sleep(2)  # Simulated delay
            display_progress("Grading Assignment", 2)
            
            # Step 3: Complete and show results
            time.sleep(1)  # Simulated delay
            display_progress("Completed", 3)
            
            # Display demo results with PDF info
            display_demo_results(student_name, assignment_prompt, f"PDF: {pdf_file.name}")

def display_demo_results(student_name, question, answer):
    """Display demonstration results"""
    st.markdown("<h2 class='result-header'>Assignment Results</h2>", unsafe_allow_html=True)
    
    # Show plagiarism analysis
    st.markdown("<h3>Plagiarism & AI Content Analysis</h3>", unsafe_allow_html=True)
    
    # Demo plagiarism score
    demo_score = 12.5  # Low score for demo
    
    # Display AI detection score
    st.markdown(f"""
    <div style="background-color: #c8e6c9; color: #2e7d32; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;">
        <strong>AI Content Score:</strong> {demo_score:.2f}% - Low likelihood of AI-generated content - likely original work
    </div>
    """, unsafe_allow_html=True)
    
    # Show grade in a prominent way
    st.markdown("<h3>Grade</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="grade-display">
        A- (90%)
    </div>
    """, unsafe_allow_html=True)
    
    # Sample feedback based on common patterns
    feedback = generate_demo_feedback(question, answer, student_name)
    
    # Show feedback with improved formatting
    st.markdown("<h3>Feedback</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="feedback-box">
        {feedback}
    </div>
    """, unsafe_allow_html=True)
    
    # Show detailed analysis in an expander
    with st.expander("Detailed Analysis"):
        analysis = generate_demo_analysis(question, answer)
        st.markdown(f"""
        <div class="analysis-box">
            {analysis}
        </div>
        """, unsafe_allow_html=True)
    
    # Add download button for the results as JSON
    if st.button("Download Results"):
        # Convert result to dict for JSON export
        result_data = {
            "student_name": student_name,
            "grade": "A- (90%)",
            "feedback": feedback,
            "analysis": analysis,
            "plagiarism_score": demo_score,
            "ai_generated": False,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # Convert to JSON
        json_result = json.dumps(result_data, indent=2)
        # Create a download button
        st.download_button(
            label="Download Results as JSON",
            data=json_result,
            file_name=f"assignment_result_{student_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

def generate_demo_feedback(question, answer, student_name):
    """Generate demo feedback based on submission"""
    # This is just sample feedback for the demo
    return f"""
    <p>Overall, this is an excellent submission that demonstrates strong understanding of the subject matter. Your arguments are well-structured and supported by evidence.</p>
    
    <p><strong>Strengths:</strong></p>
    <ul>
        <li>Clear organization and logical flow of ideas</li>
        <li>Effective use of relevant examples to support key points</li>
        <li>Strong critical analysis of the topic</li>
    </ul>
    
    <p><strong>Areas for Improvement:</strong></p>
    <ul>
        <li>Consider expanding on the implications of your third point</li>
        <li>Some citations could be more recent to reflect current research</li>
    </ul>
    
    <p>Keep up the good work, {student_name}!</p>
    """

def generate_demo_analysis(question, answer):
    """Generate demo detailed analysis"""
    # This is just sample analysis for the demo
    return f"""
    <h4>Content Analysis</h4>
    <p>The submission addresses all aspects of the prompt thoroughly. Key concepts are well explained and the arguments are supported with appropriate evidence. The response demonstrates comprehensive understanding of the subject matter.</p>
    
    <h4>Structure Analysis</h4>
    <p>The assignment follows a clear logical structure with a strong introduction, well-developed body paragraphs, and a conclusion that effectively synthesizes the main points. Transitions between ideas are smooth and coherent.</p>
    
    <h4>Critical Thinking</h4>
    <p>The response shows excellent critical thinking skills, with insightful analysis of multiple perspectives on the topic. The student has gone beyond surface-level understanding to explore deeper implications.</p>
    
    <h4>Language and Style</h4>
    <p>The writing is clear, concise, and academic in tone. Technical terminology is used accurately. There are minimal grammar or spelling errors.</p>
    
    <h4>Recommendations</h4>
    <p>To further improve future assignments:</p>
    <ul>
        <li>Consider incorporating more diverse sources</li>
        <li>Develop the counterarguments more fully</li>
        <li>Expand the discussion of practical applications</li>
    </ul>
    """

def main():
    # Display header
    st.markdown("<h1 class='main-header'>AI Teacher Assistant</h1>", unsafe_allow_html=True)
    
    # Add descriptive text
    st.markdown("""
    This tool helps teachers grade assignments and check for plagiarism or AI-generated content.
    Submit either a text-based assignment or upload a PDF document to get started.
    
    > **Note**: This is a demonstration version of the app for Streamlit Cloud deployment.
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
        
        This is a simplified demo version for Streamlit Cloud.
        """)
        
        # Show environment status
        st.markdown("### Environment Status")
        
        # Always show as online since everything is integrated
        st.markdown("""
        <div class="status-box status-online">
            Status: ACTIVE (DEMO MODE)
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Important Notes")
        st.markdown("""
        - This is a demonstration version
        - Full functionality requires setting up with proper dependencies
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