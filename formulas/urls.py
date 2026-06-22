from django.urls import path
from . import views


urlpatterns=[
    path("", views.RegisterView.as_view(), name='signup'),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("base", views.BaseView.as_view(), name="base-page"),
    path("index", views.IndexView.as_view(), name="index-page"),
    path("formula/<int:pk>", views.SingleFormulaView.as_view(), name="single-formula-page"),
    path("saved", views.SavedFormulasView.as_view(), name="saved-page"),
    path('unsave/<int:pk>/', views.unsave,  name ="unsave-formula"),
    path("try", views.TryView.as_view()),
    path("chatbot/", views.ChatbotView.as_view(), name="chatbot"),
    path("<str:category>/", views.CategoryView.as_view(), name="category"),
    path("me", views.AboutMeView.as_view(), name="me"),
    path('panel/', views.mini_panel, name='mini_panel'),
    path('panel/add-formula/', views.add_formula, name='add_formula'),
    path('panel/edit-formula/<int:pk>/', views.edit_formula, name='edit_formula'),
    path('panel/delete-formula/<int:pk>/', views.delete_formula, name='delete_formula'),
    path('panel/add-category/', views.add_category, name='add_category'),
    path('profile/', views.profile, name="profile"),
    path('upload-pic/', views.upload_pic, name='upload_pic'),
    path('practice/<int:formula_id>/', views.practice_question,
     name='practice_question'),








]