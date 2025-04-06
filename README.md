# AI Teacher Assistant

An intelligent application that uses AI to grade assignments, detect plagiarism, and identify AI-generated content.

## Features

- **Assignment Grading**: Automatically grades student assignments using AI
- **Plagiarism Detection**: Detects similarities to reference materials
- **AI Content Detection**: Identifies content likely generated by AI tools
- **Detailed Feedback**: Provides comprehensive feedback on student work
- **PDF Support**: Works with both text and PDF submissions

## Setup Instructions

### Prerequisites

- Python 3.9+ installed
- Google API key for Gemini AI model

### Installation

1. Clone this repository
   ```
   git clone https://github.com/yourusername/ai-teacher-assistant.git
   cd ai-teacher-assistant
   ```

2. Create a virtual environment
   ```
   python -m venv venv
   ```

3. Activate the virtual environment
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

4. Install dependencies
   ```
   pip install -r requirements.txt
   ```

5. Create a `.env` file in the root directory with your Google API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

### Running Locally

Start the Streamlit application:
```
streamlit run streamlit_app.py
```

The application will be available at http://localhost:8501

## Deploying to Streamlit Cloud

This application is designed to be easily deployed on Streamlit Cloud:

1. Push your code to a GitHub repository
2. Log in to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app, pointing to your GitHub repository
4. Set the main file path to `streamlit_app.py`
5. Add your `GOOGLE_API_KEY` as a secret in the Streamlit Cloud dashboard
6. Deploy!

## File Structure

- `streamlit_app.py`: Main application file with both UI and processing logic
- `AssignmentChecker.py`: Core checker functionality with Gemini AI integration
- `assistant/`: Helper modules for functionality like plagiarism detection
- `vector_db/`: Storage for vector embeddings 
- `.streamlit/`: Configuration for Streamlit appearance

## Usage

1. Enter the student name and assignment details
2. Paste the assignment text or upload a PDF
3. Add any reference materials for plagiarism comparison
4. Submit and wait for the AI to process
5. Review the grading, plagiarism detection, and feedback
6. Download the results if needed

## Notes

- Processing time varies based on assignment length
- PDF files are automatically parsed for text content
- The application now runs entirely on Streamlit for easy deployment
