import streamlit as st
import requests
import os
import subprocess

# Set FastAPI endpoint
FASTAPI_ENDPOINT = "https://samay-video-subtitle.onrender.com/upload-video"



# Helper function to merge video and subtitles
def merge_video_with_subtitles(video_path, subtitles_path, output_path):
    try:
        command = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"subtitles={subtitles_path}",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-strict", "experimental",
            output_path
        ]
        subprocess.run(command, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error merging video and subtitles: {e}")

# Streamlit UI
st.title("Video Subtitle Generator and Merger")
st.write("Upload a video file to generate subtitles and merge them into the video.")

# File uploader
uploaded_file = st.file_uploader("Upload your video file (MP4, MKV, etc.)", type=["mp4", "mkv", "avi", "mov"])

if uploaded_file:
    st.video(uploaded_file)  # Preview the uploaded video
    st.write("Processing your video... Please wait.")

    # Save the uploaded file temporarily
    with open("temp_video.mp4", "wb") as f:
        f.write(uploaded_file.read())

    # Send video to FastAPI backend
    with open("temp_video.mp4", "rb") as f:
        response = requests.post(FASTAPI_ENDPOINT, files={"file": f})

    # Handle the response
    if response.status_code == 200:
        # Save the subtitles file
        with open("subtitles.srt", "wb") as srt_file:
            srt_file.write(response.content)

        st.success("Subtitles generated successfully!")
        st.download_button(
            label="Download Subtitles (SRT)",
            data=response.content,
            file_name="subtitles.srt",
            mime="text/plain",
        )

        # Merge subtitles into the video
        if st.button("Merge Subtitles with Video"):
            try:
                merged_video_path = "output_video.mp4"
                merge_video_with_subtitles("temp_video.mp4", "subtitles.srt", merged_video_path)
                st.success("Video merged successfully!")

                # Provide a download link for the merged video
                with open(merged_video_path, "rb") as video_file:
                    st.download_button(
                        label="Download Merged Video",
                        data=video_file,
                        file_name="output_video.mp4",
                        mime="video/mp4",
                    )
            except Exception as e:
                st.error(f"Error merging video and subtitles: {e}")

        # Clean up temporary files
        os.remove("temp_video.mp4")
        os.remove("subtitles.srt")
    else:
        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

# Footer
st.write("Powered by Whisper, FFmpeg, and Streamlit")
