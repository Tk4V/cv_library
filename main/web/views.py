from django.http import HttpResponseRedirect
from typing import Optional
from django.views.generic import DetailView, ListView, FormView, RedirectView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout, authenticate, get_user_model
from django import forms
from django.urls import reverse_lazy
from django.contrib import messages

from ..models import CV
from ..services import CVService
from ..enums import Language
from ..filters.cv_filters import filter_cvs_by_query
from ..forms import CVForm
from .view_handlers import CVDetailHandler


class HomeView(TemplateView):
    template_name = "main/home.html"


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)


class LoginView(FormView):
    template_name = "main/login.html"
    form_class = LoginForm

    def form_valid(self, form):
        user = authenticate(self.request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is None:
            form.add_error(None, "Invalid credentials")
            return self.form_invalid(form)
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        return "/cvs/"


class LogoutView(RedirectView):
    pattern_name = "home"

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class RegisterView(FormView):
    template_name = "main/register.html"
    form_class = RegisterForm

    def form_valid(self, form):
        User = get_user_model()
        if User.objects.filter(username=form.cleaned_data['username']).exists():
            form.add_error('username', 'Username already exists')
            return self.form_invalid(form)
        user = User.objects.create_user(
            username=form.cleaned_data['username'],
            email=form.cleaned_data.get('email') or "",
            password=form.cleaned_data['password'],
        )
        login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        return "/cvs/"


class CVListView(LoginRequiredMixin, ListView):
    model = CV
    template_name = "main/cv_list.html"
    context_object_name = "cvs"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._service = None
    
    @property
    def service(self):
        """Lazy initialization of CVService."""
        if self._service is None:
            self._service = CVService()
        return self._service

    def get_queryset(self):
        # Get sorting parameters from URL
        sort_by = self.request.GET.get("sort", "created_at")
        order = self.request.GET.get("order", "desc")
        
        # Get sorted queryset
        queryset = self.service.list_cvs_sorted(sort_by, order)
        
        # Apply search filter
        query = self.request.GET.get("q", "")
        return filter_cvs_by_query(queryset, query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        context["sort_by"] = self.request.GET.get("sort", "created_at")
        context["order"] = self.request.GET.get("order", "desc")
        return context


class CVDetailView(LoginRequiredMixin, DetailView):
    """View for displaying CV details with analysis and translation capabilities."""
    
    model = CV
    template_name = "main/cv_detail.html"
    context_object_name = "cv"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handler = CVDetailHandler()

    def post(self, request, *args, **kwargs):
        """Handle POST requests for various CV operations."""
        cv = self.get_object()
        
        # Handle async PDF download request
        if 'download_pdf_async' in request.POST:
            return self._handle_async_pdf_download_request(request, cv.pk)
        
        # Handle other POST requests
        self._handle_email_request(request, cv.pk)
        self._handle_translation_request(request, cv)
        self._handle_analysis_request(request, cv.pk)
        self._handle_clear_analysis_request(request)
        
        return self.get(request, *args, **kwargs)
    
    def _handle_async_pdf_download_request(self, request, cv_id: int) -> HttpResponseRedirect:
        """Handle async PDF download request."""
        from celery_tasks.tasks.pdf import generate_cv_pdf_download_task
        
        # Start async PDF generation
        task = generate_cv_pdf_download_task.delay(cv_id)
        
        # Store task ID in session
        request.session['pdf_task_id'] = task.id
        request.session['pdf_processing'] = True
        
        # Redirect back to the same page to show progress
        return HttpResponseRedirect(request.path)
    
    def _handle_email_request(self, request, cv_id: int) -> None:
        """Handle email PDF request."""
        if 'email' in request.POST:
            result = self.handler.handle_email_request(request, cv_id)
            if result:
                if 'error' in result:
                    messages.error(request, result['error'])
                elif 'success' in result:
                    messages.success(request, result['message'])
    
    def _handle_translation_request(self, request, cv: CV) -> None:
        """Handle translation request."""
        if 'lang' in request.POST:
            result = self.handler.handle_translation_request(request, cv)
            if result:
                request.session['cv_translations'] = result
    
    def _handle_analysis_request(self, request, cv_id: int) -> None:
        """Handle analysis request."""
        if 'start_analysis' in request.POST:
            result = self.handler.handle_analysis_request(request, cv_id)
            if result and 'error' in result:
                messages.error(request, result['error'])
    
    def _handle_clear_analysis_request(self, request) -> None:
        """Handle clear analysis request."""
        if 'clear_analysis' in request.POST:
            self.handler.handle_clear_analysis_request(request)
    
    def get_context_data(self, **kwargs):
        """Get context data for template rendering."""
        context = super().get_context_data(**kwargs)
        
        # Add translation context
        context.update(self.handler.get_translation_context(self.request))
        
        # Add analysis context
        context.update(self.handler.get_analysis_context(self.request))
        
        # Add PDF progress context
        context.update(self._get_pdf_progress_context())
        
        # Add languages for translation dropdown
        context['languages'] = [lang.value for lang in Language]
        
        
        return context
    
    def _get_pdf_progress_context(self):
        """Get PDF progress context for template."""
        context = {
            'pdf_processing': False,
            'pdf_progress': 0,
            'pdf_status': '',
            'pdf_download_url': None
        }
        
        pdf_task_id = self.request.session.get('pdf_task_id')
        if not pdf_task_id:
            return context
        
        try:
            from celery.result import AsyncResult
            task_result = AsyncResult(pdf_task_id)
            state = task_result.state
            
            if state == 'SUCCESS':
                result = task_result.result
                if result.get('status') == 'success':
                    # PDF is ready for download
                    context['pdf_download_url'] = result.get('download_url')
                    # Clear session data
                    self.request.session.pop('pdf_task_id', None)
                    self.request.session.pop('pdf_processing', None)
                else:
                    context['pdf_status'] = 'PDF generation failed'
                    self.request.session.pop('pdf_task_id', None)
                    self.request.session.pop('pdf_processing', None)
            elif state == 'PENDING':
                context['pdf_processing'] = True
                context['pdf_progress'] = 0
                context['pdf_status'] = 'Starting PDF generation...'
            elif state == 'PROGRESS':
                context['pdf_processing'] = True
                meta = task_result.info
                context['pdf_progress'] = meta.get('current', 0)
                context['pdf_status'] = meta.get('status', 'Processing...')
            else:
                # Task failed or unknown state
                context['pdf_status'] = 'PDF generation failed'
                self.request.session.pop('pdf_task_id', None)
                self.request.session.pop('pdf_processing', None)
                
        except Exception:
            # If there's any error checking the task, assume it's still processing
            context['pdf_processing'] = True
            context['pdf_progress'] = 50
            context['pdf_status'] = 'Processing...'
        
        return context






class CVCreateView(LoginRequiredMixin, CreateView):
    """Create a new CV."""
    model = CV
    form_class = CVForm
    template_name = "main/cv_form.html"
    success_url = reverse_lazy("cv_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "CV created successfully!")
        return super().form_valid(form)


class CVUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing CV."""
    model = CV
    form_class = CVForm
    template_name = "main/cv_form.html"
    success_url = reverse_lazy("cv_list")

    def form_valid(self, form):
        messages.success(self.request, "CV updated successfully!")
        return super().form_valid(form)

    def get_queryset(self):
        # Only allow users to edit their own CVs (unless they're admin)
        if self.request.user.is_superuser:
            return CV.objects.all()
        return CV.objects.filter(owner=self.request.user)


class CVDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a CV."""
    model = CV
    template_name = "main/cv_confirm_delete.html"
    success_url = reverse_lazy("cv_list")

    def get_queryset(self):
        # Only allow users to delete their own CVs (unless they're admin)
        if self.request.user.is_superuser:
            return CV.objects.all()
        return CV.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "CV deleted successfully!")
        return super().delete(request, *args, **kwargs)


