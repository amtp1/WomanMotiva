"""
The name of the 'profile' in the comments will belong to the surgeon profile.
"""

from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from .views import *

urlpatterns = [
    # ===WEB urls==
    # Main urls.
    path("", Web.index, name="index"),
    path("surgeons", Web.surgeons, name="surgeons"),
    path("deals", Web.deals, name="deals"),
    path("cities", Web.cities, name="cities"),
    path("questions", Web.questions, name="questions"),
    path("settings", Web.settings, name="settings"),
    path("upload_to_excel", Web.upload_to_excel, name="upload_to_excel"),
    path("activate_code", Web.activate_code, name="activate_code"),

    # Save urls.
    # Save new profile.
    path("save_profile/", Web.save_profile, name="save_profile"),
    path("save_city", Web.save_city, name="save_city"),  # Save new city.
    # Save new question.
    path("save_question", Web.save_question, name="save_question"),
    # Save settings.
    path("save_settings", Web.save_settings, name="save_settings"),

    # Edit urls.
    # Edit profile.
    path("edit_profile/", Web.edit_profile, name="edit_profile"),

    # Del urls.
    # Delete profile.
    path("del_profile/", Web.delete_profile, name="delete_profile"),
    # Delete profile with deals.
    path("del_profile_with_deals", Web.delete_profile_with_deals,
         name="del_profile_with_deals"),
    path("del_city/", Web.delete_city, name="delete_city"),  # Delete city.
    # Delete question.
    path("del_question/", Web.delete_question, name="delete_question"),

    # ===API urls===
    # Main urls.
    # Get profiles by city.
    path("api/surgeons/<str:city>",
         API.SurgeonsView.as_view(), name="api-surgeons"),
    path("api/create_deal/<int:surgeon_id>/<int:user_id>/<int:phone>/<str:city>/<str:fio>/<str:email>/<str:cons_format>/<str:start_session>/<str:end_session>",
         API.CreateDealView.as_view(), name="create_deal"),  # Create new deal by input data.
    # Change deal status by id.
    path("api/change_status/<int:deal_id>/<str:status>",
         API.ChangeStatusView.as_view(), name="change_status"),
    # Get cities.
    path("api/get_cities", API.CitiesView.as_view(), name="get_cities"),
    # Get questions.
    path("api/get_questions", API.QuestionsView.as_view(), name="get_questions"),
    # Cancel deal.
    path("api/cancel_deal/<int:deal_id>",
         API.CancelDealView.as_view(), name="cancel_deal"),

    # Notices and QRCodeNotices.
    # Get notices.
    path("api/get_notices", API.NoticesView.as_view(), name="get_notices"),
    path("api/change_notice_status/<int:deal_id>", API.ChangeNoticeStatusView.as_view(),
         name="change_notice_status"),  # Change notice status by deal id.

    # Get qrcode notices.
    path("api/get_qrcode_notices", API.QRCodeNoticesView.as_view(),
         name="get_qrcode_notices"),
    path("api/change_qrcode_notice_status/<int:deal_id>", API.ChangeQRCodeNoticeView.as_view(),
         name="change_qrcode_notice_status")  # Change qrcode notice status by deal id.

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
