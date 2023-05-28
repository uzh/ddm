from ddm.models.core import DonationProject
from ddm.views.participation_flow import BriefingView, DebriefingView
from ddm_pooled.models import PooledProject
from django.utils.deprecation import MiddlewareMixin


class PooledProjectMiddleware(MiddlewareMixin):

    def _init_(self, get_response):
        self.get_response = get_response

    def _call_(self, request):
        print('Middleware called: 1!')
        # Code that is executed in each request before the view is called

        response = self.get_response(request)

        """
        if called_view is BriefingView:
            project = get_project()
            if project is PooledProject:
                check if url contains appropriate url parameter;
                if url parameters are missing:  
                    add general information (or raise exception)
        
        if called_view is DebriefingView:
            project = get_project()
            if project is PooledProject:
                if PooledProject.show_donation_question:
                    redirect to donation_question_view
                
        """

        # Code that is executed in each request after the view is called
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # This code is executed just before the view is called
        print('Middleware called: 2!!!!!!')
        print(f'request: {request.GET}')
        request.GET = request.GET.copy()
        request.GET['new'] = 'abc'
        print(f'request: {request.GET}')

        if hasattr(view_func, 'view_class'):
            view_class = view_func.view_class
            print(view_class)

            if view_class is BriefingView:

                # get project
                project_slug = view_kwargs.get('slug', None)
                project = self.get_project(project_slug)

                pooled_project = PooledProject.objects.filter(project=project)
                if pooled_project:
                    required_params = ['pool_id']
                    if not all(p in request.GET for p in required_params):
                        pass

                print('briefing view identified!')
                print(f'view_args: {view_args}')
                print(f'view_kwargs: {view_kwargs}')
                print(f'request: {request.GET}')

                # retrieve project with slug parameter in request

                return

            if view_class is DebriefingView:
                print('DEbriefing view identified!')
                return

        print(view_func.view_class.__dict__)

        return

    def process_exception(self, request, exception):
        # This code is executed if an exception is raised
        return

    def process_template_response(self, request, response):
        # This code is executed if the response contains a render() method
        return response

    def get_project(self, slug):
        project = DonationProject.objects.filter(slug=slug).first()
        return project

