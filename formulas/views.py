from django.shortcuts import render,redirect
from django.views import View
from django.views.generic import ListView
from django.views.generic import DetailView,TemplateView, CreateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy, reverse
from .models import Formula, Chapter, SimpleUser, PurchasedChapter, has_purchased, SavedFormula, ExamDate, DailyChallenge
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import  FormulaForm, ChapterForm
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .chatbot import ask_chatbot
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from .chatbot import generate_practice_question
import random
from datetime import date, datetime
import requests
import os
import razorpay
import hmac
from django.db.models import Count
from django.conf import settings
from django.templatetags.static import static
from .chatbot import get_daily_physics_fact
from django.db.models import Case, When, Value, IntegerField
from django.http import FileResponse, Http404, JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
from django.template.loader import render_to_string
from .pdf_utils import render_formula_media_url, simplify_latex_for_text, format_units_for_display
import logging
from weasyprint import HTML
from django.utils import timezone
from collections import Counter
from django.db.models import Max

#from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

#from allauth.account.adapter import DefaultAccountAdapter

# Create your views here.


class BaseView(TemplateView):
    template_name="formulas/base.html"


class IndexView(ListView):
    template_name = "formulas/index.html"
    context_object_name = "formulas"
    model = Formula

    def get(self, request):
        formulas = Formula.objects.all()
        total = formulas.count()
        formula= formulas.filter(derivation_image__isnull=False)

        # Saved count
        saved_count = 0
        if request.user.is_authenticated:
            saved_count = Formula.objects.filter(
                is_saved=True,
                user=request.user
            ).count()

        category_counts = {
            cat.name.lower().replace(' ', '_').replace('&', 'and'): cat.formula_count
            for cat in Chapter.objects.annotate(formula_count=Count('formula'))
            }

        visited_ids= request.session.get("visited_formulas", [])

        visited_counts= {
            cat.name.lower().replace(' ', '_').replace('&', 'and'):
                Formula.objects.filter(chapter=cat, slug__in=visited_ids).count()
            for cat in Chapter.objects.all()
            }



        formula_of_day = random.choice(list(formula)) if formula.exists() else None


        return render(request, "formulas/index.html", {
            "formulas": formulas,
            "total": total,
            "saved_count": saved_count,
            "user": request.user,
            "formula_of_day": formula_of_day,
            "count" : category_counts,
            "visited" : visited_counts,
        })



class SingleFormulaView(DetailView):
    template_name="formulas/single_formula.html"
    model=Formula
    fields="__all__"
    context_object_name="formula"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['similar_formulas'] = Formula.objects.filter(
            chapter = self.object.chapter
            ).exclude(pk=self.object.pk)[:5]


        variables = self.object.formula_variables.filter(is_solvable=True).order_by("order")
        constants = self.object.constants.all()

        context['calculator_config'] = {
            "variables": [
                {
                    "symbol": v.symbol,
                    "name": v.name,
                    "unit": v.unit,
                    "expr": v.expr,
                }
                for v in variables
            ],
            "constants": {c.symbol: c.value for c in constants},
        }


        return context

    def get(self, request, *args, **kwargs):
        response= super().get(request, *args, **kwargs)

        visited= request.session.get("visited_formulas", [])
        if self.object.slug not in visited:
            visited.append(self.object.slug)
            request.session['visited_formulas']= visited
            request.session.modified= True

        return response

    def post(self, request, *args, **kwargs):
        self.object=self.get_object()

        if "image" in request.FILES:
            self.object.image = request.FILES["image"]
            self.object.save()


        context=self.get_context_data()

        correct_answer=(self.object.correct_answer or '').strip().lower()
        user_answer=(request.POST.get("user_answer") or '').strip().lower()
        explanation=self.object.explanation



        if user_answer:

                if (user_answer.strip().lower()) == (correct_answer.strip().lower()):
                    context["result"]="✔️Correct Answer"
                else:
                 context["result"]=f"❌Wrong Answer! Correct answer is: {correct_answer} "
                 context["explanation"]= explanation



                return self.render_to_response(context)

        if not user_answer:
            context["result"]="Please enter some answer"
            return render(request, "formulas/single_formula.html", context)


