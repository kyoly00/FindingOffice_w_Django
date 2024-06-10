from django import template

register = template.Library()

@register.filter
def get_office_facilities(office, selected_facilities):
    return [facility for facility in selected_facilities if facility in office.facilities]
