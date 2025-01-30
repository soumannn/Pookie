import smbus

# Initialize I2C bus 3
bus = smbus.SMBus(3)
address = 0x68  # MPU6050 I2C address

try:
    # Wake up the MPU6050 (write to power management register)
    bus.write_byte_data(address, 0x6B, 0)
    print("MPU6050 connected on bus 3!")

    # Read the WHO_AM_I register (0x75) to verify communication
    who_am_i = bus.read_byte_data(address, 0x75)
    print(f"WHO_AM_I register: 0x{who_am_i:X}")
except Exception as e:
    print(f"Error communicating with MPU6050: {e}")

# MPU6050 Register Map
ACCEL_XOUT_H = 0x3B  # Accelerometer X-axis high byte
ACCEL_YOUT_H = 0x3D  # Accelerometer Y-axis high byte
ACCEL_ZOUT_H = 0x3F  # Accelerometer Z-axis high byte
GYRO_XOUT_H = 0x43   # Gyroscope X-axis high byte
GYRO_YOUT_H = 0x45   # Gyroscope Y-axis high byte
GYRO_ZOUT_H = 0x47   # Gyroscope Z-axis high byte

def read_word(bus, address, reg):
    """Read two bytes (a word) from a given register and combine them."""
    high = bus.read_byte_data(address, reg)
    low = bus.read_byte_data(address, reg + 1)
    value = (high << 8) + low
    # Convert to signed value (16-bit)
    if value >= 0x8000:
        value = -((65535 - value) + 1)
    return value

def read_accel_data(bus, address):
    """Read accelerometer data (X, Y, Z)."""
    accel_x = read_word(bus, address, ACCEL_XOUT_H)
    accel_y = read_word(bus, address, ACCEL_YOUT_H)
    accel_z = read_word(bus, address, ACCEL_ZOUT_H)
    return accel_x, accel_y, accel_z

def read_gyro_data(bus, address):
    """Read gyroscope data (X, Y, Z)."""
    gyro_x = read_word(bus, address, GYRO_XOUT_H)
    gyro_y = read_word(bus, address, GYRO_YOUT_H)
    gyro_z = read_word(bus, address, GYRO_ZOUT_H)
    return gyro_x, gyro_y, gyro_z

try:
    # Read accelerometer and gyroscope data
    accel_x, accel_y, accel_z = read_accel_data(bus, address)
    gyro_x, gyro_y, gyro_z = read_gyro_data(bus, address)

    # Print sensor data
    print(f"Accelerometer: X={accel_x}, Y={accel_y}, Z={accel_z}")
    print(f"Gyroscope: X={gyro_x}, Y={gyro_y}, Z={gyro_z}")
except Exception as e:
    print(f"Error reading MPU6050 data: {e}")