class SavedFormulasView(View):
    slug_field = "slug"
    slug_url_kwarg = "slug"


    def post(self, request, slug, *args, **kwargs):
        user_id = request.session.get('user_session_id')
        if not user_id:
            return redirect('single-formula-page', slug=slug)

        user = SimpleUser.objects.get(session_id=user_id)
        formula = get_object_or_404(Formula, slug=slug)
        SavedFormula.objects.get_or_create(user=user, formula=formula)
        return redirect('saved-page', slug=slug)

    def get(self, request, slug):
        formula = get_object_or_404(Formula, slug=slug)
        user_id = request.session.get('user_session_id')
        user = SimpleUser.objects.get(session_id=user_id)

        # NEW: query the through-table directly (instead of Formula via
        # savedformula__user) so we can read each save's timestamp and
        # attach a days_since_saved value the template can check.
        saved_rows = (
            SavedFormula.objects
            .filter(user=user)
            .select_related('formula')
            .order_by('-saved_at')  # most recently saved first
        )

        today = timezone.localdate()
        saved_formulas = []
        for row in saved_rows:
            f = row.formula
            f.days_since_saved = (today - row.saved_at.date()).days
            saved_formulas.append(f)

        return render(request, "formulas/saved_formulas.html", {
            "savedformulas": saved_formulas,
            "last_formula": formula
        })


def unsave(request, slug):
    formula = get_object_or_404(Formula, slug=slug)
    if request.method != "POST":
        return redirect("single-formula-page", slug=slug)

    user_id = request.session.get('user_session_id')
    if not user_id:
        return redirect("single-formula-page", slug=slug)

    user = SimpleUser.objects.get(session_id=user_id)
    SavedFormula.objects.filter(user=user, formula=formula).delete()
    return redirect("single-formula-page", slug=slug)


class TryView(TemplateView):
    template_name="formulas/try.html"


@method_decorator(csrf_exempt, name='dispatch')
class ChatbotView(View):

    def post(self, request):
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")
            chat_history = data.get("history", [])

            if not user_message:
                return JsonResponse({"error": "No message provided"}, status=400)

            response = ask_chatbot(user_message, chat_history)
            return JsonResponse({"response": response})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    def get(self, request):
        return JsonResponse({"error": "Only POST allowed"}, status=405)



