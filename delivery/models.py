from django.db import models
from django.utils.safestring import mark_safe


def format_rating_stars(rating):
    """Show one golden star with the numeric rating."""
    try:
        value = max(0.0, min(5.0, float(rating)))
    except (TypeError, ValueError):
        value = 0.0

    return mark_safe(
        f'<span style="color:#e8a317;font-size:1.1em;">★</span> {value:g}'
    )


# Create your models here.
class Customer(models.Model):
    username = models.CharField(max_length= 20)
    password = models.CharField(max_length= 20)
    email = models.CharField(max_length= 20)
    mobile = models.CharField(max_length= 10)
    address = models.CharField(max_length= 50)

class Restaurant(models.Model):
    name = models.CharField(max_length= 20) 
    picture = models.URLField(max_length= 200, default= 'https://assets.cntraveller.in/photos/63d8ec9e6b0232438760225f/master/w_1600%2Cc_limit/Daysie%25201.jpg') 
    cuisine = models.CharField(max_length= 200)
    rating = models.FloatField()

    @property
    def rating_stars(self):
        return format_rating_stars(self.rating)

class Item(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete = models.CASCADE, related_name = "items")
    name = models.CharField(max_length= 20)
    picture = models.URLField(max_length = 400, default='https://www.shutterstock.com/image-photo/petty-burger-isolated-on-transparent-260nw-2614206767.jpg')
    description = models.CharField(max_length = 200)
    price = models.FloatField()
    vegetarian = models.BooleanField(default=False)
    
class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete = models.CASCADE, related_name = "cart")
    items = models.ManyToManyField("Item", related_name = "carts")

    def total_price(self):
        return sum(item.price for item in self.items.all())
    

