from rest_framework import routers
from .views import TargetViewSet

router = routers.DefaultRouter()
router.register("targets", TargetViewSet, basename="targets")
urlpatterns = router.urls
