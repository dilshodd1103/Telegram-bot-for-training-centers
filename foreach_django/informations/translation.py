from modeltranslation.translator import register, TranslationOptions
from .models import Kurslar

@register(Kurslar)
class KurslarTranslationOptions(TranslationOptions):
    fields = ('nom', 'tarif')

