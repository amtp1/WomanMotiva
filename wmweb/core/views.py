import os
import random
from json import dumps
from datetime import datetime as dt
from datetime import timedelta
import mimetypes
from dateutil import parser
from time import sleep

from loguru import logger
import pandas as pd

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models.query import QuerySet
from rest_framework.generics import ListAPIView

from .models import *
from .config import Config

config = Config()


class API:
    class SurgeonsView(ListAPIView):
        serializer_class = Surgeons
        def get(self, request, city) -> HttpResponse:
            queryset: QuerySet = Surgeons.objects.filter(city=city).all()
            surgeons = [surgeon.to_dict() for surgeon in queryset]
            return HttpResponse(dumps({"surgeons": surgeons}), content_type='application/json')


    class CreateDealView(ListAPIView):
        serializer_class = Deals
        def get(self, request, surgeon_id,
            user_id, phone, city,
            fio, email, cons_format,
            start_session, end_session
        ) -> HttpResponse:
            surgeon = Surgeons.objects.get(pk=surgeon_id)
            deal = Deals.objects.filter(user_id=user_id, surgeon=surgeon,
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

            return HttpResponse(dumps({"deal_id": deal.pk, "code": code.code, "deal_created": str(deal.created)}), content_type='application/json')


    class ChangeStatusView(ListAPIView):
        serializer_class = Deals
        def get(self, request, deal_id: int, status: str):
            deal = Deals.objects.get(pk=deal_id)
            deal.status = status
            deal.save()
            return HttpResponse(dumps({"response": True}), content_type='application/json')


    class CitiesView(ListAPIView):
        serializer_class = Cities
        def get(self, request):
            cities = Cities.objects.all()
            cities = [city.name for city in cities if Surgeons.objects.filter(city=city.name).exists()]
            return HttpResponse(dumps({"cities": cities}), content_type='application/json')


    class QuestionsView(ListAPIView):
        serializer_class = Questions
        def get(self, request):
            questions = Questions.objects.all()
            questions = [question.to_dict() for question in questions]
            return HttpResponse(dumps({"questions": questions}), content_type='application/json')


    class NoticesView(ListAPIView):
        serializer_class = Notices
        def get(self, request):
            sleep(1)
            notices = Notices.objects.filter(is_send=False).all()
            notices = [notice.to_dict() for notice in notices]
            return HttpResponse(dumps({"notices": notices}), content_type='application/json')


    class ChangeNoticeStatusView(ListAPIView):
        serializer_class = Notices
        def get(self, request, deal_id: int):
            deal = Deals.objects.get(pk=deal_id)
            notice = Notices.objects.filter(deal=deal).get()
            notice.is_send = True
            notice.save()
            return HttpResponse(dumps({"response": True}), content_type='application/json')


    class QRCodeNoticesView(ListAPIView):
        serializer_class = QRCodeNotices
        def get(self, request):
            sleep(1)
            qrcode_notices = QRCodeNotices.objects.filter(is_send=False).all()
            qrcode_notices = [notice.to_dict() for notice in qrcode_notices]
            return HttpResponse(dumps({"qrcode_notices": qrcode_notices}), content_type='application/json')


    class ChangeQRCodeNoticeView(ListAPIView):
        serializer_class = QRCodeNotices
        def get(self, request, deal_id: int):
            deal = Deals.objects.get(pk=deal_id)
            notice = QRCodeNotices.objects.filter(deal=deal).get()
            notice.is_send = True
            notice.save()
            return HttpResponse(dumps({"response": True}), content_type='application/json')


    class CancelDealView(ListAPIView):
        serializer_class = Deals
        def get(self, request, deal_id: int):
            status = "cancel_by_client"
            deal = Deals.objects.filter(pk=deal_id).get()
            deal.status = status
            deal.save()
            return HttpResponse(dumps({"response": True}), content_type='application/json')


class Web:
    def index(request) -> HttpResponse:
        """The index function.
        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            statistic : HttpResponse
        """

        surgeons = Surgeons.objects.all()
        deals = Deals.objects.all()
        cities = Cities.objects.all()
        questions = Questions.objects.all()
        new_deals = Deals.objects.filter(status="new").all()
        activate_deals = Deals.objects.filter(status="attendance_confirmed").all()
        confirmed_deals = Deals.objects.filter(status="confirmed").all()
        unconfirmed_deals = Deals.objects.filter(status="unconfirmed").all()
        data = dict(surgeons=surgeons, deals=deals,
            new_deals=new_deals, activate_deals=activate_deals,
            confirmed_deals=confirmed_deals, unconfirmed_deals=unconfirmed_deals,
            cities=cities, questions=questions)
        return render(request, "statistic.html", data)

    def surgeons(request) -> HttpResponse:
        _surgeons = Surgeons.objects.all()
        cities = Cities.objects.all()
        return render(request, "surgeons.html", dict(surgeons=_surgeons, cities=cities))

    def deals(request) -> HttpResponse:
        today = dt.today().strftime("%Y-%m-%d")
        max_date = dt.strftime(Deals.objects.latest('created').created, "%Y-%m-%d")
        min_date  = dt.strftime(Deals.objects.latest('-created').created, "%Y-%m-%d")
        _deals = Deals.objects.all()
        return render(request, "deals.html", dict(deals=_deals, today=today, min_date=min_date, max_date=max_date))

    def cities(request) -> HttpResponse:
        cities = Cities.objects.all()
        data = dict(cities=cities)
        return render(request, "cities.html", data)

    def questions(request):
        _questions = Questions.objects.all()
        return render(request, "questions.html", dict(questions=_questions))

    def activate_code(request):
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

    def save_profile(request) -> HttpResponseRedirect:
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

    def save_city(request) -> HttpResponse:
        city = request.POST['city']
        city_db_obj = Cities.objects.filter(name=city)
        if not city_db_obj:
            Cities.objects.create(name=city)
        return redirect("cities")

    def save_question(request):
        question = request.POST['question']
        answer = request.POST['answer']
        Questions.objects.create(question=question, answer=answer)
        return redirect("questions")

    def delete_profile(request) -> HttpResponse:
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

    def delete_city(request) -> HttpResponse:
        city_id = request.POST['id']
        Cities.objects.filter(pk=city_id).delete()
        return HttpResponse(dumps(True), content_type="application/json")

    def delete_question(request):
        question_id = request.POST['id']
        Questions.objects.filter(pk=question_id).delete()
        return HttpResponse(dumps(True), content_type="application/json")

    def edit_profile(request) -> HttpResponseRedirect:
        edit_surgeon_id = request.COOKIES.get("edit_surgeon_id")
        surgeon = Surgeons.objects.filter(pk=edit_surgeon_id)
        if request.method == 'POST':
            name = request.POST['name']
            city = request.POST['city']
            wa_phone = request.POST['wa_phone']
            clinic = request.POST['clinic']
            address = request.POST['address']
            instagram_link = request.POST['instagram_link']
            if request.FILES:
                user_pic = F"profile_pictures/{request.FILES['user_pic']}"
                surgeon.update(name=name, city=city, image=user_pic, wa_phone=wa_phone, clinic=clinic, address=address, instagram_link=instagram_link)
            surgeon.update(name=name, city=city, wa_phone=wa_phone, clinic=clinic, address=address, instagram_link=instagram_link)
        response = redirect("surgeons")
        response.delete_cookie("edit_surgeon_id")
        return response

    def delete_profile_with_deals(request):
        try:
            delete_profile_id = request.COOKIES.get("delete_profile_id")
            surgeon = Surgeons.objects.filter(pk=delete_profile_id)
            deals = Deals.objects.filter(surgeon_id=surgeon.get())
            os.remove(str(settings.BASE_DIR)+surgeon.get().image.url)
        except FileNotFoundError:
            logger.error(F"При удалении пользователя с id: {surgeon.pk}, не было найдено изображение!")
        deals.delete()
        surgeon.delete()
        response = redirect("surgeons")
        response.delete_cookie("delete_profile_id")
        return response

    def upload_to_excel(request, basename="analytic_deals"):
        from_trip_start = request.POST['from-trip-start']
        before_trip_start = request.POST['before-trip-start']
        from_trip_start = dt.strftime(parser.parse(from_trip_start), "%Y-%m-%d")
        before_trip_start = dt.strftime(parser.parse(before_trip_start), "%Y-%m-%d")
        deals = Deals.objects.filter(created__range=[from_trip_start, before_trip_start]).all()
        deals = [deal.to_excel_dict() for deal in deals]
        suffix = dt.now().strftime("%y%m%d_%H%M%S")
        filename = "_".join([basename, suffix]) # e.g. 'analytic_deals_120508_171442'
        filepath = rF"{settings.BASE_DIR}/media/excel_analytics/{filename}.xlsx"
        df = pd.DataFrame(deals) # Convert data to the DataFrame.
        if deals:
            df['created'] = df['created'].apply(lambda a: dt.strftime(a,"%Y-%m-%d %H:%M:%S"))
            df['start_session'] = df['start_session'].apply(lambda a: dt.strftime(a,"%Y-%m-%d %H:%M:%S"))
            df['end_session'] = df['end_session'].apply(lambda a: dt.strftime(a,"%Y-%m-%d %H:%M:%S"))
        writer = pd.ExcelWriter(filepath,
                        engine='xlsxwriter', datetime_format='dd-mmm-yyyy')
        df.to_excel(writer, sheet_name='Заявки')
        writer.save()
        path = open(filepath, 'rb')
        mime_type, _ = mimetypes.guess_type(filepath)
        # Set the return value of the HttpResponse
        response = HttpResponse(path, content_type=mime_type)
        # Set the HTTP header for sending to browser
        response['Content-Disposition'] = "attachment; filename=%s" % filepath
        return response

    def settings(request):
        config = Config()
        qr_code_seconds_timeout = config.timeout_sec
        return render(request, "settings.html", dict(timeout=qr_code_seconds_timeout))

    def save_settings(request):
        timeout = request.POST['timeout']
        try:
            timeout = int(timeout)
            if not timeout or timeout == 0:
                return redirect("settings")
            else:
                config.change_value("TIMEOUT_SEC", str(timeout))
                return redirect("settings")
        except ValueError:
            return redirect("settings")

def generate_code():
    code = random.choice(range(100000, 999999))  # generating 6 digit random code
    return code