from rest_framework import permissions
from rest_framework.generics import (
    CreateAPIView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import Http404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from utils.jwt_token import token_decoder
from django.core.mail import EmailMessage
from utils.email import EmailThread
from utils.jwt_token import token_generator
from .serializers import (
    RegisterSerializer,
    ResendEmailVerificationSerializer,
    ResetPasswordSerializer,
    SetPasswordSerializer,
)

from django.conf import settings
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token


# Get the user from active model
User = get_user_model()


class RegisterAPIView(CreateAPIView):
    """Register a new user"""

    model = User
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class EmailVerificationAPIView(APIView):
    """Confirm users email"""

    def get(self, request, token):
        # Decode the token to get the user id
        user_id = token_decoder(token)
        # Attempt to retrieve the user and activate the account
        try:
            user = get_object_or_404(User, pk=user_id)
            if user.is_verified:
                return Response(
                    {"message": "You are already verified"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.is_active = True
            user.is_verified = True
            user.save()
            return Response(
                {"message": "Account activated successfully!"},
                status=status.HTTP_200_OK,
            )
        except Http404:
            return Response(
                {"error": "Activation link is invalid!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except TypeError:
            return Response(user_id)

class ResendEmailVerificationAPIView(APIView):
    """Resend a verification email to user"""

    permission_classes = [permissions.AllowAny]
    serializer_class = ResendEmailVerificationSerializer

    def post(self, request):
        serializer = ResendEmailVerificationSerializer(data=request.data)
        if serializer.is_valid():
            # Get user from serilizer validate method
            user = serializer.validated_data["user"]
            # Generate a jwt token for resend confirm email
            token = token_generator(user)
            # Resending confirm email token
            FRONTEND_URL = "https://todo-frontend-m4yu.onrender.com"

            confirm_url = f"{FRONTEND_URL}/auth/verified/{token['access']}"
            msg = f"For confirm email click on: {confirm_url}"
            email_obj = EmailMessage("Confirm email", msg, to=[user.email])
            EmailThread(email_obj).start()
            return Response(
                {"message": "The activation email has been sent again successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordAPIView(APIView):
    """Reset user password"""

    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user: User = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"error": "User does not exist!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Generate a jwt token for reset password
            token = token_generator(user)
            # Sending reset password email token
            # set_password_url = self.request.build_absolute_uri(
            #     reverse("set_password", kwargs={"token": token["access"]})
            # )
            FRONTEND_URL = "https://todo-frontend-m4yu.onrender.com"

            confirm_url = f"{FRONTEND_URL}/auth/setpassword/{token['access']}"
        
            msg = f"for reset password click on: {confirm_url}"
            email_obj = EmailMessage("Set password", msg, to=[user.email])
            # Sending email with threading
            EmailThread(email_obj).start()
            return Response(
                {"message: Reset password email has been sent!"},
                status=status.HTTP_200_OK,
            )

        return Response("")


class SetPasswordAPIView(APIView):
    """Set user password"""

    permission_classes = [permissions.AllowAny]
    serializer_class = SetPasswordSerializer

    def post(self, request, token):
        serializer = SetPasswordSerializer(data=request.data)
        # Decode the token to get the user id
        user_id = token_decoder(token)

        try:
            user = get_object_or_404(User, pk=user_id)
        except Http404:
            return Response(
                {"error": "Activation link is invalid!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Token is not valid or expired
        except TypeError:
            return Response(user_id)

        if serializer.is_valid():
            new_password = serializer.validated_data["new_password"]
            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Your password has been changed successfully!"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
   
class LogoutView(APIView):
    # permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            # Get refresh token from the cookie instead of request.data
            refresh_token = request.COOKIES.get("refresh_token")
            if not refresh_token:
                return Response({"error": "No refresh token in cookies"}, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the token
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Create response and delete cookie
            response = Response({"message": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie("refresh_token")
            return response

        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        data = response.data

        # Extract refresh token
        refresh_token = data.get("refresh")
        access_token = data.get("access")
        
        # Put refresh token in cookie (HttpOnly so JS can't read it)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,   # ❌ set True in production (with HTTPS)
            samesite="None",     # ✅ must be None for cross-site cookies
            path="/"
        )
        
        del data["refresh"]

        return response
    
    
class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh = request.data.get("refresh") or request.COOKIES.get("refresh_token")

        if not refresh:
            return Response({"error": "No refresh token provided"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={"refresh": refresh})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class GoogleAuth(APIView):
    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"error": "Token not provided", "status": False}, status=status.HTTP_400_BAD_REQUEST)

        try:
            id_info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_OAUTH_CLIENT_ID
            )

            email = id_info.get("email")
            first_name = id_info.get("given_name", "")
            last_name = id_info.get("family_name", "")
            profile_pic_url = id_info.get("picture", "")

            user, created = User.objects.get_or_create(email=email)
            if created:
                user.set_unusable_password()
                user.first_name = first_name
                user.last_name = last_name
                user.username = first_name
                user.registration_method = "google"
                user.is_active = True
                user.is_verified = True
                user.save()
            else:
                if user.registration_method != "google":
                    return Response({
                        "error": "User needs to sign in through email",
                        "status": False
                    }, status=status.HTTP_403_FORBIDDEN)

            # create tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # build response
            response = Response({
                "tokens": {
                    "access": access_token,
                    "refresh": str(refresh),
                },
                "status": True
            }, status=status.HTTP_200_OK)

            # set secure HTTP-only cookie
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=True,   # True in production
                samesite="None",
                path="/"
            )
            return response

        except ValueError:
            return Response({"error": "Invalid token", "status": False}, status=status.HTTP_400_BAD_REQUEST)
