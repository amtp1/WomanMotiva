"""
The name of the 'profile' in the comments will belong to the surgeon profile.
"""

import os
import random
import mimetypes
from json import dumps
from time import sleep
from typing import Any
from dateutil import parser
from datetime import datetime as dt

import pandas as pd
from loguru import logger
from django.conf import settings
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from rest_framework.generics import ListAPIView
from django.http import (HttpRequest, HttpResponse,
                         HttpResponseRedirect, HttpResponsePermanentRedirect)
from django.core.files.uploadedfile import UploadedFile

from .models import *
from .config import Config

config: Config = Config()  # Init new Config object.


class API:
    class SurgeonsView(ListAPIView):
        serializer_class: Surgeons = Surgeons  # Set serializer object.

        def get(self, request: HttpRequest, city: str) -> HttpResponse:
            queryset: QuerySet = Surgeons.objects.filter(city=city).all()
            surgeons: list = [surgeon.to_dict() for surgeon in queryset]
            return HttpResponse(dumps({"surgeons": surgeons}), content_type='application/json')

    class CreateDealView(ListAPIView):
        serializer_class: Deals = Deals  # Set serializer object.

        def get(self, request: HttpRequest, surgeon_id: int,
                user_id: int, phone: int, city: str,
                fio: str, email: str, cons_format: str,
                start_session: str, end_session: str
                ) -> HttpResponse:
            surgeon: Any = Surgeons.objects.get(pk=surgeon_id)
            deal: QuerySet = Deals.objects.filter(
                surgeon=surgeon, user_id=user_id,
                phone=phone, city=city, fio=fio,
                email=email, cons_format=cons_format,
                start_session=start_session, end_session=end_session)

            if not deal.exists():
                deal: QuerySet = Deals.objects.create(
                    surgeon=surgeon, user_id=user_id,
                    phone=phone, city=city, fio=fio,
                    email=email, cons_format=cons_format,
                    start_session=start_session, end_session=end_session
                )
                code: Any = GenerateOTP.objects.create(
                    deal=deal, code=generate_code())
                deal.code = code
                deal.save()

                Notices.objects.create(deal=deal)
                QRCodeNotices.objects.create(deal=deal)

                return HttpResponse(dumps({
                    "is_created": True, "deal_id": deal.pk,
                    "code": code.code, "deal_created": str(deal.created)}),
                    content_type='application/json')
            else:
                return HttpResponse(dumps({"is_created": False}), content_type='application/json')

    class ChangeStatusView(ListAPIView):
        serializer_class: Deals = Deals  # Set serializer object.

        def get(self, request: HttpRequest, deal_id: int, status: str) -> HttpResponse:
            deal: Any = Deals.objects.get(pk=deal_id)
            deal.status = status
            deal.save()
            return HttpResponse(dumps({"response": True}), content_type='application/json')

    class CitiesView(ListAPIView):
        serializer_class: Cities = Cities  # Set serializer object.

        def get(self, request: HttpRequest) -> HttpResponse:
            cities: list = Cities.objects.all()
            cities: list = [city.name for city in cities if Surgeons.objects.filter(
                city=city.name).exists()]
            return HttpResponse(dumps({"cities": cities}), content_type='application/json')

    class QuestionsView(ListAPIView):
        serializer_class: Questions = Questions  # Set serializer object.

        def get(self, request: HttpRequest) -> HttpResponse:
            questions: list = Questions.objects.all()
            questions: list = [question.to_dict() for question in questions]
            return HttpResponse(dumps({"questions": questions}), content_type='application/json')

    class NoticesView(ListAPIView):
        serializer_class: Notices = Notices  # Set serializer object.

        def get(self, request: HttpRequest) -> HttpResponse:
            sleep(1)
            notices: list = Notices.objects.filter(is_send=False).all()
            notices: list = [notice.to_dict() for notice in notices]
            return HttpResponse(dumps({"notices": notices}), content_type='application/json')

    class ChangeNoticeStatusView(ListAPIView):
        serializer_class: Notices = Notices  # Set serializer object.

        def get(self, request: HttpRequest, deal_id: int) -> HttpResponse:
            deal: Any = Deals.objects.get(pk=deal_id)
            notice: Any = Notices.objects.filter(deal=deal).get()
            notice.is_send = True
            notice.save()
            return HttpResponse(dumps({"response": True}), content_type='application/json')

    class QRCodeNoticesView(ListAPIView):
        # Set serializer object.
        serializer_class: QRCodeNotices = QRCodeNotices

        def get(self, request: HttpRequest) -> HttpResponse:
            sleep(1)
            qrcode_notices: list = QRCodeNotices.objects.filter(
                is_send=False).all()
            qrcode_notices: list = [notice.to_dict()
                                    for notice in qrcode_notices]
            return HttpResponse(dumps({"qrcode_notices": qrcode_notices}), content_type='application/json')

    class ChangeQRCodeNoticeView(ListAPIView):
        # Set serializer object.
        serializer_class: QRCodeNotices = QRCodeNotices

        def get(self, request: HttpRequest, deal_id: int) -> HttpResponse:
            deal: Any = Deals.objects.get(pk=deal_id)
            notice: Any = QRCodeNotices.objects.filter(deal=deal).get()
            notice.is_send = True
            notice.save()
            return HttpResponse(dumps({"response": True}), content_type='application/json')

    class CancelDealView(ListAPIView):
        serializer_class: Deals = Deals  # Set serializer object.

        def get(self, request: HttpRequest, deal_id: int) -> HttpResponse:
            status: str = "cancel_by_client"
            deal: Any = Deals.objects.filter(pk=deal_id).get()
            deal.status = status
            deal.save()
            return HttpResponse(dumps({"response": True}), content_type='application/json')


