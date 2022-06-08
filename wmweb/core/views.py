"""
The name of the 'profile' in the comments will belong to the surgeon profile.
"""

import os
import random
import mimetypes
from json import dumps
from time import sleep
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

from .models import *
from .config import Config

config = Config()


class API:
    class SurgeonsView(ListAPIView):
        serializer_class = Surgeons # Set serializer object.
        def get(self, request: HttpRequest, city: str) -> HttpResponse:
            queryset: QuerySet = Surgeons.objects.filter(city=city).all()
            surgeons = [surgeon.to_dict() for surgeon in queryset]
            return HttpResponse(dumps({"surgeons": surgeons}), content_type='application/json')


    class CreateDealView(ListAPIView):
        serializer_class = Deals # Set serializer object.
        def get(self, request: HttpRequest, surgeon_id: int,
            user_id: int, phone: int, city: str,
            fio: str, email: str, cons_format: str,
            start_session: str, end_session: str
        ) -> HttpResponse:
            surgeon = Surgeons.objects.get(pk=surgeon_id)
            deal = Deals.objects.filter(
                surgeon=surgeon, user_id=user_id,
                phone=phone, city=city, fio=fio,
                email=email, cons_format=cons_format,
                start_session=start_session, end_session=end_session)

            if not deal.exists():
                deal = Deals.objects.create(
                    surgeon=surgeon, user_id=user_id,
                    phone=phone, city=city, fio=fio,
                    email=email, cons_format=cons_format,
                    start_session=start_session, end_session=end_session
                )
                code = GenerateOTP.objects.create(deal=deal, code=generate_code())
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
        serializer_class = Deals # Set serializer object.
        def get(self, request: HttpRequest, deal_id: int, status: str):
            deal = Deals.objects.get(pk=deal_id)
            deal.status = status
            deal.save()
            return HttpResponse(dumps({"response": True}), content_type='application/json')


    class CitiesView(ListAPIView):
        serializer_class = Cities # Set serializer object.
        def get(self, request: HttpRequest):
            cities = Cities.objects.all()
            cities = [city.name for city in cities if Surgeons.objects.filter(city=city.name).exists()]
            return HttpResponse(dumps({"cities": cities}), content_type='application/json')


    class QuestionsView(ListAPIView):
        serializer_class = Questions # Set serializer object.
        def get(self, request: HttpRequest):
            questions = Questions.objects.all()
            questions = [question.to_dict() for question in questions]
            return HttpResponse(dumps({"questions": questions}), content_type='application/json')


    class NoticesView(ListAPIView):
        serializer_class = Notices # Set serializer object.
        def get(self, request: HttpRequest):
            sleep(1)
            notices = Notices.objects.filter(is_send=False).all()
            notices = [notice.to_dict() for notice in notices]
            return HttpResponse(dumps({"notices": notices}), content_type='application/json')


    class ChangeNoticeStatusView(ListAPIView):
        serializer_class = Notices # Set serializer object.
        def get(self, request: HttpRequest, deal_id: int):
            deal = Deals.objects.get(pk=deal_id)
            notice = Notices.objects.filter(deal=deal).get()
            notice.is_send = True
            notice.save()
            return HttpResponse(dumps({"response": True}), content_type='application/json')


    class QRCodeNoticesView(ListAPIView):
        serializer_class = QRCodeNotices # Set serializer object.
        def get(self, request: HttpRequest):
            sleep(1)
            qrcode_notices = QRCodeNotices.objects.filter(is_send=False).all()
            qrcode_notices = [notice.to_dict() for notice in qrcode_notices]
            return HttpResponse(dumps({"qrcode_notices": qrcode_notices}), content_type='application/json')


    class ChangeQRCodeNoticeView(ListAPIView):
        serializer_class = QRCodeNotices # Set serializer object.
        def get(self, request: HttpRequest, deal_id: int):
            deal = Deals.objects.get(pk=deal_id)
            notice = QRCodeNotices.objects.filter(deal=deal).get()
            notice.is_send = True
            notice.save()
            return HttpResponse(dumps({"response": True}), content_type='application/json')

    class CancelDealView(ListAPIView):
        serializer_class = Deals # Set serializer object.
        def get(self, request: HttpRequest, deal_id: int):
            status = "cancel_by_client"
            deal = Deals.objects.filter(pk=deal_id).get()
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

        percent_new_deals = 0
        percent_activate_deals = 0
        percent_confirmed_deals = 0
        percent_unconfirmed_deals = 0

        surgeons = Surgeons.objects.all()
        deals = Deals.objects.all()
        cities = Cities.objects.all()
        questions = Questions.objects.all()
        new_deals = Deals.objects.filter(status="new").all()
        activate_deals = Deals.objects.filter(status="attendance_confirmed").all()
        confirmed_deals = Deals.objects.filter(status="confirmed").all()
        unconfirmed_deals = Deals.objects.filter(status="unconfirmed").all()

        if new_deals:
            percent_new_deals = "{:.2f}".format(float(len(new_deals) / len(deals)) * 100)
        if confirmed_deals:
            percent_confirmed_deals = "{:.2f}".format(float(len(confirmed_deals) / len(deals)) * 100)
        if unconfirmed_deals:
            percent_unconfirmed_deals = "{:.2f}".format(float(len(unconfirmed_deals) / len(deals)) * 100)
        if activate_deals:
            percent_activate_deals = "{:.2f}".format(float(len(activate_deals) / len(deals)) * 100)

        data = dict(surgeons=surgeons, deals=deals,
            new_deals=new_deals, activate_deals=activate_deals,
            confirmed_deals=confirmed_deals, unconfirmed_deals=unconfirmed_deals,
            cities=cities, questions=questions,
            percent_new_deals=percent_new_deals, percent_confirmed_deals=percent_confirmed_deals,
            percent_unconfirmed_deals=percent_unconfirmed_deals, percent_activate_deals=percent_activate_deals)
        return render(request, "statistic.html", data)

    def surgeons(request: HttpRequest) -> HttpResponse:
        _surgeons = Surgeons.objects.all()
        cities = Cities.objects.all()
        return render(request, "surgeons.html", dict(surgeons=_surgeons, cities=cities))

    def deals(request: HttpRequest) -> HttpResponse:
        _deals = Deals.objects.all()
        if _deals:
            today = dt.today().strftime("%Y-%m-%d")
            max_date = dt.strftime(Deals.objects.latest('created').created, "%Y-%m-%d")
            min_date  = dt.strftime(Deals.objects.latest('-created').created, "%Y-%m-%d")
            return render(request, "deals.html", dict(deals=_deals, today=today, min_date=min_date, max_date=max_date))
        return render(request, "deals.html")

    def cities(request: HttpRequest) -> HttpResponse:
        cities = Cities.objects.all()
        data = dict(cities=cities)
        return render(request, "cities.html", data)

    def questions(request: HttpRequest):
        _questions = Questions.objects.all()
        return render(request, "questions.html", dict(questions=_questions))

    def activate_code(request: HttpRequest):
        status = None
        message = None
        if request.POST:
            if "digit_code" in request.POST:
                digit_code = request.POST['digit_code']
                if digit_code:
                    try:
                        digit_code = int(digit_code)
                        if len(str(digit_code))!= 6:
                            status = False
                            message = "Неккоректный размер кода!"
                        else:
                            code = GenerateOTP.objects.filter(code=digit_code)
                            if not code.exists():
                                status = False
                                message = "Неверный код!"
                            else:
                                code_obj = code.get()
                                deal = code_obj.deal
                                if deal.status == "new":
                                    deal.status = "attendance_confirmed"
                                    deal.save()
                                    status = True
                                    message = "Активация успешно пройдена!"
                                elif deal.status == "attendance_confirmed":
                                    status = False
                                    message = "Код был активирован ранее!"
                    except ValueError:
                        status = False
                        message = "Неккоректный код!"
        return render(request, "activate_code.html", dict(status=status, message=message))

    def save_profile(request: HttpRequest) -> HttpResponseRedirect:
        if request.method == 'POST' and request.FILES:
            image = request.FILES["image"]
            name = request.POST['name']
            city = request.POST['city']
            wa_phone = request.POST['wa_phone']
            address = request.POST['address']
            instagram_link = request.POST['instagram_link']
            clinic = request.POST['clinic']

            Surgeons.objects.create(
                name=name, city=city,
                image=image, wa_phone=wa_phone,
                clinic=clinic, address=address,
                instagram_link=instagram_link
            )
            return HttpResponse(dumps({"response": True}), content_type='application/json')

    def save_city(request: HttpRequest) -> HttpResponse:
        city = request.POST['city']
        city_db_obj = Cities.objects.filter(name=city)
        if not city_db_obj:
            Cities.objects.create(name=city)
        return redirect("cities")

    def save_question(request: HttpRequest):
        question = request.POST['question']
        answer = request.POST['answer']
        Questions.objects.create(question=question, answer=answer)
        return redirect("questions")

    def delete_profile(request: HttpRequest) -> HttpResponse:
        surgeon_id = request.POST['id']
        surgeon = Surgeons.objects.filter(pk=surgeon_id)
        deals = Deals.objects.filter(surgeon_id=surgeon.get())
        if deals.exists():
            deals = [deal.id for deal in deals.all()]
            return HttpResponse(dumps({"response": False, "deals": deals}), content_type="application/json")
        else:
            os.remove(str(settings.BASE_DIR)+surgeon.get().image.url)
            surgeon = Surgeons.objects.filter(pk=surgeon_id)
            surgeon.delete()
            return HttpResponse(dumps({"response": True}), content_type="application/json")

    def delete_city(request: HttpRequest) -> HttpResponse:
        city_id = request.POST['id']
        Cities.objects.filter(pk=city_id).delete()
        return HttpResponse(dumps(True), content_type="application/json")

    def delete_question(request: HttpRequest):
        question_id = request.POST['id']
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
            surgeon = Surgeons.objects.filter(pk=request.POST['surgeon_id'])
            name = request.POST.get('name') # Get profile
            city = request.POST.get('city')
            wa_phone = request.POST.get('wa_phone')
            clinic = request.POST.get('clinic')
            address = request.POST.get('address')
            instagram_link = request.POST.get('instagram_link')
            image = request.FILES.get('image')
            surgeon.update(name=name, city=city, wa_phone=wa_phone,
                clinic=clinic, address=address, instagram_link=instagram_link)
            surgeon = surgeon.get()
            try:
                os.remove(str(settings.BASE_DIR)+surgeon.image.url) # Remove image profile.
            except FileNotFoundError:
                logger.error(F"При удалении пользователя с id: {surgeon.pk}, не было найдено изображение!") # If image does not found.
            surgeon.image = image # Set new image profile.
            surgeon.save() # Save new profile data.
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

        delete_profile_id = request.COOKIES.get("delete_profile_id") # Get profile id from cookie.
        surgeon = Surgeons.objects.filter(pk=delete_profile_id) # Get profile object by id.
        deals = Deals.objects.filter(surgeon_id=surgeon.get()) # Get deals object by surgeon id.
        deal_ids = [deal.pk for deal in deals] # Get all deal ids.
        generate_otp = GenerateOTP.objects.filter(deal__in=[deal for deal in deals.all()]) # Get generate otp objects by deal ids.
        notices = Notices.objects.filter(deal_id__in=deal_ids) # Get notices objects by deal ids.
        qr_code_notices = QRCodeNotices.objects.filter(deal_id__in=deal_ids) # Get qr code notices objects by deal ids.
        try:
            os.remove(str(settings.BASE_DIR)+surgeon.get().image.url) # Remove surgeon image profile.
        except FileNotFoundError:
            logger.error(F"При удалении пользователя с id: {surgeon.get().pk}, не было найдено изображение!") # If image does not found.
        notices.delete() # Delete all notice objects by ids.
        qr_code_notices.delete() # Delete all qrcode notice objects by ids.
        generate_otp.delete() # Delete all generate otp objects by ids.
        deals.delete() # Delete all deal objects by ids.
        surgeon.delete() # Delete all notice objects by ids.
        response = redirect("surgeons")
        response.delete_cookie("delete_profile_id") # Delete profile id from cookie.
        return response

    def upload_to_excel(request: HttpRequest, basename="analytic_deals") -> HttpResponse:
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

        from_trip_start = dt.strftime(parser.parse(request.POST['from-trip-start']), "%Y-%m-%d")
        before_trip_start = dt.strftime(parser.parse(request.POST['before-trip-start']), "%Y-%m-%d")
        # Get all deals range from date to before date.
        deals = Deals.objects.filter(created__range=[from_trip_start, before_trip_start]).all()
        deals = [deal.to_excel_dict() for deal in deals]
        # Create file name and path.
        suffix = dt.now().strftime("%y%m%d_%H%M%S")
        filename = "_".join([basename, suffix]) # e.g. 'analytic_deals_20220101_101010'
        filepath = rF"{settings.BASE_DIR}/media/excel_analytics/{filename}.xlsx"
        df = pd.DataFrame(deals) # Convert data to the DataFrame.
        # Convert datetime to correct format.
        if deals:
            df['created'] = df['created'].apply(lambda a: dt.strftime(a,"%Y-%m-%d %H:%M:%S")) # Convert 'created' field to correct format.
            df['start_session'] = df['start_session'].apply(lambda a: dt.strftime(a,"%Y-%m-%d %H:%M:%S")) # Convert 'start_session' field to correct format.
            df['end_session'] = df['end_session'].apply(lambda a: dt.strftime(a,"%Y-%m-%d %H:%M:%S")) # Convert 'end_session' field to correct format.
        # Write data to excel sheet.
        writer = pd.ExcelWriter(filepath, engine='xlsxwriter', datetime_format='dd-mmm-yyyy')
        df.to_excel(writer, sheet_name='Заявки')
        writer.save()
        # Write data to file.
        path = open(filepath, 'rb')
        mime_type, _ = mimetypes.guess_type(filepath)
        # Set the return value of the HttpResponse.
        response = HttpResponse(path, content_type=mime_type)
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

        config = Config() # Init Config object.
        qr_code_seconds_timeout = config.timeout_sec # Set timeout seconds for temp var.
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

        timeout = request.POST['timeout'] # Get timeout value.
        try:
            timeout = int(timeout) # Convert timeout value to int type.
            # Check timeout value for empty or 0.
            if not timeout or timeout == 0:
                return redirect("settings")
            else:
                config.change_value("TIMEOUT_SEC", str(timeout)) # Reset timeout value in the .env file.
                return redirect("settings")
        except ValueError:
            return redirect("settings")

def generate_code():
    """The generate code function.

    Returns
    -------
        code : int
    """

    code = random.choice(range(100000, 999999)) # generating 6 digit random code.
    return code