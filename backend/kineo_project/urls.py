from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from kineo.views import StudioViewSet, MovieViewSet, SessionViewSet, ReviewViewSet

router = DefaultRouter()
router.register("studios", StudioViewSet, basename="studio")
router.register("movies", MovieViewSet, basename="movie")
router.register("sessions", SessionViewSet, basename="session")
router.register("reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path("", RedirectView.as_view(url="/api/", permanent=False)),
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
