import streamlit as st

section_map_data_preprocessing = {
        "about_the_job": [
            "About the Job", "Job Summary", "Overview", "Who We Are", "About Us"
        ],
        "role_responsibilities": [
            "Role Responsibilities", "Responsibilities", "Key Responsibilities", "Duties", "What You'll Do"
        ],
        "role_requirements": [
            "Role Requirements", "Requirements", "Qualifications", "Must-Have", "Experience"
        ],
        "preferred_qualifications": [
            "Nice-to-Have", "Preferred Qualifications", "Highly Desirable", "Desirable Skills"
        ],
        "benefits": [
            "Benefits", "What We Offer", "Perks", "Compensation & Benefits"
        ]
    }

# === Setup ===
profile = {
    "email": st.session_state.get("email_ext", None),
    "password": st.session_state.get("password_ext", None),
    "mobie": "+44 7459146448"
}
#------------------ Define dummy data for each field ----------------
my_information_data = {
    "source--source": {
        "type": "listbox",
        "value": "Direct Mail",
        "alternate_ids": [
            "sourceSection_source",
        ],
        "needs_done_button": True 
    },
    "candidateIsPreviousWorker": {
        "type": "radio",
        "value": "No",
        "alternate_ids": [
            "previousWorker_candidateIsPreviousWorker"
        ],
        "needs_done_button": False,
    },
    "country--country": {
        "type": "listbox",
        "value": "United Kingdom",
        "alternate_ids": [
            "countryDropdown",
        ],
        "needs_done_button": True,
    },
    "name--legalName--title": {
        "type": "listbox",
        "value": "Mr",
        "alternate_ids": [
            "legalNameSection_title",
        ],
        "needs_done_button": False,
    },
    "name--legalName--firstName": {
        "type": "text",
        "value": "Don",
        "alternate_ids": [
            "legalNameSection_firstName",
        ],
        "needs_done_button": False,
    },
    "name--legalName--lastName": {
        "type": "text",
        "value": "Aaja",
        "alternate_ids": [
            "legalNameSection_lastName",
        ],
        "needs_done_button": False,
    },
    "name--preferredCheck": {
        "type": "checkbox",
        "value": True,
        "alternate_ids": [
            "preferredNameCheckbox",
        ],
        "needs_done_button": False,
    },
    "name--preferredName--title": {
        "type": "listbox",
        "value": "Dr",
        "alternate_ids": [
            "preferredNameSection_title",
        ],
        "needs_done_button": False,
    },
    "name--preferredName--firstName": {
        "type": "text",
        "value": "Ramu",
        "alternate_ids": [
            "preferredNameSection_firstName",
        ],
        "needs_done_button": False,
    },
    "name--preferredName--lastName": {
        "type": "text",
        "value": "Kaka",
        "alternate_ids": [
            "preferredNameSection_lastName",
        ],
        "needs_done_button": False,
    },
    "address--addressLine1": {
        "type": "text",
        "value": "1423 Main St",
        "alternate_ids": [
            "addressSection_addressLine1",
        ],
        "needs_done_button": False,
    },
    "address--addressLine2": {
        "type": "text",
        "value": "Sui5te 456",
        "alternate_ids": [
            "addressSection_addressLine2",
        ],
        "needs_done_button": False,
    },
    "address--addressLine3": {
        "type": "text",
        "value": "Bu8ilding A",
        "alternate_ids": [
            "addressSection_addressLine3",
        ],
        "needs_done_button": False,
    },
    "address--city": {
        "type": "text",
        "value": "Notting8ham",
        "alternate_ids": [
            "addressSection_city",
        ],
        "needs_done_button": False,
    },
    "address--countryRegion": {
        "type": "listbox",
        "value": "Nottinghamshire",
        "alternate_ids": [
            "addressSection_countryRegion",
        ],
        "needs_done_button": False,
    },
    "address--postalCode": {
        "type": "text",
        "value": "NG1 2DB",
        "alternate_ids": [
            "addressSection_postalCode",
        ],
        "needs_done_button": False,
    },
    "phoneNumber--phoneType": {
        "type": "listbox",
        "value": "Mobile",
        "alternate_ids": [
            "phone-device-type",
        ],
        "needs_done_button": False,
    },
    "phoneNumber--countryPhoneCode": {
        "type": "text",
        "value": "+44",
        "alternate_ids": [
            "country-phone-code",
        ],
        "needs_done_button": True,
    },
    "phoneNumber--phoneNumber": {
        "type": "text",
        "value": "7469137449",
        "alternate_ids": [
            "phone-number",
        ],
        "needs_done_button": False,
    }
}


