!pip install -qU langchain langchain-openai gradio

import os, gradio as gr
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# 4. Set up OpenAI API key
import os
os.environ["OPENAI_API_KEY"] = ""  # Replace with your real key

SYSTEM = "You are a concise, audience-aware content generator. Follow the formatting rules per content type."

HUMAN = """
Generate {content_type} content about: "{topic}"
Tone: {tone}
Target length (words): {length}
Audience: {audience}
Keywords (optional): {keywords}
CTA (optional): {cta}

Formatting rules by type:
- blog: title + intro + 3–5 sections with short subheadings + conclusion.
- tweet: ≤ 280 chars; 1–2 hashtags; no emojis unless tone is 'playful'.
- linkedin: 120–220 words; scannable lines; ≤2 emojis only if tone is 'playful'.
- instagram_caption: 60–150 words; 3–5 hashtags; emojis allowed unless tone is 'professional'.
- video_script: HOOK, INTRO, BODY (3 beats), CTA; annotate approx timing in parentheses.
- ad_copy: headline (≤8 words), body (≤60 words), CTA.

Avoid fake facts or prices. Weave keywords naturally; no stuffing.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM),
    ("human", HUMAN),
])

llm = ChatOpenAI(temperature=0.5, max_tokens=900, model="gpt-4o-mini")

def generate_content(content_type, topic, tone, length, cta, keywords, audience):
    if not topic.strip():
        return "Please enter a topic."
    # sane minimums for long forms
    if content_type in {"blog", "video_script"} and length < 120:
        length = 200
    try:
        chain = prompt | llm
        out = chain.invoke({
            "content_type": content_type,
            "topic": topic.strip(),
            "tone": tone,
            "length": int(length),
            "cta": cta.strip(),
            "keywords": keywords.strip(),
            "audience": audience.strip(),
        }).content.strip()
        if content_type == "tweet" and len(out) > 280:
            out = out[:277].rstrip() + "..."
        return out
    except Exception as e:
        return f"Oops—couldn't generate content: {e}"

with gr.Blocks() as demo:
    gr.Markdown("## AI-Powered Content Creator")
    with gr.Row():
        content_type = gr.Dropdown(
            ["blog","tweet","linkedin","instagram_caption","video_script","ad_copy"],
            value="blog", label="Content Type"
        )
        tone = gr.Dropdown(
            ["professional","casual","persuasive","educational","playful"],
            value="educational", label="Tone"
        )
    topic = gr.Textbox(label="Topic", placeholder="e.g., Benefits of compound interest for beginners")
    with gr.Row():
        length = gr.Slider(60, 1000, value=400, step=20, label="Target length (words)")
        audience = gr.Textbox(label="Audience (optional)", placeholder="e.g., college students")
    keywords = gr.Textbox(label="Keywords (optional)", placeholder="comma-separated")
    cta = gr.Textbox(label="CTA (optional)", placeholder="e.g., Subscribe for weekly tips")
    out = gr.Textbox(label="Generated Content", lines=18)
    btn = gr.Button("Generate", variant="primary")
    btn.click(generate_content, [content_type, topic, tone, length, cta, keywords, audience], out)

demo.launch(share=True, debug = True)

