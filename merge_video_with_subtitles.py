import os
import subprocess

def merge_video_with_subtitles(video_path, subtitles_path, output_path):
    """
    Merge a video file with subtitles using FFmpeg.

    Args:
        video_path (str): Path to the input video file.
        subtitles_path (str): Path to the subtitles (.srt) file.
        output_path (str): Path to save the output video.

    Returns:
        str: Path to the merged video.
    """
    try:
        # FFmpeg command to merge video and subtitles
        command = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"subtitles={subtitles_path}",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-strict", "experimental",
            output_path
        ]

        # Run the FFmpeg command
        subprocess.run(command, check=True)

        # Return the output path if successful
        return output_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error merging video and subtitles: {e}")

# Example usage
if __name__ == "__main__":
    video = "temp_video.mp4"
    subtitles = "subtitles.srt"
    output = "output_video.mp4"

    merged_video = merge_video_with_subtitles(video, subtitles, output)
    print(f"Merged video saved at: {merged_video}")
