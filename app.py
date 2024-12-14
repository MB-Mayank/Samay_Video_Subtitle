from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import os
import tempfile
import subprocess
import mimetypes
import logging

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def is_valid_video(file: UploadFile):
    """
    Validate if the uploaded file is a video based on MIME type and file extension.
    """
    mime_type = file.content_type
    file_extension = os.path.splitext(file.filename)[-1].lower()

    # Fallback to mimetypes module if content_type is None
    if mime_type is None:
        mime_type, _ = mimetypes.guess_type(file.filename)

    logger.debug(f"Uploaded file MIME type: {mime_type}, File extension: {file_extension}")

    # Check MIME type and file extension
    valid_video_types = ["video/mp4", "video/avi", "video/mov", "video/mkv"]
    valid_extensions = [".mp4", ".avi", ".mov", ".mkv"]
    return mime_type in valid_video_types or file_extension in valid_extensions

@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    try:
        # Debug: Log uploaded file details
        logger.debug(f"Uploaded file: {file.filename}, Content-Type: {file.content_type}")

        # Validate file type
        if not is_valid_video(file):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a video file.")

        # Save the uploaded video temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp:
            temp.write(await file.read())
            temp_path = temp.name
        logger.debug(f"Temporary video file saved at: {temp_path}")

        # Generate subtitles for the video
        subtitles_path = generate_subtitles(temp_path)

        # Clean up the temporary video file
        os.remove(temp_path)
        logger.debug(f"Temporary video file deleted: {temp_path}")

        # Return the subtitle file for download
        return FileResponse(subtitles_path, media_type="application/octet-stream", filename=os.path.basename(subtitles_path))

    except HTTPException as http_exc:
        logger.error(f"HTTP exception: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the video.")

def generate_subtitles(video_path):
    """
    Generate subtitles for a given video using Whisper.
    """
    try:
        # Define the expected subtitles path
        output_dir = os.path.dirname(video_path)
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        subtitles_path = os.path.join(output_dir, f"{base_name}.srt")

        # Call Whisper CLI to generate subtitles
        subprocess.run(
            ["whisper", video_path, "--model", "base", "--output_format", "srt", "--output_dir", output_dir],
            check=True
        )

        # Verify if subtitles file was created
        if not os.path.exists(subtitles_path):
            logger.error(f"Subtitles file not found at: {subtitles_path}")
            raise HTTPException(status_code=500, detail="Failed to generate subtitles.")

        logger.debug(f"Subtitles generated at: {subtitles_path}")
        return subtitles_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Error generating subtitles: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate subtitles.")

@app.get("/")
def read_root():
    """
    Health check endpoint.
    """
    return {"message": "Welcome to the Video Subtitle Generator API!"}
