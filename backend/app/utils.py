import re
from app.ExtractionProperties import *

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory


from langchain_community.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain, create_extraction_chain_pydantic
from langchain.prompts import PromptTemplate
from langchain.vectorstores.faiss import FAISS


from langchain.chains.summarize import load_summarize_chain

import retry

import json
import os
from dotenv import load_dotenv
from retry import retry


load_dotenv()
index_name = "langchain-demo"

embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])


@retry(tries=5, delay=1, backoff=2)
async def get_doc_data(docs):
    try:
        map_prompt = """
            Write a concise summary of the following:                
            "{text}"
            CONCISE SUMMARY:
            """
        map_prompt_template = PromptTemplate(template=map_prompt, input_variables=["text"])
        combine_prompt ="""
        You are Evva Health's virtual medical assistant, here to help the patient and their caregiver to understand their recent doctor visit. You are provided with their Doctor Visit Transcription. Summarize the  visit in straightforward language, as if you're guiding a patient. Use the active voice. Ensure readability at a 9th-grade level. Keep it crisp and short. Follow the word count - 30 words. Correct any misspellings with your knowlodge base. Avoid using keywords like "Answer."
        ```{text}```
        """
        combine_prompt_template = PromptTemplate(template=combine_prompt, input_variables=["text"])
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
        summarization_chain = load_summarize_chain(llm = llm,
                                                    chain_type="map_reduce",
                                    map_prompt=map_prompt_template,
                                    combine_prompt=combine_prompt_template,
                                    )
    
        output_summary = summarization_chain.run(docs)
        wrapped_text = re.sub(r'\s+', ' ', output_summary.strip())
    except Exception as e:
        print(f"Error getting doc data: {e}")
        return {}
    print(wrapped_text)
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
    vectorstore = FAISS.from_documents(docs, embeddings)
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True, output_key='answer')

    
    prompt_template = """
        You are Evva Health's virtual medical assistant. Your role is to assist patients and their caregivers in understanding recent doctor visits and keeping track of important details. You have access to a Doctor Visit Transcription. Use the information provided in the transcription to answer the questions at the end. \n Important Instructions: \n 1. You do not have access to external data sources. \n 2. Correct any misspellings of diseases, medications, or labs based on your knowledge base. \n 3.Avoid responses like “Data is not provided in the transcription” or “Not mentioned in the transcription.” Instead, respond with “Not discussed” if the answer is absent from the transcription. Transcription: {context}\nQuestion: {question}
    """
    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )
    qa = ConversationalRetrievalChain.from_llm(
        ChatOpenAI(temperature=1, model="gpt-3.5-turbo-16k"),
        vectorstore.as_retriever(),
        memory = memory,
        combine_docs_chain_kwargs={"prompt": PROMPT}
    ) 



    # llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k")
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k", openai_api_key=os.getenv("OPENAI_API_KEY"))
    visit = {}
    visit['Summary'] = wrapped_text
    try:
        with open('app/veterans.json', 'rb') as f:
                visitsummary = json.load(f)
                print(visitsummary)
       
        try:
            print("Starting to extract the Subjective data")
            subjective_details = create_extraction_chain_pydantic(pydantic_schema=Subjective_schema, llm=llm)
            questions = visitsummary['subjective']
            print(questions)
            text = ""
            for question in questions:
                result = qa({"question": question})
                text += result["answer"] + " "
            text_list = [text]
            print(text_list)
            extracted_data = subjective_details.run(text_list)
            print(extracted_data)
            visit['Subjective'] = {}
            # Extracting HPI
            visit["Subjective"]["History_of_PresentIllness"] = extracted_data[0].HistoryofPresentIllness

             # Extracting ReviewOfSystems
            visit["Subjective"]["Review_of_Systems"] = extracted_data[0].ReviewOfSystems
            
            # Extracting PertinentPastMedicalHistory
            visit["Subjective"]["Pertinent_Past_MedicalHistory"] = extracted_data[0].PertinentPastMedicalHistory


            # Extracting CurrentMedications
            visit["Subjective"]["Current_Medications"] = []
            for medication in extracted_data[0].CurrentMedications:
                visit["Subjective"]["Current_Medications"].append({
                    "Medication_Name": medication.MedicationName,
                    "Dosage_Frequency": medication.Dosage
                })
                
            visit["Subjective"]["Medication_Allergies"] = extracted_data[0].Allergies
            
            visit["Subjective"]["Family_History"] = extracted_data[0].FamilyHistory
            
            visit["Subjective"]["Social_History"] = extracted_data[0].SocialHistory
            

        except Exception as sub_error:
            print(f"Error extracting Subjective: {sub_error}")
            visit['Subjective'] = {'History_of_PresentIllness': 'Not discussed by doctor', 'Review_of_Systems': 'Not discussed by doctor', 'Pertinent_Past_MedicalHistory': 'Not discussed by doctor', 'Current_Medications': [{'Medication Name': 'Not discussed by doctor', 'Dosage_Frequency': 'Not discussed by doctor'}], 'Medication_Allergies': 'Not discussed by doctor', 'Family_History': 'Not discussed by doctor', 'Social_History': 'Not discussed by doctor'}
            
        try:
            print("Starting to extract the Ojective data")
            objecttive_details = create_extraction_chain_pydantic(pydantic_schema=objective_schema, llm=llm)
            questions = visitsummary['objective']
            print(questions)
            text = ""
            for question in questions:
                result = qa({"question": question})
                text += result["answer"] + " "
            text_list = [text]
            extracted_data = objecttive_details.run(text_list)
            print("Objective = ",extracted_data)
            visit["Objective"] = {
                "VitalSigns": {
                    "Heart_Rate": extracted_data[0].Objectives.VitalSign.HeartRate,
                    "Blood_Pressure": extracted_data[0].Objectives.VitalSign.BloodPressure,
                    "Respiratory_Rate": extracted_data[0].Objectives.VitalSign.RespiratoryRate,
                    "Temperature": extracted_data[0].Objectives.VitalSign.Temperature,
                    "Oxygen_Saturation": extracted_data[0].Objectives.VitalSign.OxygenSaturation
                },
                "Physical_Exam": extracted_data[0].Objectives.PhysicalExam,
                "Lab_Data": extracted_data[0].Objectives.LabData
            }
        except Exception as obj_error:
            print(f"Error extracting Objective: {obj_error}")
            visit['Objective'] = {'VitalSigns': {'Heart_Rate': 'Not discussed by doctor', 'Blood_Pressure': 'Not discussed by doctor', 'Respiratory_Rate': 'Not discussed by doctor', 'Temperature': 'Not discussed by doctor', 'Oxygen_Saturation': 'Not discussed by doctor'}, 'Physical_Exam': 'Not discussed by doctor', 'Lab_Data': 'Not discussed by doctor'}
            
            
        try:
            print("Starting to extract the Assessment data")
            assessment_details = create_extraction_chain_pydantic(pydantic_schema=assessment_schema, llm=llm)
            questions
            questions = visitsummary['Assessment']
            print(questions)
            text = ""
            for question in questions:
                result = qa({"question": question})
                text += result["answer"] + " "
            text_list = [text] 
            extracted_data = assessment_details.run(text_list)
            print("Assessment = ", extracted_data)
            visit["Assessment"] = {
                "Assessment_Description": extracted_data[0].Assessments.AssessmentDescription,
                "ProblemList": [
                    {
                        "Problem_Number": problem.ProblemNumber,
                        "Problem_Description": problem.ProblemDescription
                    }
                    for problem in extracted_data[0].Assessments.ProblemList
                ],
                "Differential_Diagnoses": extracted_data[0].Assessments.DifferentialDiagnoses
            }
        except Exception as assis_error:
            print(f"Error extracting Assessment: {assis_error}")
            visit['Assessment'] = {'Assessment_Description': 'Not discussed by doctor', 'ProblemL_ist': [{'Problem_Number': 0, 'Problem_Description': 'Not discussed by doctor'}], 'Differential_Diagnoses': ['Not discussed by doctor']}
        
        try:
            print("Starting to extract the Plan data")
            plan_details = create_extraction_chain_pydantic(pydantic_schema=plan_schema, llm=llm)
            questions = visitsummary['Plan']
            print(questions)
            text = ""
            for question in questions:
                result = qa({"question": question})
                text += result["answer"] + " "
            text_list = [text]
            extracted_data = plan_details.run(text_list)
            # visit['Plan'] = extracted_data[0].Plans
            print("Plans = ", extracted_data)
            visit["Plan"] = {
                "Diagnostic_Plan": extracted_data[0].Plans.DiagnosticPlan,
                "Treatment_Plan": {
                    "Patient_Education": extracted_data[0].Plans.TreatmentPlans.PatientEducation,
                    "Pharmacotherapy": extracted_data[0].Plans.TreatmentPlans.Pharmacotherapy,
                    "Other_Therapeutic_Procedures": extracted_data[0].Plans.TreatmentPlans.OtherTherapeuticProcedures
                },
                "FollowUp": extracted_data[0].Plans.FollowUp
            }
        except Exception as plan_error:
            print(f"Error extracting Plan: {plan_error}")
            visit['Plans'] = {'Diagnostic_Plan': 'Not discussed by doctor', 'Treatmen_tPlan': {'Patient Education': 'Not discussed by doctor', 'Pharmacotherapy': 'Not discussed by doctor', 'Other_Therapeutic_Procedures': 'Not discussed by doctor'}, 'FollowUp': 'Not discussed by doctor'}
            
        print("start",visit,"end")
        return visit 
    except Exception as e:
    # Catch any errors and provide more detailed feedback to the user
        print(f"Error extracting data from documents: {e}")
        return {"Error extracting data from documents:"}