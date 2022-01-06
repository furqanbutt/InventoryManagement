import datetime

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db import connection
from django.db.models import Sum, Count
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
        productId = request.POST["productId"]
        product = Product.objects.get(id=productId)
        product.productDescription = request.POST["productDescription"]
        product.quantity = request.POST["quantity"]
        product.location = request.POST["location"]
        print(request.FILES.get("image"))
        print(request.POST.get("image"))
        if len(request.FILES) > 0:
            print("File is submitted")
            product.image = request.FILES.get("image")
        product.save()
        return redirect("/")

    if request.GET:
        productId = request.GET["productId"]
        product = Product.objects.get(id=productId)
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
        productLocation = request.POST["location"]
        product = Product.objects.filter(productSku__iexact=productSku,
                                         location__iexact=productLocation).first()
        withDrawalQuantity = request.POST["quantity"]
        typeOfUse = request.POST["typeOfUse"]
        if int(product.quantity) > int(withDrawalQuantity):
            transaction = Transaction.objects.create(product=product, quantityUsed=withDrawalQuantity, type=typeOfUse)
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
        productSkuAndLocation = str(request.GET["productSkuAndLocation"]).split(",")
        productSku = productSkuAndLocation[0]
        productLocation = ""
        if len(productSkuAndLocation) > 1:
            productLocation = productSkuAndLocation[1]

        print(productSku + "," + productLocation)

        if (productLocation):
            product = Product.objects.filter(productSku__iexact=productSku,
                                             location__iexact=productLocation).first()
        else:
            return render(request, 'useProduct.html',
                          {"msg": "Location of product missing. Please use the format [SKU,LOCATION]",
                           "products": products})

        if len(products) > 0:
            return render(request, 'useProduct.html', {"product": product, "products": products})
        else:
            return render(request, 'useProduct.html', {"msg": "Unable to fetch product", "products": products})

    return render(request, "useProduct.html", {"products": products})


def dashboard(request):
    if not request.user.is_authenticated:
        print("user not authenticated")
        return HttpResponseRedirect(reverse("login"))
    totalProductsUsed = Transaction.objects.all().aggregate(Sum("quantityUsed"))["quantityUsed__sum"]
    productsUsedLast30Days = \
        Transaction.objects.filter(dateUsed__gt=datetime.datetime.today() - datetime.timedelta(days=30)).aggregate(
            Sum("quantityUsed"))["quantityUsed__sum"]
    averageProductsUsedLast30Days = round(productsUsedLast30Days / 30)

    productsUsedLast7Days = \
        Transaction.objects.filter(dateUsed__gt=datetime.datetime.today() - datetime.timedelta(days=7)).aggregate(
            Sum("quantityUsed"))["quantityUsed__sum"]

    transactions = Transaction.objects.all().order_by("-dateUsed")
    with connection.cursor() as cursor:
        productUsageList = list(cursor.execute("""select sum(main_transaction.quantityUsed) as totalUsed,productSku
        from main_transaction inner
        join
        main_product
        mp
        on
        mp.id = main_transaction.product_id
        group
        by
        main_transaction.product_id
        order
        by
        totalUsed
        DESC;
    
        """))
        graphList = list()
        print(productUsageList)
        for productUsage in productUsageList:
            tempList = list()
            totalQuantityOfProduct = Product.objects.filter(productSku=productUsage[1]).first().quantity
            percentageUsed = (float(productUsage[0]) / totalQuantityOfProduct) * 100
            tempList.append(productUsage[1])
            tempList.append(str(percentageUsed))
            tempList.append(str(100 - percentageUsed))
            print(tempList)
            graphList.append(tempList)
            graphList.sort(key=lambda x: x[1])

    return render(request, "dashboard.html",
                  {"transactions": transactions, "averageProductsUsedLast30Days": averageProductsUsedLast30Days,
                   "productsUsedLast7Days": productsUsedLast7Days, "productsUsedLast30Days": productsUsedLast30Days,
                   "totalProductsUsed": totalProductsUsed,
                   "graphList": graphList})


def register_request(request):
    # if request.user.is_authenticated:
    #     return redirect("/")
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("login"))
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


def reports(request):
    # products = Product.objects.annotate(total=Sum("productSku")).values("productSku", "productDescription",
    #                                   "dateAdded","total")
    with connection.cursor() as cursor:
        products = list(
            cursor.execute(
                "select sum(quantity) as total,image,productSku,productDescription,dateAdded from main_product group by main_product.productSku order by dateAdded DESC"))
        print(products)
        return render(request, "reports.html", context={"products": products})


def qrGenerator(request):
    return render(request, "qrGenerator.html")


def deleteProduct(request):
    if not request.user.is_authenticated:
        print("user not authenticated")
        return HttpResponseRedirect(reverse("login"))
    if not request.user.is_superuser:
        return HttpResponseRedirect(reverse("login"))
    if request.GET:
        productId = request.GET["productId"]
        productSKU = request.GET["productSKU"]
        product = Product.objects.get(id=productId, productSku=productSKU)
        if product:
            product.delete()
        return HttpResponseRedirect(reverse("products"))


def weeklyUsageReport(request):
    productsUsedLast7Days = \
        Transaction.objects.filter(dateUsed__gt=datetime.datetime.today() - datetime.timedelta(days=7)).order_by("type")
    print(productsUsedLast7Days)
    return render(request, "weeklyUsageReport.html", context={"transactions": productsUsedLast7Days})