class Web:
    def index(request: HttpRequest) -> HttpResponse:
        """The index function.
        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            statistic : HttpResponse
        """

        percent_new_deals: float = 0.0
        percent_activate_deals: float = 0.0
        percent_confirmed_deals: float = 0.0
        percent_unconfirmed_deals: float = 0.0

        surgeons: QuerySet = Surgeons.objects.all()
        deals: QuerySet = Deals.objects.all()
        cities: QuerySet = Cities.objects.all()
        questions: QuerySet = Questions.objects.all()
        new_deals: QuerySet = Deals.objects.filter(status="new").all()
        activate_deals: QuerySet = Deals.objects.filter(
            status="attendance_confirmed").all()
        confirmed_deals: QuerySet = Deals.objects.filter(
            status="confirmed").all()
        unconfirmed_deals: QuerySet = Deals.objects.filter(
            status="unconfirmed").all()

        if new_deals:
            percent_new_deals: float = "{:.2f}".format(
                float(len(new_deals) / len(deals)) * 100)
        if confirmed_deals:
            percent_confirmed_deals: float = "{:.2f}".format(
                float(len(confirmed_deals) / len(deals)) * 100)
        if unconfirmed_deals:
            percent_unconfirmed_deals: float = "{:.2f}".format(
                float(len(unconfirmed_deals) / len(deals)) * 100)
        if activate_deals:
            percent_activate_deals: float = "{:.2f}".format(
                float(len(activate_deals) / len(deals)) * 100)

        data: dict[str, QuerySet | float] = dict(surgeons=surgeons, deals=deals,
                                                 new_deals=new_deals, activate_deals=activate_deals,
                                                 confirmed_deals=confirmed_deals, unconfirmed_deals=unconfirmed_deals,
                                                 cities=cities, questions=questions,
                                                 percent_new_deals=percent_new_deals, percent_confirmed_deals=percent_confirmed_deals,
                                                 percent_unconfirmed_deals=percent_unconfirmed_deals, percent_activate_deals=percent_activate_deals)
        return render(request, "statistic.html", data)

    def surgeons(request: HttpRequest) -> HttpResponse:
        _surgeons: QuerySet = Surgeons.objects.all()
        cities: QuerySet = Cities.objects.all()
        return render(request, "surgeons.html", dict(surgeons=_surgeons, cities=cities))

    def deals(request: HttpRequest) -> HttpResponse:
        _deals: QuerySet = Deals.objects.all()
        if _deals:
            today: str = dt.today().strftime("%Y-%m-%d")
            max_date: str = dt.strftime(
                Deals.objects.latest('created').created, "%Y-%m-%d")
            min_date: str = dt.strftime(
                Deals.objects.latest('-created').created, "%Y-%m-%d")
            return render(request, "deals.html", dict(deals=_deals, today=today, min_date=min_date, max_date=max_date))
        return render(request, "deals.html")

    def cities(request: HttpRequest) -> HttpResponse:
        cities: QuerySet = Cities.objects.all()
        data: dict[str, QuerySet] = dict(cities=cities)
        return render(request, "cities.html", data)

    def questions(request: HttpRequest) -> HttpResponse:
        _questions: QuerySet = Questions.objects.all()
        return render(request, "questions.html", dict(questions=_questions))

    def activate_code(request: HttpRequest) -> HttpResponse:
        status: bool = False
        message: None = None
        digit_code: str | None = request.POST.get("digit_code")
        if digit_code:
            try:
                digit_code: int = int(digit_code)
                if len(str(digit_code)) != 6:
                    message: str = "Неккоректный размер кода!"  # Set message.
                else:
                    code: QuerySet = GenerateOTP.objects.filter(
                        code=digit_code)
                    if not code.exists():
                        message: str = "Неверный код!"  # Set message.
                    else:
                        code_obj: Any = code.get()
                        deal: Any = code_obj.deal
                        if deal.status == "new":
                            deal.status = "attendance_confirmed"
                            deal.save()  # Save deal status.
                            status = True
                            # Set message.
                            message: str = "Активация успешно пройдена!"
                        elif deal.status == "attendance_confirmed":
                            # Set message.
                            message: str = "Код был активирован ранее!"
            except ValueError:
                message: str = "Неккоректный код!"  # Set message.
        return render(request, "activate_code.html", dict(status=status, message=message))

    def save_profile(request: HttpRequest) -> HttpResponseRedirect:
        if request.method == 'POST' and request.FILES:
            # Form data (method: POST).
            # Get profile image from temp.
            image: UploadedFile | None = request.FILES.get("image")
            # Get profile name from temp.
            name: str | None = request.POST.get('name')
            # Get profile city from temp.
            city: str | None = request.POST.get('city')
            # Get profile wa_phone from temp.
            wa_phone: str | None = request.POST.get('wa_phone')
            # Get profile address from temp.
            address: str | None = request.POST.get('address')
            # Get profile instagram_link from temp.
            instagram_link: str | None = request.POST.get('instagram_link')
            # Get profile clinic from temp.
            clinic: str | None = request.POST.get('clinic')

            Surgeons.objects.create(
                name=name, city=city,
                image=image, wa_phone=wa_phone,
                clinic=clinic, address=address,
                instagram_link=instagram_link
            )
            return HttpResponse(dumps({"response": True}), content_type='application/json')

    def save_city(request: HttpRequest) -> HttpResponse:
        # Get city from request POST.
        city: str | None = request.POST.get('city')
        # Get city object from model.
        city_object: QuerySet = Cities.objects.filter(name=city)
        if not city_object:
            Cities.objects.create(name=city)  # Create new city object.
        return redirect("cities")

    def save_question(request: HttpRequest) -> HttpResponseRedirect:
        # Get question from request POST.
        question: str | None = request.POST.get('question')
        # Get answer of question from request POST.
        answer: str | None = request.POST.get('answer')
        # Get question object from model.
        question_object: QuerySet = Questions.objects.filter(
            question=question, answer=answer)
        if not question_object:
            # Create new question with answer.
            Questions.objects.create(question=question, answer=answer)
        return redirect("questions")

    def delete_profile(request: HttpRequest) -> HttpResponse:
        # Get profile id from request POST.
        surgeon_id: str | None = request.POST.get('id')
        # Get profile object by id.
        surgeon: QuerySet = Surgeons.objects.filter(pk=surgeon_id)
        # Get deals object by surgeon object.
        deals: QuerySet = Deals.objects.filter(surgeon_id=surgeon.get())
        if deals.exists():
            # Seperation objects of deals to list.
            deals: list = [deal.id for deal in deals.all()]
            return HttpResponse(dumps({"response": False, "deals": deals}), content_type="application/json")
        else:
            try:
                os.remove(str(settings.BASE_DIR)+surgeon.get().image.url)
            except FileNotFoundError:
                # If image does not found.
                logger.error(
                    F"При удалении пользователя с id: {surgeon.get().pk}, не было найдено изображение!")
            surgeon.delete()
            return HttpResponse(dumps({"response": True}), content_type="application/json")

    def delete_city(request: HttpRequest) -> HttpResponse:
        """The delete city function.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            HttpResponse : HttpResponse
                If found id and deleted city then 'True' answer.
        """

        # Get city id from request POST.
        city_id: str | None = request.POST.get('id')
        Cities.objects.filter(pk=city_id).delete()  # Delete city by id.
        return HttpResponse(dumps(True), content_type="application/json")

    def delete_question(request: HttpRequest) -> HttpResponse:
        """The delete question function.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            HttpResponse : HttpResponse
                If found id and deleted question then 'True' answer.
        """

        # Get question id from request POST.
        question_id: str | None = request.POST.get('id')
        # Delete question by id.
        Questions.objects.filter(pk=question_id).delete()
        return HttpResponse(dumps(True), content_type="application/json")

    def edit_profile(request: HttpRequest) -> HttpResponse:
        """The edit profile function.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            HttpResponse : HttpResponse
        """

        # Check for request method. Should be POST.
        if request.method == 'POST':
            # Form data (method: POST).
            # Get profile from model.
            surgeon: QuerySet = Surgeons.objects.filter(
                pk=request.POST.get('surgeon_id'))
            # Get profile name from temp.
            name: str | None = request.POST.get('name')
            # Get profile city from temp.
            city: str | None = request.POST.get('city')
            # Get profile wa_phone from temp.
            wa_phone: str | None = request.POST.get('wa_phone')
            # Get profile clinic from temp.
            clinic: str | None = request.POST.get('clinic')
            # Get profile address from temp.
            address: str | None = request.POST.get('address')
            # Get profile instagram link from temp.
            instagram_link: str | None = request.POST.get('instagram_link')
            # Get profile image from temp.
            image: UploadedFile | None = request.FILES.get('image')
            # Update profile data.
            surgeon.update(name=name, city=city, wa_phone=wa_phone,
                           clinic=clinic, address=address, instagram_link=instagram_link)
            surgeon: QuerySet = surgeon.get()
            try:
                # Remove image profile.
                os.remove(str(settings.BASE_DIR)+surgeon.image.url)
            except FileNotFoundError:
                # If image does not found.
                logger.error(
                    F"При изменении пользователя с id: {surgeon.pk}, не было найдено изображение!")
            surgeon.image = image  # Set new image profile.
            surgeon.save()  # Save new profile data.
        return HttpResponse(dumps({"response": True}), content_type="application/json")

    def delete_profile_with_deals(request: HttpRequest) -> HttpResponsePermanentRedirect:
        """The delete profile with deals function.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            response : HttpResponsePermanentRedirect
        """

        # Get profile id from cookie.
        delete_profile_id: str | None = request.COOKIES.get(
            "delete_profile_id")
        # Get profile object by id.
        surgeon: QuerySet = Surgeons.objects.filter(pk=delete_profile_id)
        # Get deals object by surgeon id.
        deals: QuerySet = Deals.objects.filter(surgeon_id=surgeon.get())
        deal_ids: list = [deal.pk for deal in deals]  # Get all deal ids.
        # Get generate otp objects by deal ids.
        generate_otp: QuerySet = GenerateOTP.objects.filter(
            deal__in=[deal for deal in deals.all()])
        # Get notices objects by deal ids.
        notices: QuerySet = Notices.objects.filter(deal_id__in=deal_ids)
        # Get qr code notices objects by deal ids.
        qr_code_notices: QuerySet = QRCodeNotices.objects.filter(
            deal_id__in=deal_ids)
        try:
            # Remove surgeon image profile.
            os.remove(str(settings.BASE_DIR)+surgeon.get().image.url)
        except FileNotFoundError:
            # If image does not found.
            logger.error(
                F"При удалении пользователя с id: {surgeon.get().pk}, не было найдено изображение!")
        notices.delete()  # Delete all notice objects by ids.
        qr_code_notices.delete()  # Delete all qrcode notice objects by ids.
        generate_otp.delete()  # Delete all generate otp objects by ids.
        deals.delete()  # Delete all deal objects by ids.
        surgeon.delete()  # Delete all notice objects by ids.
        response = redirect("surgeons")
        # Delete profile id from cookie.
        response.delete_cookie("delete_profile_id")
        return response

    def upload_to_excel(request: HttpRequest, basename: str = "analytic_deals") -> HttpResponse:
        """The upload to excel function.

        Parameters
        ----------
            request : HttpRequest
            basename : str
                File name. Deafault: analytic_deals

        Returns
        -------
            render : HttpResponse
        """

        # Convert 'from' and 'before' time in correct datetime format.
        from_trip_start: str = dt.strftime(parser.parse(
            request.POST['from-trip-start']), "%Y-%m-%d")
        before_trip_start: str = dt.strftime(parser.parse(
            request.POST['before-trip-start']), "%Y-%m-%d")
        # Get all deals range from date to before date.
        deals: list = Deals.objects.filter(
            created__range=[from_trip_start, before_trip_start]).all()
        deals: list = [deal.to_excel_dict() for deal in deals]
        # Create file name and path.
        suffix = dt.now().strftime("%y%m%d_%H%M%S")
        # e.g. 'analytic_deals_20220101_101010'
        filename: str = "_".join([basename, suffix])
        filepath: str = rF"{settings.BASE_DIR}/media/excel_analytics/{filename}.xlsx"
        # Convert data to the DataFrame.
        df: pd.DataFrame = pd.DataFrame(deals)
        # Convert datetime to correct format.
        if deals:
            # Convert 'created' field to correct format.
            df['created'] = df['created'].apply(
                lambda a: dt.strftime(a, "%Y-%m-%d %H:%M:%S"))
            # Convert 'start_session' field to correct format.
            df['start_session'] = df['start_session'].apply(
                lambda a: dt.strftime(a, "%Y-%m-%d %H:%M:%S"))
            # Convert 'end_session' field to correct format.
            df['end_session'] = df['end_session'].apply(
                lambda a: dt.strftime(a, "%Y-%m-%d %H:%M:%S"))
        # Write data to excel sheet.
        writer: pd.ExcelWriter = pd.ExcelWriter(
            filepath, engine='xlsxwriter', datetime_format='dd-mmm-yyyy')
        df.to_excel(writer, sheet_name='Заявки')
        writer.save()
        # Write data to file.
        path = open(filepath, 'rb')
        mime_type, _ = mimetypes.guess_type(filepath)
        # Set the return value of the HttpResponse.
        response: HttpResponse = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser.
        response['Content-Disposition'] = "attachment; filename=%s" % filepath
        return response

    def settings(request: HttpRequest) -> HttpResponse:
        """The settings function.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            render : HttpResponse
        """

        config: Config = Config()  # Init Config object.
        # Set timeout seconds for temp var.
        qr_code_seconds_timeout: int = config.timeout_sec
        return render(request, "settings.html", dict(timeout=qr_code_seconds_timeout))

    def save_settings(request: HttpRequest) -> HttpResponseRedirect:
        """The save settings function.

        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            redirect : HttpResponseRedirect
        """

        timeout: str | None = request.POST.get('timeout')  # Get timeout value.
        if timeout:
            try:
                timeout = int(timeout)  # Convert timeout value to int type.
                # Check timeout value more than 0.
                if timeout > 0:
                    # Reset timeout value in the .env file.
                    config.change_value("TIMEOUT_SEC", str(timeout))
            except ValueError:
                logger.info(
                    F"Значение ({timeout}) таймаута является неккоректным! Изменения настроек не вступили в силу.")
        return redirect("settings")


def generate_code() -> int:
    """The generate code function.

    Returns
    -------
        code : int
    """

    # generating 6 digit random code.
    code: int = random.choice(range(100000, 999999))
    return code
