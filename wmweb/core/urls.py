"""
The name of the 'profile' in the comments will belong to the surgeon profile.
"""

from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from .views import *

urlpatterns = [
    ## ===WEB urls==
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
    path("save_profile/", Web.save_profile, name="save_profile"), # Save new profile.
    path("save_city", Web.save_city, name="save_city"), # Save new city.
    path("save_question", Web.save_question, name="save_question"), # Save new question.
    path("save_settings", Web.save_settings, name="save_settings"), # Save settings.

    # Edit urls.
    path("edit_profile/", Web.edit_profile, name="edit_profile"), # Edit profile.

    # Del urls.
    path("del_profile/", Web.delete_profile, name="delete_profile"), # Delete profile.
    path("del_profile_with_deals", Web.delete_profile_with_deals, name="del_profile_with_deals"), # Delete profile with deals.
    path("del_city/", Web.delete_city, name="delete_city"), # Delete city.
    path("del_question/", Web.delete_question, name="delete_question"), # Delete question.

    ## ===API urls===
    # Main urls.
    path("api/surgeons/<str:city>", API.SurgeonsView.as_view(), name="api-surgeons"), # Get profiles by city.
    path("api/create_deal/<int:surgeon_id>/<int:user_id>/<int:phone>/<str:city>/<str:fio>/<str:email>/<str:cons_format>/<str:start_session>/<str:end_session>",
        API.CreateDealView.as_view(), name="create_deal"), # Create new deal by input data.
    path("api/change_status/<int:deal_id>/<str:status>", API.ChangeStatusView.as_view(), name="change_status"), # Change deal status by id.
    path("api/get_cities", API.CitiesView.as_view(), name="get_cities"), # Get cities.
    path("api/get_questions", API.QuestionsView.as_view(), name="get_questions"), # Get questions.
    path("api/cancel_deal/<int:deal_id>", API.CancelDealView.as_view(), name="cancel_deal"), # Cancel deal.

    # Notices and QRCodeNotices.
    path("api/get_notices", API.NoticesView.as_view(), name="get_notices"), # Get notices.
    path("api/change_notice_status/<int:deal_id>", API.ChangeNoticeStatusView.as_view(), name="change_notice_status"), # Change notice status by deal id.

    path("api/get_qrcode_notices", API.QRCodeNoticesView.as_view(), name="get_qrcode_notices"), # Get qrcode notices.
    path("api/change_qrcode_notice_status/<int:deal_id>", API.ChangeQRCodeNoticeView.as_view(), name="change_qrcode_notice_status") # Change qrcode notice status by deal id.

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)