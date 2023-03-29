from reportlab.platypus import (SimpleDocTemplate, PageBreak, Image, Spacer,
Paragraph, Table,)
from pysnmp.hlapi import *
from reportlab.pdfgen import canvas
import time

def consultaSNMP(comunidad,host,oid, puerto):
    errorIndication, errorStatus, errorIndex, varBinds = next(
        getCmd(SnmpEngine(),
               CommunityData(comunidad),
               UdpTransportTarget((host, int(puerto))),
               ContextData(),
               ObjectType(ObjectIdentity(oid))))

    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
    else:
        for varBind in varBinds:
            varB=(' = '.join([x.prettyPrint() for x in varBind]))
            resultado= varB.split("=")[1]
    return resultado

def agregarDispositivo():
    print()
    comunidad = input("Comunidad: ")
    version = input("Version: ")
    puerto = input("Puerto: ")
    ip = input("IP: ")

    with open("bdd.txt", "a") as file:
        file.write(comunidad + " " + version + " " + puerto + " " + ip + "\n")

def change():
    print()
    i = 1
    print("Dispositivos: ")
    with open("bdd.txt", "r") as file:
        datos = file.readlines()

    with open("bdd.txt", "r") as file:
        for line in file:
            print(str(i) + "\t" + line)
            i = i + 1

    borrar = int(input("Dispositivo a modificar: "))
    i = 1
    print()
    comunidad = input("Comunidad: ")
    version = input("Version: ")
    puerto = input("Puerto: ")
    ip = input("IP: ")
    print()

    with open("bdd.txt", "w") as file:
        for line in datos:
            if i != borrar:
                file.write(line)
            else:
                file.write(comunidad + " " + version + " " + puerto + " " + ip + "\n")
            i = i + 1

def delete():
    print()
    i = 1
    
    with open("bdd.txt", "r") as file:
        datos = file.readlines()
    print("Dispositivos: ")
    with open("bdd.txt", "r") as file:
        for line in file:
            print(str(i) + "\t" + line)
            i = i + 1
    
    borrar = int(input("Dispositivo a borrar: "))
    i = 1
    with open("bdd.txt", "w") as file:
        for line in datos:
            if i != borrar:
                file.write(line)
            i = i + 1

def report():
    print()
    
    with open("bdd.txt", "r") as file:
        devices = file.readlines()

    i = 1
    print("Dispositivos: ")
    with open("bdd.txt", "r") as file:
        for line in file:
            print(str(i) + "\t" + line)
            i = i + 1
    numero = int(input("Dispositivo a generar reporte: ")) - 1
    datos = devices[numero].split()

    comunidad = datos[0]
    version = datos[1]
    puerto = datos[2]
    ip = datos[3]

    datosSNMP = consultaSNMP(comunidad, ip, "1.3.6.1.2.1.1.1.0", puerto)
    os = "hola"
    if datosSNMP.find("Linux") == 1:
        os = datosSNMP.split()[0]
    else:
        os = datosSNMP.split()[12]
    
    name = consultaSNMP(comunidad, ip, "1.3.6.1.2.1.1.5.0", puerto)
    contact = consultaSNMP(comunidad, ip, "1.3.6.1.2.1.1.4.0", puerto)
    ubi = consultaSNMP(comunidad, ip, "1.3.6.1.2.1.1.6.0", puerto)
    numInter = consultaSNMP(comunidad, ip, "1.3.6.1.2.1.2.1.0", puerto)

    i = 1
    interfaces = []
    while i <= 6:
        interfaz = consultaSNMP(comunidad, ip, "1.3.6.1.2.1.2.2.1.7." + str(i), puerto)
        interfaces.append(interfaz)
        # print(str(i))
        i = i + 1
    #print(interfaces)

    timestr = time.strftime("%Y%m%d-%H%M%S")

    output = canvas.Canvas("SNMPreport" + timestr + ".pdf")
    output.setTitle("SNMPReport")
    output.drawString(50, 800, "Administración de Servicios en Red")
    output.drawString(50, 775, "Práctica 1")
    output.drawString(50, 750, "Baldovinos Gutiérrez Kevin 4CM14")
    
    output.drawString(75, 700, "Nombre del dispositivo: " + name)
    output.drawString(75, 725, "S.O.: " + os)
    output.drawString(75, 675, "Info. de contacto: " + contact)
    output.drawString(75, 650, "Ubicacion: " + ubi)
    output.drawString(75, 625, "# de interfaces: " + numInter)

    i = 1
    matriz = [["INTERFACE", "STATUS"]]
    while i <= 6:
        if os.find("Linux") != -1:
            descrInterfaz = consultaSNMP(comunidad, ip, "1.3.6.1.2.1.2.2.1.2." + str(i), puerto)
        else:
            res = consultaSNMP(comunidad, ip, "1.3.6.1.2.1.2.2.1.2." + str(i), puerto)[3:]
            descrInterfaz = bytes.fromhex(res).decode('utf-8')

        estadoInterfaz = consultaSNMP(comunidad, ip, "1.3.6.1.2.1.2.2.1.7." + str(i), puerto)

        if estadoInterfaz == " 1":
            matriz.append([descrInterfaz, "UP"])
        elif estadoInterfaz == " 2":
            matriz.append([descrInterfaz, "DOWN"])
        else:
            matriz.append([descrInterfaz, "TESTING"])
        i = i + 1

    width = 200
    height = 400
    x = 50
    y = 450
    f = Table(matriz)
    f.wrapOn(output, width, height)
    f.drawOn(output, x, y)
    
    output.save()


print("*************************************************")
print("\tSistema de administración de red")
print("\tPractica 1 - Adquisición de Información")
print("\tBaldovinos Gutiérrez Kevin   4CM14   2020630037")
print("#*************************************************")

option = 1

while option != 0:
    print("1. Agregar dispositivo")
    print("2. Cambiar informacion de dispositivo")
    print("3. Eliminar informacion de dipostivo")
    print("4. Generar reporte")
    print()
    print("0. Salir")
    print()
    option = int(input("Acción a realizar: "))
    if option == 1:
        agregarDispositivo()
    elif option == 2:
        change()
    elif option == 3:
        delete()
    elif option == 4:
        report()
    elif option == 0:
        print("Adios")
    else:
        print("not valid")
    print()