import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


def Resume_Ranker(job_description,pdf_resume_path,candidate_name):

    # Function to extract text from PDF
    def extract_text_from_pdf(pdf_path):
        text = ""
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
        return text


    def extract_entities(text,candidate_name):
        #Name 
        name = True if candidate_name in text else False
        #Skills
        skills = True if "SKILLS" in text else False
        #Projects
        projects = True if "PROJECTS" in text else False
        #Education
        education = True if "EDUCATION" in text else False
        #Certificates
        certificates = True if "CERTIFICATES" or "CERTIFICATIONS" in text else False
        #languages
        languages  = True if "LANGUAGES" in text else False
        #email
        email = re.findall(r'\S+@\S+',text)
        #mobile
        mobile = re.findall(r'\b\d{10}\b', text)
        #profile
        profile = True if "PROFILE" or "SUMMARY" or "OBJECTIVE" in text else False

        return name,skills,projects,education,certificates,languages,email,mobile,profile



    # Function to match job description and resume
    def match_resume(job_description, resume_text, candidate_name):

        name,skills,projects,education,certificates,languages,email,mobile,profile = extract_entities(resume_text,candidate_name)


        if name :

            # Calculate cosine similarity between job description and resume
            vectorizer = TfidfVectorizer()
            job_description_vector = vectorizer.fit_transform([job_description])
            resume_vector = vectorizer.transform([resume_text])
            similarity_score = cosine_similarity(job_description_vector, resume_vector)[0][0]
            similarity_score *= 100


            # Extra score for additional resume details 

            extra_score = 20
     
            extra_score += 10 if skills else 0        
            extra_score += 10 if projects else 0        
            extra_score += 10 if education else 0        
            extra_score += 10 if certificates else 0        
            extra_score += 10 if languages else 0        
            extra_score += 10 if email else 0        
            extra_score += 10 if mobile else 0        
            extra_score += 10 if profile else 0 

        else :
            extra_score = 0
            similarity_score = 0

        return similarity_score,extra_score


    # Extract text from PDF resume
    resume_text = extract_text_from_pdf(pdf_resume_path)

    # Match job description and resume
    similarity_score,extra_score = match_resume(job_description, resume_text, candidate_name)

    overall_score = int((similarity_score + extra_score)/2)

    return overall_score
    



