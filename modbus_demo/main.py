from Client import ModbusClient
from Detector import PersonDetector

def main():

  client = ModbusClient("localhost", 8081)

  # video_path = "resources/videos/person.mp4"
  video_path = "rtsp://192.168.1.101:8080/h264.sdp"

  person_detector = PersonDetector(video_path, client)
  person_detector.start_detection()

if __name__ == "__main__":
    main()
