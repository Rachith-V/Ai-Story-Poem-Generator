import streamlit as st
import requests
from urllib.parse import quote
import json
import time
import os
import requests


def generate_comfyui_image(prompt_text):

    with open("storygenerator.json", "r", encoding="utf-8") as f:
        workflow = json.load(f)

    # Positive prompt node
    workflow["6"]["inputs"]["text"] = prompt_text

    response = requests.post(
        "http://127.0.0.1:8188/prompt",
        json={"prompt": workflow}
    )

    prompt_id = response.json()["prompt_id"]

    return prompt_id


def wait_for_image(prompt_id):

    while True:

        history = requests.get(
            f"http://127.0.0.1:8188/history/{prompt_id}"
        ).json()

        if prompt_id in history:

            outputs = history[prompt_id]["outputs"]

            for node_id in outputs:

                node_output = outputs[node_id]

                if "images" in node_output:

                    image = node_output["images"][0]

                    return image

        time.sleep(1)


def get_image_path(image_info):

    filename = image_info["filename"]

    return (
        f"http://127.0.0.1:8188/view"
        f"?filename={filename}"
        f"&type=output"
    )

st.set_page_config(
    page_title="DreamForge AI",
    page_icon="✨",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#0f172a,#1e293b,#312e81);
}
.main { padding-top: 1rem; }
section[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.95);
}
textarea {
    font-size: 18px !important;
    border-radius: 12px !important;
}
.stButton button {
    width: 100%;
    height: 55px;
    border-radius: 12px;
    font-size: 18px;
    font-weight: bold;
    border: none;
    background: linear-gradient(90deg,#7c3aed,#2563eb);
    color: white;
}
.gradient-title {
    text-align:center;
    font-size:3rem;
    font-weight:bold;
    background: linear-gradient(90deg,#8b5cf6,#3b82f6,#06b6d4);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
}
.subtitle {
    text-align:center;
    color:#cbd5e1;
    font-size:18px;
    margin-bottom:30px;
}
.card {
    padding:20px;
    border-radius:15px;
    background:rgba(255,255,255,0.08);
    backdrop-filter:blur(10px);
    margin-bottom:15px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="gradient-title">✨ DreamForge AI</div>
<div class="subtitle">Transform imagination into stories, poems and visuals</div>
""", unsafe_allow_html=True)

st.sidebar.title("⚙️ Generator Settings")

content_type = st.sidebar.selectbox("Content Type", ["Poem", "Story"])

style = st.sidebar.selectbox(
    "Writing Style",
    ["Fantasy", "Funny", "Romantic", "Dark", "Motivational"]
)

length = st.sidebar.slider("Content Length", 50, 500, 150, 50)

temperature = st.sidebar.slider("Creativity", 0.1, 1.5, 0.8, 0.1)

num_outputs = st.sidebar.selectbox("Number of Outputs", [1, 2, 3])

st.sidebar.markdown("---")
st.sidebar.subheader("📖 Guidelines")
st.sidebar.info("""
1. Enter a topic.
2. Choose Story or Poem.
3. Select a writing style.
4. Adjust length and creativity.
5. Click Generate.
6. Download your favorite result.
""")

st.markdown("## 💡 Describe Your Idea")

topic = st.text_area(
    "",
    placeholder="Type your fantasies here... see them come to life!",
    height=220
)

generate = st.button("✨ Generate")

if generate:

    if not topic.strip():
        st.warning("Please enter a topic.")
        st.stop()

    with st.spinner("Generating content..."):

        for i in range(num_outputs):

            if content_type == "Poem":
                prompt = f"""
Write a creative poem about:

{topic}

Style: {style}
Length: approximately {length} words.

Requirements:
- Beautiful language
- Strong imagery
- Rhyming if possible
- Output only the poem
"""
            else:
                prompt = f"""
Write an engaging short story about:

{topic}

Style: {style}
Length: approximately {length} words.

Requirements:
- Interesting beginning
- Engaging middle
- Satisfying ending
- Output only the story
"""

            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "dolphin-mistral:7b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": temperature}
                },
                timeout=300
            )

            output = response.json()["response"]
            word_count = len(output.split())

            st.markdown("---")
            st.markdown(f"## Output {i+1}")

            col1, col2 = st.columns([1.7, 1])

            with col1:
                st.markdown(
                    f'<div class="card"><h3>📖 Generated {content_type}</h3></div>',
                    unsafe_allow_html=True
                )

                st.write(output)

                

                st.download_button(
                    "📥 Download",
                    output,
                    file_name=f"{content_type.lower()}_{i+1}.txt",
                    mime="text/plain"
                )

            with col2:
                st.markdown(
                    '<div class="card"><h3>🎨 Illustration</h3></div>',
                    unsafe_allow_html=True
                )

                image_prompt = f"""
                {style} illustration of {topic}

                cinematic lighting,
                masterpiece,
                ultra detailed,
                fantasy concept art,
                8k
                """

                with st.spinner("Generating image..."):

                    prompt_id = generate_comfyui_image(image_prompt)

                    time.sleep(15)  # wait for generation

                    output_folder = r"D:\ComfyUI\output"

                    pngs = sorted(
                        [
                            os.path.join(output_folder, f)
                            for f in os.listdir(output_folder)
                            if f.endswith(".png")
                        ],
                        key=os.path.getmtime
                    )

                    latest_image = pngs[-1]

                    st.image(
                        latest_image,
                        use_container_width=True
                    )

                st.caption("Generated using DreamShaper XL + ComfyUI")
                
