from django.urls import path


from . import views

urlpatterns = [
    path('policy_upload', views.PolicyUploadView.as_view()),
    path('outStandings_excel_upload', views.XclOtStndgUpldVw.as_view()),
    path('check_expiries', views.GetExpiryView.as_view()),
]