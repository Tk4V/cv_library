from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Protocol, Tuple

from django.conf import settings
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
import logging

from .models import CV
from celery_tasks.services.pdf_service import PDFService

logger = logging.getLogger(__name__)


class CVRepository:
    """Data access layer for CV model."""

    def get_all_lightweight(self) -> QuerySet[CV]:
        return CV.objects.select_related('owner').only(
            "firstname", "lastname", "created_at", "updated_at", "bio", "skills", "projects", "contacts", "owner_id"
        ).order_by("-created_at")
    
    def get_all_lightweight_sorted(self, sort_by: str = "created_at", order: str = "desc") -> QuerySet[CV]:
        """
        Get all CVs with custom sorting.
        
        Args:
            sort_by: Field to sort by ('created_at', 'updated_at', 'firstname', 'lastname')
            order: Sort order ('asc' or 'desc')
            
        Returns:
            QuerySet of CVs sorted by specified field
        """
        valid_sort_fields = ['created_at', 'updated_at', 'firstname', 'lastname']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        
        if order == 'asc':
            sort_field = sort_by
        else:  # desc
            sort_field = f"-{sort_by}"
        
        return CV.objects.select_related('owner').only(
            "firstname", "lastname", "created_at", "updated_at", "bio", "skills", "projects", "contacts", "owner_id"
        ).order_by(sort_field)

    def get_by_id(self, cv_id: int) -> CV:
        return get_object_or_404(CV, pk=cv_id)


@dataclass
class PDFExportResult:
    file_path: Path


class CVPdfExporter:
    """Handles rendering CV to a PDF file on disk."""

    def __init__(self, output_root: Optional[Path] = None) -> None:
        self.output_root = Path(output_root or settings.MEDIA_ROOT) / "pdf"
        self.output_root.mkdir(parents=True, exist_ok=True)
        self.template_name = "main/cv_pdf.html"

    def export_to_file(self, cv: CV) -> PDFExportResult:
        pdf_service = PDFService()
        pdf_bytes = pdf_service.render_to_pdf_bytes(self.template_name, {"cv": cv})
        file_path = self.output_root / f"cv_{cv.pk}.pdf"
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)
        return PDFExportResult(file_path=file_path)


class CVService:
    """Business logic for CVs."""

    def __init__(self, repository: Optional[CVRepository] = None, exporter: Optional[CVPdfExporter] = None) -> None:
        self.repository = repository or CVRepository()
        self.exporter = exporter or CVPdfExporter()

    def list_cvs_for_listing(self) -> Iterable[CV]:
        return self.repository.get_all_lightweight()
    
    def list_cvs_sorted(self, sort_by: str = "created_at", order: str = "desc") -> Iterable[CV]:
        """
        Get CVs with custom sorting.
        
        Args:
            sort_by: Field to sort by ('created_at', 'updated_at', 'firstname', 'lastname')
            order: Sort order ('asc' or 'desc')
            
        Returns:
            QuerySet of CVs sorted by specified field
        """
        return self.repository.get_all_lightweight_sorted(sort_by, order)

    def retrieve_cv(self, cv_id: int) -> CV:
        return self.repository.get_by_id(cv_id)

    def generate_pdf_file(self, cv_id: int) -> Path:
        cv = self.retrieve_cv(cv_id)
        result = self.exporter.export_to_file(cv)
        return result.file_path


class TranslationProvider(Protocol):
    def translate(self, text: str, target_language: str) -> str: ...
    def is_enabled(self) -> bool: ...


class OpenAITranslationProvider:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key or getattr(settings, 'OPENAI_API_KEY', None)
        self.model = model or getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini-translator')
        self.project = getattr(settings, 'OPENAI_PROJECT', None)
        self._client = None
        
        # Debug logging
        logger.info(f"OpenAI API key length: {len(self.api_key) if self.api_key else 0}")
        logger.info(f"OpenAI API key starts with: {self.api_key[:10] if self.api_key else 'None'}...")
        logger.info(f"OpenAI model: {self.model}")
        logger.info(f"OpenAI project: {self.project}")
        
        if not self.api_key:
            logger.info("OpenAI API key not configured; translation will be a no-op")
            return
        try:
            from openai import OpenAI  # type: ignore
            # 2025 pattern: pass project if present
            if self.project:
                self._client = OpenAI(api_key=self.api_key, project=self.project)
            else:
                self._client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as err:
            logger.exception("Failed to initialize OpenAI client: %s", err)
            self._client = None

    def is_enabled(self) -> bool:
        return self._client is not None

    def translate(self, text: str, target_language: str) -> str:
        if not self._client:
            return text  # fallback: no-op if OpenAI not configured
        try:
            # 2025: Responses API supports text instruction with JSON output if needed.
            instruction = f"Translate into {target_language}. Return only the translated text without quotes."
            resp = self._client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": "You are a precise translation engine. Preserve meaning; do not add explanations.",
                    },
                    {"role": "user", "content": instruction + "\n\n" + text},
                ],
                temperature=1,
                max_output_tokens=1200,
            )
            # responses API: text lives at output_text
            out = getattr(resp, 'output_text', None)
            return out or text
        except Exception as err:
            logger.exception("OpenAI translate failed: %s", err)
            return text


