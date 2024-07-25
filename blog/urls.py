from django.urls import path
from . import views

# urlpatterns = patterns('',
#    url(r'^adminurl/filebrowser/', include(site.urls)),
# )

urlpatterns = [
    path('', views.homepage, name = 'homepage'),
     path('instructions', views.instructions, name = 'instructions'), 
    path('configure_merge', views.homepage, name = 'configure_merge'), 
    path('download/<str:table>/', views.download_merged_dataset, name='download_merged_dataset')
]