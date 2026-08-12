from django.urls import path
from . import views


urlpatterns=[
    path("", views.BaseView.as_view(), name="base-page"),
    path("me", views.AboutMeView.as_view(), name="me"),
    path("index/", views.IndexView.as_view(), name="index-page"),
    path('privacy/', views.privacy, name="privacy"),
    path('terms/', views.terms, name="terms"),
    path("chatbot/", views.ChatbotView.as_view(), name="chatbot"),
    path('jee/', views.ExamFilterView.as_view(), name='jee-formulas'),
    path('neet/', views.ExamFilterView.as_view(), name='neet-formulas'),
    path('both/', views.ExamFilterView.as_view(), name='both-formulas'),
    path('dashboard/', views.progress_dashboard, name='dashboard'),
    path('constants/', views.ConstantsView.as_view(), name='constants'),
    path('pyq-papers/', views.pyq_papers, name="pyq-papers"),
    path('units-dimensions/', views.UnitsDimensionsView.as_view(), name="units-dimensions"),
    path('my-purchase/', views.my_purchases, name="my-purchase"),
    path('api/daily-facts/', views.daily_physics_fact_view, name="daily_fact"),
    path('daily-sprint/', views.daily_sprint_view, name="daily-sprint"),
    path('simple-login/', views.simple_login, name='simple_login'),
    path('get-captcha/', views.get_captcha, name='get_captcha'),
    path('logout/', views.logout_view, name='logout'),
    path("saved/<slug:slug>/", views.SavedFormulasView.as_view(), name="saved-page"),
    path('all-saved/', views.AllSavedFormulasView.as_view(), name='all-saved'),
    path("formula/<slug:slug>/", views.SingleFormulaView.as_view(), name="single-formula-page"),
    path('formula/<slug:slug>/unsave/', views.unsave, name='unsave-formula'),
    path("chapter/<str:topic>/unlock/", views.unlock_chapter, name="unlock-chapter"),
    path("chapter/<str:topic>/create-order/", views.create_razorpay_order, name="create-razorpay-order"),
    path("payment/verify/", views.verify_razorpay_payment, name="verify-razorpay-payment"),
    path("payment/webhook/", views.razorpay_webhook, name="razorpay-webhook"),
    path("cheatsheet.pdf/", views.TopicCheatsheetPDFView.as_view(), name="topic-cheatsheet-pdf"),
    path('sim-guide/<int:pk>/', views.SimGuide.as_view(),  name="sim-guide"),
    path("chapter/<str:chapter>/", views.CategoryView.as_view(), name="category"),
    path('practice/<slug:slug>/', views.practice_question, name='practice_question'),
    path('save-fcm-token/', views.save_fcm_token, name='save_fcm_token'),


]