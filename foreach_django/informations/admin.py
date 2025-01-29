from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils import timezone
from modeltranslation.admin import TranslationAdmin

from .models import Kurslar
from .models import Malumotlar
from .models import Statistika
from .models import Xabar_yuborish, Obunachilar
from .services import send_message_to_subscriber_sync
from .tasks import send_scheduled_message

admin.site.unregister(Group)


@admin.register(Statistika)
class StatistikaAdmin(admin.ModelAdmin):
    list_display = ('all_subscribers', 'for_last_month', 'bot_users_within_24_hours')
    actions = ['update_statistics']

    @admin.action(description="Statistikani yangilash")
    def update_statistics(self, request, queryset):
        for stat in queryset:
            stat.update_statistics()
        self.message_user(request, "Statistikalar muvaffaqiyatli yangilandi!")


@admin.register(Kurslar)
class KurslarAdmin(TranslationAdmin):
    list_display = ('nom', 'tarif',)
    search_fields = ('nom',)
    list_filter = ('nom',)


@admin.register(Obunachilar)
class ObunachilarAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'full_name', 'phone_num', 'last_active_at', 'language',
        'admin', 'telegram_id', 'joined_at')
    search_fields = (
        'username', 'phone_num', 'full_name')
    list_filter = ('language', 'admin')
    ordering = ('-joined_at',)
    readonly_fields = ('joined_at',)


@admin.action(description="Obunachilarga xabar jo'natish (Vaqtni belgilash)")
def send_messages_to_selected_subscribers_celery(modeladmin, request, queryset):
    for xabar in queryset:
        for subscriber in xabar.obunachilar.all():
            if subscriber.telegram_id:
                if xabar.schedule_date:
                    send_scheduled_message.apply_async(
                        args=(
                            subscriber.telegram_id,
                            xabar.content,
                            xabar.img.path if xabar.img else None,
                            xabar.video.path if xabar.video else None
                        ),
                        eta=xabar.schedule_date
                    )
    modeladmin.message_user(request, "Xabar userlar uchun rejalashtirildi!")


@admin.action(description="Obunachilarga xabar jo'natish")
def send_messages_to_selected_subscribers(modeladmin, request, queryset):
    sent_count = 0
    failed_count = 0
    for xabar in queryset:
        for subscriber in xabar.obunachilar.all():
            if subscriber.telegram_id:
                success = send_message_to_subscriber_sync(
                    chat_id=subscriber.telegram_id,
                    message=xabar.content,
                    img_path=xabar.img.path if xabar.img else None,
                    video_path=xabar.video.path if xabar.video else None
                )
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
    modeladmin.message_user(request, f"Xabarlar yuborildi: {sent_count} ta, Xatoliklar: {failed_count} ta")


@admin.register(Xabar_yuborish)
class Xabar_yuborishAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'sent_date',)
    search_fields = ('content_type', 'content')
    list_filter = ('sent_date',)
    date_hierarchy = 'sent_date'
    filter_horizontal = ('obunachilar',)
    actions = [send_messages_to_selected_subscribers, send_messages_to_selected_subscribers_celery]


@admin.register(Malumotlar)
class MalumotlarAdmin(admin.ModelAdmin):
    list_display = ('Adminlar', 'last_message_sent_date', 'get_time_since_last_message', 'subscribers_count')

    def get_time_since_last_message(self, obj):
        last_message_info = obj.last_message_info
        if last_message_info and last_message_info['sent_date']:
            return f"{(timezone.now() - last_message_info['sent_date']).days} kun oldin"
        return "Noma'lum"

    def subscribers_count(self, obj):
        last_message_info = obj.last_message_info
        return last_message_info['subscribers_count'] if last_message_info else "Noma'lum"

    get_time_since_last_message.short_description = "Oxirgi xabar qachon"
    subscribers_count.short_description = "Xabar yuborilgan obunachilar soni"
    actions = ['update_last_message_sent_date']

    def update_last_message_sent_date(self, request, queryset):
        for obj in queryset:
            last_message_info = obj.last_message_info
            if last_message_info:
                obj.last_message_sent_date = last_message_info['sent_date']
                obj.save()
        self.message_user(request, "Malumotlar muvaffaqiyatli yangilandi!")

    update_last_message_sent_date.short_description = "Malumotlarni yangilash"
