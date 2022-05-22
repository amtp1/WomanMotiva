from enum import Enum

from django.db import models


class Surgeons(models.Model):
    name = models.CharField(max_length=255, null=False)
    clinic = models.CharField(max_length=255, null=False)
    city = models.CharField(max_length=255, null=False)
    wa_phone = models.BigIntegerField(null=True)
    instagram_link = models.TextField(null=True)
    image = models.ImageField(upload_to="profile_pictures/", null=True)

    def to_dict(self):
        return dict(
            id=self.id, name=self.name,
            clinic=self.clinic, city=self.city,
            wa_phone=self.wa_phone, instagram_link=self.instagram_link,
            image=self.image.url
        )


class Deals(models.Model):
    class STATUS(Enum):
        new = ('new', 'Is when the request has been sent but the patient has not yet clicked "Yes"')
        confirmed = ('confirmed', 'Is when the patient pressed yes to the question about whether the surgeon had contacted')
        unconfirmed = ('unconfirmed', 'Is when the patient pressed no when asked if the surgeon had contacted her')
        without_visit = ('without_visit', 'Is when the time of consultation has already come but the QR code is not scanned')
        attendance_confirmed = ('attendance_confirmed', 'Is when you have scanned the QR code and entered a 6-digit code')
        сancel_by_client = ('cancel_by_client', 'Is when the customer personally cancels the application')

        @classmethod
        def get_value(cls, member):
            return cls[member].value[0]

    surgeon = models.ForeignKey(Surgeons, on_delete=models.PROTECT, null=True)
    user_id = models.BigIntegerField(null=True)
    phone = models.BigIntegerField(null=True)
    city = models.CharField(max_length=255, null=True)
    fio = models.CharField(max_length=255, null=True)
    email = models.CharField(max_length=255, null=True)
    start_session = models.DateTimeField(null=True)
    end_session = models.DateTimeField(null=True)
    status = models.CharField(max_length=32, choices=[x.value for x in STATUS], default=STATUS.get_value('new'))
    created = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return dict(
            id=self.id, surgeon_id=self.surgeon_id,
            user_id=self.user_id, phone=self.phone,
            city=self.city, start_session=self.start_session,
            end_session = self.end_session, created=self.created
        )


class Cities(models.Model):
    name = models.CharField(max_length=255)


class Questions(models.Model):
    question = models.TextField()
    answer = models.TextField()