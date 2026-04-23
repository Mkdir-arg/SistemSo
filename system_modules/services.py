import json

from django.contrib.auth.models import Group
from django.db.utils import OperationalError, ProgrammingError

from .models import ModuleState
from .registry import get_module_registry


class ModuleResolver:
    def __init__(self, registry=None):
        self.registry = registry or get_module_registry()
        self._states = None

    def _load_states(self):
        if self._states is not None:
            return self._states
        try:
            self._states = {state.slug: state for state in ModuleState.objects.all()}
        except (OperationalError, ProgrammingError):
            self._states = {}
        return self._states

    def get_definition(self, slug):
        return self.registry.get(slug)

    def is_registered(self, slug):
        return self.registry.has(slug)

    def is_active(self, slug):
        if not self.is_registered(slug):
            return False
        definition = self.get_definition(slug)
        state = self._load_states().get(slug)
        active = definition.default_enabled if state is None else state.is_enabled
        if not active:
            return False
        return all(self.is_active(dep_slug) for dep_slug in definition.depends_on)

    def build_capabilities(self):
        capabilities = {}
        for definition in self.registry.all():
            capabilities[definition.slug] = {
                "slug": definition.slug,
                "display_name": definition.display_name,
                "description": definition.description,
                "is_installed": True,
                "is_active": self.is_active(definition.slug),
                "managed_groups": list(definition.managed_groups),
                "depends_on": list(definition.depends_on),
                "nav_items": [
                    {
                        "handle": item.handle,
                        "label": item.label,
                        "url_name": item.url_name,
                        "required_groups": list(item.required_groups),
                    }
                    for item in definition.nav_items
                ],
                "handles": definition.handles,
            }
        return capabilities

    def get_inactive_managed_groups(self):
        names = set()
        for definition in self.registry.all():
            if not self.is_active(definition.slug):
                names.update(definition.managed_groups)
        for state in self._load_states().values():
            if not state.is_installed:
                names.update(state.managed_groups)
        return names


def module_is_registered(slug):
    return ModuleResolver().is_registered(slug)


def module_is_active(slug):
    return ModuleResolver().is_active(slug)


def get_module_capabilities():
    resolver = ModuleResolver()
    capabilities = resolver.build_capabilities()
    return capabilities, json.dumps(capabilities)


def sync_module_catalog():
    registry = get_module_registry()
    registered_slugs = {definition.slug for definition in registry.all()}
    created = 0
    updated = 0
    for definition in registry.all():
        state, was_created = ModuleState.objects.get_or_create(
            slug=definition.slug,
            defaults=definition.as_state_defaults(),
        )
        if was_created:
            created += 1
            continue

        dirty = []
        for field_name, value in definition.as_state_defaults().items():
            if field_name == "is_enabled":
                continue
            if getattr(state, field_name) != value:
                setattr(state, field_name, value)
                dirty.append(field_name)
        if not state.is_installed:
            state.is_installed = True
            dirty.append("is_installed")
        if dirty:
            state.save(update_fields=dirty + ["updated_at"])
            updated += 1
    stale_states = ModuleState.objects.exclude(slug__in=registered_slugs).filter(is_installed=True)
    if stale_states.exists():
        updated += stale_states.update(is_installed=False, is_enabled=False)
    return created, updated


def get_assignable_groups_queryset(*, instance=None):
    queryset = Group.objects.all().order_by("name")
    hidden_names = ModuleResolver().get_inactive_managed_groups()
    if not hidden_names:
        return queryset

    if instance is not None:
        hidden_names = hidden_names - set(instance.groups.values_list("name", flat=True))
    return queryset.exclude(name__in=hidden_names)
