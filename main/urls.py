from django.conf.urls.static import static
from django.urls import path

from InventoryManagement import settings
from . import views

urlpatterns = [
                  path("", views.index, name='index'),
                  path("products", views.index, name='products'),
                  path("editProduct", views.editProduct, name='editProduct'),
                  path("addProduct", views.addProduct, name='addProduct'),
                  path("useProduct", views.useProduct, name='useProduct'),
                  path("register", views.register_request, name="register"),
                  path("login", views.login_request, name="login"),
                  path("logout", views.logout_request, name="logout"),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
