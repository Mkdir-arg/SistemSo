from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class NavItemDefinition:
    handle: str
    label: str
    url_name: str
    required_groups: tuple[str, ...] = ()


@dataclass(frozen=True)
class UrlDefinition:
    handle: str
    route: str
    urlconf: str
    namespace: str | None = None
    app_name: str | None = None


@dataclass(frozen=True)
class WebsocketDefinition:
    handle: str
    urlconf: str
    attribute: str = "websocket_urlpatterns"


@dataclass(frozen=True)
class ModuleDefinition:
    slug: str
    display_name: str
    app_config: str
    module_type: str = "removable"
    description: str = ""
    removable: bool = True
    is_core: bool = False
    depends_on: tuple[str, ...] = ()
    managed_groups: tuple[str, ...] = ()
    nav_items: tuple[NavItemDefinition, ...] = ()
    web_routes: tuple[UrlDefinition, ...] = ()
    api_routes: tuple[UrlDefinition, ...] = ()
    websocket_routes: tuple[WebsocketDefinition, ...] = ()
    route_handles: tuple[str, ...] = ()
    api_handles: tuple[str, ...] = ()
    websocket_handles: tuple[str, ...] = ()
    startup_hooks: tuple[str, ...] = ()
    adapter_points: tuple[str, ...] = ()
    default_enabled: bool = True

    def as_state_defaults(self):
        return {
            "display_name": self.display_name,
            "description": self.description,
            "module_type": self.module_type,
            "removable": self.removable,
            "is_core": self.is_core,
            "depends_on": list(self.depends_on),
            "managed_groups": list(self.managed_groups),
            "nav_items": [asdict(item) for item in self.nav_items],
            "route_handles": [route.handle for route in self.web_routes] or list(self.route_handles),
            "api_handles": [route.handle for route in self.api_routes] or list(self.api_handles),
            "websocket_handles": [route.handle for route in self.websocket_routes] or list(self.websocket_handles),
            "startup_hooks": list(self.startup_hooks),
            "adapter_points": list(self.adapter_points),
            "is_enabled": self.default_enabled,
        }

    @property
    def handles(self):
        return {
            "routes": [route.handle for route in self.web_routes] or list(self.route_handles),
            "api": [route.handle for route in self.api_routes] or list(self.api_handles),
            "websocket": [route.handle for route in self.websocket_routes] or list(self.websocket_handles),
            "startup_hooks": list(self.startup_hooks),
            "adapter_points": list(self.adapter_points),
        }
