import json

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)

from sqlalchemy.orm import Session

from backend.app.ai.career_advisor import career_advice
from backend.app.ai.job_analyzer import extract_skills
from backend.app.ai.job_matcher import (
    normalize_skills,
    calculate_match_score,
)
from backend.app.ai.resume_optimizer import optimize_resume
from backend.app.ai.resume_parser import extract_resume_text
from backend.app.ai.skill_gap import calculate_skill_gap

from backend.app.api.deps import get_current_user
from backend.app.database.connection import get_db

from backend.app.models.user import User
from backend.app.models.analysis import ResumeAnalysis

from backend.app.schemas.analysis import (
    ResumeAnalysisRequest,
    ResumeAnalysisResponse,
)

from backend.app.services.resume_service import create_resume


router = APIRouter(
    prefix="/analysis",
    tags=["AI Analysis"]
)


# ============================================================
# REQUIRED SKILLS FOR DIFFERENT JOB ROLES
# ============================================================

REQUIRED_SKILLS = {

    "software engineer": [
        "python",
        "sql",
        "git",
        "dsa",
        "oop",
    ],

    "python developer": [
        "python",
        "fastapi",
        "sql",
        "git",
        "rest api",
    ],

    "backend developer": [
        "python",
        "fastapi",
        "sql",
        "git",
        "rest api",
    ],

    "data analyst": [
        "python",
        "sql",
        "pandas",
        "power bi",
        "excel",
    ],

    "data scientist": [
        "python",
        "sql",
        "pandas",
        "numpy",
        "machine learning",
    ],

    "frontend developer": [
        "html",
        "css",
        "javascript",
        "react",
        "git",
    ],
}


# ============================================================
# 1. ANALYZE RESUME TEXT
# ============================================================

@router.post(
    "/resume",
    response_model=ResumeAnalysisResponse
)
def analyze_resume(
    payload: ResumeAnalysisRequest
):
    """
    Analyze resume text and calculate:

    - Resume skills
    - Matched skills
    - Missing skills
    - Skill match score
    - Resume improvement recommendations
    - Career recommendations
    """

    # Extract skills from resume
    skills = extract_skills(
        payload.resume_text
    )

    # Get target role
    role = (
        payload.target_role
        or "software engineer"
    ).lower().strip()

    # Select required skills
    required_skills = REQUIRED_SKILLS.get(
        role,
        REQUIRED_SKILLS["software engineer"]
    )

    # Calculate skill gap
    gap = calculate_skill_gap(
        skills,
        required_skills
    )

    # Generate resume recommendations
    recommendations = optimize_resume(
        payload.resume_text,
        gap["missing_skills"]
    )

    # Generate career recommendations
    recommendations.extend(
        career_advice(
            skills,
            role
        )
    )

    # Remove duplicate recommendations
    recommendations = list(
        dict.fromkeys(recommendations)
    )

    return ResumeAnalysisResponse(
        score=gap["score"],
        matched_skills=gap["matched_skills"],
        missing_skills=gap["missing_skills"],
        recommendations=recommendations,
    )


