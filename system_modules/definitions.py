from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class NavItemDefinition:
    handle: str
    label: str
    url_name: str
    required_groups: tuple[str, ...] = ()


@dataclass(frozen=True)
class ModuleDefinition:
    slug: str
    display_name: str
    description: str = ""
    depends_on: tuple[str, ...] = ()
    managed_groups: tuple[str, ...] = ()
    nav_items: tuple[NavItemDefinition, ...] = ()
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
            "depends_on": list(self.depends_on),
            "managed_groups": list(self.managed_groups),
            "nav_items": [asdict(item) for item in self.nav_items],
            "route_handles": list(self.route_handles),
            "api_handles": list(self.api_handles),
            "websocket_handles": list(self.websocket_handles),
            "startup_hooks": list(self.startup_hooks),
            "adapter_points": list(self.adapter_points),
            "is_enabled": self.default_enabled,
        }

    @property
    def handles(self):
        return {
            "routes": list(self.route_handles),
            "api": list(self.api_handles),
            "websocket": list(self.websocket_handles),
            "startup_hooks": list(self.startup_hooks),
            "adapter_points": list(self.adapter_points),
        }
