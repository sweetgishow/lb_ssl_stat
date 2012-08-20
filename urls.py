
from django.conf.urls.defaults import *
#from mysite.blog.views import archive
from mysite.lb_ssl_stat.views import *

urlpatterns = patterns('',
    url(r'^$', summary),
)
