from django.urls import path
from .serializers import SignUpSerializer
from .views import CreateUserView, VerifyUserView, GetNewVerificationCodeView

urlpatterns = [
    path('signup/', CreateUserView.as_view(), name='signup'),
    path('newverify/', GetNewVerificationCodeView.as_view(), name='newverify'),
    path('verify/', VerifyUserView.as_view(), name='verify'),
]