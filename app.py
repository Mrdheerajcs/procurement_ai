from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel

from docx import Document

from reportlab.pdfgen import canvas

import shutil
import os

from ocr_service import (

    scan_pdf,

    scan_word_document,

    search_documents,

    get_ai_pdf_suggestions,

    get_auto_suggestions
)

app = FastAPI()

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

UPLOAD_FOLDER = "PDFs"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

tenders = [

    {

        "title": "Desktop Computer Procurement",

        "items": [

            {

                "item_name": "Desktop Computer",

                "quantity": 20,

                "rate": 55000,

                "specification":
                "Intel i7 16GB RAM SSD"

            }

        ]
    },

    {

        "title": "Network Infrastructure Setup",

        "items": [

            {

                "item_name": "Router",

                "quantity": 10,

                "rate": 12000,

                "specification":
                "Cisco enterprise router"

            }

        ]
    },

    {

        "title": "CCTV Security Installation",

        "items": [

            {

                "item_name": "CCTV Camera",

                "quantity": 25,

                "rate": 8000,

                "specification":
                "Night vision security camera"

            }

        ]
    },

    {

        "title": "SAP Software License",

        "items": [

            {

                "item_name": "SAP License",

                "quantity": 50,

                "rate": 25000,

                "specification":
                "Cloud ERP Integration"

            }

        ]
    }
]


class TenderRequest(BaseModel):

    requirement: str


def get_workflow(requirement):

    requirement = requirement.lower()

    if "sap" in requirement:

        return [

            "Requirement Analysis",

            "SAP License Selection",

            "Cloud ERP Planning",

            "Vendor Approval",

            "Deployment Setup",

            "Testing & Integration"

        ]

    elif "camera" in requirement:

        return [

            "CCTV Requirement Collection",

            "Camera Placement Planning",

            "DVR Configuration",

            "Network Integration",

            "Installation",

            "Security Monitoring Setup"

        ]

    elif "desktop" in requirement:

        return [

            "Hardware Requirement Analysis",

            "Desktop Configuration",

            "Vendor Shortlisting",

            "Budget Approval",

            "Procurement",

            "Installation & Testing"

        ]

    elif "network" in requirement:

        return [

            "Network Planning",

            "Router Selection",

            "Firewall Configuration",

            "Switch Setup",

            "Testing",

            "Deployment"

        ]

    elif "docker" in requirement:

        return [

            "Container Requirement Analysis",

            "Docker Environment Setup",

            "Image Configuration",

            "Deployment Pipeline Setup",

            "Testing",

            "Production Deployment"

        ]

    elif "cloud" in requirement:

        return [

            "Cloud Requirement Analysis",

            "Provider Selection",

            "Infrastructure Planning",

            "Security Configuration",

            "Deployment",

            "Monitoring Setup"

        ]

    else:

        return [

            "Requirement Collection",

            "Vendor Selection",

            "Procurement",

            "Deployment",

            "Testing"

        ]


@app.get("/")
def home():

    return FileResponse("index.html")


@app.post("/upload-pdf")

async def upload_pdf(

    file: UploadFile = File(...),

    category: str = "General",

    sub_category: str = "General"
):

    folder_path = os.path.join(

        UPLOAD_FOLDER,

        "Past_Tenders",

        category,

        sub_category
    )

    os.makedirs(

        folder_path,

        exist_ok=True
    )

    file_path = os.path.join(

        folder_path,

        file.filename
    )

    with open(file_path, "wb") as buffer:

        shutil.copyfileobj(

            file.file,

            buffer
        )

    if file.filename.endswith(".pdf"):

        scan_pdf(

            file_path,

            file.filename,

            category,

            sub_category
        )

        return {

            "success": True,

            "message":
            "PDF uploaded and scanned successfully",

            "file_path":
            file_path
        }

    elif file.filename.endswith(".docx"):

        scan_word_document(

            file_path,

            file.filename,

            category,

            sub_category
        )

        return {

            "success": True,

            "message":
            "Word document uploaded and scanned successfully",

            "file_path":
            file_path
        }

    else:

        return {

            "success": False,

            "message":
            "Only PDF and DOCX files are allowed"
        }


@app.get("/search-pdf")
def search_pdf(query: str):

    results = search_documents(query)

    return {

        "matching_files": results
    }


@app.get("/suggestions")
def suggestions(query: str):

    results = get_auto_suggestions(query)

    return {

        "success": True,

        "results": results
    }


@app.post("/api/ai/generate-tender")
def generate_tender(request: TenderRequest):

    requirement = request.requirement

    workflow = get_workflow(
        requirement
    )

    top_matches = []

    for tender in tenders:

        title = tender["title"]

        items = tender["items"]

        combined_text = title.lower()

        for item in items:

            combined_text += " "

            combined_text += item["item_name"].lower()

            combined_text += " "

            combined_text += item["specification"].lower()

        if requirement.lower() in combined_text:

            top_matches.append({

                "title": title,

                "items": items
            })

    pdf_suggestions = get_ai_pdf_suggestions(
        requirement
    )

    suggestions = []

    for pdf in pdf_suggestions:

        for keyword in pdf["keywords"]:

            if (
                requirement.lower()
                in keyword.lower()
            ):

                if keyword not in suggestions:

                    suggestions.append(keyword)

    return {

        "success": True,

        "message":
        "New tender recommendations generated",

        "top_matches": top_matches,

        "pdf_suggestions": pdf_suggestions,

        "suggestions": suggestions,

        "workflow": workflow
    }


@app.get("/download-word")
def download_word():

    doc = Document()

    doc.add_heading(
        "AI Tender Report",
        level=1
    )

    doc.add_paragraph(
        "Generated by E-Procurement AI System"
    )

    file_name = "Tender_Report.docx"

    doc.save(file_name)

    return FileResponse(

        file_name,

        media_type=
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",

        filename=file_name
    )


@app.get("/download-pdf")
def download_pdf():

    file_name = "Tender_Report.pdf"

    c = canvas.Canvas(file_name)

    c.drawString(

        100,

        750,

        "AI Tender Report"
    )

    c.drawString(

        100,

        720,

        "Generated by E-Procurement AI System"
    )

    c.save()

    return FileResponse(

        file_name,

        media_type="application/pdf",

        filename=file_name
    )