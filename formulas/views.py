from django.shortcuts import render,redirect
from django.views import View
from django.views.generic import ListView
from django.views.generic import DetailView,TemplateView, CreateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .models import Formula, Chapter, SimpleUser
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
from datetime import date
import requests
import os
from django.db.models import Count
from django.conf import settings
from django.templatetags.static import static
from .chatbot import get_daily_physics_fact
from django.db.models import Case, When, Value, IntegerField

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
                Formula.objects.filter(chapter=cat, id__in=visited_ids).count()
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['similar_formulas'] = Formula.objects.filter(
            chapter = self.object.chapter
            ).exclude(pk=self.object.pk)[:5]
        return context

    def get(self, request, *args, **kwargs):
        response= super().get(request, *args, **kwargs)

        visited= request.session.get("visited_formulas", [])
        if self.object.id not in visited:
            visited.append(self.object.id)
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
    def post(self, request, pk, *args, **kwargs):
        if not request.session.get('user_session_id'):
            return redirect('single-formula-page', pk=pk)

        formula_id = request.POST.get("formula_id")
        formula = get_object_or_404(Formula, id=pk)

        if not request.session.session_key:

            request.session.create()

        session_key = request.session.session_key
        formula.is_saved = True
        formula.session_key = session_key
        formula.save()
        return redirect('saved-page', pk=pk)

    def get(self, request, pk):
        formula = get_object_or_404(Formula, id=pk)
        session_key = request.session.session_key
        saved_formulas = Formula.objects.filter(
            is_saved=True,
            session_key = session_key
        )
        return render(request, "formulas/saved_formulas.html", {
            "savedformulas": saved_formulas,
            "last_formula" : formula
        })


def unsave(request, pk):
        formula = get_object_or_404(Formula, id=pk)
        formula.is_saved = False
        formula.save()
        return redirect("single-formula-page", pk=pk)



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
    fields = "_all_"
    template_name = "formulas/categories.html"
    context_object_name = "formulas"

    def get_queryset(self):
        return Formula.objects.filter(chapter__name__iexact=self.kwargs['chapter'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chapter_name'] = self.kwargs['chapter'].title()

        category_obj = Chapter.objects.filter(name__iexact=self.kwargs['chapter']).first()
        context['category'] = category_obj
        return context




class AboutMeView(TemplateView):
    template_name = "formulas/me.html"




@staff_member_required
def mini_panel(request):
    formulas = Formula.objects.select_related('category').all().order_by('category__name')
    categories = Category.objects.all()
    return render(request, 'mini_panel.html', {
        'formulas': formulas,
        'categories': categories,
    })

@staff_member_required
def add_formula(request):
    form = FormulaForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Formula added successfully!')
        return redirect('add_formula')
    return render(request, 'add_formula.html', {'form': form, 'title': 'Add Formula'})

@staff_member_required
def edit_formula(request, pk):
    formula = get_object_or_404(Formula, pk=pk)
    form = FormulaForm(request.POST or None, request.FILES or None, instance=formula)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Formula updated!')
        return redirect('mini_panel')
    return render(request, 'add_formula.html', {'form': form, 'title': 'Edit Formula'})

@staff_member_required
def delete_formula(request, pk):
    formula = get_object_or_404(Formula, pk=pk)
    if request.method == 'POST':
        formula.delete()
        messages.success(request, 'Formula deleted!')
    return redirect('mini_panel')

@staff_member_required
def add_category(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category added!')
        return redirect('add_category')
    return render(request, 'add_category.html', {'form': form})




def practice_question(request, formula_id):
    try:
        formula = Formula.objects.get(id=formula_id)
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


class ExamFilterView(View):
    def get(self, request, *args, **kwargs):
        # Get exam type from URL
        path = request.path.strip('/')  # 'jee', 'neet', or 'both'

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

        return render(request, 'formulas/exam_filter.html', {
            'formulas': formulas,
            'exam_label': exam_label,
            'total': formulas.count(),
        })



def progress_dashboard(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    # Get all saved formulas for this session
    saved_formulas = Formula.objects.filter(
        is_saved=True,
        session_key=session_key
    )

    total_saved = saved_formulas.count()
    total_formulas = Formula.objects.count()

    # Category breakdown
    from collections import Counter
    category_counts = Counter(
        saved_formulas.values_list('chapter__name', flat=True)
    )
    favourite_chapter = max(category_counts, key=category_counts.get) if category_counts else "None"

    # JEE vs NEET breakdown
    jee_count = saved_formulas.filter(exam_tag='jee').count()
    neet_count = saved_formulas.filter(exam_tag='neet').count()
    both_count = saved_formulas.filter(exam_tag='both').count()

    context = {
        'total_saved': total_saved,
        'total_formulas': total_formulas,
        'favourite_chapter': favourite_chapter,
        'category_counts': dict(category_counts),
        'jee_count': jee_count,
        'neet_count': neet_count,
        'both_count': both_count,
        'saved_formulas': saved_formulas,
        'completion_percent': round((total_saved / total_formulas) * 100) if total_formulas else 0,
    }
    return render(request, 'formulas/dashboard.html', context)




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
        dob = data.get("dob")
        answer = data.get("answer")
        correct_answer = request.session.get("captcha_answer")

        if str(answer) != str(correct_answer):
            return JsonResponse({"success": False, "error": "Wrong answer, try again."})

        user = SimpleUser.objects.create(date_of_birth=dob)
        request.session['user_session_id'] = str(user.session_id)
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