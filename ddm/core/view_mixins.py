class DDMContextMixin:
    """Add breadcrumbs and back target to CBVs."""

    back_target = None
    submit_label = None

    def get_breadcrumbs(self):
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        breadcrumbs = self.get_breadcrumbs()
        context['breadcrumbs'] = breadcrumbs
        context['back_target'] = self.get_back_target(breadcrumbs)
        context['submit_label'] = self.submit_label
        return context

    def get_back_target(self, breadcrumbs: list | None = None):
        if self.back_target:
            return self.back_target

        if breadcrumbs and len(breadcrumbs) > 1:
            target = breadcrumbs[-2]
            if len(target) > 1:
                return target[1]

        return None

    def get_submit_label(self):
        return self.submit_label
