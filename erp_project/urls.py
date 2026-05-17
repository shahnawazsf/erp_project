from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('hr/', include('hr.urls')),
    path('inventory/', include('inventory.urls')),
    path('finance/', include('finance.urls')),
    path('sales/', include('sales.urls')),
    path('purchasing/', include('purchasing.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
