import requests
from django.contrib.auth.models import Permission, Group, User

"""
def crearAdministrador():
   
    admin_username = input('Ingresa el nombre de usuario: ')
    admin_password = input('Ingresa la contraseña del administrador: ')
    admin_email = input('Ingresa el email del administrador: ')

    while True:
        response = requests.get(
            "https://isitarealemail.com/api/email/validate",
            params={'email': admin_email}
        )
    
        status = response.json()['status']
        if status == "valid":
            break
        else:
            admin_email = input("El email es invalido o no existe, vuelva a ingresarlo: ")
    
    admin = User.objects.create_user(username=admin_username, email=admin_email, password=admin_password)
    admin_group = Group.objects.create(name='Administrador')
    for permission in Permission.objects.all():
        admin_group.permissions.add(permission)
    admin.groups.add(admin_group) """
