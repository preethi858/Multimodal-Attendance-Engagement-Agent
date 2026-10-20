# EduSense AI: Multimodal Attendance & Engagement Agent

## Project Overview
EduSense AI is a classroom assistance dashboard built using Python and Streamlit. It helps teachers record attendance, monitor basic classroom presence through a camera, estimate classroom engagement, and view session reports and analytics.

This project runs locally on the computer and is designed as a prototype for classroom assistance.

## Features
- **Attendance Management:** Record students' attendance manually and download attendance reports.
- **Camera-Based Person Detection:** Uses OpenCV to detect people visible to the camera.
- **Presence Duration:** Displays an estimated duration based on continuous person detection.
- **Engagement Dashboard:** Allows teachers to enter an estimated classroom engagement score.
- **Session Reports:** Save and download classroom session summaries.
- **Analytics Dashboard:** View attendance charts and engagement trends.
- **Project Summary:** Generate and download a project summary.

## Technologies Used
- Python
- Streamlit
- Pandas
- OpenCV
- Streamlit-WebRTC
- SQLite is not required for the current prototype; reports are stored in CSV files.

## Project Structure
```text
Multimodal-Attendance-Engagement-Agent/
├── app.py
├── camera.py
├── requirements.txt
├── README.md
├── .gitignore
├── attendance.csv        # Generated when attendance is saved
└── session_reports.csv   # Generated when session reports are saved
```

## Installation and Setup

### 1. Clone the repository
```bash
git clone https://github.com/preethi858/Multimodal-Attendance-Engagement-Agent.git
cd Multimodal-Attendance-Engagement-Agent
```

### 2. Install dependencies
```bash
python -m pip install -r requirements.txt
```

### 3. Run the application
```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

## How to Use
1. Enter the classroom and teacher details.
2. Enter student names and record attendance.
3. Allow camera access to test basic person detection.
4. Enter an estimated engagement score.
5. Save the classroom session report.
6. Explore the analytics and download available reports.

## Limitations
- Camera-based detection identifies visible people; it does not recognize individual student identities.
- Attendance is recorded manually and is not automatically assigned to detected individuals.
- Engagement scores are entered manually and are not automatically measured by AI.
- Person detection may be affected by lighting, camera angle, and visibility.
- CSV reports are stored locally on the computer.

## Future Improvements
- Improve person detection and classroom presence tracking.
- Add secure teacher login.
- Add privacy-conscious student identification workflows.
- Develop more detailed classroom analytics.

## Author
Preethi G. V.

## License
This project is intended for educational and demonstration purposes.
