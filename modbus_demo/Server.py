from pymodbus.server import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

map_slaves = {
    1: "Person",
    2: "Not Person"
}

class LoggingDataBlock(ModbusSequentialDataBlock):
    """
    Custom ModbusSequentialDataBlock that logs read and write actions.
    Each data block logs the slave ID, address, and values for debugging and traceability.
    """
    def __init__(self, slave_id, address, values):
        super().__init__(address, values)
        self.slave_id = slave_id

    def setValues(self, address, values):
        logger.info(f"[{map_slaves[self.slave_id]}] Set Values - {values}\n")
        super().setValues(address, values)

    def getValues(self, address, count=1):
        values = super().getValues(address, count)
        logger.info(f"[{map_slaves[self.slave_id]}] Get Values - {values}\n")
        return values

class ModbusServer:
    """
    Configures and runs a Modbus server with separate slaves for person and not person detection.
    """
    def __init__(self, ip, port) -> None:
        self.ip = ip
        self.port = port
        self.device_identities = self.setIdentity()
        self.setContext()

    def run(self) -> None:
        """
        Start the Modbus TCP server, running on the specified IP and port.
        """
        try:
            logger.info("Starting Modbus Server...")
            StartTcpServer(context=self.context,
                           identity=self.global_identity, address=(self.ip, self.port))
        except Exception as e:
            logger.error(f"Error starting server: {e}")

    def setContext(self) -> None:
        """
        Define contexts for multiple slaves with separate data blocks for each.
        Each slave device (representing 'person' and 'not person') has its own DI, CO, HR, and IR blocks.
        """
        # Create data blocks with logging for each slave (1 and 2)
        slave_1_store = ModbusSlaveContext(
            di=LoggingDataBlock(slave_id=1, address=0, values=range(5)),
            co=LoggingDataBlock(slave_id=1, address=0, values=range(5)),
            hr=LoggingDataBlock(slave_id=1, address=0, values=range(5)),
            ir=LoggingDataBlock(slave_id=1, address=0, values=range(5))
        )
        slave_2_store = ModbusSlaveContext(
            di=LoggingDataBlock(slave_id=2, address=0, values=range(5)),
            co=LoggingDataBlock(slave_id=2, address=0, values=range(5)),
            hr=LoggingDataBlock(slave_id=2, address=0, values=range(5)),
            ir=LoggingDataBlock(slave_id=2, address=0, values=range(5))
        )

        # Store context for multiple slaves
        self.context = ModbusServerContext(
            slaves={1: slave_1_store, 2: slave_2_store}, single=False
        )

    def setIdentity(self):
        """
        Set general identity of the Modbus server and specific details for each slave.
        """
        # General server identity
        self.global_identity = ModbusDeviceIdentification()
        self.global_identity.VendorName = "Redes Industriais"
        self.global_identity.ProductCode = "ENGG55"
        self.global_identity.VendorUrl = "https://www.ufba.br/"
        self.global_identity.ProductName = "Person Detection PLC System"
        self.global_identity.ModelName = "PeopleControl"
        self.global_identity.MajorMinorRevision = "1.0"

        # Detailed identities for each slave (custom for 'person' and 'not person' roles)
        device_identities = {
            1: {
                "VendorName": "Industrial Networks",
                "ProductName": "Person Detection PLC",
                "ModelName": "Siemens Model Person",
                "SerialNumber": "PERSON12345",
                "Description": "PLC for control based on person detection"
            },
            2: {
                "VendorName": "Industrial Networks",
                "ProductName": "Not Person Detection PLC",
                "ModelName": "Siemens Model Not Person",
                "SerialNumber": "NOTPERSON67890",
                "Description": "PLC for control based on not person detection"
            }
        }
        return device_identities

    def log_device_identity(self, slave_id):
        """
        Logs identity details for a given slave, useful for debugging and tracking.
        """
        identity = self.device_identities.get(slave_id)
        if identity:
            logger.info(f"Device Identity for Slave {slave_id}: {identity}")

if __name__ == "__main__":
    # Initialize and run the Modbus server on localhost
    server = ModbusServer("localhost", 8081)
    server.run()
