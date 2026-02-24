class BreadcrumbMixin:
    """Add breadcrumbs = [('Label', 'url'), ...] to any CBV."""

    def get_breadcrumbs(self):
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context
