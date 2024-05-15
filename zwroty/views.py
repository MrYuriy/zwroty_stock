from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View



class HomeView(View):
    template_name = "index.html"

    # write_report_gs()
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
