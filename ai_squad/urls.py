from rest_framework.routers import DefaultRouter
from .views import SquadRunViewSet

router = DefaultRouter()
router.register(r"ai-squad/runs", SquadRunViewSet, basename="ai-squad-runs")

urlpatterns = router.urls
