from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import PyPDF2
import io
from sqlalchemy.ext.asyncio import AsyncSession

from ..dependencies import get_db
from ..utils.openai_integration import OpenAIIntegration
from ..models.pydantic_models import CareStayInfo, CVAnalysisRequest, CVAnalysisResult

router = APIRouter()

@router.get("/care_stays/list", response_model=List[CareStayInfo])
async def get_care_stays_list(
    agency_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    Get list of care stays with basic information for CV quality analysis
    """
    try:
        from ..queries.care_stays.care_stays_list import get_care_stays_for_cv_analysis
        
        care_stays = await get_care_stays_for_cv_analysis(
            agency_id=agency_id,
            limit=limit,
            offset=offset
        )
        
        return care_stays
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/care_stays/{care_stay_id}/communications")
async def get_care_stay_communications(care_stay_id: str):
    """
    Get all email and ticket communications for a specific care stay
    """
    try:
        from ..queries.care_stays.care_stay_communications import get_communications_for_stay
        
        communications = await get_communications_for_stay(care_stay_id)
        
        return {
            "care_stay_id": care_stay_id,
            "emails": communications.get("emails", []),
            "tickets": communications.get("tickets", []),
            "total_count": communications.get("total_count", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze", response_model=CVAnalysisResult)
async def analyze_cv_quality(
    care_stay_id: str,
    cv_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze CV quality for a specific care stay
    """
    try:
        # Extract text from CV
        cv_content = await extract_cv_content(cv_file)
        
        # Get communications for this care stay
        from ..queries.care_stays.care_stay_communications import get_communications_for_stay
        communications = await get_communications_for_stay(care_stay_id)
        
        # Get care stay details
        from ..queries.care_stays.care_stays_list import get_care_stay_details
        care_stay_details = await get_care_stay_details(care_stay_id)
        
        # Analyze with OpenAI
        openai_client = OpenAIIntegration()
        analysis_result = await openai_client.analyze_cv_quality(
            cv_content=cv_content,
            communications=communications,
            care_stay_info=care_stay_details
        )
        
        # Store result in database
        await store_cv_analysis_result(db, care_stay_id, analysis_result)
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def extract_cv_content(cv_file: UploadFile) -> str:
    """
    Extract text content from uploaded CV file (PDF or text)
    """
    content = await cv_file.read()
    
    if cv_file.content_type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    elif cv_file.content_type in ["text/plain", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        # For now, just decode as text for plain text files
        return content.decode('utf-8', errors='ignore')
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {cv_file.content_type}")

async def store_cv_analysis_result(db: AsyncSession, care_stay_id: str, result: Dict[str, Any]):
    """
    Store CV analysis result in database
    """
    from ..models.database import CVAnalysisResult as CVAnalysisResultDB
    
    # Extract agency_id from result
    agency_id = result.get("agency_id") or result.get("care_stay_info", {}).get("agency_id")
    
    db_result = CVAnalysisResultDB(
        care_stay_id=care_stay_id,
        agency_id=agency_id
    )
    
    # Use the model's setter methods
    db_result.set_categories(result.get("categories", {}))
    db_result.set_fulfillment_scores(result.get("fulfillment_scores", {}))
    db_result.set_discrepancies(result.get("discrepancies", []))
    db_result.set_overall_score(result.get("overall_score", 5.0))
    db_result.set_analysis_details(result.get("details", {}))
    
    db.add(db_result)
    await db.commit()