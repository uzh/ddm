from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, render

from ddm.forms import FilterSequenceForm, FilterFormset, FilterForm
from ddm.models import (
    FilterCondition, FilterSequence, Question, QuestionItem
)


@login_required
def update_filter(request, filter_target, target_id):
    template = 'ddm/admin/questions/filters.html'

    if filter_target == 'q':
        target_item = None
        target_question = get_object_or_404(Question, pk=target_id)
        filter_conditions = FilterCondition.objects.filter(
            target_question=target_question, target_question_item=None)
        filter_sequence = FilterSequence.objects.get(
            question=target_question, question_item=None)
    elif filter_target == 'qi':
        target_item = get_object_or_404(QuestionItem, pk=target_id)
        target_question = target_item.question
        filter_conditions = FilterCondition.objects.filter(
            target_question_item=target_item)
        filter_sequence = FilterSequence.objects.get(
            question=None, question_item=target_item)
    else:
        raise Http404()

    # Add additional information to the context.
    questionnaire = target_question.page.questionnaire
    context = {
        'questionnaire': questionnaire,
        'page': target_question.page,
        'question': target_question,
        'question_item': target_item,
        'target_question_pk': target_question.pk,
        'target_question_type': target_question.question_type,
    }

    # Get the list of available variables for this particular filter and add it
    # to the context.
    filter_variables = questionnaire.get_var_selection_for_filter(
        target_question)
    filter_formset = modelformset_factory(
        FilterCondition, FilterForm, can_delete=True, formset=FilterFormset)
    formset = filter_formset(queryset=filter_conditions,
                             form_kwargs={'variable_choices': filter_variables,
                                          'target_question': target_question,
                                          'target_question_item': target_item})
    context['formset'] = formset

    # Add the filter sequence form to the context.
    if filter_target == 'q':
        filter_sequence = FilterSequence.objects.get(
            question=target_question, question_item=None)
    elif filter_target == 'qi':
        filter_sequence = FilterSequence.objects.get(
            question=None, question_item=target_item)

    context['filter_sequence_form'] = FilterSequenceForm(instance=filter_sequence)

    if request.method == 'GET':
        return render(request, template, context)

    if request.method == 'POST':
        # Handle the filter condition formset.
        form = filter_formset(request.POST,
                              form_kwargs={
                                  'variable_choices': filter_variables,
                                  'target_question': target_question,
                                  'target_question_item': target_item,
                              })
        if form.is_valid():
            instances = form.save(commit=False)
            for instance in instances:
                instance.save()
            for instance in form.deleted_objects:
                instance.delete()
        else:
            context['formset'] = form

        # Handle the filter sequence form.
        filter_sequence_form = FilterSequenceForm(
            request.POST, instance=filter_sequence)
        if filter_sequence_form.is_valid():
            filter_sequence_form.save()
        context['filter_sequence_form'] = filter_sequence_form

        return render(request, template, context)
