from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from .views import *

urlpatterns = [
    path("", Web.index, name="index"),
    path("surgeons", Web.surgeons, name="surgeons"),
    path("deals", Web.deals, name="deals"),
    path("cities", Web.cities, name="cities"),
    path("questions", Web.questions, name="questions"),

    path("save_profile", Web.save_profile, name="save_profile"),
    path("save_city", Web.save_city, name="save_city"),
    path("save_question", Web.save_question, name="save_question"),
    path("edit_profile", Web.edit_profile, name="edit_profile"),

    path("del_profile/", Web.delete_profile, name="delete_profile"),
    path("del_profile_with_deals", Web.delete_profile_with_deals, name="del_profile_with_deals"),
    path("del_city/", Web.delete_city, name="delete_city"),
    path("del_question/", Web.delete_question, name="delete_question"),

    path("activate_code", Web.activate_code, name="activate_code"),

    path("api/surgeons/<str:city>", API.SurgeonsView.as_view(), name="api-surgeons"),
    path("api/create_deal/<int:surgeon_id>/<int:user_id>/<int:phone>/<str:city>/<str:fio>/<str:email>/<str:start_session>/<str:end_session>",
        API.CreateDealView.as_view(), name="create_deal")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)