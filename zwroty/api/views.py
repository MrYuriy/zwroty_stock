from rest_framework.views import APIView
from rest_framework.response import Response
from zwroty.models import ReturnOrder


class WZApiView(APIView):
    def get(self, request):
        orders = ReturnOrder.objects.filter(complite_status=True)\
            .select_related("shop", "user").prefetch_related(
        "products__sku",
        "products__reasone",
    )
        order_list = []
        for order in orders:
            order_data = {
                "bw_nr": order.nr_order,
                "wz_nr":  order.position_nr,
                "data": order.date_recive.strftime("%d.%m.%Y"),
                "user_name": order.user.full_name,
                "shop_desct": order.shop.description,
                "shop_nr": order.shop.description,
                "ship_doc": order.shop.ship_doc,
                "lines": []
            }
            
            for product in order.products.all():
                product_data = {
                    "reasone":  product.reasone.name,
                    "sku_log": "" if product.sku.sku_log == None else str(product.sku.sku_log).replace("999999999999",""),
                    "sku_hand": "" if product.sku.sku_hand == None else str(product.sku.sku_hand),
                    "descript": "" if product.sku.name_of_product == None else product.sku.name_of_product,
                    "qty": f"{product.quantity} {product.tape_of_delivery}"
                }
                order_data["lines"].append(product_data)
            order_list.append(order_data)



        return Response(order_list)