my_experience_data = {
    "workExperience": [
        {
            "jobTitle": "Software Engineer",
            "companyName": "ABC Corp",
            "location": "Bangalore",
            "currentlyWorkHere": True,
            "startDate": "28/01/2020",
            "endDate": "31/12/2022",
            "roleDescription": "Developed web applications and maintained software systems."
        },
        {
            "jobTitle": "Senior Developer",
            "companyName": "XYZ Ltd",
            "location": "London",
            "currentlyWorkHere": False,
            "startDate": "28/02/2017",
            "endDate": "31/12/2019",
            "roleDescription": "Led a team of developers and implemented enterprise solutions."
        },
        {
            "jobTitle": "Full Stack Developer",
            "companyName": "Tech Solutions",
            "location": "Remote",
            "currentlyWorkHere": False,
            "startDate": "01/03/2015",
            "endDate": "01/01/2017",
            "roleDescription": "Built web and mobile applications for clients worldwide."
        },
        {
            "jobTitle": "Software Intern",
            "companyName": "Startup Inc.",
            "location": "Berlin",
            "currentlyWorkHere": False,
            "startDate": "01/06/2014",
            "endDate": "01/02/2015",
            "roleDescription": "Assisted with developing internal tools and automations."
        },
        {
            "jobTitle": "Junior Developer",
            "companyName": "Innovatech",
            "location": "New York",
            "currentlyWorkHere": False,
            "startDate": "01/01/2013",
            "endDate": "01/05/2014",
            "roleDescription": "Worked on backend systems and contributed to product launches."
        }
    ],
    "education": [
        {
            "schoolName": "University of Nottingham",
            "degree": "Bachelor of Engineering",
            "fieldOfStudy": "Computer Science",
            "gradeAverage": "Merit",
            "startDate": "01/09/2016",
            "endDate": "01/06/2020"
        },
        {
            "schoolName": "University of Brighsa",
            "degree": "Masters",
            "fieldOfStudy": "Mathematics",
            "gradeAverage": "Merit",
            "startDate": "01/09/2016",
            "endDate": "01/06/2020"
        }
    ],
    "certifications": [
        {
            "certification": "AWS Certified Solutions Architect",
            "certificationNumber": "AWS-12345",
            "issuedDate": "15/06/2022",
            "expirationDate": "15/06/2025",
            "attachments": r"C:\Users\ajayc\Downloads\Ajay Hiremath  Resume.pdf"
        },
        {
            "certification": "Google Cloud Certified",
            "certificationNumber": "GCP-67890",
            "issuedDate": "20/03/2021",
            "expirationDate": "20/03/2024",
            "attachments": r"C:\Users\ajayc\Downloads\Ajay Hiremath Other Work Experience.docx"
        }
    ],    
    "languages": ["English"],
    "skills": ["Python","AWS","PySpark"],
    "resume": "/path/to/test_resume.pdf"  # Replace with an actual path.
}

workexperience_field_mapping = {"jobTitle": "text",
                               "companyName": "text",
                               "location": "text",
                               "currentlyWorkHere": "checkbox",
                               "startDate-dateSectionDay": "date",
                               "startDate-dateSectionMonth": "date",
                               "startDate-dateSectionYear": "date",
                               "endDate-dateSectionDay": "date",
                               "endDate-dateSectionMonth": "date",
                               "endDate-dateSectionYear": "date",
                               "roleDescription": "text"
                               }

certification_field_mapping = {"certification": "multiselect",
                        "certificationNumber": "text",
                        "issuedDate-dateSectionDay": "date",
                        "issuedDate-dateSectionMonth": "date",
                        "issuedDate-dateSectionYear": "date",
                        "expirationDate-dateSectionDay": "date",
                        "expirationDate-dateSectionMonth": "date",
                        "expirationDate-dateSectionYear": "date",
                        "attachments": "file"
                        }

education_field_mapping = {"schoolName": "text",
                           "degree": "listbox",
                           "fieldOfStudy": "multiselect",
                           "gradeAverage": "text",
                           "startDate-firstYearAttended-dateSectionDay": "date",
                           "startDate-firstYearAttended-dateSectionMonth": "date",
                           "startDate-firstYearAttended-dateSectionYear": "date",
                           "endDate-lastYearAttended-dateSectionDay": "date",
                           "endDate-lastYearAttended-dateSectionMonth": "date",
                           "endDate-lastYearAttended-dateSectionYear": "date"
                           }
