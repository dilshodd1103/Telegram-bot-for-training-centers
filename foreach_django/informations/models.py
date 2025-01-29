from ckeditor_uploader.fields import RichTextUploadingField
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.timezone import now
from django.utils.timezone import timedelta


class Kurslar(models.Model):
    nom = models.CharField(verbose_name="Kurs nomi", max_length=255)
    tarif = RichTextUploadingField(verbose_name="Kursga ta'rif bering")
    rasm = models.ImageField(
        verbose_name="Kurs rasmi",
        upload_to="rasmlar/",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Kurs"
        verbose_name_plural = "Kurslar"

    def __str__(self):
        return self.nom


class Obunachilar(models.Model):
    username = models.CharField(verbose_name="Foydalanuvchi username", max_length=150, unique=False, null=False)
    full_name = models.CharField(verbose_name="Foydalanuvchining ismi", max_length=150, unique=False, null=True)
    phone_num = models.CharField(verbose_name="Telefon raqami", max_length=15, unique=True, null=True)
    admin = models.BooleanField(default=False)
    language = models.CharField(
        verbose_name="Til",
        max_length=15,
    )
    telegram_id = models.BigIntegerField(verbose_name="Telegram ID ", unique=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_active_at = models.DateTimeField(verbose_name="Oxirgi faollik vaqti", null=True, blank=True)

    class Meta:
        verbose_name = "Obunachi"
        verbose_name_plural = "Obunachilar"

    def __str__(self):
        return self.full_name


class Xabar_yuborish(models.Model):
    content_type = models.CharField(verbose_name="Xabar turi", max_length=50)
    content = RichTextUploadingField(verbose_name="Xabar uchun matn jo'nating ", blank=True, null=True)
    img = models.ImageField(upload_to='images_uploaded', null=True, blank=True)
    video = models.FileField(
        upload_to='videos_uploaded',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['MOV', 'avi', 'mp4', 'webm', 'mkv'])]
    )
    sent_date = models.DateTimeField(auto_now_add=True, verbose_name='Saqlangan vaqt')
    schedule_date = models.DateTimeField(
        verbose_name="Yuborish vaqti",
        null=True,
        blank=True,
        help_text="Agar vaqt ko'rsatilmasa, xabar darhol jo'natiladi."
    )
    obunachilar = models.ManyToManyField('Obunachilar', blank=True)

    class Meta:
        verbose_name = "Xabar yuborish"
        verbose_name_plural = "Xabar yuborish"

    def __str__(self):
        return f"Xabar: {self.content_type} ({self.sent_date})"


class Statistika(models.Model):
    all_subscribers = models.IntegerField(verbose_name='Barcha obunachilar', default=0)
    for_last_month = models.IntegerField(verbose_name='Oxirgi oyda qushilganlar', default=0)
    bot_users_within_24_hours = models.IntegerField(verbose_name="Botdan foydalanganlar (24 saot)", default=0)

    def update_statistics(self):
        self.all_subscribers = Obunachilar.objects.count()
        one_month_ago = now() - timedelta(days=30)
        self.for_last_month = Obunachilar.objects.filter(joined_at__gte=one_month_ago).count()
        one_day_ago = now() - timedelta(hours=24)
        self.bot_users_within_24_hours = Obunachilar.objects.filter(last_active_at__gte=one_day_ago).count()
        self.save()

    class Meta:
        verbose_name = "Statistika"
        verbose_name_plural = "Statistikalar"

    def __str__(self):
        return str(self.all_subscribers)


class Malumotlar(models.Model):
    admins = models.IntegerField(verbose_name="Adminlar", null=True, blank=True)
    last_message_sent_date = models.DateTimeField(null=True, verbose_name="Oxirgi xabar yuborilgan")

    @property
    def Adminlar(self):
        return Obunachilar.objects.filter(admin=True).count()

    @property
    def last_message_info(self):
        last_message = Xabar_yuborish.objects.order_by('-sent_date').first()
        if last_message:
            return {
                "sent_date": last_message.sent_date,
                "subscribers_count": last_message.obunachilar.count()
            }
        return None

    class Meta:
        verbose_name = "Malumot"
        verbose_name_plural = "Malumotlar"

    def __str__(self):
        return f"Malumotlar"

