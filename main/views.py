from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.core.mail import send_mail

# Create your views here.
from django.http import HttpResponseRedirect
from django.urls import reverse

from main.forms import NewUserForm
from main.models import Product, Transaction


def index(request):
    if not request.user.is_authenticated:
        print("user not authenticated")
        return redirect("/login")
    if not request.user.is_superuser:
        print("user not authorized")
        return redirect("/login")
    products = Product.objects.all()
    return render(request, 'products.html', {"products": products})


def editProduct(request):
    if not request.user.is_authenticated:
        print("user not authenticated")
        return HttpResponseRedirect(reverse("login"))
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("login"))
    if request.POST:
        productSku = request.POST["productSku"]
        product = Product.objects.get(productSku=productSku)
        product.productDescription = request.POST["productDescription"]
        product.quantity = request.POST["quantity"]
        product.location = request.POST["location"]
        product.save()
        return redirect("/")

    if request.GET:
        productId = request.GET["productId"]
        product = Product.objects.get(productSku=productId)
        return render(request, 'editProduct.html', {"product": product})


def addProduct(request):
    if not request.user.is_authenticated:
        print("user not authenticated")
        return HttpResponseRedirect(reverse("login"))
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("login"))
    if request.POST:
        print("In AddProduct POST")

        productSku = request.POST["productSku"]
        productDescription = request.POST["productDescription"]
        quantity = request.POST["quantity"]
        location = request.POST["location"]
        image = request.FILES.get("image")
        print(request.FILES.get("image"))
        print(request.POST.get("image"))
        Product.objects.create(productSku=productSku, productDescription=productDescription,
                               quantity=quantity, location=location, image=image).save()

        return redirect("/")
    print("In AddProduct GEt")
    return render(request, 'addProduct.html')


def useProduct(request):
    if not request.user.is_authenticated:
        print("user not authenticated")
        return HttpResponseRedirect(reverse("login"))
    products = list(Product.objects.values_list('productSku', flat=True))
    print(products)
    if request.POST:
        productSku = request.POST["productSku"]
        product = Product.objects.get(productSku__iexact=productSku)
        withDrawalQuantity = request.POST["quantity"]
        if int(product.quantity) > int(withDrawalQuantity):
            transaction = Transaction.objects.create(product=product, quantityUsed=withDrawalQuantity)
            transaction.save()
            product.quantity = str(int(product.quantity) - int(withDrawalQuantity))
            product.save()
            if int(product.quantity) < 10:
                send_mail(
                    'Product [' + product.productSku + '] quantity dropped below 10',
                    'The product [' + product.productSku + '] is left with only ' + product.quantity + ' units.',
                    'InventoryManagement',
                    ['Eric_godoy@hotmail.com'],
                )
        return redirect("/")
    if request.GET:
        productSku = request.GET["productSku"]
        try:
            product = Product.objects.get(productSku__iexact=productSku)
            return render(request, 'useProduct.html', {"product": product, "products": products})
        except:
            return render(request, 'useProduct.html', {"msg": "Unable to fetch product", "products": products})

    return render(request, "useProduct.html", {"products": products})


def register_request(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # messages.success(request, "Registration successful.")
            if user.is_superuser:
                return redirect("/")
            else:
                return redirect("useProduct")
        # messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request, template_name="register.html", context={"register_form": form})


def login_request(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("products")
        else:
            return redirect("useProduct")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # messages.info(request, f"You are now logged in as {username}.")
                if user.is_superuser:
                    return redirect("/products")
                else:
                    return redirect("/useProduct")
            # else:
            # messages.error(request, "Invalid username or password.")
        # else:
        # messages.error(request, "Invalid username or password.")
    form = AuthenticationForm()
    return render(request=request, template_name="login.html", context={"login_form": form})


def logout_request(request):
    logout(request)
    # messages.info(request, "You have successfully logged out.")
    return redirect("/")
