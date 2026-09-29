from .views import es_cliente

def access_role(request):
    return {"is_customer": es_cliente(request.user)}