# ============================================================
# 2. UPLOAD RESUME AND EXTRACT TEXT
# ============================================================

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a resume file.

    Supported formats:
    TXT
    PDF
    DOCX

    The uploaded file is converted into text.
    """

    # Check filename
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select a resume file."
        )

    # Allowed extensions
    allowed_extensions = {
        ".txt",
        ".pdf",
        ".docx"
    }

    filename = file.filename.lower()

    extension = ""

    if "." in filename:
        extension = "." + filename.rsplit(
            ".",
            1
        )[1]

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Please upload a TXT, PDF or DOCX resume."
            )
        )

    # Extract resume text
    try:
        extracted_text = await extract_resume_text(
            file
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Resume processing failed: {str(error)}"
        )

    # Make sure text was extracted
    if not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail=(
                "No readable text was found "
                "in the uploaded resume."
            )
        )

    return {
        "message": (
            "Resume uploaded and text "
            "extracted successfully."
        ),
        "filename": file.filename,
        "user_id": current_user.id,
        "text_length": len(extracted_text),
        "text": extracted_text,
    }


# ============================================================
# 3. UPLOAD + ANALYZE + SAVE RESUME + SAVE ANALYSIS
# ============================================================

@router.post("/upload-and-analyze")
async def upload_and_analyze_resume(
    file: UploadFile = File(...),
    target_role: str = Form("software engineer"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a resume and automatically:

    1. Extract resume text
    2. Extract skills
    3. Calculate skill gap
    4. Generate recommendations
    5. Save resume to database
    6. Save analysis to database
    7. Link analysis to the saved resume
    8. Return complete analysis
    """

    # --------------------------------------------------------
    # STEP 1 — Validate filename
    # --------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please select a resume file."
        )

    # --------------------------------------------------------
    # STEP 2 — Validate file type
    # --------------------------------------------------------

    allowed_extensions = {
        ".txt",
        ".pdf",
        ".docx"
    }

    filename = file.filename.lower()

    extension = ""

    if "." in filename:
        extension = "." + filename.rsplit(
            ".",
            1
        )[1]

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Please upload a TXT, PDF or DOCX resume."
            )
        )

    # --------------------------------------------------------
    # STEP 3 — Extract resume text
    # --------------------------------------------------------

    try:
        extracted_text = await extract_resume_text(
            file
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Resume processing failed: {str(error)}"
        )

    # --------------------------------------------------------
    # STEP 4 — Check extracted text
    # --------------------------------------------------------

    if not extracted_text.strip():
        raise HTTPException(
            status_code=400,
            detail=(
                "No readable text was found "
                "in the uploaded resume."
            )
        )

    # --------------------------------------------------------
    # STEP 5 — Extract skills
    # --------------------------------------------------------

    skills = extract_skills(
        extracted_text
    )

    # --------------------------------------------------------
    # STEP 6 — Normalize target role
    # --------------------------------------------------------

    role = (
        target_role
        or "software engineer"
    ).lower().strip()

    # --------------------------------------------------------
    # STEP 7 — Get required skills
    # --------------------------------------------------------

    required_skills = REQUIRED_SKILLS.get(
        role,
        REQUIRED_SKILLS["software engineer"]
    )

    # --------------------------------------------------------
    # STEP 8 — Calculate skill gap
    # --------------------------------------------------------

    gap = calculate_skill_gap(
        skills,
        required_skills
    )

    # --------------------------------------------------------
    # STEP 9 — Generate recommendations
    # --------------------------------------------------------

    recommendations = optimize_resume(
        extracted_text,
        gap["missing_skills"]
    )

    recommendations.extend(
        career_advice(
            skills,
            role
        )
    )

    # Remove duplicate recommendations
    recommendations = list(
        dict.fromkeys(recommendations)
    )

    # --------------------------------------------------------
    # STEP 10 — Save resume
    # --------------------------------------------------------

    resume = create_resume(
        db=db,
        user_id=current_user.id,
        filename=file.filename,
        content=extracted_text,
    )

    # --------------------------------------------------------
    # STEP 11 — Save analysis
    # --------------------------------------------------------

    analysis = ResumeAnalysis(
        user_id=current_user.id,
        resume_id=resume.id,
        target_role=role,
        score=gap["score"],
        matched_skills=json.dumps(
            gap["matched_skills"]
        ),
        missing_skills=json.dumps(
            gap["missing_skills"]
        ),
        recommendations=json.dumps(
            recommendations
        ),
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # --------------------------------------------------------
    # STEP 12 — Return complete result
    # --------------------------------------------------------

    return {
        "message": (
            "Resume uploaded, analyzed "
            "and saved successfully."
        ),

        "analysis_id": analysis.id,

        "resume_id": resume.id,

        "user_id": current_user.id,

        "filename": file.filename,

        "target_role": role,

        "text_length": len(
            extracted_text
        ),

        "extracted_skills": skills,

        "score": gap["score"],

        "matched_skills": gap[
            "matched_skills"
        ],

        "missing_skills": gap[
            "missing_skills"
        ],

        "recommendations": recommendations,
    }


# ============================================================
# 4. GET USER ANALYSIS HISTORY
# ============================================================

@router.get("/history")
def get_analysis_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all previous resume analyses
    belonging to the currently logged-in user.
    """

    analyses = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.user_id == current_user.id
        )
        .order_by(
            ResumeAnalysis.id.desc()
        )
        .all()
    )

    results = []

    for analysis in analyses:

        # Convert matched skills from JSON text
        try:
            matched_skills = json.loads(
                analysis.matched_skills or "[]"
            )
        except Exception:
            matched_skills = []

        # Convert missing skills from JSON text
        try:
            missing_skills = json.loads(
                analysis.missing_skills or "[]"
            )
        except Exception:
            missing_skills = []

        # Convert recommendations from JSON text
        try:
            recommendations = json.loads(
                analysis.recommendations or "[]"
            )
        except Exception:
            recommendations = []

        results.append({
            "analysis_id": analysis.id,

            "resume_id": analysis.resume_id,

            "target_role": analysis.target_role,

            "score": analysis.score,

            "matched_skills": matched_skills,

            "missing_skills": missing_skills,

            "recommendations": recommendations,
        })

    return {
        "user_id": current_user.id,

        "total_analyses": len(results),

        "analyses": results,
    }


# ============================================================
# 5. EXTERNAL JOB DESCRIPTION MATCHING
# ============================================================

@router.post("/external-job-match")
async def match_external_job_description(
    resume_file: UploadFile = File(...),
    job_description_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Compare a resume against an externally uploaded
    job description.

    Supported files:
    PDF
    DOCX
    TXT
    """

    # --------------------------------------------------------
    # STEP 1 — Validate filenames
    # --------------------------------------------------------

    if not resume_file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please upload a resume file."
        )

    if not job_description_file.filename:
        raise HTTPException(
            status_code=400,
            detail="Please upload a job description file."
        )

    # --------------------------------------------------------
    # STEP 2 — Validate file extensions
    # --------------------------------------------------------

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt"
    }

    resume_filename = (
        resume_file.filename.lower()
    )

    job_description_filename = (
        job_description_file.filename.lower()
    )

    resume_extension = ""

    if "." in resume_filename:
        resume_extension = (
            "." +
            resume_filename.rsplit(
                ".",
                1
            )[1]
        )

    job_description_extension = ""

    if "." in job_description_filename:
        job_description_extension = (
            "." +
            job_description_filename.rsplit(
                ".",
                1
            )[1]
        )

    if resume_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Resume must be a PDF, DOCX or TXT file."
            )
        )

    if job_description_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Job description must be a PDF, DOCX or TXT file."
            )
        )

    # --------------------------------------------------------
    # STEP 3 — Extract resume text
    # --------------------------------------------------------

    try:
        resume_text = await extract_resume_text(
            resume_file
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Could not read resume: {str(error)}"
            )
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Resume processing failed: {str(error)}"
            )
        )

    # --------------------------------------------------------
    # STEP 4 — Check resume text
    # --------------------------------------------------------

    if not resume_text.strip():
        raise HTTPException(
            status_code=400,
            detail=(
                "No readable text was found in the resume."
            )
        )

    # --------------------------------------------------------
    # STEP 5 — Extract job description text
    # --------------------------------------------------------

    try:
        job_description_text = await extract_resume_text(
            job_description_file
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=(
                "Could not read job description: "
                f"{str(error)}"
            )
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=(
                "Job description processing failed: "
                f"{str(error)}"
            )
        )

    # --------------------------------------------------------
    # STEP 6 — Check job description text
    # --------------------------------------------------------

    if not job_description_text.strip():
        raise HTTPException(
            status_code=400,
            detail=(
                "No readable text was found "
                "in the job description."
            )
        )

    # --------------------------------------------------------
    # STEP 7 — Extract resume skills
    # --------------------------------------------------------

    resume_skills = extract_skills(
        resume_text
    )

    # --------------------------------------------------------
    # STEP 8 — Extract job description skills
    # --------------------------------------------------------

    job_skills = extract_skills(
        job_description_text
    )

    # --------------------------------------------------------
    # STEP 9 — Normalize skills
    # --------------------------------------------------------

    resume_skills = normalize_skills(
        resume_skills
    )

    job_skills = normalize_skills(
        job_skills
    )

    # --------------------------------------------------------
    # STEP 10 — Calculate match score
    # --------------------------------------------------------

    match_result = calculate_match_score(
        resume_skills,
        job_skills
    )

    # --------------------------------------------------------
    # STEP 11 — Get matched and missing skills
    # --------------------------------------------------------

    matched_skills = match_result[
        "matched_skills"
    ]

    missing_skills = match_result[
        "missing_skills"
    ]

    match_score = match_result[
        "score"
    ]

    # --------------------------------------------------------
    # STEP 12 — Generate recommendations
    # --------------------------------------------------------

    recommendations = []

    if missing_skills:

        for skill in missing_skills:

            recommendations.append(
                f"Consider learning or improving {skill} "
                f"to increase your match for this job."
            )

    else:

        recommendations.append(
            "Your resume contains all recognized skills "
            "required by this job description."
        )

    # Additional recommendations based on score

    if match_score < 40:

        recommendations.append(
            "Your current profile has a low match score. "
            "Focus on the missing technical skills before applying."
        )

    elif match_score < 70:

        recommendations.append(
            "Your profile is a partial match. "
            "Adding the missing skills can significantly "
            "improve your chances."
        )

    elif match_score < 90:

        recommendations.append(
            "Your profile is a strong match. "
            "Consider tailoring your resume to emphasize "
            "the matched skills."
        )

    else:

        recommendations.append(
            "Excellent match. Tailor your resume keywords "
            "to the job description before applying."
        )

    # Remove duplicate recommendations

    recommendations = list(
        dict.fromkeys(
            recommendations
        )
    )

    # --------------------------------------------------------
    # STEP 13 — Return complete result
    # --------------------------------------------------------

    return {

        "message": (
            "External job description "
            "analyzed successfully."
        ),

        "user_id": current_user.id,

        "resume_filename": (
            resume_file.filename
        ),

        "job_description_filename": (
            job_description_file.filename
        ),

        "resume_skills": resume_skills,

        "job_skills": job_skills,

        "match_score": match_score,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills,

        "recommendations": recommendations,
    }