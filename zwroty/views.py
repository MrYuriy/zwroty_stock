import datetime
import io
from django.conf import settings
from django.http import FileResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import View
from datetime import datetime
from .models import (
    Barcode, Product, 
    ReturnOrder, Shop, 
    ReasoneComment, SkuInformation,
    SkuInformationBarcode
    )
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.barcode import code128


def admin_panel(request):
    return render(request, "zwroty/admin_panel.html")

class HomeView(LoginRequiredMixin, View):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    

class WZMenagment(LoginRequiredMixin, View):
    template_name = "zwroty/wz_menagment.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class ReturnOrderCreate(LoginRequiredMixin, View):
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


class AddLineMenuView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "zwroty/add_line_menu.html")
    def post(self, request, *args, **kwargs):
        identifier = request.POST.get('identifier', None)
        compile_exces = request.POST.get("compile_exces", None)
        print(compile_exces, identifier)
        try:
            order = ReturnOrder.objects.get(identifier=identifier)
            if compile_exces:
                return HttpResponseRedirect(reverse('zwroty:add_product') + '?identifier=' + str(identifier))
            if order.complite_status:
              return render(
                request, 
                "zwroty/add_line_menu.html", 
                context={"error_message": "Order complite Are you shure", "complite":True, "identifier":identifier}
                )  
        except ObjectDoesNotExist:
            return render(
                request, 
                "zwroty/add_line_menu.html", 
                context={"error_message": "Nieprawidlowy indetufukator"}
                )
        return HttpResponseRedirect(reverse('zwroty:add_product') + '?identifier=' + str(identifier))

class AddProduct(LoginRequiredMixin, View):
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
                    reasone = reas_queryset.get(name=line["reas_name"]),
                    actual_barcode = line["ean"]
                )
                for line in cache.get(identifier)
            ])
           
            order.products.add(*product_list)
            order.complite_status = True
            order.save()
            cached_value = cache.get(identifier)
            cache.delete(identifier)
            return redirect("zwroty:home")



        sku_inform_barcode = SkuInformationBarcode.objects.filter(
            barcode__barcode__icontains=ean
            )
        if sku_inform_barcode:
            if len(sku_inform_barcode)>1:
                sku_inform_barcode=sku_inform_barcode.filter(barcode__barcode=ean)
            sku = sku_inform_barcode[0].sku_information
        else:
            sku = None

        if not sku or int(ean) == 999999999999:
            barcode, _ = Barcode.objects.get_or_create(barcode=ean)

            description = ""
            if sku_deskript:
                description = sku_deskript
                
            sku = SkuInformation(
                sku_log=ean,name_of_product=description
            )

            sku.save()
            sku_inform_barcode = SkuInformationBarcode(
                barcode = barcode,
                sku_information = sku
            )
            sku_inform_barcode.save()

        order_line = {
                "user": user, 
                "qty": qty,
                "reas_name": reas_name, 
                "sku": sku,
                "ean": ean, 
                "tape_of_delivery": tape_of_delivery, 
                }

        cached_value = cache.get(identifier)
        if cached_value:
            cached_value.append(order_line)
        else:
            cached_value = [order_line]
        cache.set(identifier, cached_value, timeout=300)
        return HttpResponseRedirect(reverse('zwroty:add_product') + '?identifier=' + str(identifier))


class ReportWZView(LoginRequiredMixin, View):
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
            my_canvas.drawString(300, 570, f"<-- Zeskanuj ({order.identifier})")
            my_canvas.showPage()
        my_canvas.save()
        buffer.seek(0)
        response = FileResponse(buffer, as_attachment=False, filename="Protokół szkody.pdf")
        return response
    
class OrderStorageView(LoginRequiredMixin, View):
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
            queryset = queryset.filter(identifier__icontains=identifier)
        if position_nr:
            queryset = queryset.filter(identifier__icontains=position_nr)
        if nr_order:
            queryset = queryset.filter(nr_order__icontains=nr_order)
        if status:
            status = int(status)
            queryset = queryset.filter(complite_status=status)
        if date_recive:
            date_recive = datetime.strptime(date_recive, "%Y-%m-%d")
            queryset = queryset.filter(date_recive__date=date_recive)
        
        context = {"order_list": queryset.order_by("-date_recive")}
        return render(request, "zwroty/return_order_list.html", context)


class ReturnOrderDetailView(LoginRequiredMixin, View):
    def get_context_data(self, oredr_id):
        context = {}
        order = get_object_or_404(ReturnOrder, id=oredr_id)
        date_recive = order.date_recive.strftime("%d.%m.%Y")
        context["date_recive"] = date_recive
        context["order"] = order
        context["order_products"] = [
            f"sku_log: {product.sku.sku_log}\n\
                sku_hand: {product.sku.sku_hand}\n\
                    sku_ean: {product.actual_barcode}\n\
                        sku_deskript: {product.sku.name_of_product}\n\
                            typ: {product.reasone.name}" 
                        
                for product in order.products.all()]
        return context

    def get(self, request, *args, **kwargs):
        order_id = self.kwargs.get("pk")
        context = self.get_context_data(oredr_id=order_id)
        return render(request, "zwroty/return_order_detail.html", context)


class ReturnOrderListView(LoginRequiredMixin, View):
    template_name = "zwroty/return_order_list.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
