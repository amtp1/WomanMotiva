import os
from json import dumps

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models.query import QuerySet
from rest_framework.generics import ListAPIView

from .models import *


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
            start_session, end_session
        ) -> HttpResponse:
            surgeon = Surgeons.objects.get(pk=surgeon_id)
            deal = Deals.objects.filter(user_id=user_id, surgeon=surgeon,
                    phone=phone, city=city, start_session=start_session,
                    end_session=end_session)
            if not deal.exists():
                deal = Deals.objects.create(
                    surgeon=surgeon, user_id=user_id,
                    phone=phone, city=city, start_session=start_session,
                    end_session=end_session
                )
            return HttpResponse(dumps({"deal_id": deal.pk, "deal_created": str(deal.created)}), content_type='application/json')


class Web:
    def index(request) -> HttpResponse:
        """The index function.
        Parameters
        ----------
            request : HttpRequest

        Returns
        -------
            If user auth then 'render'.
            If user is not auth then 'redirect'.
        """
        surgeons = Surgeons.objects.all()
        deals = Deals.objects.all()
        new_deals = Deals.objects.filter(status="new").all()
        cities = Cities.objects.all()
        data = dict(surgeons=surgeons, deals=deals,
            new_deals=new_deals, cities=cities)
        return render(request, "statistic.html", data)

    def surgeons(request) -> HttpResponse:
        _surgeons = Surgeons.objects.all()
        cities = Cities.objects.all()
        return render(request, "surgeons.html", dict(surgeons=_surgeons, cities=cities))

    def deals(request) -> HttpResponse:
        _deals = Deals.objects.all()
        return render(request, "deals.html", dict(deals=_deals))

    def cities(request) -> HttpResponse:
        cities = Cities.objects.all()
        data = dict(cities=cities)
        return render(request, "cities.html", data)

    def activate_code(request):
        return render(request, "activate_code.html")

    def save_profile(request) -> HttpResponseRedirect:
        if request.method == 'POST' and request.FILES:
            user_pic = request.FILES['user_pic']
            name = request.POST['name']
            city = request.POST['city']
            wa_phone = request.POST['wa_phone']
            instagram_link = request.POST['instagram_link']
            Surgeons.objects.create(
                name=name, city=city,
                image=user_pic, wa_phone=wa_phone,
                instagram_link=instagram_link
            )
        return redirect("surgeons")

    def save_city(request) -> HttpResponse:
        city = request.POST['city']
        city_db_obj = Cities.objects.filter(name=city)
        if not city_db_obj:
            Cities.objects.create(name=city)
        return redirect("cities")

    def delete_profile(request) -> HttpResponse:
        surgeon_id = request.POST['id']
        surgeon = Surgeons.objects.filter(pk=surgeon_id)
        os.remove(str(settings.BASE_DIR)+surgeon.get().image.url)
        surgeon = Surgeons.objects.filter(pk=surgeon_id)
        surgeon.delete()
        return HttpResponse(dumps(True), content_type="application/json")

    def delete_city(request) -> HttpResponse:
        city_id = request.POST['id']
        Cities.objects.filter(pk=city_id).delete()
        return HttpResponse(dumps(True), content_type="application/json")

    def edit_profile(request) -> HttpResponseRedirect:
        edit_surgeon_id = request.COOKIES.get("edit_surgeon_id")
        surgeon = Surgeons.objects.filter(pk=edit_surgeon_id)
        if request.method == 'POST':
            name = request.POST['name']
            city = request.POST['city']
            wa_phone = request.POST['wa_phone']
            instagram_link = request.POST['instagram_link']
            if request.FILES:
                #user_pic = request.FILES['user_pic']
                user_pic = F"profile_pictures/{request.FILES['user_pic']}"
                surgeon.update(name=name, city=city, image=user_pic, wa_phone=wa_phone, instagram_link=instagram_link)
            surgeon.update(name=name, city=city, wa_phone=wa_phone, instagram_link=instagram_link)
        return redirect("surgeons")