from django import template


register = template.Library()


@register.simple_tag(takes_context=True)
def module_active(context, slug):
    capabilities = context.get("module_capabilities", {})
    return bool(capabilities.get(slug, {}).get("is_active"))


@register.simple_tag(takes_context=True)
def module_registered(context, slug):
    capabilities = context.get("module_capabilities", {})
    return slug in capabilities
