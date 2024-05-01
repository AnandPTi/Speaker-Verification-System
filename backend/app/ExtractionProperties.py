from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict


# class diagnosis_schema(BaseModel):
#     diagnosis: List[str] = Field(default=['Not discussed by doctor'], description="Diagnosis found.")
    
# class MedicationInstruction(BaseModel):
#     title: str = Field(default="Not discussed by Doctor", description="Name of the medication.")
#     dosage: str = Field(default="Not discussed by Doctor", description="Dosage of the medication.")
#     timing_frequency: str = Field(default="Not discussed by Doctor", description="Timing and frequency of taking the medication.")
#     indication: str = Field(default="Not discussed by Doctor", description="Indication for taking the medication.")

# class medicationschema(BaseModel):
#     medication: List[MedicationInstruction] = Field(default_factory=list, description="List of all the medications with details.")
    
# class lifestyle_adjustments_schema(BaseModel):
#     lifestyle_adjustments: List[str] = Field(default=['Not discussed by doctor'], description="List of lifestyle adjustments recommended by the doctor.")

# class followUp_schema(BaseModel):
#     followUp : str = Field(default='Not discussed by doctor', description="Details about follow-up appointment. Example: Doctor suggested + response")


# from typing import List
# from pydantic import BaseModel, Field

class CurrentMedication(BaseModel):
    MedicationName: str = Field(default="Not discussed by Doctor", description="Name of the medication.")
    Dosage: str = Field(default="Not discussed by Doctor", description="Dosage of the medication.")

class VitalSigns(BaseModel):
    HeartRate: str = Field(default="Not discussed by Doctor", description="Heart rate of the patient.")
    BloodPressure: str = Field(default="Not discussed by Doctor", description="Blood pressure of the patient.")
    RespiratoryRate: str = Field(default="Not discussed by Doctor", description="Respiratory rate of the patient.")
    Temperature: str = Field(default="Not discussed by Doctor", description="Temperature of the patient.")
    OxygenSaturation: str = Field(default="Not discussed by Doctor", description="Oxygen saturation of the patient.")

class ProblemList(BaseModel):
    ProblemNumber: int = Field(default=1, description="Problem number.")
    ProblemDescription: str = Field(default="Not discussed by Doctor", description="Description of the problem.")

class Assessment(BaseModel):
    AssessmentDescription: str = Field(default="Not discussed by Doctor", description="Details of the Patient and the problem.")
    ProblemList: List[ProblemList]
    DifferentialDiagnoses: List[str]

class TreatmentPlan(BaseModel):
    PatientEducation: str = Field(default="Not discussed by Doctor", description="Details of the patient education.")
    Pharmacotherapy: str = Field(default="Not discussed by Doctor", description="Details of the pharmacotherapy.")
    OtherTherapeuticProcedures = str = Field(default="Not discussed by Doctor", description="Details of other therapeutic procedures.")
    
    
class Objective(BaseModel):
    VitalSign: VitalSigns = Field(default_factory=dict, description="Vital signs of the patient.")
    PhysicalExam: str = Field(default="Not discussed by Doctor", description="Physical examination findings.")
    LabData: str = Field(default="Not discussed by Doctor", description="Details of all pertinent labs, x-rays, etc. completed and results.")

class Subjective_schema(BaseModel):
    HistoryofPresentIllness: str = Field(default="Not discussed by Doctor", description="Details of the history of present illness. Include all symptoms or signs mentioned in the HPI.")
    ReviewOfSystems: str = Field(default="Not discussed by Doctor", description="Details of the review of systems. Include all symptoms or signs mentioned in the HPI.")
    CurrentMedications: List[CurrentMedication] = Field(default_factory=list)
    PertinentPastMedicalHistory: str = Field(default="Not discussed by Doctor", description="Include past medical history, family history, and social history")
    Allergies: str = Field(default="Not discussed by Doctor", description="Details of the allergies.")
    FamilyHistory: str = Field(default="Not discussed by Doctor", description="Details of the family history.")
    SocialHistory: str = Field(default="Not discussed by Doctor", description="Details of the social history.")

class Plan(BaseModel):
    DiagnosticPlan: str = Field(default="Not discussed by Doctor", description="Details of the diagnostic plan.")
    TreatmentPlans: TreatmentPlan
    FollowUp: str = Field(default="Not discussed by Doctor", description="Details of the follow-up plan.")


class objective_schema(BaseModel):
    Objectives: Objective = Field(default_factory=dict, description="Objective data found.")



class assessment_schema(BaseModel):
    Assessments: Assessment = Field(default_factory=dict, description="Assessment data found.")
    
class plan_schema(BaseModel):
    Plans: Plan = Field(default_factory=dict, description="Plan data found.")