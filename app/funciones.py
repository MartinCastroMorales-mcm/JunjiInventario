# valida que 'name' (el parametro que vendra desde la validacion en proveedor.py) sea igual a uno de los caracteres en char= de ser asi lo retorna
char = '<>"' "!#$%&/()=-.,"


def validarChar(name):
    # se recorre char y se almacena en i
    for i in char:
        if i == name:
            return i

#deberia ser un rut sin puntos y con guion
def validarRut(rut):
    rutGrupo = rut.split("-")
    if len(rutGrupo) != 2:
        return False
    num = rutGrupo[0]
    digVerificador = rutGrupo[1]
    try:
        num = int(num)
    except:
        return False
    mod = num % 11
    if digVerificador == "k":
        digVerificador = 10
    else:
        try:
            digVerificador = int(digVerificador)
        except:
            return False

    if mod == digVerificador:
        return True
    else:
        return False

def getPerPage():
    return 2