import os
import gradio as gr
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document

# Initialize the Groq client
client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    with open(pdf_file.name, 'rb') as file:
        reader = PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

# Function to extract text from Word file
def extract_text_from_word(docx_file):
    doc = Document(docx_file.name)
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

# Function to handle chat interaction with the document
def chat_with_document(user_input, file):
    # Check if a file has been uploaded
    if file is not None:
        if file.name.endswith(".pdf"):
            text = extract_text_from_pdf(file)
        elif file.name.endswith(".docx"):
            text = extract_text_from_word(file)
        else:
            return "Unsupported file type. Please upload a PDF or Word document."
    else:
        return "Please upload a document first."

    # Now, use the extracted text from the document to interact with the Groq API
    # Pass the document text and user input to Groq for answering
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": f"Using this document text: {text}, answer this question: {user_input}"}
        ],
        model="llama3-8b-8192",  # Use the correct model
    )

    return chat_completion.choices[0].message.content

# Function to clear inputs and outputs
def clear_interface():
    return gr.File(value=None), gr.Textbox(value=""), gr.Textbox(value="")

# Gradio Interface with submit and clear button and vertical arrangement using gr.Column()
with gr.Blocks() as iface:
    with gr.Column():  # Arrange inputs and output vertically
        file_input = gr.File(label="Upload PDF/Word file")
        question_input = gr.Textbox(label="Ask a question about the document", placeholder="Type your question here...")
        output = gr.Textbox(label="Answer", interactive=False)
        submit_button = gr.Button("Submit")  # Submit button
        clear_button = gr.Button("Clear")  # Clear button

    # When the submit button is clicked, it will call `chat_with_document` function
    submit_button.click(fn=chat_with_document, inputs=[question_input, file_input], outputs=output)

    # When the clear button is clicked, it will clear inputs and outputs
    clear_button.click(fn=clear_interface, inputs=[], outputs=[file_input, question_input, output])

# Launch the interface
iface.launch()
