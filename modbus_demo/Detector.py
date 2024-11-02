from ultralytics import YOLO
import cv2

class PersonDetector:
    def __init__(self, video_path, modbus_client, model_path="yolo-Weights/yolov8n.pt", confidence_threshold=0.5, no_person_threshold=30):
        self.cap = cv2.VideoCapture(video_path)
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        self.model = YOLO(model_path)
        self.class_name = "person"
        self.confidence_threshold = confidence_threshold
        self.modbus_client = modbus_client
        self.modbus_client.start_connection()

        self.previous_state = None 
        self.no_person_count = 0  # Contador para rastrear quadros sem detecção

        # Limite de quadros sem detecção antes de disparar a alerta
        self.no_person_threshold = no_person_threshold

    def __del__(self):
        self.modbus_client.close_connection()

    def alert_person(self):
        coils_person = [True, True, True, True]
        self.modbus_client.write_coils(coils_person, slave_id=1)

        registers_person = [22, 9, 12, 7]
        self.modbus_client.write_holding_registers(registers_person, slave_id=1)

        coils_not_person = [False, False, False, False]
        self.modbus_client.write_coils(coils_not_person, slave_id=2)

        registers_not_person = [0, 0, 0, 0]
        self.modbus_client.write_holding_registers(registers_not_person, slave_id=2)

    def alert_not_person(self):
        coils_person = [False, False, False, False]
        self.modbus_client.write_coils(coils_person, slave_id=1)

        registers_person = [0, 0, 0, 0]
        self.modbus_client.write_holding_registers(registers_person, slave_id=1)

        coils_not_person = [True, True, True, True]
        self.modbus_client.write_coils(coils_not_person, slave_id=2)

        registers_not_person = [22, 9, 12, 7]
        self.modbus_client.write_holding_registers(registers_not_person, slave_id=2)

    def process_frame(self, img):
        results = self.model(img, stream=True)

        current_state = False

        for r in results:
            boxes = r.boxes

            if boxes:
                for box in boxes:
                    cls = int(box.cls[0])

                    if cls == 0: 
                        confidence = box.conf[0].item()
                        
                        if confidence >= self.confidence_threshold:
                            x1, y1, x2, y2 = box.xyxy[0]
                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

                            org = (x1, y1)
                            font = cv2.FONT_HERSHEY_SIMPLEX
                            fontScale = 1
                            color = (255, 0, 0)
                            thickness = 2
                            cv2.putText(img, f"{self.class_name} {confidence:.2f}", org, font, fontScale, color, thickness)

                            current_state = True 
                            self.no_person_count = 0  # Reseta o contador ao detectar uma pessoa
                            break

        if current_state:
            if self.previous_state != True:
                self.alert_person()
            self.previous_state = True  # Atualiza o estado anterior para "pessoa detectada"
            self.no_person_count = 0  # Reseta o contador
        else:
            self.no_person_count += 1  # Incrementa o contador se não houver detecção
            
            # Verifica se o contador excede o threshold
            if self.no_person_count >= self.no_person_threshold:
                if self.previous_state != False:
                    self.alert_not_person()
                self.previous_state = False  # Atualiza o estado anterior para "não há pessoa"

        return img

    def start_detection(self):
        while True:
            success, img = self.cap.read()
            if not success:
                break

            img = self.process_frame(img)

            resized_img = cv2.resize(img, (320, 240))  
            cv2.imshow('Person Detection', resized_img) 

            # Ajustando o tempo de espera para 200 ms para uma exibição mais lenta
            if cv2.waitKey(1) == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()
