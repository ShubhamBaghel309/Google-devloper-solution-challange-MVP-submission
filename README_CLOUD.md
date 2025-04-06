# AI Teacher Assistant - Streamlit Cloud Demo

This is a demonstration version of the AI Teacher Assistant application specifically modified to run on Streamlit Cloud.

## About This Demo

Due to dependency limitations on Streamlit Cloud (specifically older SQLite version and potential issues with some AI libraries), this version provides a simplified demonstration of the application's interface and workflow, without the actual AI-powered grading functionality.

### Features in This Demo

- Complete user interface matching the full application
- Simulated grading and feedback workflow
- PDF and text submission support
- Result display with sample feedback

### What's Different from the Full Version?

- No actual AI processing or grading (simulated responses)
- No ChromaDB vector database integration
- No Google Gemini AI integration
- No real plagiarism detection

## Running This Demo

You can access the live demo here:
[https://ai-teacher-assistant-demo.streamlit.app](https://ai-teacher-assistant-demo.streamlit.app)

Or run it locally with:

```bash
streamlit run streamlit_app_cloud.py
```

## Setting Up the Full Version Locally

To run the complete version with all AI capabilities:

1. Clone the repository
   ```
   git clone https://github.com/yourusername/ai-teacher-assistant.git
   cd ai-teacher-assistant
   ```

2. Install full dependencies
   ```
   pip install -r requirements.txt
   ```

3. Set up your Google API key in a `.env` file
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```

4. Run the full version
   ```
   streamlit run streamlit_app.py
   ```

## Deployment Notes

This demo version is specifically designed to work around the following Streamlit Cloud limitations:

1. **SQLite Version**: Streamlit Cloud has an older SQLite version (< 3.35.0) which is incompatible with ChromaDB
2. **Dependency Conflicts**: Some AI libraries may have complex dependencies that are difficult to satisfy in the cloud environment
3. **Environment Variables**: API keys need to be set up as Streamlit secrets when deploying

## Full Version Features

The complete application includes:

- **Intelligent Assignment Grading**: Automated assessment using Google's Gemini AI model
- **Plagiarism Detection**: Detects similarities to reference materials and AI-generated content
- **Detailed Feedback Generation**: Numerical grades with structured, actionable feedback
- **Vector Database Storage**: Efficient assignment storage and retrieval using ChromaDB 