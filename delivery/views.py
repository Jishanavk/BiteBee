from django.shortcuts import get_object_or_404, render ,redirect
from django.http import HttpResponse
import razorpay
from django.contrib import messages
from django.conf import settings


from .models import Customer , Restaurant, Item , Cart 


# Create your views here.
def say_hello(request):
    #return HttpResponse('Say Hello my app is working!')
    return render(request, "delivery/index.html")

def open_signup(request):
    return render(request, "delivery/signup.html")

def open_signin(request):
    return render(request, "delivery/signin.html")
def signup(request):
    if request.method != 'POST':
        return redirect('open_signup')

    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    mobile = request.POST.get('mobile')
    address = request.POST.get('address')

    if Customer.objects.filter(username=username).exists():
        return HttpResponse("Duplicate username")

    Customer.objects.create(
        username=username,
        password=password,
        email=email,
        mobile=mobile,
        address=address,
    )
    return render(request, 'delivery/signin.html')

def signin(request):
    if request.method != 'POST':
        return redirect('open_signin')

    username = request.POST.get('username')
    password = request.POST.get('password')

    try:
        Customer.objects.get(username=username, password=password)
        if username == 'admin':
            return render(request, 'delivery/admin_home.html')
        restaurantList = Restaurant.objects.all()
        return render(request, 'delivery/customer_home.html', {
            "restaurantList": restaurantList,
            "username": username,
        })
    except Customer.DoesNotExist:
        return render(request, 'delivery/fail.html')

def open_add_restaurant(request):
    return render(request, 'delivery/add_restaurant.html')

def add_restaurant(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')

        try:
            Restaurant.objects.get(name = name)
            return HttpResponse("Duplicate restaurant!")
        except:
            Restaurant.objects.create(
                name=name,
                picture=picture,
                cuisine=cuisine,
                rating=float(rating),
            )
    return render(request, 'delivery/admin_home.html')

def open_show_restaurant(request):
    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurant.html',{"restaurantList" : restaurantList})
def open_update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    return render(request, 'delivery/update_restaurant.html', {"restaurant" : restaurant})

def update_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    if request.method == "POST":
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        cuisine = request.POST.get('cuisine')
        rating = request.POST.get('rating')

        restaurant.name = name
        restaurant.picture = picture
        restaurant.cuisine = cuisine
        restaurant.rating = rating

        restaurant.save()

    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurant.html', {"restaurantList" : restaurantList})    
        
def delete_restaurant(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    restaurant.delete()

    restaurantList = Restaurant.objects.all()
    return render(request, 'delivery/show_restaurant.html',{"restaurantList" : restaurantList})

def open_update_menu(request,restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()
    return render(request, 'delivery/update_menu.html',{"itemList" : itemList, "restaurant" : restaurant})

def update_menu(request, restaurant_id):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    if request.method == "POST":
        name = request.POST.get('name')
        picture = request.POST.get('picture')
        description = request.POST.get('description')
        price = request.POST.get('price')
        vegetarian = request.POST.get('vegetarian') == 'on'

        if Item.objects.filter(restaurant=restaurant, name=name).exists():
            return HttpResponse("Duplicate item for this restaurant!")
        else:
            Item.objects.create(
                restaurant = restaurant,
                name = name,
                description = description,
                price = price,
                vegetarian = vegetarian,
                picture = picture,
            )
    itemList = restaurant.items.all()
    return render(request, 'delivery/update_menu.html', {"itemList": itemList, "restaurant": restaurant})

def open_edit_menu_item(request, restaurant_id, item_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    item = get_object_or_404(Item, id=item_id, restaurant=restaurant)
    return render(request, "delivery/edit_menu_item.html", {"restaurant": restaurant, "item": item})

def edit_menu_item(request, restaurant_id, item_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    item = get_object_or_404(Item, id=item_id, restaurant=restaurant)
    if request.method == "POST":
        name = request.POST.get("name")
        picture = request.POST.get("picture")
        description = request.POST.get("description")
        price = request.POST.get("price")
        vegetarian = request.POST.get("vegetarian") == "on"

        if Item.objects.filter(restaurant=restaurant, name=name).exclude(id=item.id).exists():
            return HttpResponse("Duplicate item name for this restaurant!")

        item.name = name
        if picture:
            item.picture = picture
        item.description = description
        item.price = float(price)
        item.vegetarian = vegetarian
        item.save()

    itemList = restaurant.items.all()
    return render(request, "delivery/update_menu.html", {"itemList": itemList, "restaurant": restaurant})

def delete_menu_item(request, restaurant_id, item_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    item = get_object_or_404(Item, id=item_id, restaurant=restaurant)
    item.delete()
    itemList = restaurant.items.all()
    return render(request, "delivery/update_menu.html", {"itemList": itemList, "restaurant": restaurant})

def view_menu(request,restaurant_id,username):
    restaurant = Restaurant.objects.get(id = restaurant_id)
    itemList = restaurant.items.all()
    #itemList = Item.objects.all()
    return render(request, 'delivery/customer_menu.html', {"itemList" : itemList, "restaurant" : restaurant, "username" : username})


def add_to_cart(request,item_id,username):
    item = Item.objects.get(id = item_id)
    customer = Customer.objects.get(username = username)

    cart, created = Cart.objects.get_or_create(customer = customer)

    cart.items.add(item)
    messages.success(request, "Item added to cart!")
    return redirect('view_menu', item.restaurant.id, username)

def show_cart(request, username):
    customer = Customer.objects.get(username = username)
    cart = Cart.objects.filter(customer=customer).first()
    items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0
    
    return render(request, 'delivery/show_cart.html',{"itemList" : items, "total_price" : total_price, "username":username})

def checkout(request, username):
    # Fetch customer and their cart
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()
    cart_items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    if total_price == 0:
        return render(request, 'delivery/checkout.html', {
            'username': username,
            'error': 'Your cart is empty!',
        })

    
    #initialising razorpay
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    client.session.trust_env = False
    #create razorpay order
    order_data = {
        'amount': int(total_price * 100),
        'currency': 'INR',
        'payment_capture': '1',
    }
    try:
        order = client.order.create(data=order_data)
    except Exception:
        return render(request, 'delivery/checkout.html', {
            'username': username,
            'cart_items': cart_items,
            'total_price': total_price,
            'error' : "Payment service is currently unreachable. Please check your internet/proxy settings and try again.",
    })

    return render(request, 'delivery/checkout.html', {
         'username': username,
        'cart_items': cart_items,
        'total_price': total_price,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'order_id': order['id'],  # Razorpay order ID
        'amount_paise': order_data['amount'],
    })
    



def orders(request, username):
    customer = get_object_or_404(Customer, username=username)
    cart = Cart.objects.filter(customer=customer).first()

    # Fetch cart items and total price before clearing the cart
    cart_items = cart.items.all() if cart else []
    total_price = cart.total_price() if cart else 0

    # Clear the cart after fetching its details
    if cart:
        cart.items.clear()

    return render(request, 'delivery/orders.html', {
        'username': username,
        'customer': customer,
        'cart_items': cart_items,
        'total_price': total_price,
    })
