# myapp/context_processors.py

from .models import Category


def categories(request):
    # Hier können Sie die Logik für die Kategorien einfügen, zum Beispiel:
    c = Category.objects.all().order_by('order_number')
    return {'categories': c}
