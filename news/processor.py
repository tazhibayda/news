from articles.models import Genre


def general_context(request):
    genres = Genre.objects.all()
    return {'genres': genres}
