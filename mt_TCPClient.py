import socket
import json
import copy
import time
import threading
import select


def mostrarTablero(tablero):
    print("Tablero actual")
    for n_fila in range(len(tablero)):
        for valor in tablero[n_fila]:
            print("\t", valor, end=" ")
        print()

def actualizarTablero(tablero,casilla,cas_actual):
    for n_fila in range(len(tablero)):
        for valor in range(len(tablero[n_fila])):
            if tablero[n_fila][valor]==casilla:
                tablero[n_fila][valor]=cas_actual
    return tablero

def mostrarTableroTemporal(tablero_t,casilla1,casilla2,cas1_actual,cas2_actual):
    print()
    for n_fila in range(len(tablero_t)):
        for valor in range(len(tablero_t[n_fila])):
            if tablero_t[n_fila][valor]==casilla1:
                print("\t",cas1_actual, end=" ")
                #tablero_t[n_fila][valor]=cas1_actual
            elif tablero_t[n_fila][valor]==casilla2:
                print("\t",cas2_actual, end=" ")
                #tablero_t[n_fila][valor]=cas2_actual
            else:
                print("\t",tablero_t[n_fila][valor], end=" ")
        print()

def tableroCompleto(tablero_cpy,tablero):
    for n_fila in range(len(tablero_cpy)):
        for valor in range(len(tablero_cpy[n_fila])):
            if tablero_cpy[n_fila][valor]==tablero[n_fila][valor]:
                return False

    return True

print("*** Bienvenido ***")
HOST = "127.0.0.1"#input("Ingrese la dirección a la que se quiere conectar: ")
PORT = 12345 #int(input("Ingrese el puerto destino: "))
buffer_size = 1024


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
    TCPClientSocket.connect((HOST, PORT))
    primer_msg = str(TCPClientSocket.recv(buffer_size), 'utf-8')
    print(primer_msg)
    respuesta = input("Respuesta:")
    TCPClientSocket.sendall(respuesta.encode())
    print("Esperando tablero...")
    tablero = TCPClientSocket.recv(buffer_size)
    tablero = json.loads(tablero.decode())
    tablero_cpy = copy.deepcopy(tablero)
    mostrarTablero(tablero)
    id_jugador = str(TCPClientSocket.recv(buffer_size), 'utf-8')
    print("Soy {} en la partida".format(id_jugador))
    while tableroCompleto(tablero_cpy,tablero)==False:
        try:
            ready = select.select([TCPClientSocket], [], [], 8)
            if ready[0]:
                jugador_actual = str(TCPClientSocket.recv(buffer_size), 'utf-8')
                print("se espera  a {}".format(jugador_actual))

                if id_jugador==jugador_actual:
                    print("\n\nIngresa las casillas a destapar (lo conforman una letra MAYUSCULA y un numero)")
                    casilla1 = str(input("Casilla 1 a voltear:"))
                    casilla2 = str(input("Casilla 2 a voltear:"))

                    #Enviando casillas a verificar
                    TCPClientSocket.sendall(casilla1.encode())   #enviando casilla1
                    TCPClientSocket.sendall(casilla2.encode())
                    #Recibo mis actualizaciones
                    casilla1 = str(TCPClientSocket.recv(buffer_size), 'utf-8')
                    casilla2 = str(TCPClientSocket.recv(buffer_size), 'utf-8')
                    cas1_actual = str(TCPClientSocket.recv(buffer_size), 'utf-8')
                    cas2_actual = str(TCPClientSocket.recv(buffer_size), 'utf-8')
                    print(cas1_actual)
                    print(cas2_actual)

                    if(cas1_actual==cas2_actual):
                        print("\nTuviste un par correcto\n")
                        tablero = actualizarTablero(tablero,casilla1,cas1_actual)
                        tablero = actualizarTablero(tablero,casilla2,cas2_actual)
                        mostrarTablero(tablero)

                    else:
                        print("\nNO tuviste un par correcto")
                        mostrarTableroTemporal(tablero,casilla1,casilla2,cas1_actual,cas2_actual)

        except Exception as e:
            print(e)

        print("Espero actualizaciones de otros jugadores")
        casilla1 = str(TCPClientSocket.recv(buffer_size), 'utf-8')
        casilla2 = str(TCPClientSocket.recv(buffer_size), 'utf-8')
        cas1_actual = str(TCPClientSocket.recv(buffer_size), 'utf-8')
        cas2_actual = str(TCPClientSocket.recv(buffer_size), 'utf-8')
        print(cas1_actual)
        print(cas2_actual)
        if(cas1_actual==cas2_actual):
            print("\nHubo un par correcto\n")
            tablero = actualizarTablero(tablero,casilla1,cas1_actual)
            tablero = actualizarTablero(tablero,casilla2,cas2_actual)
            mostrarTablero(tablero)

        else:
            print("\nNO hubo un par correcto")
            mostrarTableroTemporal(tablero,casilla1,casilla2,cas1_actual,cas2_actual)
    print("\nJUEGO TERMINADO")
    

        


