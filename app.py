import streamlit as st
import os
import subprocess
from moviepy.editor import VideoFileClip, AudioFileClip

st.title("🎧 Video Cleaner (環境音除去)")
st.caption("動画から環境音を自動で除去します")

uploaded_file = st.file_uploader("動画をアップロード", type=["mp4", "mov", "avi"])

if uploaded_file is not None:
    input_video_path = uploaded_file.name

    with open(input_video_path, "wb") as f:
        f.write(uploaded_file.read())

    st.video(input_video_path)

    if st.button("環境音を除去する"):
        progress = st.progress(0)

        # ===== 音声抽出 =====
        st.write("🎵 音声抽出中...")
        video = VideoFileClip(input_video_path)
        audio_path = "audio.wav"
        video.audio.write_audiofile(audio_path, verbose=False, logger=None)
        progress.progress(30)

        # ===== Demucs処理 =====
        st.write("🤖 AIで分離中...")
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        command = [
            "python3", "-m", "demucs",
            "-n", "htdemucs",
            "-o", output_dir,
            audio_path
        ]

        with st.spinner("AI処理中...（少し時間かかる）"):
            result = subprocess.run(command, capture_output=True, text=True)

        progress.progress(70)

        if result.returncode != 0:
            st.error("❌ Demucsエラー")
            st.text(result.stderr)

        else:
            # ===== vocals取得 =====
            st.write("🎬 動画生成中...")
            vocals_path = os.path.join(output_dir, "htdemucs", "audio", "vocals.wav")

            if not os.path.exists(vocals_path):
                st.error("❌ vocals.wavが見つかりません")
            else:
                output_video = "cleaned_video.mp4"

                new_audio = AudioFileClip(vocals_path)
                final_video = video.set_audio(new_audio)

                final_video.write_videofile(
                    output_video,
                    codec="libx264",
                    audio_codec="aac",
                    verbose=False,
                    logger=None
                )

                progress.progress(100)

                st.success("✅ 完成！")
                st.video(output_video)

                with open(output_video, "rb") as f:
                    st.download_button(
                        "⬇ ダウンロード",
                        f,
                        file_name="cleaned_video.mp4"
                    )

        video.close()