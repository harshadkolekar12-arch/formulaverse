from django.shortcuts import render,redirect
from django.views import View
from django.views.generic import ListView
from django.views.generic import DetailView,TemplateView, CreateView
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .models import Formula, Profile
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import RegisterForm, FormulaForm, CategoryForm
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .chatbot import ask_chatbot
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .chatbot import generate_practice_question
import random
from datetime import date
import requests
import os
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

        # Saved count
        saved_count = 0
        if request.user.is_authenticated:
            saved_count = Formula.objects.filter(
                is_saved=True,
                user=request.user
            ).count()


        formula_of_day = random.choice(list(formulas)) if formulas.exists() else None


        return render(request, "formulas/index.html", {
            "formulas": formulas,
            "total": total,
            "saved_count": saved_count,
            "user": request.user,
            "formula_of_day": formula_of_day,
        })



class SingleFormulaView(DetailView):
    template_name="formulas/single_formula.html"
    model=Formula
    fields="__all__"
    context_object_name="formula"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        formula = self.object

        if not formula.video_url:
            url = get_youtube_video(formula.title)
            if url:
                formula.video_url = url
                formula.save(update_fields=['video_url'])

        context['video_url'] = formula.video_url
        return context

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
    fields = "__all__"
    template_name= "formulas/categories.html"
    context_object_name = "formulas"


    def get_queryset(self):
        return Formula.objects.filter(category__name__iexact=self.kwargs['category'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_name'] = self.kwargs['category'].title()
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
