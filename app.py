
import os
import threading
import time
from datetime import datetime

import av
import cv2
import pandas as pd
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode


# Page Settings
st.set_page_config(
    page_title="EduSense AI",
    page_icon="🎓",
    layout="wide"
)

st.title("EduSense AI")
st.subheader("Multimodal Attendance & Engagement Agent")

st.write(
    "An AI-powered classroom assistant for attendance, "
    "engagement analysis, and teaching recommendations."
)

st.info(
    "Current prototype: manual attendance and basic camera-based "
    "person detection. Individual student identification is not available yet."
)


# Classroom Session
st.header("Classroom Session")

class_name = st.text_input("Class name", "CSE Classroom")
teacher_name = st.text_input("Teacher name", "Teacher")

duration = st.number_input(
    "Session duration (minutes)",
    min_value=1,
    max_value=300,
    value=60
)

st.write("Class:", class_name)
st.write("Teacher:", teacher_name)
st.write("Duration:", duration, "minutes")


# Student Attendance
st.header("Student Attendance")

student_names = st.text_area(
    "Enter student names (one name per line)",
    "Preethi\nStudent 2\nStudent 3\nStudent 4\nStudent 5"
)

students = [
    name.strip()
    for name in student_names.splitlines()
    if name.strip()
]

st.write("Total students:", len(students))

present_names = st.multiselect(
    "Select students who are present",
    students
)

if st.button("Save Attendance"):
    if not students:
        st.warning("Please enter at least one student name.")

    elif len(students) != len(set(students)):
        st.warning("Please remove duplicate student names.")

    else:
        # One timestamp for the complete attendance session
        session_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        attendance_records = []

        for student in students:
            status = (
                "Present"
                if student in present_names
                else "Absent"
            )

            attendance_records.append({
                "Date": session_time,
                "Class": class_name,
                "Teacher": teacher_name,
                "Student": student,
                "Status": status
            })

        new_data = pd.DataFrame(attendance_records)
        file_name = "attendance.csv"

        if os.path.exists(file_name):
            old_data = pd.read_csv(file_name)
            new_data = pd.concat(
                [old_data, new_data],
                ignore_index=True
            )

        new_data.to_csv(file_name, index=False)

        st.success("Attendance saved successfully!")

        total_count = len(students)
        present_count = len(present_names)
        absent_count = total_count - present_count

        st.write("Present:", present_count)
        st.write("Absent:", absent_count)

        st.write(
            "Attendance Percentage:",
            f"{present_count / total_count * 100:.2f}%"
        )

        st.dataframe(
            new_data[new_data["Date"] == session_time],
            use_container_width=True
        )

        with open(file_name, "rb") as file:
            st.download_button(
                "Download Attendance CSV",
                data=file,
                file_name="attendance.csv",
                mime="text/csv"
            )


# Session Overview
st.header("Session Overview")

if os.path.exists("attendance.csv"):
    saved_data = pd.read_csv("attendance.csv")

    if not saved_data.empty:
        latest_time = saved_data["Date"].max()

        latest_session = saved_data[
            saved_data["Date"] == latest_time
        ]

        total_students = len(latest_session)

        present_count = len(
            latest_session[
                latest_session["Status"] == "Present"
            ]
        )

        attendance_percentage = (
            present_count / total_students * 100
            if total_students > 0 else 0
        )

        col1, col2, col3 = st.columns(3)

        col1.metric("Students Present", present_count)

        col2.metric(
            "Attendance",
            f"{attendance_percentage:.2f}%"
        )

        col3.metric("Engagement", "Not analyzed yet")

    else:
        st.info("No attendance records found yet.")

else:
    st.info("Save attendance to see the session metrics.")


# Attendance Report
st.header("Attendance Report")

if os.path.exists("attendance.csv"):
    report_data = pd.read_csv("attendance.csv")

    if not report_data.empty:
        st.dataframe(
            report_data,
            use_container_width=True
        )
    else:
        st.info("No attendance records available.")

else:
    st.info(
        "Your attendance report will appear here "
        "after saving attendance."
    )


# Teaching Suggestions
st.header("Teaching Suggestions")

st.write(
    "Sample suggestion: Include a short interactive activity "
    "to encourage student participation."
)


# Person Detector
hog = cv2.HOGDescriptor()

hog.setSVMDetector(
    cv2.HOGDescriptor_getDefaultPeopleDetector()
)

presence_lock = threading.Lock()
presence_start = None
last_seen = 0.0
presence_seconds = 0


# Live Camera
st.header("Live Camera Feed with Person Detection")

st.write(
    "Click START to activate the webcam. Allow camera permission "
    "if your browser asks for it."
)


