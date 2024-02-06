from django import views
from django.contrib.auth.models import User
from django.shortcuts import redirect, render ,HttpResponse, get_object_or_404 
from django.views import View
from django.contrib import messages
from .models import Address, Collection, Product, Customer, Cart ,CartItem, Order,OrderItem
from .forms import CustomerRegistrationForm ,AddAddressForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from decimal import *
# # Create your views here.


@login_required()
def product_list(request):
    customer=Customer.objects.filter(user=request.user).exists()    
    if customer:
        customer=Customer.objects.get(user=request.user)
    else:
        Customer.objects.create(user=request.user,phone="+91")
        cartItems=0

    cart=Cart.objects.filter(customer=customer).exists()
    if cart:
        cart=Cart.objects.get(customer=customer)
    else:    
        if request.user.is_authenticated:
            customer=Customer.objects.get(user=request.user)
            reg=Cart()
            reg.customer=customer
            reg.save()
        else:
            reg=Cart()
            reg.save() 
    
    cart=Cart.objects.get(customer=customer)
    cartItems=CartItem.objects.filter(cart=cart).count()
    products=Product.objects.order_by('title')
    products=list(products)
    data={
        "products":products,
        "cartCount":cartItems
    }

    return render(request , "shop.html",data)
    # return HttpResponse(list(querySet))


# def create_product(request):
#     if request.method == "POST":
#         data=request.POST
#         print(data)
#         return HttpResponse("done")

@login_required
def product_detail(request, id):
    
    product=Product.objects.get(pk=id)
    user=request.user
    customer=Customer.objects.get(user=user)
    cart=Cart.objects.get(customer=customer)
    cartItems=CartItem.objects.filter(cart=cart).count()
    context={
        "product":product,
        "cartCount":cartItems,
    }
    return render(request,"product_details.html", context)

def searchProduct(request):
    search_term=request.POST.get("search")
    products=Product.objects.filter(title__contains=search_term)
    user=request.user
    customer=Customer.objects.get(user=user)
    cart=Cart.objects.get(customer=customer)
    cartItems=CartItem.objects.filter(cart=cart).count()
    return render(request, "search.html", {"products":products, "search_term":search_term,"cartCount":cartItems})


class customerRegistration(View):
    def get(self , request):
        if request.user.is_authenticated:
            return redirect('/')
        form= CustomerRegistrationForm()
        return render(request,"sign-up.html",{"form":form})
    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        emailCheck=form.data['email']
        if User.objects.filter(email=emailCheck).exists():
            messages.success(request,'email already exists!')
            return render(request,"sign-up.html", {"form":form})
        
        if form.is_valid():
            messages.success(request,'Congratulations!! Registered Successfully')
            form.save()
            first_name=form.cleaned_data["first_name"]
            last_name=form.cleaned_data["last_name"]
            username=form.cleaned_data["username"]
            password=form.cleaned_data["password1"]
            
        return render(request,"sign-up.html", {"form":form})

@login_required
def profile(request):
        

    if request.user.is_authenticated:
        user=request.user
        customer=Customer.objects.get(user=user)
        cart=Cart.objects.get(customer=customer)
        cartItems=CartItem.objects.filter(cart=cart).count()
    else:
        cartItems=0
    if request.method == "POST":
        phone=request.POST['phone']
        street=request.POST['street']
        city=request.POST['city']
        country=request.POST['country']
        addUpd=Customer.objects.filter(user=request.user)
        addUpd.update(phone=phone)
        Address.objects.update_or_create(customer=customer,street=street,city=city,country=country)
        return redirect('profile')

    address=Address.objects.filter(customer=customer).first() 
       
    orders=Order.objects.filter(customer=customer).order_by("-placed_at")
    
    
    return render(request, "profile.html",{"customer":customer,"address":address,'orders':orders,"cartCount":cartItems})

def category(request,id):
    category_products=Product.objects.select_related("collection").filter(collection=id).order_by('title')
    if request.user.is_authenticated:
        user=request.user
        customer=Customer.objects.get(user=user)
        cart=Cart.objects.get(customer=customer)
        cartItems=CartItem.objects.filter(cart=cart).count()
    else:
        cartItems=0
    return render(request , "category_products.html",{"products": category_products,"category_id":id,"cartCount":cartItems})

class addressBook(View):
    def get(self,request):
        form=AddAddressForm()
        add=Address.objects.filter(customer=Customer.objects.get(user=request.user) )
        return render(request,'address_book.html',{'form':form ,'add':add})

    def post(self,request):
        form=AddAddressForm(request.POST)
        customer=Customer.objects.get(user=request.user)
        if form.is_valid():
            street=form.cleaned_data['street']
            city=form.cleaned_data['city']
            # reg=Customer(customer=user,street=street,city=city)
            reg= Address()
            reg.street=street
            reg.city=city
            reg.customer= customer
            reg.save()
            messages.success(request,' Address added successfully!')
        add=Address.objects.filter(customer=customer )
        return render(request,'address_book.html',{'form':form ,'add':add})


