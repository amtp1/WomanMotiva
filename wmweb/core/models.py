from django.db import models


class Surgeons(models.Model):
    name = models.CharField(max_length=255, null=False)
    clinic = models.CharField(max_length=255, null=False)
    city = models.CharField(max_length=255, null=False)
    wa_phone = models.BigIntegerField(null=True)
    image = models.ImageField(upload_to="profile_pictures/")

    def to_dict(self):
        return dict(
            id=self.id, name=self.name,
            clinic=self.clinic, city=self.city,
            wa_phone=self.wa_phone, image=self.image.url
        )


class Deals(models.Model):
    surgeon = models.ForeignKey(Surgeons, on_delete=models.PROTECT, null=True)
    user_id = models.BigIntegerField(null=True)
    phone = models.BigIntegerField(null=True)
    city = models.CharField(max_length=255, null=True)
    start_session = models.DateTimeField(null=True)
    end_session = models.DateTimeField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return dict(
            id=self.id, surgeon_id=self.surgeon_id,
            user_id=self.user_id, phone=self.phone,
            city=self.city, start_session=self.start_session,
            end_session = self.end_session, created=self.created
        )