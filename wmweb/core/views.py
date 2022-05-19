import os
from json import dumps

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models.query import QuerySet
from rest_framework.generics import ListAPIView

from .models import *


class API:
    class SurgeonsView(ListAPIView):
        serializer_class = Surgeons
        def get(self, request, city):
            queryset: QuerySet = Surgeons.objects.filter(city=city).all()
            surgeons = [surgeon.to_dict() for surgeon in queryset]
            return HttpResponse(dumps({"surgeons": surgeons}), content_type='application/json')


    class CreateDealView(ListAPIView):
        serializer_class = Deals
        def get(self, request, surgeon_id, user_id, phone, city, start_session, end_session):
            #surgeon = Surgeons.objects.get(pk=surgeon_id)
            deal = Deals.objects.filter(user_id=user_id, surgeon_id=surgeon_id,
                    phone=phone, city=city, start_session=start_session,
                    end_session=end_session)
            if not deal.exists():
                deal = Deals.objects.create(
                    surgeon_id=surgeon_id, user_id=user_id,
                    phone=phone, city=city, start_session=start_session,
                    end_session=end_session
                )
            return HttpResponse(dumps({"deal_id": deal.pk, "deal_created": str(deal.created)}), content_type='application/json')


class Web:
    def index(request):
        return render(request, "profile.html")

    def surgeons(request):
        _surgeons = Surgeons.objects.all()
        return render(request, "surgeons.html", dict(surgeons=_surgeons))

    def deals(request):
        _deals = Deals.objects.all()
        return render(request, "deals.html", dict(deals=_deals))

    def save_profile(request):
        if request.method == 'POST' and request.FILES['user_pic']:
            user_pic = request.FILES['user_pic']
            name = request.POST['name']
            city = request.POST['city']
            wa_phone = request.POST['wa_phone']
            Surgeons.objects.create(
                name=name, city=city,
                image=user_pic, wa_phone=wa_phone
            )
        return redirect("surgeons")

    def delete_profile(request):
        surgeon_id = request.POST['id']
        surgeon = Surgeons.objects.filter(pk=surgeon_id)
        os.remove(str(settings.BASE_DIR)+surgeon.get().image.url)
        surgeon = Surgeons.objects.filter(pk=surgeon_id)
        surgeon.delete()
        return HttpResponse(dumps(True), content_type="application/json")