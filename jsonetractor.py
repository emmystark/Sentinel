import json
from transformers import pipeline
import PyPDF2
from typing import List, Dict

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file.
    """
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def extract_text_from_txt(txt_path: str) -> str:
    """
    Extract text from a TXT file.
    """
    with open(txt_path, 'r', encoding='utf-8') as file:
        return file.read()

def split_text_into_chunks(text: str, chunk_size: int = 500) -> List[str]:
    """
    Split text into chunks for processing.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(' '.join(words[i:i + chunk_size]))
    return chunks

def generate_qa_pairs(text: str, num_questions_per_chunk: int = 3) -> List[Dict[str, str]]:
    """
    Generate question-answer pairs from text using pre-trained models.
    """
    # Load question generation pipeline (generates questions from text)
    qg_pipeline = pipeline("e2e-qg", model="valhalla/t5-base-e2e-qg")
    
    # Load QA pipeline (answers questions based on context)
    qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    
    chunks = split_text_into_chunks(text)
    dataset = []
    
    for chunk in chunks:
        # Generate questions
        questions = qg_pipeline(chunk, num_questions=num_questions_per_chunk)
        
        for question in questions:
            # Generate answer using the QA model
            result = qa_pipeline(question=question, context=chunk)
            answer = result['answer']
            
            dataset.append({
                "question": question,
                "response": answer
            })
    
    return dataset

def generate_dataset(file_path: str, output_file: str = 'finetune_data.json', num_questions_per_chunk: int = 3):
    """
    Main function to generate dataset from document.
    Supports PDF and TXT files.
    """
    if file_path.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.txt'):
        text = extract_text_from_txt(file_path)
    else:
        raise ValueError("Unsupported file format. Use PDF or TXT.")
    
    dataset = generate_qa_pairs(text, num_questions_per_chunk)
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=4)
    
    print(f"Dataset generated and saved to {output_file}. Total pairs: {len(dataset)}")

# Example usage (uncomment and modify)
if __name__ == "__main__":
    generate_dataset('./thinking.pdf')