def createCart(request):
    if request.user.is_authenticated:
        customer=Customer.objects.get(user=request.user)
        reg=Cart()
        reg.customer=customer
        reg.save()
        return HttpResponse(reg.id)
    else:
        reg=Cart()
        reg.save()
        return HttpResponse(reg.id)
@csrf_exempt
def addToCart(request):
    if request.method =="POST":
        
        # cartId= request.POST.get('cartId')
        # productId= request.POST.get('productId')
        # quantity= request.POST.get('quantity')
        # cart=Cart.objects.get(pk=cartId)
        productId = request.POST['productid']
        quantity = request.POST['quantity']
        customer=Customer.objects.get(user=request.user)
        cart = Cart.objects.get(customer=customer)
        if request.user.is_authenticated:
            customer=Customer.objects.get(user=request.user)
            cart.customer=customer
            cart.save()
        
        product=Product.objects.get(pk=productId)
        CartItem.objects.create(cart=cart,product=product,quantity=quantity)
        messages.success(request,"Product Addred to Cart!")
        return redirect('/product/'+str(productId))
    return HttpResponse("Product Added to Cart!")

def cart(request):
    user=request.user
    customer=Customer.objects.get(user=user)
    cart=Cart.objects.get(customer=customer)
    cartItems=CartItem.objects.filter(cart=cart)
    cartIt=CartItem.objects.filter(cart=cart).count()
    cartItems=list(cartItems)
    if request.method == "POST":
        CartItem.objects.filter(pk=request.POST['cartid']).delete()
        return redirect('cart')
    
    subTotal=0
    for x in cartItems:
        y=x.get_total_price()
        subTotal=subTotal+y
    return render(request,'cart.html',{"items":cartItems, "subTotal":subTotal,"cartCount":cartIt})

@login_required
def checkout(request):
    if request.user.is_authenticated:
        user=request.user
        customer=Customer.objects.get(user=user)
        cart=Cart.objects.get(customer=customer)
        cartItems=CartItem.objects.filter(cart=cart)
        cartItems=list(cartItems)
        cartIt=CartItem.objects.filter(cart=cart).count()

        getcontext().prec = 2
        subTotal=Decimal(0)
        for x in cartItems:
            y=x.get_total_price()
            subTotal=subTotal+y
        add=Address.objects.filter(customer=customer).first()
        return render(request, "checkout.html",{"items":cartItems, "subTotal":subTotal , "add":add, "cartCount":cartIt})
    else:
        return redirect('login')

def placeOrder(request):
        if request.user.is_authenticated:
            user=request.user
            customer=Customer.objects.get(user=user)
            cart=Cart.objects.get(customer=customer)
            cartItems=CartItem.objects.filter(cart=cart)

            order= Order()
            order.customer=customer
            order.save()

            for c in cartItems:
                OrderItem(order=order,product=c.product,quantity=c.quantity ,unit_price=c.product.unit_price).save()
                
            cart.delete()
            context= {
                "order_id":order.id,
            }
        return render(request,"order_placed.html",context)

def myOrders(request):
    if request.user.is_authenticated:
        user=request.user
        customer = Customer.objects.get(user=user)    
        orders=Order.objects.filter(customer=customer).order_by("-placed_at")
        add=Address.objects.filter(customer=customer).first()
        
        
    return render(request, "my_orders.html",{"orders":orders,"add":add})

def orderDetail(request,id):
    if request.user.is_authenticated:
        customer=Customer.objects.get(user=request.user)
        order=Order.objects.get(pk=id)
        
        order_items=OrderItem.objects.filter(order=order)
        orderItems=list(order_items)

        getcontext().prec = 2
        subTotal=Decimal(0)
        for x in orderItems:
            y=x.get_total_price()
            subTotal=subTotal+y
        add=Address.objects.filter(customer=customer).first()
        return render(request, "order_detail.html",{"items":orderItems, "subTotal":subTotal , "add":add})
    else:
        return redirect('login')
    # if request.user.is_authenticated:
    #     order=Order.objects.get(pk=id)
    #     order_items=OrderItem.objects.filter(order=order)

    #     return HttpResponse(order_items)


@login_required
def trackPage(request,id):
    order=Order.objects.get(pk=id) 
    
    orderPlaced = order.orderPlaced
    orderShipment = order.orderShipment
    outForDelivery = order.outForDelivery
    delivered = order.delivered
    context = {
        'order':order,
        'st1':orderPlaced,
        'st3':orderShipment,
        'st4':outForDelivery,
        'st5':delivered
    }
    return render(request,'track.html',context)
