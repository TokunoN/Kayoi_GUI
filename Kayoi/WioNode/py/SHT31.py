import time
import smbus

class SHT31:
    def __init__(self):
        self.i2c = smbus.SMBus(1)
        # ADRとGNDをはんだで接続すると0x44にアドレスが変更される。
        # 1つのラズパイに2つSHT31を接続するときに使用する。
        self.i2c_addr = 0x45                                                           # P3
        time.sleep(0.5)  

    def tempChanger(self, msb, lsb):
        mlsb = ((msb << 8) | lsb)                                             # P1
        return (-45 + 175 * int(str(mlsb), 10) / (pow(2, 16) - 1))            # P2

    def humidChanger(self, msb, lsb):
        mlsb = ((msb << 8) | lsb)
        return (100 * int(str(mlsb), 10) / (pow(2, 16) - 1))

    def get_temperature_and_humidity(self):
        # 温湿度取得命令
        self.i2c.write_byte_data(self.i2c_addr, 0x2C, 0x06)
        # 取得した温湿度を読み込む
        data = self.i2c.read_i2c_block_data(self.i2c_addr, 0x00, 6)                     # P6
        # 温湿度をそれぞれ℃とRH%に変換
        temperature = self.tempChanger(data[0], data[1])
        humidity = self.humidChanger(data[3], data[4])
        
        return temperature, humidity