from pymodbus.client import ModbusTcpClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModbusClient:
    def __init__(self, ip, port) -> None:
        self.ip = ip
        self.port = port

    def start_connection(self) -> None:
        try:
            self.client = ModbusTcpClient(self.ip, port=self.port)
            self.client.connect()
            logger.info("Connected to Modbus server")
        except Exception as e:
            logger.error(f"Error starting connection: {e}")

    def close_connection(self) -> None:
        try:
            self.client.close()
            logger.info("Connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")

    def read_coils(self, slave_id=1) -> None:
        response = self.client.read_coils(0, 4, slave_id) 
        if response.isError():
            logger.error(f"Error reading coils from Slave {slave_id}: {response}")
        else:
            logger.info(f"Coils from Slave {slave_id}: {response.bits[:4]}")

    def read_holding_registers(self, slave_id=1) -> None:
        response = self.client.read_holding_registers(0, 4, slave_id)  
        if response.isError():
            logger.error(f"Error reading holding registers from Slave {slave_id}: {response}")
        else:
            logger.info(f"Holding registers from Slave {slave_id}: {response.registers}")

    def write_coils(self, coils, slave_id=1) -> None:
        response = self.client.write_coils(0, coils, slave_id) 
        if response.isError():
            logger.error(f"Error writing coils to Slave {slave_id}: {response}")
        else:
            logger.info(f"Coils successfully written to Slave {slave_id}")

    def write_holding_registers(self, holding_registers, slave_id=1) -> None:
        response = self.client.write_registers(0, holding_registers, slave_id)  
        if response.isError():
            logger.error(f"Error writing holding registers to Slave {slave_id}: {response}")
        else:
            logger.info(f"Holding registers successfully written to Slave {slave_id}")

if __name__ == "__main__":
    client = ModbusClient("localhost", 8081)
    client.start_connection()

    coils_person = [True, False, True, False]
    client.write_coils(coils_person, slave_id=1)
    client.read_coils(slave_id=1)

    registers_person = [22, 9, 12, 7]
    client.write_holding_registers(registers_person, slave_id=1)
    client.read_holding_registers(slave_id=1)

    coils_not_person = [False, True, False, True]
    client.write_coils(coils_not_person, slave_id=2)
    client.read_coils(slave_id=2)

    registers_not_person = [1, 2, 3, 4]
    client.write_holding_registers(registers_not_person, slave_id=2)
    client.read_holding_registers(slave_id=2)

    client.close_connection()
