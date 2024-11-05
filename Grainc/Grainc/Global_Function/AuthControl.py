import jwt
from django.conf import settings
from AuthUser.models import ServiceUser
from django.http import JsonResponse
from rest_framework.response import Response


def decodeUserToken(auth_header):
    # Extract the access token from the Authorization header
    token = auth_header.split(' ')[1]
    # Decode the token using the secret key
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    # Extract user_id from the decoded token
    user_id = decoded.get('id')

    return user_id

    
def getUserInformation(request):
    auth_header = request.headers.get('Authorization')
    user = None
    if (auth_header):
        try:
            user_id = decodeUserToken(auth_header)
            user = ServiceUser.objects.get(id=user_id)
            return (user)
        except ServiceUser.DoesNotExist:
            return JsonResponse({'status': 'user does not exist'}, status=404)
        except jwt.ExpiredSignatureError:
            return Response({'status': 'Token expired'}, status=401)
        except jwt.InvalidTokenError:
            return Response({'status': 'Invalid token'}, status=401)

