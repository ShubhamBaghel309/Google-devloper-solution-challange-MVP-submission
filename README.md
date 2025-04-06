# AI Teacher Assistant (MVP)

![GDSC Solution Challenge](https://img.shields.io/badge/GDSC-Solution%20Challenge%202024-blue)
![SDG 4](https://img.shields.io/badge/SDG-4%20Quality%20Education-red)

## 📚 Project Overview

AI Teacher Assistant is an intelligent system designed to automate assignment grading and provide personalized feedback to students. By leveraging advanced AI technologies, we aim to reduce teacher workload while ensuring students receive timely, detailed, and constructive feedback on their work.

### 🎯 Addressing SDG 4: Quality Education

This project directly contributes to the UN Sustainable Development Goal 4 (Quality Education) by:

- Reducing teacher workload, enabling more time for personal interaction with students
- Providing equitable access to quality feedback for all students
- Enabling personalized learning at scale
- Making education more accessible and efficient

## 🚀 Getting Started

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ai-teacher-assistant.git
   cd ai-teacher-assistant
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file with your Google API key
   ```bash
   GOOGLE_API_KEY=your_api_key_here
   ```

4. **Run the backend server:**
   ```bash
   uvicorn app:app --reload
   ```

5. **Run the frontend application:**
   ```bash
   streamlit run streamlit_app.py
   ```

That's it! Your AI Teacher Assistant should now be running with the backend available at http://localhost:8000 and the frontend at http://localhost:8501.

## 📁 Project Structure

```
ai-teacher-assistant/
│
├── app.py                   # FastAPI backend server
├── streamlit_app.py         # Streamlit frontend application
├── AssignmentChecker.py     # Core assignment checking logic
├── demo_plagiarism_checker.py # Plagiarism detection functionality
│
├── assistant/               # LangGraph agents and workflow components
│
├── vector_db/              # ChromaDB vector database components
│
├── tests/                  # Test suite
│
├── requirements.txt        # Python dependencies
└── .env                    # Environment variables (create this file)
```

## ✨ Current Features

- **Intelligent Assignment Grading**: Automated assessment using Google's Gemini-2.0-Flash model
- **Multi-stage Assessment Pipeline**: Three-node workflow (research → analyze → grade)
- **Detailed Feedback Generation**: Numerical grades with structured, actionable feedback
- **Multiple Format Support**: Handles both text assignments and PDF submissions
- **Knowledge Storage**: Vector database (ChromaDB) for efficient assignment storage and retrieval

## 🚀 Planned Enhancements

### MVP Features 

1. **Complete Frontend UI Using Streamlit**
   - Submission interface
   - Results visualization

2. **Plagiarism Detection**
   - Vector similarity comparison
   - Plagiarism measures used - Perplexity and Burstiness

3. **Enhanced AI Grading**
   - Using LangGraph to create a research agent which researches based on answers given by the student, then analyzes them and provides detailed feedback reports
   - Confidence scores for evaluations
   - Teacher review/override capability

4. **About Section** 
    - Explains the complete workflow
    

### Advanced Future Features 

- **Voice Teacher Assistant Interface** using Google Text-to-Speech and Speech-to-Text
- **Advanced Plagiarism Detection** with external source checking
- **Learning Analytics Dashboard** to track progress and identify knowledge gaps
- **Collaborative Feedback** with peer review capabilities
- **LMS Integration** with Canvas, Google Classroom, and Moodle
- **Automatic Assignment Generation** based on the subject chosen by the teacher

## 🏗️ Technical Architecture

### Backend
- FastAPI for API endpoints
- LangGraph for AI workflow management
- Google Gemini AI for natural language processing
- ChromaDB for vector storage

### Frontend
- Currently using Streamlit but will develop a more scalable frontend using React with Material UI for Google-like design language
- Data visualization components for feedback display
- Responsive design for mobile access

### Google Services Integration
- Gemini API for advanced language processing

## 💻 Running Tests

To run the test suite:
```bash
python -m pytest tests/ -v
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
