import streamlit as st
import requests
import json
import io
import os
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime

# Configuration
API_URL = "http://127.0.0.1:8000"  # FastAPI backend URL

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

def check_api_status():
    """Check if the FastAPI backend is running."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def display_server_status():
    """Display the server status in the sidebar."""
    api_status = check_api_status()
    status_class = "status-online" if api_status else "status-offline"
    status_text = "ONLINE" if api_status else "OFFLINE"
    
    st.sidebar.markdown(f"""
    <div class="status-box {status_class}">
        Server Status: {status_text}
    </div>
    """, unsafe_allow_html=True)
    
    if not api_status:
        st.sidebar.warning("""
        The backend server appears to be offline. 
        - Check if uvicorn is running on port 8000
        - Make sure there are no firewall issues
        - Try refreshing the page
        """)
        
        # Add a refresh button for convenience
        if st.sidebar.button("Retry Connection"):
            st.rerun()
    
    return api_status

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
    score = plagiarism_data.get("score", 0)
    is_ai_generated = plagiarism_data.get("ai_generated", False)
    ai_analysis = plagiarism_data.get("ai_analysis", {})
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
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="color: #1565C0;">How AI Content Detection Works</h3>
        <p style="color: #333333;">
        This system uses two key metrics to identify potential AI-generated content:
        </p>
        <ul style="color: #333333;">
            <li><strong>Perplexity:</strong> Measures how predictable the text is. AI-generated content typically has lower perplexity (more predictable patterns).</li>
            <li><strong>Burstiness:</strong> Measures variation in word usage. AI writing often shows different patterns of word repetition than human writing.</li>
        </ul>
        <p style="color: #333333;">
        Lower perplexity combined with unusual burstiness patterns suggests potential AI-generated content.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create visual representation of AI analysis
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <h3 style="color: #1565C0;">AI Content Analysis Metrics</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Show explanation of the result
        ai_result_explanation = ""
        if "AI Generated" in result_text:
            if score < 20:
                ai_result_explanation = " (Low confidence - may be a false positive)"
            else:
                ai_result_explanation = " (High confidence)"
        
        st.write(f"**Result:** {result_text}{ai_result_explanation}")
        
        metrics = {
            "Perplexity": ai_analysis.get("perplexity", 0),
            "Burstiness": ai_analysis.get("burstiness", 0)
        }
        
        # Create DataFrame for the metrics
        metrics_df = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value'])
        st.dataframe(metrics_df, hide_index=True)
        
        # Add an interpretation guide
        if perplexity < 100:
            perplexity_interp = "Very low perplexity - highly indicative of AI-generated text"
        elif perplexity < 500:
            perplexity_interp = "Low perplexity - potentially AI-generated text"
        elif perplexity < 1000:
            perplexity_interp = "Medium perplexity - could be human or AI text"
        else:
            perplexity_interp = "High perplexity - likely human-written text"
            
        st.write(f"**Perplexity interpretation:** {perplexity_interp}")
    
    with col2:
        # Plot the metrics
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.bar(metrics.keys(), metrics.values(), color=['#1E88E5', '#43A047'])
        ax.set_title('AI Detection Metrics')
        ax.set_ylabel('Value')
        ax.grid(axis='y', alpha=0.3)
        st.pyplot(fig)

def text_assignment_tab():
    """UI for submitting text assignments."""
    st.markdown('<p class="sub-header">Text Assignment Submission</p>', unsafe_allow_html=True)
    
    # Form for text assignment
    with st.form("text_assignment_form"):
        student_name = st.text_input("Student Name", placeholder="Enter student name")
        question = st.text_area("Assignment Question", placeholder="Enter the assignment question or prompt", height=150)
        answer = st.text_area("Student Answer", placeholder="Enter the student's answer", height=300)
        reference_material = st.text_area("Reference Material (Optional)", placeholder="Enter any reference material to compare against", height=150)
        
        submit_button = st.form_submit_button("Check Assignment")
    
    if submit_button:
        if not student_name or not question or not answer:
            st.error("Please fill in all required fields.")
            return
        
        # Show initial status
        st.info("Processing assignment submission...")
        display_progress("Assignment Check", 0, 3)
        
        # Prepare request data
        data = {
            "student_name": student_name,
            "question": question,
            "answer": answer,
            "reference_material": reference_material
        }
        
        try:
            # Step 1: Start plagiarism check
            display_progress("Assignment Check", 1, 3)
            
            # Send request to FastAPI backend
            with st.spinner("Checking assignment..."):
                response = requests.post(
                    f"{API_URL}/check-text-assignment",
                    json=data,
                    headers={"Content-Type": "application/json"},
                    timeout=180  # 3-minute timeout for LLM processing
                )
            
            # Step 2: Analysis and grading
            display_progress("Assignment Check", 2, 3)
            
            # Step 3: Display results
            display_progress("Assignment Check", 3, 3)
            
            if response.status_code == 200:
                result = response.json()
                
                # Display plagiarism results first
                if "plagiarism" in result:
                    display_plagiarism_results(result["plagiarism"])
                
                # Then display grading results
                display_results(result)
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            st.error(f"Error connecting to server: {str(e)}")

def pdf_assignment_tab():
    """UI for submitting PDF assignments."""
    st.markdown('<p class="sub-header">PDF Assignment Submission</p>', unsafe_allow_html=True)
    
    # Form for PDF assignment
    with st.form("pdf_assignment_form"):
        student_name = st.text_input("Student Name", placeholder="Enter student name")
        assignment_prompt = st.text_area("Assignment Instructions", placeholder="Enter the assignment instructions", height=150)
        reference_material = st.text_area("Reference Material (Optional)", placeholder="Enter any reference material to compare against", height=150)
        uploaded_file = st.file_uploader("Upload PDF Assignment", type=["pdf"])
        
        submit_button = st.form_submit_button("Check PDF Assignment")
    
    if submit_button:
        if not student_name or not assignment_prompt or not uploaded_file:
            st.error("Please fill in all required fields and upload a PDF file.")
            return
        
        # Show initial status
        st.info("Processing PDF submission...")
        display_progress("PDF Assignment Check", 0, 3)
        
        try:
            # Prepare form data
            form_data = {
                "student_name": student_name,
                "assignment_prompt": assignment_prompt,
                "reference_material": reference_material
            }
            
            files = {
                "pdf_file": (uploaded_file.name, uploaded_file, "application/pdf")
            }
            
            # Step 1: Plagiarism check
            display_progress("PDF Assignment Check", 1, 3)
            
            # Send request to FastAPI backend
            with st.spinner("Processing PDF and checking assignment... This may take several minutes."):
                response = requests.post(
                    f"{API_URL}/check-pdf-assignment",
                    data=form_data,
                    files=files,
                    timeout=300  # 5-minute timeout for PDF processing
                )
            
            # Step 2: Analysis and grading
            display_progress("PDF Assignment Check", 2, 3)
            
            # Step 3: Display results
            display_progress("PDF Assignment Check", 3, 3)
            
            if response.status_code == 200:
                result = response.json()
                
                # Display plagiarism results first
                if "plagiarism" in result:
                    display_plagiarism_results(result["plagiarism"])
                
                # Then display grading results
                display_results(result)
            else:
                st.error(f"Error: {response.status_code} - {response.text}")
        except requests.RequestException as e:
            st.error(f"Error connecting to server: {str(e)}")

def display_results(result):
    """Display the assignment checking results."""
    st.markdown('<p class="result-header">Assignment Results</p>', unsafe_allow_html=True)
    
    # Display grade with dark text on light background
    st.markdown(f"""
    <div class="grade-display" style="color: #000000; background-color: #f0f7ff;">
        <strong>Grade:</strong> {result.get('grade', 'No grade available')}
    </div>
    """, unsafe_allow_html=True)
    
    # Display feedback with dark text on light background
    st.markdown('<p class="sub-header">Feedback</p>', unsafe_allow_html=True)
    
    # Apply styling to ensure text is visible
    feedback_text = result.get('feedback', 'No feedback available').replace('\n', '<br>')
    st.markdown(f"""
    <div class="feedback-box" style="color: #000000; background-color: #f5f5f5;">
        {feedback_text}
    </div>
    """, unsafe_allow_html=True)
    
    # Display analysis if available with dark text on light background
    if result.get('analysis'):
        with st.expander("View Detailed Analysis", expanded=False):
            analysis_text = result.get('analysis', '').replace('\n', '<br>')
            st.markdown(f"""
            <div class="analysis-box" style="color: #000000; background-color: #f0f7ff;">
                {analysis_text}
            </div>
            """, unsafe_allow_html=True)
    
    # Save results option
    if st.button("Save Results"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"results_{result.get('student_name', 'student').replace(' ', '_')}_{timestamp}.json"
        
        # Create results directory if it doesn't exist
        os.makedirs("results", exist_ok=True)
        
        # Save results to file
        with open(f"results/{filename}", "w") as f:
            json.dump(result, f, indent=4)
        
        st.success(f"Results saved to results/{filename}")
        
        # Offer download
        with open(f"results/{filename}", "r") as f:
            st.download_button(
                label="Download Results",
                data=f,
                file_name=filename,
                mime="application/json"
            )

# Main application
def main():
    # Display header
    st.markdown('<h1 class="main-header">AI Teacher Assistant</h1>', unsafe_allow_html=True)
    
    # Check API status and display in sidebar
    api_online = display_server_status()
    
    # Sidebar information
    st.sidebar.markdown("## About")
    st.sidebar.markdown("""
    The AI Teacher Assistant helps educators automate assignment grading and feedback. 
    Upload text or PDF assignments and receive AI-generated feedback and grades.
    """)
    
    st.sidebar.markdown("## How it works")
    st.sidebar.markdown("""
    1. Submit your assignment (Text or PDF)
    2. AI checks for plagiarism and AI-generated content
    3. Assignment is analyzed and graded 
    4. Detailed feedback is generated
    5. Results are displayed with option to save
    """)
    
    # Instructions for using the app in the sidebar
    st.sidebar.markdown("## Instructions")
    st.sidebar.markdown("""
    **For Text Assignments:**
    - Enter student name, question, and answer
    - Optionally provide reference material
    - Click "Check Assignment"
    
    **For PDF Assignments:**
    - Enter student name and assignment instructions
    - Upload a PDF file
    - Optionally provide reference material
    - Click "Check PDF Assignment"
    """)
    
    if api_online:
        # Create tabs
        tab1, tab2 = st.tabs(["Text Assignment", "PDF Assignment"])
        
        with tab1:
            text_assignment_tab()
        
        with tab2:
            pdf_assignment_tab()
    else:
        st.error("""
        The backend server is currently offline. Please start the FastAPI server with:
        ```
        uvicorn app:app --reload
        ```
        """)

if __name__ == "__main__":
    main() 