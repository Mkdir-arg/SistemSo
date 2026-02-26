from django.urls import re_path
from .consumers import SquadRunConsumer

websocket_urlpatterns = [
    re_path(r"^ws/ai-squad/runs/(?P<run_id>\d+)/$", SquadRunConsumer.as_asgi()),
]
