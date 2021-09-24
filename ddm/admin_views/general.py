from django.shortcuts import render


class SurquestContextMixin(object):

    inline_formsets = []
    fieldsets = []

    def get_context_data(self, **kwargs):

        def get_inline_formset_for_context(obj):
            formsets = []
            for inline_formset in obj.inline_formsets:
                formset_class = inline_formset['formset']
                if self.request.POST:
                    formset = formset_class(self.request.POST, instance=self.object)
                else:
                    formset = formset_class(instance=self.object)

                formsets.append({
                    'label': inline_formset['label'],
                    'formset': formset
                })

            return formsets

        def get_fieldsets_for_context(obj):
            fieldsets = []
            for fieldset in obj.fieldsets:
                if 'formset_class' in fieldset:
                    formset_class = fieldset['formset_class']

                    if obj.request.POST:
                        formset = formset_class(obj.request.POST, instance=obj.object)
                    else:
                        formset = formset_class(instance=obj.object)

                    fieldset['formset'] = formset

                fieldsets.append(fieldset)
            return fieldsets

        context = super().get_context_data(**kwargs)

        # Add inline_formsets to context if present in object.
        if hasattr(self, 'inline_formsets'):
            context['inline_formsets'] = get_inline_formset_for_context(self)

        # Add fieldsets to context if present in object.
        if hasattr(self, 'fieldsets'):
            context['fieldsets'] = get_fieldsets_for_context(self)

        return context


class SurquestUpdateMixin(object):

    def form_valid(self, form):

        def get_formsets(context):
            formsets = []
            # Collect all inline formsets on the first level.
            if 'inline_formsets' in context:
                for formset in context['inline_formsets']:
                    formsets.append(formset['formset'])
            # Collect all inline formsets within fieldsets.
            if 'fieldsets' in context:
                for fieldset in context['fieldsets']:
                    if 'formset' in fieldset:
                        formsets.append(fieldset['formset'])
            return formsets

        context = self.get_context_data()

        formsets = get_formsets(context)
        formset_valid = True

        for formset in formsets:
            if formset.is_valid():
                instances = formset.save(commit=False)

                for instance in instances:
                    instance.save()

                for instance in formset.deleted_objects:
                    instance.delete()

            else:
                formset_valid = False

        if not formset_valid:
            return render(self.request, self.template_name, context)

        return super().form_valid(form)
