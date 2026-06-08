"""
Milestone 5: Gradio query interface.
Run with: python app.py
Then open http://localhost:7860
"""

import gradio as gr
from query import ask


def handle_query(question: str):
    if not question.strip():
        return "Please enter a question.", "", ""

    result = ask(question)

    answer = result["answer"]
    sources = "\n".join(f"• {s}" for s in result["sources"])
    chunks_display = ""
    for i, chunk in enumerate(result["chunks"]):
        chunks_display += f"[{i+1}] ({chunk['distance']:.3f}) {chunk['source']}\n{chunk['text'][:200]}...\n\n"

    return answer, sources, chunks_display


with gr.Blocks(title="Zelda: TotK Unofficial Guide") as demo:
    gr.Markdown("# 🗡️ The Legend of Zelda: Tears of the Kingdom — Unofficial Guide")
    gr.Markdown("Ask about the story, lore, characters, abilities, or gameplay. Answers are grounded in collected documents only.")

    with gr.Row():
        with gr.Column(scale=2):
            question_input = gr.Textbox(
                label="Your Question",
                placeholder="e.g. Why did Zelda turn into a dragon? How does Fuse work?",
                lines=2,
            )
            ask_btn = gr.Button("Ask", variant="primary")

        with gr.Column(scale=3):
            answer_output = gr.Textbox(label="Answer", lines=8)
            sources_output = gr.Textbox(label="Sources", lines=3)

    with gr.Accordion("Retrieved Chunks (debug view)", open=False):
        chunks_output = gr.Textbox(label="Top Retrieved Chunks", lines=10)

    ask_btn.click(
        handle_query,
        inputs=question_input,
        outputs=[answer_output, sources_output, chunks_output],
    )
    question_input.submit(
        handle_query,
        inputs=question_input,
        outputs=[answer_output, sources_output, chunks_output],
    )

    gr.Examples(
        examples=[
            ["Why did Zelda turn into a dragon?"],
            ["Who is Ganondorf and what is his backstory?"],
            ["What are the main temples in the game?"],
            ["How does the Ultrahand ability work?"],
            ["What happened at the end of the game?"],
        ],
        inputs=question_input,
    )

demo.launch()