def video_frame_callback(frame):
    global presence_start, last_seen, presence_seconds

    img = frame.to_ndarray(format="bgr24")
    now = time.monotonic()

    # Detect people
    boxes, weights = hog.detectMultiScale(
        img,
        winStride=(4, 4),
        padding=(8, 8),
        scale=1.05
    )

    # Keep detections above the confidence threshold
    detected_boxes = []

    for box, confidence in zip(boxes, weights):
        if float(confidence) > 0.2:
            detected_boxes.append(box)

    # Draw green boxes around detected people
    for (x, y, w, h) in detected_boxes:
        cv2.rectangle(
            img,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

    # Update presence duration with a 2-second grace period
    with presence_lock:
        if detected_boxes:
            if presence_start is None:
                presence_start = now

            last_seen = now

        elif (
            presence_start is not None
            and now - last_seen > 2
        ):
            presence_start = None

        recently_present = (
            presence_start is not None
            and now - last_seen <= 2
        )

        if recently_present:
            presence_seconds = int(now - presence_start)
        else:
            presence_seconds = 0

        seconds = presence_seconds

    # Display detection count
    cv2.putText(
        img,
        f"People detected: {len(detected_boxes)}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    # Display presence status
    status = (
        "PERSON PRESENT"
        if recently_present
        else "NO PERSON DETECTED"
    )

    color = (
        (0, 255, 0)
        if recently_present
        else (0, 0, 255)
    )

    cv2.putText(
        img,
        status,
        (10, 100),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        color,
        2
    )

    # Display presence duration
    cv2.putText(
        img,
        f"Presence duration: {seconds} seconds",
        (10, 135),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

    return av.VideoFrame.from_ndarray(
        img,
        format="bgr24"
    )


webrtc_streamer(
    key="edusense-person-detection",
    mode=WebRtcMode.SENDRECV,
    video_frame_callback=video_frame_callback,
    media_stream_constraints={
        "video": True,
        "audio": False
    },
    async_processing=True
)


st.caption(
    "EduSense AI prototype | Person detection does not identify "
    "individual students or automatically verify attendance."
)

# Engagement Dashboard
st.header("Classroom Engagement")

st.write(
    "Record an estimated engagement score based on classroom "
    "participation and activities. This is a manual estimate, "
    "not an automatic measurement from the camera."
)

engagement_score = st.slider(
    "Estimated classroom engagement (%)",
    min_value=0,
    max_value=100,
    value=70
)

st.progress(engagement_score / 100)

if engagement_score >= 75:
    st.success("High engagement: Continue interactive activities.")
elif engagement_score >= 40:
    st.warning("Moderate engagement: Try asking more questions.")
else:
    st.info("Low estimated engagement: Consider a short group activity.")

st.metric("Engagement Score", f"{engagement_score}%")

# Save Classroom Session Report
st.header("Classroom Session Reports")

if st.button("Save Session Report"):
    report = {
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Class": class_name,
        "Teacher": teacher_name,
        "Duration (minutes)": duration,
        "Engagement Score (%)": engagement_score
    }

    report_df = pd.DataFrame([report])
    file_name = "session_reports.csv"

    if os.path.exists(file_name):
        old_reports = pd.read_csv(file_name)
        report_df = pd.concat(
            [old_reports, report_df],
            ignore_index=True
        )

    report_df.to_csv(file_name, index=False)

    st.success("Session report saved successfully!")

# View saved reports
st.subheader("Saved Session Reports")

if os.path.exists("session_reports.csv"):
    saved_reports = pd.read_csv("session_reports.csv")

    st.dataframe(
        saved_reports,
        use_container_width=True
    )

    with open("session_reports.csv", "rb") as file:
        st.download_button(
            "Download Session Reports",
            data=file,
            file_name="session_reports.csv",
            mime="text/csv"
        )
else:
    st.info("No session reports saved yet.")

# Analytics Dashboard
st.header("Attendance & Engagement Analytics")

# Attendance Chart
if os.path.exists("attendance.csv"):
    attendance_df = pd.read_csv("attendance.csv")

    if not attendance_df.empty:
        attendance_summary = (
            attendance_df.groupby("Status")
            .size()
            .reset_index(name="Students")
        )

        st.subheader("Attendance Summary")
        st.bar_chart(
            attendance_summary,
            x="Status",
            y="Students"
        )
    else:
        st.info("No attendance data available for the chart.")
else:
    st.info("Save attendance to display the attendance chart.")


# Engagement Chart
if os.path.exists("session_reports.csv"):
    reports_df = pd.read_csv("session_reports.csv")

    if not reports_df.empty:
        st.subheader("Engagement Scores Over Time")

        reports_df["Date"] = pd.to_datetime(
            reports_df["Date"],
            errors="coerce"
        )

        reports_df = reports_df.dropna(subset=["Date"])
        reports_df = reports_df.sort_values("Date")

        if not reports_df.empty:
            chart_data = reports_df.set_index("Date")[
                ["Engagement Score (%)"]
            ]

            st.line_chart(chart_data)
        else:
            st.info("No valid engagement dates found.")
    else:
        st.info("No session reports available for the chart.")
else:
    st.info("Save a session report to display the engagement chart.")

# Download Project Summary
st.header("Download Classroom Summary")

if st.button("Generate Summary"):
    summary = f"""
EDUSENSE AI
Multimodal Attendance & Engagement Agent

Class: {class_name}
Teacher: {teacher_name}
Session Duration: {duration} minutes
Report Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

PROJECT FEATURES
1. Manual student attendance
2. CSV attendance records
3. Live webcam person detection
4. Presence-duration estimation
5. Engagement score input
6. Teaching suggestions
7. Session reports and analytics charts

IMPORTANT NOTE
Camera-based person detection does not identify individual students.
Engagement scores are entered manually in this prototype.
"""

    st.download_button(
        "Download Project Summary",
        data=summary,
        file_name="edusense_project_summary.txt",
        mime="text/plain"
    )
