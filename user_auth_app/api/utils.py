from rest_framework.response import Response
from rest_framework import status

def _check_user_permission( request_user_id, profile_id):
   if request_user_id != profile_id:
       return Response(
           {"error": "You can only edit your own profile."},
           status=status.HTTP_403_FORBIDDEN
       )
   return None

def _update_user_data(user, data):
   if 'first_name' in data:
       user.first_name = data['first_name']
   if 'last_name' in data:
       user.last_name = data['last_name']
   if 'email' in data:
       user.email = data['email']
   user.save()

def _clean_profile_data(data):
   profile_data = data.copy()
   profile_data.pop('first_name', None)
   profile_data.pop('last_name', None)
   profile_data.pop('email', None)
   return profile_data

def _handle_profile_update(profile, serializer_class, data):
   serializer = serializer_class(profile, data=data, partial=True)
   if serializer.is_valid():
       serializer.save()
       return Response(serializer.data, status=status.HTTP_200_OK)
   return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)