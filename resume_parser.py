import pymupdf


def load_resume(path) -> str:
    doc = pymupdf.open(path)
    resume_text = ""
    for page in doc:
        resume_text += f"\n {page.get_text()}"
    return resume_text
