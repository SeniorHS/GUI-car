import cv2
import torch
import numpy as np
from ultralytics import YOLO, solutions
import threading
from queue import Queue
from time import sleep


# Verificar si se puede usar la GPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# YOLOv8 - Cargar el modelo preentrenado
model = YOLO('./yolo11n.pt')


# Línea para contar objetos y clases a detectar (0: personas, 2: autos)
#line_points = [(220, 90), (500, 90)]  # Puntos de la línea para conteo
region_points = [(20, 251), (600, 251)] # Puntos de la línea para conteo

# classes_to_count = [2]  # Clases para contar (persona, automóvil) 
# Para webcam, usa source=0 

# Configuración del contador
counter = solutions.ObjectCounter(
    show=True,
    view_img=True,
    region=region_points,
    names=model.names,
    draw_tracks=True,
    line_width=2,
    classes=[67]
    #show_in=True,
    #show_out=True
    
)

# Función para redimensionar el fotograma
def resize_frame(frame, width=640):
    height = int(frame.shape[0] * (width / frame.shape[1]))
    return cv2.resize(frame, (width, height))

# Cola de fotogramas (buffer) para el procesamiento y la captura
frame_queue = Queue(maxsize=10)

# Función de captura del video
def capture_video():
    #cap = cv2.VideoCapture("rtsp://admin:admin2024@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0")
    cap = cv2.VideoCapture(0)
    # guarda info de anteriores fotogramas por defecto
    # al indicar el valor 1 le decimos que solo guarde el más reciente
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reducir el buffer de la cámara RTSP
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Reducir la resolución del fotograma
        frame = resize_frame(frame, width=640)

        # cv2.putText(img=frame, text=f"Disponible:", org=(18,80), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1, color=(255,255,255), thickness=1)
        # cv2.putText(img=frame, text=f"{conteo} de 200", org=(18,100), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1, color=(255,255,255), thickness=1)

        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
    
        
        # Agregar fotograma a la cola
        if not frame_queue.full():
            frame_queue.put(frame)

        # sleep(1/30)

    cap.release()
    # cv2.destroyAllWindows()

# Función de procesamiento del video
def process_video():
    cupos = 200
    detections_1 = 0
    detections_2 = 0
    global processed_frame
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()

            # YOLO procesa el fotograma y genera los "tracks" de los objetos
            # tracks = model.track(frame, persist=True, show=False, classes=classes_to_count, verbose=False)

            # autos que entran
            detections_1 = counter.show_in

            # autos que salen
            detections_2 = counter.show_out

            # si 200 - los autos que salen + los autos que entran es mayor o igual a 201 pasa

            if cupos == 200 and (cupos - detections_1) + detections_2 > 200:
                pass
            else:
                cupos = (200 - detections_1) + detections_2

            # if cupos == 200 & (cupos - detections_2) + detections_1 == 199:
            #     cupos = 200
            # if cupos == 200 & ()
            # if (cupos - detections_2) + detections_1 >= 201:
            #     pass
            # else:
            #     cupos = (200 - detections_2) + detections_1

            # if (cupos + detections_2) - detections_1:
            #     cupos = (200 - detections_2) + detections_1
            cv2.rectangle(frame, (115, 115), (15, 50), (0, 0, 0), -1)  # Fill rectangle
            cv2.putText(img=frame, text=f"Disponible:", org=(18,80), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1, color=(255,255,255), thickness=1)
            cv2.putText(img=frame, text=f"{cupos} de 200", org=(18,100), fontFace=cv2.FONT_HERSHEY_PLAIN, fontScale=1, color=(255,255,255), thickness=1)

            # Contador de objetos
            counter.count(frame)
            
            # Guardar el fotograma procesado en una variable compartida
            with lock:
                processed_frame = frame
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    # cv2.destroyAllWindows()

# Función para visualizar el video
def display_video():
    global processed_frame
    while True:
        # Mostrar el fotograma procesado
        with lock:
            if processed_frame is not None:
                cv2.imshow('Video con YOLOv8 - Conteo de Objetos', processed_frame)

        # Presionar 'q' para salir
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()

# def display_video():
#     global processed_frame
#     while True:
#         if cv2.waitKey(1) & 0xFF == ord('q'):
            # break
        # Mostrar el fotograma procesado
        # with lock:
        #     if processed_frame is not None:
        #         cv2.imshow('Video con YOLOv8 - Conteo de Objetos', processed_frame)
        
        # Presionar 'q' para salir
        #   break
    
    # cv2.destroyAllWindows()

if __name__ == '__main__':
    print(f"Dispositivo utilizado: {device}")

    # Crear bloqueo para sincronización
    lock = threading.Lock()

    # Crear y ejecutar el hilo de captura de video
    capture_thread = threading.Thread(target=capture_video)
    capture_thread.start()

    # Crear y ejecutar el hilo de procesamiento de video
    processing_thread = threading.Thread(target=process_video)
    processing_thread.start()

    # Ejecutar la visualización en el hilo principal
    # display_video()

    # Esperar a que los hilos terminen
    capture_thread.join()
    processing_thread.join()
