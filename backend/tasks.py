from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import yaml
import requests
from backend.models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter

@shared_task
def send_email_task(subject, message, to_email):
    msg = EmailMultiAlternatives(subject, message, settings.EMAIL_HOST_USER, [to_email])
    msg.send()

@shared_task
def do_import_task(user_id, url):
    response = requests.get(url)
    if response.status_code != 200:
        return f"Error loading URL: {response.status_code}"
    
    data = yaml.safe_load(response.content)

    # ИСПРАВЛЕНИЕ ТУТ: Ищем ТОЛЬКО по user_id
    shop, created = Shop.objects.get_or_create(user_id=user_id, defaults={'name': data['shop']})
    
    # Если магазин уже был, но в файле другое имя — обновляем имя
    if not created and shop.name != data['shop']:
        shop.name = data['shop']
        shop.save()
    
    # Дальше код остается без изменений
    ProductInfo.objects.filter(shop_id=shop.id).delete()

    for category in data['categories']:
        cat_obj, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
        cat_obj.shops.add(shop.id)

    for item in data['goods']:
        product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])
        product_info = ProductInfo.objects.create(
            product_id=product.id,
            external_id=item['id'],
            model=item['model'],
            price=item['price'],
            price_rrc=item['price_rrc'],
            quantity=item['quantity'],
            shop_id=shop.id
        )
        for name, value in item['parameters'].items():
            param_obj, _ = Parameter.objects.get_or_create(name=name)
            ProductParameter.objects.create(
                product_info_id=product_info.id,
                parameter_id=param_obj.id,
                value=value
            )
    return f"Import for shop '{data['shop']}' completed"