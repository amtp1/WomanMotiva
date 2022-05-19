from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from .views import *

urlpatterns = [
    path("", Web.index, name="index"),
    path("surgeons", Web.surgeons, name="surgeons"),
    path("deals", Web.deals, name="deals"),
    path("save_profile", Web.save_profile, name="save_profile"),

    path("del_profile/", Web.delete_profile, name="delete_profile"),

    path("api/surgeons/<str:city>", API.SurgeonsView.as_view(), name="api-surgeons"),
    path("api/create_deal/<int:surgeon_id>/<int:user_id>/<int:phone>/<str:city>/<str:start_session>/<str:end_session>",
        API.CreateDealView.as_view(), name="create_deal")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)