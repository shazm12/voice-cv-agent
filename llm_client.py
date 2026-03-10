from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv


load_dotenv()


def answer(question: str, resume_text: str) -> str:
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.2,
        max_retries=2
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         """
        You are a helpful Talent assistant who helps users to answer questions about the candidates profiles based on the resume text provided. {resume_text}
        
        Answer the question based on the resume text provided. If the answer is not found in the resume text, say "Sorry, I don't know the answer to that question."
        
        Give a concise answer speaking about:
        1. The candidate's professional experience like Years of experience, companies worked at, roles and responsibilities, etc.
        2. The candidate's education background like degrees, universities attended, etc.
        3. The candidates skills and projects, just give a breif overview in one line about projects and first mention the category of the skills followed by the list of skills.
        """),
        ("human", "{question}")
    ])

    chain = prompt | llm | StrOutputParser()

    return chain.invoke({"question": question, "resume_text": resume_text})
