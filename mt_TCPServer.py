import socket
import random
import copy
import string
import json
import time
import threading
import queue
import sys

def llenarMatriz(filas,columnas,nivel):
    tablero = []
    #se inicializa la matriz
    for inicializar in range(filas):
            tablero.append([0]*columnas)

    #se ingresan valores a la matriz
    for i in range(filas):
        for j in range(columnas):
            tablero[i][j] = nivel[i][j]
    return tablero

def llenarTabJuego(tablero):
    tab_juego = copy.deepcopy(tablero)
    for n_fila in range(len(tab_juego)):
        for valor in range(len(tab_juego[n_fila])):
            tab_juego[n_fila][valor]=string.ascii_uppercase[n_fila] + str(valor)
    return tab_juego

def mostrarTablero(tablero):
    for n_fila in range(len(tablero)):
        for valor in tablero[n_fila]:
            print("\t", valor, end=" ")
        print()

def tableroCompleto(tablero_juego,tablero_real):
    for n_fila in range(len(tablero_juego)):
        for valor in range(len(tablero_juego[n_fila])):
            if tablero_juego[n_fila][valor]!=tablero_real[n_fila][valor]:
                return False

    return True

def obtenerValor(tablero_real,tablero_juego,casilla):
    for n_fila in range(len(tablero_juego)):
        for valor in range(len(tablero_juego[n_fila])):
            if tablero_juego[n_fila][valor]==casilla:
                return tablero_real[n_fila][valor]

def checarPar(tablero_real,tablero_juego,casilla1,casilla2):    
    if(obtenerValor(tablero_real,tablero_juego,casilla1)==obtenerValor(tablero_real,tablero_juego,casilla2)):
        print(obtenerValor(tablero_real,tablero_juego,casilla1),obtenerValor(tablero_real,tablero_juego,casilla2))
        return True
        #mandar actualizacion del tablero
    else:
        return False

def actualizarTablero(tablero_real,tablero_juego,casilla):
    valor_real = obtenerValor(tablero_real,tablero_juego,casilla)
    for n_fila in range(len(tablero_juego)):
        for valor in range(len(tablero_juego[n_fila])):
            if tablero_juego[n_fila][valor]==casilla:
                tablero_juego[n_fila][valor]=valor_real
            #else:
                #tablero_juego = tablero_juego
    return tablero_juego

def nivelEscogido(nivel):
    if nivel==1:
        filas=4;columnas=4
        nivel_p = [['llave','mesa','mango','plata'],['mora','libro','dulce','globo'],
                ['llave','mesa','mango','plata'],['mora','libro','dulce','globo']]

        #se mezclan las opciones
        random.shuffle(nivel_p)
        for x in nivel_p:
            random.shuffle(x)

        tablero_real = llenarMatriz(filas,columnas,nivel_p)
        return tablero_real
    elif nivel==2:
        filas=6;columnas=6
        nivel_a = [['mono','azul','mar','vaca','negro','pato'],['menta','avion','rosa','gato','perro','pollo'],
                    ['coco','pluma','buho','fresa','flor','nube'],['mono','azul','mar','fresa','negro','pato'],
                    ['menta','avion','rosa','gato','perro','pollo'],['coco','pluma','buho','vaca','flor','nube']]

        #se mezclan las opciones
        random.shuffle(nivel_a)
        for z in nivel_a:
            random.shuffle(z)

        tablero_real = llenarMatriz(filas,columnas,nivel_a)
        return tablero_real

def accept_client(TCPServerSocket):
    while True:
        Client_conn, Client_addr = TCPServerSocket.accept()
        listaConexiones.append(Client_conn)
        #verifica si es el primer cliente en entrar, el decide que nivel se jugara
        if(listaConexiones.index(Client_conn)==0):
            Client_conn.sendall(str.encode("Escoge el nivel: \n1: Principiante\n2: Avanzado"))
            nivel = int(Client_conn.recv(buffer_size))  
            tablero_real = nivelEscogido(nivel)
            mostrarTablero(tablero_real)
        #los siguientes clientes solo reciben la notificación del nivel a jugar
        else:
            Client_conn.sendall(str.encode("Se jugara en el nivel {}, presione 1 para confirmar".format(nivel)))
            confirmar = int(Client_conn.recv(buffer_size))  

        #Crear un hilo independiente para cada cliente
        thread = threading.Thread( name="Jugador " + str(listaConexiones.index(Client_conn)),target=worker, args=(Client_conn,barrier,tablero_real,lock,q))
        # Establecer como hilo de demonio
        #thread.setDaemon(True)
        thread.start()

def worker(Client_conn,barrier,tablero_real,lock,q):
    #global actualizacion
#    global n_intentos
    tablero_juego = llenarTabJuego(tablero_real)
    bytesToSend = json.dumps(tablero_juego)
    cur_thread = threading.current_thread()
    Client_conn.sendall(bytesToSend.encode())
    print("Se envio tablero a {}".format(cur_thread.name))
    #Se manda su identificador de cada cliente
    Client_conn.sendall(str.encode(cur_thread.name))
    #se añade a la cola para jugar
    q.put(cur_thread.name)
    aux_q.append(cur_thread.name)
    barrier.wait()
    time.sleep(.5)
    while tableroCompleto(tablero_juego,tablero_real)==False:
        lock.acquire()
        if(aux_q[0]==cur_thread.name):
            jugador = q.get()
            Client_conn.sendall(str.encode(str(jugador))) 
            print("Esperando a {}".format(jugador))
            casilla1 = Client_conn.recv(buffer_size)#recibiendo casilla1
            casilla1 = casilla1.decode('utf-8')
            casilla2 = Client_conn.recv(buffer_size)#recibiendo casilla2
            casilla2 = casilla2.decode('utf-8')
            print("casilla1: {}, casilla2: {}".format(casilla1,casilla2))
            casilla1_real = obtenerValor(tablero_real,tablero_juego,casilla1)
            casilla2_real = obtenerValor(tablero_real,tablero_juego,casilla2)
            print("Real1: {}, Real2: {}".format(casilla1_real,casilla2_real))

            for conn in listaConexiones:
                conn.sendall(str.encode(casilla1))
                conn.sendall(str.encode(casilla2)) 
            for conn in listaConexiones:
                conn.sendall(str.encode(casilla1_real))
                conn.sendall(str.encode(casilla2_real)) 

            if(checarPar(tablero_real,tablero_juego,casilla1,casilla2)):
                #se actualuza el tablero
                tablero_juego = actualizarTablero(tablero_real,tablero_juego,casilla1)
                tablero_juego = actualizarTablero(tablero_real,tablero_juego,casilla2)
            
            q.put(jugador)
            print(q.qsize())
            aux_q.pop(0)
            aux_q.append(jugador)
            print(aux_q)
            lock.release()
        else:
            lock.release()
    print("se lleno el tablero")


HOST = "127.0.0.1"#input("Direccion que recibirá solicitudes: ")
PORT = 12345 #int(input("Puerto a utilizar: "))
NUM_CONNECT = int(input("¿Cuantos jugadores serán?"))
buffer_size = 1024
listaConexiones = []
barrier = threading.Barrier(NUM_CONNECT)
q = queue.Queue(NUM_CONNECT)
aux_q = []
lock = threading.Lock()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPServerSocket:
    TCPServerSocket.bind((HOST, PORT))
    TCPServerSocket.listen(NUM_CONNECT)

    print("El servidor TCP para el juego de memoria multijugador está disponible :)")

    accept_client(TCPServerSocket)



