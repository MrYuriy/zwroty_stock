import os
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from .models import Product, ReturnOrder, Shop, ReasoneComment
from django.core.cache import cache, caches
from django.core.cache.backends.filebased import FileBasedCache


class HomeView(View):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class ReturnOrderCreate(View):
    template_name = "zwroty/return_order_create.html"

    def get(self, request, *args, **kwargs):
         return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):

        nr_order = request.POST.get("order_number")
        shop_nr = request.POST.get("shop")
        comment = request.POST.get("comment", "")
        position_nr = request.POST.get("wz_nr")
        user = self.request.user
        shop = Shop.objects.get(shop_nr=int(shop_nr))

        return_order = ReturnOrder(
            nr_order=nr_order,
            shop=shop,
            comment=comment,
            position_nr=position_nr,
            user = user
        )
        return_order.save()

        return render(request, "index.html")