class CategoryView(ListView):
    model = Formula
    fields = "__all__"
    template_name = "formulas/categories.html"
    context_object_name = "formulas"

    def get_queryset(self):
        return Formula.objects.filter(chapter__name__iexact=self.kwargs['chapter'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chapter_param = self.kwargs['chapter']

        # Fixed syntax error: added '=' after name__iexact
        chapter_obj = Chapter.objects.filter(name__iexact=chapter_param).first()

        context['chapter_name'] = chapter_param.title()
        context['chapter_slug'] = chapter_param
        context['category'] = chapter_obj
        context['chapter'] = chapter_obj  # Allows using {{ chapter.is_premium }} in template

        # Determine purchase status for paywall button UI
        if chapter_obj and chapter_obj.is_premium:
            context['is_purchased'] = has_purchased(chapter_obj, self.request)
        else:
            context['is_purchased'] = True

        return context



class AboutMeView(TemplateView):
    template_name = "formulas/me.html"








def practice_question(request, slug):
    try:
        formula = Formula.objects.get(slug=slug)
        difficulty = request.GET.get("difficulty", "medium")

        result = generate_practice_question(
            formula.title, formula.form,
            formula.chapter, formula.description,
            difficulty
        )
        return JsonResponse(result)

    except Formula.DoesNotExist:
        return JsonResponse({"error": "Formula not found"}, status=404)
    except json.JSONDecodeError as e:
        return JsonResponse({"error": f"Invalid JSON: {str(e)}"}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_youtube_video(formula_title):
    api_key = "AIzaSyAMRUukG1tvBo3947-UavtL1gIdK2RgY0E"
    query = f"{formula_title} physics explanation"

    url = f"https://www.googleapis.com/youtube/v3/search"
    params = {
        'key': api_key,
        'q': query,
        'part': 'snippet',
        'type': 'video',
        'maxResults': 1,
        'relevanceLanguage': 'en'
    }

    try:
         response = requests.get(url, params=params)
         data = response.json()

         items = data.get('items', [])
         if items:
             video_id = items[0]['id']['videoId']
             return f"https://www.youtube.com/watch?v={video_id}"
         return None
    except Exception as e:
        return None

class FormulaAnimationView(View):

    def get(self, request, formula_id):
        formula = get_object_or_404(Formula, pk=formula_id)

        prebuilt = self.get_prebuilt_animation(formula)
        if prebuilt:
            return JsonResponse({
                'html': prebuilt,
                'title': formula.title,
                'source': 'prebuilt'
            })

        # Groq API call
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.environ.get('GROQ_ANIMATION_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",  # free & fast
                    "max_tokens": 2000,
                    "messages": [{
                        "role": "user",
                        "content": f"""
                        Create a beautiful SVG + JavaScript animation explaining:
                        Formula: {formula.title}
                        Expression: {formula.formula_text}
                        Category: {formula.category.name}

                        Return ONLY an HTML snippet (no DOCTYPE, no <html> tags) with:
                        - SVG animation demonstrating this formula visually
                        - Clear variable labels
                        - Smooth animation using requestAnimationFrame or CSS
                        - Dark theme (#0d1117 background)
                        - Max 400px height
                        - Physically accurate
                        """
                    }]
                }
            )

            data = response.json()
            animation_html = data['choices'][0]['message']['content']

            return JsonResponse({
                'html': animation_html,
                'title': formula.title,
                'source': 'ai'
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def privacy(request):
    return render(request, "formulas/privacy.html")


def get_nearest_exam(exam_prefix):
    today = date.today()
    upcoming = ExamDate.objects.filter(exam_key__startswith=exam_prefix, exam_date__gte=today).order_by('exam_date').first()
    if upcoming:
        return upcoming.display_name, (upcoming.exam_date - today).days
    return None


class ExamFilterView(View):
    def get(self, request, *args, **kwargs):
        path = request.path.strip('/')

        if path == 'neet':
            formula_path = reverse('neet-formulas')
        elif path == 'jee':
            formula_path = reverse('jee-formulas')
        else:
            formula_path = reverse('both-formulas')

        if path == 'jee':
            formulas = Formula.objects.filter(
                exam_tag__in=['jee', 'both']
            ).select_related('chapter').annotate(
                tag_priority=Case(
                    When(exam_tag='jee', then=Value(0)),
                    When(exam_tag='both', then=Value(1)),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            ).order_by('tag_priority', 'title')
            exam_label = 'JEE'
        elif path == 'neet':
            formulas = Formula.objects.filter(
                exam_tag__in=['neet', 'both']
            ).annotate(
                tag_priority=Case(
                    When(exam_tag='neet', then=Value(0)),
                    When(exam_tag='both', then=Value(1)),
                    default=Value(2),
                    output_field=IntegerField(),
                )
            ).order_by('tag_priority', 'title')
            exam_label = 'NEET'
        elif path == 'both':
            formulas = Formula.objects.filter(
                exam_tag='both'
            ).order_by('title')
            exam_label = 'JEE + NEET'
        else:
            formulas = Formula.objects.none()
            exam_label = ''


        exam_key = None
        days_remaining = None
        if path in ('jee', 'neet'):
            exam_info = get_nearest_exam(path)
            if exam_info:
                exam_key, days_remaining = exam_info

        affiliate_data = None
        if path == 'jee':
            affiliate_data = {
                'title': 'DC Pandey Physics Series for JEE Main & Advanced',
                'subtitle': 'Top recommended practice book for solving JEE numericals',
                'link': 'https://amzn.to/B08txTj7c',  # Put your Amazon tag link here
                'tag_label': 'Recommended for JEE'
                }
        elif path == 'neet':
            affiliate_data = {
                'title': 'MTG Objective NCERT at your Fingertips Physics',
                'subtitle': 'Master NCERT line-by-line questions for NEET 2026',
                'link': 'https://amzn.to/B0bwwfnAy', # Put your Amazon tag link here
                'tag_label': 'Recommended for NEET'
                }

        return render(request, 'formulas/exam_filter.html', {
            'formulas': formulas,
            'exam_label': exam_label,
            'total': formulas.count(),
            'formula_path': formula_path,
            'exam_key': exam_key,
            'days_remaining': days_remaining,
            'affiliate': affiliate_data,
            })

def progress_dashboard(request):
    user_id = request.session.get('user_session_id')
    user = None

    if user_id:
        try:
            user = SimpleUser.objects.get(session_id=user_id)
        except SimpleUser.DoesNotExist:
            request.session.flush()
            user = None

    total_formulas = Formula.objects.count()

    if not user:
        # Logged-out visitor: show locked preview instead of redirecting
        context = {
            'is_logged_in': False,
            'total_saved': 0,
            'total_formulas': total_formulas,
            'favourite_chapter': "—",
            'category_counts': {},
            'jee_count': 0,
            'neet_count': 0,
            'both_count': 0,
            'saved_formulas': [],
            'completion_percent': 0,
            'chapters_started': 0,
            'strongest_chapter': None,
            'next_chapter': None,
            'streak_days': 0,
        }
        return render(request, 'formulas/dashboard.html', context)

    # Get all saved formulas for this user only
    saved_formulas = Formula.objects.filter(savedformula__user=user)

    total_saved = saved_formulas.count()

    category_counts = Counter(
        saved_formulas.values_list('chapter__name', flat=True)
    )
    favourite_chapter = max(category_counts, key=category_counts.get) if category_counts else "None"

    jee_count = saved_formulas.filter(exam_tag='jee').count()
    neet_count = saved_formulas.filter(exam_tag='neet').count()
    both_count = saved_formulas.filter(exam_tag='both').count()

    # --- NEW: Chapters Started ---
    # How many distinct chapters the user has at least one saved formula in.
    chapters_started = len(category_counts)

    # --- NEW: Strongest chapter ---
    # Same as favourite_chapter, but named for the "Strongest" badge in the template.
    # (Kept as a separate variable in case you later want the badge logic to
    # differ from the raw favourite — e.g. requiring a minimum count to qualify.)
    strongest_chapter = favourite_chapter if category_counts else None

    # --- NEW: Chapter to tackle next ---
    # Prefer a chapter the user hasn't touched at all; if they've started
    # every chapter, fall back to their weakest (lowest-count) started chapter.
    all_chapter_names = list(
        Chapter.objects.values_list('name', flat=True)
    )
    untouched_chapters = [c for c in all_chapter_names if c not in category_counts]

    if untouched_chapters:
        next_chapter = untouched_chapters[0]
    elif category_counts:
        next_chapter = min(category_counts, key=category_counts.get)
    else:
        next_chapter = None

    # --- NEW: Streak ---
    # Requires two fields on SimpleUser: last_active_date (DateField, null=True)
    # and streak_days (IntegerField, default=0). Update these wherever a
    # formula gets saved (see snippet below) — this view only reads them.
    streak_days = getattr(user, 'streak_days', 0) or 0

    context = {
        'is_logged_in': True,
        'total_saved': total_saved,
        'total_formulas': total_formulas,
        'favourite_chapter': favourite_chapter,
        'category_counts': dict(category_counts),
        'jee_count': jee_count,
        'neet_count': neet_count,
        'both_count': both_count,
        'saved_formulas': saved_formulas,
        'completion_percent': round((total_saved / total_formulas) * 100) if total_formulas else 0,
        'chapters_started': chapters_started,
        'strongest_chapter': strongest_chapter,
        'next_chapter': next_chapter,
        'streak_days': streak_days,
    }
    return render(request, 'formulas/dashboard.html', context)


# ─────────────────────────────────────────────────────────────
# OPTIONAL: streak-tracking helper.
# Call this from inside your "save formula" view, right after a
# SavedFormula gets created, to keep the streak field current.
# Requires SimpleUser to have:
#     last_active_date = models.DateField(null=True, blank=True)
#     streak_days = models.IntegerField(default=0)
# ─────────────────────────────────────────────────────────────
def update_streak(user):
    today = timezone.localdate()

    if user.last_active_date == today:
        return  # already counted today, no change

    if user.last_active_date == today - timezone.timedelta(days=1):
        user.streak_days = (user.streak_days or 0) + 1  # consecutive day
    else:
        user.streak_days = 1  # streak broken or first-ever save

    user.last_active_date = today
    user.save(update_fields=['streak_days', 'last_active_date'])

@csrf_exempt
def save_fcm_token(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data.get('token')
        # Save to session
        request.session['fcm_token'] = token
        return JsonResponse({'status': 'saved'})
    return JsonResponse({'error': 'Invalid'}, status=400)




class ConstantsView(TemplateView):
    template_name = "formulas/constants.html"


class UnitsDimensionsView(TemplateView):
    template_name = "formulas/units_dimensions.html"


def pyq_papers(request):
    pdf_dir = os.path.join(settings.BASE_DIR, 'formulas', 'static', 'formulas', 'pyq_pdfs')

    papers = []
    if os.path.exists(pdf_dir):
        for filename in sorted(os.listdir(pdf_dir)):
            if filename.endswith('.pdf'):
                # Turn "electromagnetism_pyq_formulas.pdf" into "Electromagnetism"
                display_name = (
                    filename.replace('_pyq_formulas.pdf', '')
                            .replace('_', ' ')
                            .title()
                )
                papers.append({
                    'display_name': display_name,
                    'filename': filename,
                })

    return render(request, 'formulas/pyq_papers.html', {'papers': papers})


@require_GET
def daily_physics_fact_view(request):
    """
    API endpoint that returns the daily dynamic physics fact.
    """
    fact_text = get_daily_physics_fact()
    return JsonResponse({
        "success": True,
        "fact": fact_text
    })



class SimGuide(DetailView):
    model=Chapter
    pk_url_kwarg="pk"
    template_name="formulas/sim_guide.html"
    context_object_name="chapter"




@csrf_exempt
def simple_login(request):
    if request.method == "POST":
        data = json.loads(request.body)
        name = data.get("name", "")
        dob = data.get("dob")
        answer = data.get("answer")
        correct_answer = request.session.get("captcha_answer")

        if str(answer) != str(correct_answer):
            return JsonResponse({"success": False, "error": "Wrong answer, try again."})

        try:
            dob = datetime.strptime(dob, "%Y-%m-%d").date().isoformat()
        except (ValueError, TypeError):
            return JsonResponse({"success" : False, "error" : "Invalid date format"}, status=400)

        if not name:
            return JsonResponse({"success" : False, "error" : "Name is required"}, status=400)

        user, created = SimpleUser.objects.get_or_create(date_of_birth=dob, name=name)
        request.session['user_session_id'] = str(user.session_id)
        request.session['user_name'] = name
        request.session['user_dob'] = dob
        return JsonResponse({"success": True})

    return JsonResponse({"success": False}, status=400)


def get_captcha(request):
    import random
    a, b = random.randint(1, 10), random.randint(1, 10)
    request.session['captcha_answer'] = a + b
    return JsonResponse({"question": f"{a} + {b} = ?"})



def logout_view(request):
    request.session.flush()
    return redirect('/')




logger = logging.getLogger(__name__)

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def hashlib_md5(s):
    import hashlib
    return hashlib.md5(s.encode("utf-8")).hexdigest()[:16]


class TopicCheatsheetPDFView(View):
    """
    GET /cheatsheet.pdf/?topic=<chapter name, e.g. "optics">
    ...(same docstring as before)...
    """

    CACHE_DIR = os.path.join(settings.MEDIA_ROOT, "cheatsheets")


    def get(self, request, *args, **kwargs):
        topic_slug = request.GET.get("topic")
        if not topic_slug:
            raise Http404("Missing ?topic= query parameter.")

        formulas = Formula.objects.filter(
            chapter__name__iexact=topic_slug
        ).order_by("id")

        if not formulas.exists():
            raise Http404("No formulas found for this chapter.")

        # --- paywall gate ---
        chapter = formulas.first().chapter
        if chapter.is_premium and not has_purchased(chapter, request):
            return redirect(f"/chapter/{topic_slug}/unlock/")

        # Pass 'formulas' to get_cache_path to build a dynamic fingerprint
        cache_path = self.get_cache_path(topic_slug, formulas)
        force_regen = request.GET.get("regen") == "1"

        if force_regen or not os.path.exists(cache_path):
            self.build_pdf(topic_slug, formulas, cache_path, request)

        response = FileResponse(
            open(cache_path, "rb"),
            as_attachment=True,
            filename=f"formulaverse-{topic_slug.lower()}-cheatsheet.pdf",
        )
        return response

    def get_cache_path(self, topic_slug, formulas):
        os.makedirs(self.CACHE_DIR, exist_ok=True)
        safe_slug = "".join(
            c for c in topic_slug.lower() if c.isalnum() or c in "-_"
        )

        # Fingerprint combining formula count + highest formula ID
        count = formulas.count()
        latest_id = formulas.aggregate(Max('id'))['id__max'] or 0
        fingerprint = f"c{count}_id{latest_id}"

        return os.path.join(self.CACHE_DIR, f"{safe_slug}_{fingerprint}.pdf")

    def _local_file_url(self, field_file, formula_obj=None, field_name="file"):
        """
        Handles both uploaded FileFields and plain text URL strings (e.g., Desmos URLs).
        """
        if not field_file:
            return None

        # Convert field_file to string in case it's a FieldFile or CharField
        val_str = str(field_file).strip()
        if not val_str:
            return None

        # 1. If it's a web URL (Desmos, HTTP, HTTPS), return it directly!
        if val_str.startswith("http://") or val_str.startswith("https://"):
            return val_str

        # 2. Otherwise, treat it as a file path on disk
        try:
            path = field_file.path if hasattr(field_file, 'path') else val_str
            if not os.path.exists(path):
                print(f"[PDF WARNING] Local file missing on disk for Formula ID {formula_obj.id if formula_obj else 'N/A'}: {path}")
                return None
        except (ValueError, NotImplementedError) as e:
            print(f"[PDF ERROR] Field error: {e}")
            return None

        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            png_path = self._rasterize_pdf_first_page(path)
            if png_path is None:
                return None
            return f"file://{png_path}"

        return f"file://{path}"

    def _rasterize_pdf_first_page(self, pdf_path, dpi=150):
        """
        Convert page 1 of a PDF to a cached PNG using PyMuPDF (fitz).
        Returns the PNG's filesystem path, or None on failure.
        """
        cache_dir = os.path.join(settings.MEDIA_ROOT, "pdf_page_cache")
        os.makedirs(cache_dir, exist_ok=True)

        mtime = os.path.getmtime(pdf_path)
        key = f"{pdf_path}|{mtime}"
        digest = hashlib_md5(key)
        png_path = os.path.join(cache_dir, f"{digest}.png")

        if os.path.exists(png_path):
            return png_path

        try:
            import fitz  # PyMuPDF
        except ImportError:
            print("[PDF ERROR] PyMuPDF (fitz) is not installed! PDF rasterization failed.")
            return None

        try:
            doc = fitz.open(pdf_path)
            page = doc.load_page(0)
            zoom = dpi / 72
            pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
            pix.save(png_path)
            doc.close()
            return png_path
        except Exception as e:
            print(f"[PDF ERROR] Rasterization error for {pdf_path}: {e}")
            return None

    def build_pdf(self, topic_slug, formulas, cache_path, request):
        entries = []
        for f in formulas:
            # 1. First choice: Use local uploaded diagram image file if available
            diagram_file = self._local_file_url(f.diagram_url, formula_obj=f, field_name="diagram_url")

            # 2. Fallback choice: If diagram_url is empty but desmos_graph_id exists,
            # generate the static image URL from Desmos
            if not diagram_file and getattr(f, 'desmos_graph_id', None):
                # Desmos provides static PNG thumbnail exports for saved graph IDs
                diagram_file = f"https://calc-images.desmos.com/calc_thumbs/{f.desmos_graph_id}.png"

            entries.append({
                "obj": f,
                "formula_img": render_formula_media_url(f.form),
                "diagram_path": diagram_file,
                "derivation_path": self._local_file_url(f.derivation_image, formula_obj=f, field_name="derivation_image"),
                "answer_img" : render_formula_media_url(f.answer) if hasattr(f, 'answer') and f.answer else None,
                "units_display" : format_units_for_display(f.units),
            })

        html_string = render_to_string("formulas/cheatsheet.html", {
            "topic": topic_slug,
            "entries": entries,
            "today": date.today().strftime("%d %b %Y"),
            "site_url": "formulaverse.in",
        })

        HTML(
            string=html_string,
            base_url=request.build_absolute_uri("/"),
        ).write_pdf(cache_path)

    # ... get_cache_path(), _local_file_url(), _rasterize_pdf_first_page(),
    #     and build_pdf() all stay EXACTLY as you already have them —
    #     nothing in those needs to change.


# ============================================================
# NEW: paywall views (add these as separate functions in the
# same views.py, below the class)
# ============================================================

def unlock_chapter(request, topic):
    """
    Paywall landing page. topic matches the same string used in
    ?topic=... everywhere else (e.g. "electrostatics"), NOT a slug field.
    """
    chapter = get_object_or_404(Chapter, name__iexact=topic)

    if not chapter.is_premium or has_purchased(chapter, request):
        return redirect(f"/cheatsheet.pdf/?topic={topic}")

    return render(request, "formulas/unlock_chapter.html", {
        "chapter": chapter,
        "topic_slug": topic,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
    })


@require_POST
def create_razorpay_order(request, topic):
    chapter = get_object_or_404(Chapter, name__iexact=topic)

    if not chapter.is_premium:
        return HttpResponseBadRequest("This chapter isn't a paid chapter.")

    if has_purchased(chapter, request):
        return JsonResponse({"already_purchased": True})

    amount_paise = chapter.price_inr * 100

    order = razorpay_client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1,
        "notes": {"topic": topic},
    })

    if not request.session.session_key:
        request.session.save()

    PurchasedChapter.objects.create(
        chapter=chapter,
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key,
        razorpay_order_id=order["id"],
        amount_inr=chapter.price_inr,
        status="created",
    )

    return JsonResponse({
        "order_id": order["id"],
        "amount": amount_paise,
        "currency": "INR",
        "key_id": settings.RAZORPAY_KEY_ID,
        "chapter_name": chapter.name,
    })


@csrf_exempt
@require_POST
def verify_razorpay_payment(request):
    data = json.loads(request.body)
    order_id = data.get("razorpay_order_id")
    payment_id = data.get("razorpay_payment_id")
    signature = data.get("razorpay_signature")

    if not all([order_id, payment_id, signature]):
        return HttpResponseBadRequest("Missing payment fields.")

    try:
        razorpay_client.utility.verify_payment_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        })
    except razorpay.errors.SignatureVerificationError:
        return HttpResponseForbidden("Payment signature verification failed.")

    purchase = get_object_or_404(PurchasedChapter, razorpay_order_id=order_id)
    purchase.razorpay_payment_id = payment_id
    purchase.status = "paid"
    purchase.save()

    # chapter.name is used directly as the ?topic= value here
    return JsonResponse({
        "success": True,
        "redirect_url": f"/cheatsheet.pdf/?topic={purchase.chapter.name}",
    })


@csrf_exempt
def razorpay_webhook(request):
    body = request.body
    signature = request.headers.get("X-Razorpay-Signature", "")

    expected_signature = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        return HttpResponseForbidden("Invalid webhook signature.")

    event = json.loads(body)
    if event.get("event") == "payment.captured":
        payment_entity = event["payload"]["payment"]["entity"]
        order_id = payment_entity["order_id"]
        payment_id = payment_entity["id"]

        PurchasedChapter.objects.filter(razorpay_order_id=order_id).update(
            status="paid", razorpay_payment_id=payment_id
        )

    return JsonResponse({"status": "ok"})


class AllSavedFormulasView(View):
    def get(self, request):
        user_id = request.session.get('user_session_id')
        user = SimpleUser.objects.filter(session_id=user_id).first()
        saved_formulas = Formula.objects.filter(savedformula__user=user) if user else Formula.objects.none()
        saved_rows = (
            SavedFormula.objects
            .filter(user=user)
            .select_related('formula')
            .order_by('-saved_at')  # most recently saved first
        )

        today = timezone.localdate()
        saved_formulas = []
        for row in saved_rows:
            f = row.formula
            f.days_since_saved = (today - row.saved_at.date()).days
            saved_formulas.append(f)


        return render(request, 'formulas/all_saved.html',{
            'saved_formulas': saved_formulas
            })


def terms(request):
    return render(request, "formulas/terms.html")




def daily_sprint_view(request):
    today = timezone.now().date()
    challenge = DailyChallenge.objects.filter(date=today).first()
    if not challenge:
        challenge = DailyChallenge.objects.last()

    if challenge:
        options = [
            {'title': challenge.correct_formula_name, 'is_correct': True},
            {'title': challenge.wrong_option_1, 'is_correct': False},
            {'title': challenge.wrong_option_2, 'is_correct': False},
            {'title': challenge.wrong_option_3, 'is_correct': False},
        ]
        random.seed(str(today))
        random.shuffle(options)
    else:
        options = []

    context = {
        'challenge': challenge,
        'options': options,
    }
    return render(request, 'formulas/daily_sprint.html', context)



def my_purchases(request):
    user_id = request.session.get('user_session_id')
    user = None

    if user_id:
        try:
            user = SimpleUser.objects.get(session_id=user_id)
        except SimpleUser.DoesNotExist:
            request.session.flush()
            user = None

    if not user:
        return render(request, 'formulas/my_purchase.html', {
            'is_logged_in': False,
            'purchases': [],
        })

    purchases = (
        PurchasedChapter.objects
        .filter(user=user, status="paid")
        .select_related('chapter')
        .order_by('-created_at')
    )

    return render(request, 'formulas/my_purchase.html', {
        'is_logged_in': True,
        'purchases': purchases,
    })