class TranslationService:
    def __init__(self, provider: Optional[TranslationProvider] = None) -> None:
        self.provider = provider or OpenAITranslationProvider()

    def translate_cv(self, cv: CV, target_language: str) -> Tuple[dict[str, str], bool]:
        fields = {
            'name': f"{cv.firstname} {cv.lastname}",
            'bio': cv.bio or '',
            'skills': cv.skills or '',
            'projects': cv.projects or '',
            'contacts': cv.contacts or '',
        }
        result = {k: self.provider.translate(v, target_language) for k, v in fields.items()}
        return result, self.provider.is_enabled()


class CVAnalysisProvider(Protocol):
    """Protocol for CV analysis providers."""
    
    def analyze_cv(self, content: str, question: str) -> str:
        """Analyze CV content and answer a specific question."""
        ...


class OpenAICVAnalysisProvider:
    """OpenAI-based CV analysis provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, project: Optional[str] = None) -> None:
        self.api_key = api_key or getattr(settings, 'OPENAI_API_KEY', None)
        self.model = model or getattr(settings, 'OPENAI_MODEL', 'gpt-4o-mini')
        self.project = getattr(settings, 'OPENAI_PROJECT', None)
        self._client = None
        
        # Debug logging
        logger.info(f"CV Analysis - OpenAI API key length: {len(self.api_key) if self.api_key else 0}")
        logger.info(f"CV Analysis - OpenAI API key starts with: {self.api_key[:10] if self.api_key else 'None'}...")
        logger.info(f"CV Analysis - OpenAI model: {self.model}")
        logger.info(f"CV Analysis - OpenAI project: {self.project}")
        
        if not self.api_key:
            logger.info("OpenAI API key not configured; CV analysis will be a no-op")
            return
            
        try:
            from openai import OpenAI  # type: ignore
            if self.project:
                self._client = OpenAI(api_key=self.api_key, project=self.project)
            else:
                self._client = OpenAI(api_key=self.api_key)
            logger.info("CV Analysis - OpenAI client initialized successfully")
        except Exception as err:
            logger.exception("Failed to initialize OpenAI client for CV analysis: %s", err)
            self._client = None

    def is_enabled(self) -> bool:
        return self._client is not None

    def analyze_cv(self, content: str, question: str) -> str:
        if not self._client:
            return "CV analysis is not available. Please configure OpenAI API key."
            
        try:
            prompt = f"""
            You are a professional CV reviewer and career advisor. 
            
            CV Content:
            {content}
            
            Question/Request: {question}
            
            Please provide helpful, constructive feedback and suggestions. 
            Be specific, actionable, and professional in your response.
            Focus on practical improvements the candidate can make.
            """
            
            resp = self._client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "system",
                        "content": "You are a professional CV reviewer and career advisor. Provide constructive, actionable feedback."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_output_tokens=1500,
            )
            
            return getattr(resp, 'output_text', 'Analysis not available.')
            
        except Exception as err:
            logger.exception("OpenAI CV analysis failed: %s", err)
            return f"Analysis failed: {str(err)}"


class CVAnalysisService:
    """Service for analyzing CV content using OpenAI."""
    
    def __init__(self, provider: Optional[CVAnalysisProvider] = None) -> None:
        self.provider = provider or OpenAICVAnalysisProvider()

    def analyze_cv(self, cv: CV, question: str) -> Tuple[str, bool]:
        """Analyze CV content and answer a specific question."""
        try:
            # Get CV content as text
            content = f"""
            Name: {cv.firstname} {cv.lastname}
            Bio: {cv.bio or 'Not provided'}
            Skills: {cv.skills or 'Not provided'}
            Projects: {cv.projects or 'Not provided'}
            Contacts: {cv.contacts or 'Not provided'}
            """
            
            # Analyze using provider
            analysis = self.provider.analyze_cv(content, question)
            is_enabled = self.provider.is_enabled()
            
            logger.info(f"Successfully analyzed CV {cv.id}")
            return analysis, is_enabled
            
        except Exception as e:
            logger.error(f"CV analysis failed for CV {cv.id}: {e}")
            return f"Analysis failed: {str(e)}", False
