import datetime
import io
import os
from django.conf import settings
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import View
from datetime import datetime, timedelta
from .models import Product, ReturnOrder, Shop, ReasoneComment, SkuInformation
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import code128
import emoji


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
            user=user,
        )
        return_order.save()

        return render(request, "index.html")


# def add_line_menu(request):
#     return render(request, "zwroty/add_line_menu.html")

class AddLineMenuView(View):
    def get(self, request):
        return render(request, "zwroty/add_line_menu.html")
    def post(self, request, *args, **kwargs):
        identifier = request.POST.get('identifier', None)
        try:
            ReturnOrder.objects.get(identifier=identifier)
        except ObjectDoesNotExist:
            return render(
                request, 
                "zwroty/add_line_menu.html", 
                context={"error_message": "Nieprawidlowy indetufukator"}
                )
        return HttpResponseRedirect(reverse('zwroty:add_product') + '?identifier=' + str(identifier))

class AddProduct(View):
    template_name = "zwroty/add_product.html"

    def get_context_data(self, **kwargs):
        reas_list = ReasoneComment.objects.all()
        reasons = [{"id": reas.id, "name": reas.name} for reas in reas_list]
        context = {"reasons": reasons}
        return context

    def get(self, request, *args, **kwargs):
        identifier = self.request.GET.get("identifier")
        context = self.get_context_data()
        context["identifier"] = identifier
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        reas_name = request.POST.get("reason_name")
        sku_deskript = request.POST.get("sku_deskription")
        tape_of_delivery = request.POST.get("tape_of_delivery")
        ean = request.POST.get("ean")
        qty = request.POST.get("qty")
        finish = self.request.POST.get("finish")
        identifier = self.request.POST.get("identifier")
        
        if finish:
            reas_queryset = ReasoneComment.objects.all()
            order = ReturnOrder.objects.get(identifier=identifier)
            product_list = Product.objects.bulk_create([
                Product(
                    sku = line["sku"],
                    quantity = line["qty"],
                    tape_of_delivery = line["tape_of_delivery"],
                    reasone = reas_queryset.get(name=line["reas_name"])
                )
                for line in cache.get(identifier)
            ])
           
            order.products.add(*product_list)
            order.complite_status = True
            order.save()
            cached_value = cache.get(identifier)
            return redirect("zwroty:home")
        sku = SkuInformation.objects.filter(barcodes__barcode = ean).first()

        order_line = {
                "user": user, 
                "qty": qty,
                "reas_name": reas_name, 
                "sku": sku, 
                "tape_of_delivery": tape_of_delivery, 
                }

        cached_value = cache.get(identifier)
        if cached_value:
            cached_value.append(order_line)
        else:
            cached_value = [order_line]
        cache.set(identifier, cached_value, timeout=300)
        return HttpResponseRedirect(reverse('zwroty:add_product') + '?identifier=' + str(identifier))


class ReportWZView(View):
    template_name = "zwroty/report_wz.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    def post(self, request, *args, **kwargs):
        rec_day = self.request.POST.get("day")
        rec_day = datetime.strptime(rec_day, "%Y-%m-%d")

        order_list = ReturnOrder.objects.filter(
            complite_status=False, date_recive__date=rec_day
            )
        buffer = io.BytesIO()
        my_canvas = canvas.Canvas(buffer)
        
        pdfmetrics.registerFont(TTFont("FreeSans", "freesans/FreeSans.ttf"))
        for order in order_list:
            my_canvas.setFont("FreeSans", 20)
            barcode = code128.Code128(f"{order.identifier}", barWidth=1.7, barHeight=35)
            barcode.drawOn(my_canvas, 80, 564)
            
            my_canvas.drawString(100, 654, f"Bon wyjścia: {order.nr_order}")
            my_canvas.drawString(100, 634, f"Numer wuzetki: {order.position_nr}")
            my_canvas.drawString(100, 614, f"Sklep: {order.shop.description}")
            my_canvas.drawString(300, 570, f"<-- Zeskanuj to ({order.identifier})")
            my_canvas.showPage()
        my_canvas.save()
        buffer.seek(0)
        response = FileResponse(buffer, as_attachment=False, filename="Protokół szkody.pdf")
        return response
    
class OrderStorageView(View):
    template_name = "zwroty/return_order_filter.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    
    def post(self, request, *args, **kwargs):

        identifier = request.POST.get("identifier", None)
        nr_order = request.POST.get("nr_order", None)
        position_nr = request.POST.get("position_nr", None)
        status = request.POST.get("staus", None)
        date_recive = request.POST.get("date_recive", None)

        queryset = ReturnOrder.objects.all().select_related("shop", "user").prefetch_related("products")

        if identifier:
            queryset = queryset.filter(identifier=identifier)
        if position_nr:
            queryset = queryset.filter(identifier=position_nr)
        if nr_order:
            queryset = queryset.filter(nr_order=nr_order)
        if status:
            status = int(status)
            queryset = queryset.filter(complite_status=status)
        if date_recive:
            date_recive = datetime.strptime(date_recive, "%Y-%m-%d")
            queryset = queryset.filter(date_recive__date=date_recive)
        
        context = {"order_list": queryset.order_by("-date_recive")}
        return render(request, "zwroty/return_order_list.html", context)

class ReturnOrderListView(View):
    template_name = "zwroty/return_order_list.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
