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
