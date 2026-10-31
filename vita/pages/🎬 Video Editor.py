import os
import tempfile

import moviepy.editor as pyedit
import streamlit as st
from modules.utils import add_bg_from_local, local_css, set_page_config


def render_uploaded_video(uploaded_video, speed):
    """Render an upload from temporary files and return the resulting MP4."""
    extension = os.path.splitext(uploaded_video.name)[1].lower()
    if extension not in {".mp4", ".mov", ".avi"}:
        raise ValueError("Upload an MP4, MOV, or AVI video.")

    with tempfile.TemporaryDirectory(prefix="vita-video-") as temp_dir:
        input_path = os.path.join(temp_dir, "input" + extension)
        output_path = os.path.join(temp_dir, "edited.mp4")
        with open(input_path, "wb") as source_file:
            source_file.write(uploaded_video.getvalue())

        with pyedit.VideoFileClip(input_path) as source_clip:
            with source_clip.speedx(speed) as edited_clip:
                edited_clip.write_videofile(
                    output_path,
                    codec="libx264",
                    audio_codec="aac",
                    temp_audiofile=os.path.join(temp_dir, "audio.m4a"),
                )

        with open(output_path, "rb") as output_file:
            return output_file.read()


def main():
    set_page_config()

    local_css()

    background_img_path = os.path.join(
        "static", "background", "Toolbox Logo.png"
    )
    sidebar_background_img_path = os.path.join(
        "static", "background", "Lila Gradient.png"
    )
    page_markdown = add_bg_from_local(
        background_img_path=background_img_path,
        sidebar_background_img_path=sidebar_background_img_path,
    )
    st.markdown(page_markdown, unsafe_allow_html=True)

    st.markdown(
        """<h1 style='text-align: center; color: black; font-size: 40px;'> Welcome to Video Editor 🎬 </h1> \
        <br>""",
        unsafe_allow_html=True,
    )

    video = st.file_uploader(
        "Choose a video to edit",
        type=["mp4", "mov", "avi"],
        accept_multiple_files=False,
    )
    if video is None:
        return

    st.write(video.name)
    with st.sidebar:
        _, center_col, _ = st.columns(3)
        center_col.header("Settings")
        speed = st.slider("Speed up the video", 1, 5)

    with st.spinner("Processing video"):
        video_bytes = render_uploaded_video(video, speed)

    st.video(video_bytes)
    st.download_button(
        "Download processed video",
        video_bytes,
        file_name="edited-video.mp4",
        mime="video/mp4",
    )


if __name__ == "__main__":
    main()
