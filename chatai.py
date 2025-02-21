# #streamlit run chatai.py
# from dotenv import load_dotenv
# load_dotenv()

# import streamlit as st
# import os
# import google.generativeai as genai

# # Configure the Google Generative AI API key
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# def get_gemini_response(prompt, code_snippet=None, user_question=None):
#     """
#     Sends a prompt along with optional code and/or question context
#     to the Gemini model and returns the generated response text.
#     """
#     input_data = []
#     if user_question:
#         input_data.append("Problem/Question: " + user_question)
#     if code_snippet:
#         input_data.append("User Code: " + code_snippet)
#     input_data.append("Prompt: " + prompt)
    
#     model = genai.GenerativeModel('gemini-1.5-flash')
#     response = model.generate_content(input_data)
#     return response.text

# # Streamlit App Setup
# st.set_page_config(page_title="Interactive Coding Chat Bot", layout="wide")
# st.title("Interactive Coding Chat Bot")

# feature = st.sidebar.radio("Select Feature", ["Approach Builder", "General Doubt Solver"])

# if feature == "Approach Builder":
#     st.header("Approach Builder")
#     st.write(
#         "Provide your coding problem and code snippet. The bot will analyze your current approach and give **precise** feedback on:\n"
#         "✅ **How you can proceed next**\n"
#         "❌ **Errors & incorrect logic (with line numbers, if applicable)**\n"
#         "✔ **The correct structured approach**"
#     )
#     problem_statement = st.text_area("Describe your problem:", height=150)
#     code_input = st.text_area("Paste your code snippet here:", height=150)
    
#     if st.button("Get Approach"):
#         prompt_approach = (
#             "You are an expert coding mentor. The user has provided a coding problem and a code snippet. "
#             "Analyze the code and provide a **concise and professional** response covering three key areas:\n\n"
#             "1️⃣ **How the user can proceed next** based on the current implementation.\n"
#             "2️⃣ **Identify errors (if any)**, mentioning **specific line numbers** and explaining incorrect logic.\n"
#             "3️⃣ **Give the correct approach** (without providing direct code), focusing on best practices and improvements."
#         )
#         response = get_gemini_response(
#             prompt=prompt_approach,
#             code_snippet=code_input,
#             user_question=problem_statement
#         )
#         st.subheader("Professional Guidance")
#         st.write(response)

# elif feature == "General Doubt Solver":
#     st.header("General Doubt Solver")
#     st.write(
#         "Enter your question or doubt regarding your coding problem along with the problem statement. "
#         "The bot will provide **clear explanations** and **conceptual understanding**."
#     )
#     doubt_question = st.text_area("Enter your question/doubt:", height=150)
#     problem_context = st.text_area("Provide the problem statement/context:", height=150)
    
#     if st.button("Solve Doubt"):
#         prompt_doubt = (
#             "You are a knowledgeable technical mentor with deep expertise in software development. "
#             "Answer the user's question and clarify any doubts regarding the problem statement. "
#             "Provide a **precise yet detailed explanation**, ensuring conceptual clarity."
#         )
#         combined_question = doubt_question + "\nContext: " + problem_context
#         response = get_gemini_response(
#             prompt=prompt_doubt,
#             user_question=combined_question
#         )
#         st.subheader("Clarifications and Explanations")
#         st.write(response)
from dotenv import load_dotenv
import os
import google.generativeai as genai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize FastAPI app
app = FastAPI(title="Edith - AI Coding Mentor", version="1.0")

# Allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins; for production, consider specifying allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request models
class ApproachRequest(BaseModel):
    problem_statement: str
    code_input: str

class DoubtRequest(BaseModel):
    doubt_question: str
    problem_context: str

class GeneralCodingQuestion(BaseModel):
    question: str

class ScoreRequest(BaseModel):
    question: str
    answer: str

def get_gemini_response(prompt, code_snippet=None, user_question=None):
    """
    Sends a prompt along with optional code/question context to Gemini API.
    Returns the generated response text.
    """
    input_data = []
    if user_question:
        input_data.append("Problem/Question: " + user_question)
    if code_snippet:
        input_data.append("User Code: " + code_snippet)
    input_data.append("Prompt: " + prompt)
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(input_data)
    return response.text

@app.post("/analyze")
async def analyze_code(request: ApproachRequest):
    """
    API endpoint for the Approach Builder.
    - Returns: Next steps, errors (with line numbers), and correct approach.
    """
    prompt_approach = (
        "You are an expert coding mentor named Edith. The user has provided a coding problem and a code snippet. "
        "Analyze the code and provide a **concise and professional** response covering three key areas:\n\n"
        "1️⃣ **How the user can proceed next** based on the current implementation.\n"
        "2️⃣ **Identify errors (if any)**, mentioning **specific line numbers** and explaining incorrect logic.\n"
        "3️⃣ **Give the correct approach** (without providing direct code), focusing on best practices and improvements."
    )
    
    response = get_gemini_response(
        prompt=prompt_approach,
        code_snippet=request.code_input,
        user_question=request.problem_statement
    )
    
    return {"response": response}

@app.post("/solve_doubt")
async def solve_doubt(request: DoubtRequest):
    """
    API endpoint for the General Doubt Solver.
    - Returns: Explanation and conceptual understanding.
    """
    prompt_doubt = (
        "You are a knowledgeable technical mentor named Edith. "
        "Answer the user's question and clarify any doubts regarding the problem statement. "
        "Provide a **precise yet detailed explanation**, ensuring conceptual clarity."
    )
    
    combined_question = request.doubt_question + "\nContext: " + request.problem_context
    response = get_gemini_response(
        prompt=prompt_doubt,
        user_question=combined_question
    )
    
    return {"response": response}

@app.post("/edit")
async def edit_code_thinking(request: GeneralCodingQuestion):
    """
    API endpoint for general coding-related questions.
    - Returns: Guidance on **how to think** about coding problems.
    """
    prompt_edit = (
        """You are Edith, an AI coding mentor who helps users **think** about problems instead of just providing answers. 
        For the given coding question, explain **how the user should approach it**, including:
        1️⃣ **Breaking down the problem logically**  
        2️⃣ **Identifying key concepts involved**  
        3️⃣ **Steps to derive a solution independently**  
        Encourage problem-solving without giving direct solutions."""
    )
    
    response = get_gemini_response(
        prompt=prompt_edit,
        user_question=request.question
    )
    
    return {"response": response}

@app.post("/givescore")
async def give_score(request: ScoreRequest):
    """
    API endpoint to evaluate a user's answer to a question.
    It returns a numeric score on a scale of 0 to 10.
    """
    prompt_score = (
        "You are an expert evaluator. Evaluate the following answer to the given question on a scale of 0 to 10, "
        "where 0 means completely incorrect and 10 means completely correct.\n\n"
        f"Question: {request.question}\n"
        f"Answer: {request.answer}\n\n"
        "Please respond only with the numeric score."
    )
    
    score_response = get_gemini_response(prompt_score)
    return {"score": score_response}
