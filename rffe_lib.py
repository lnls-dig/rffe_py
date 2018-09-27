#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import struct
import re

class RFFEControllerBoard:
    """Class used to send commands and acquire data from the RF front-end controller board."""

    ATT_VALID_VALUES = [x * .5 for x in range(64)]

    def __init__(self, ip, port=6791):
        """Class constructor. Here the socket connection to the board is initialized. The argument
        required is the IP adress of the instrument (string)."""
        self.ip = ip
        self.port = 6791

        self.board_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.board_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.board_socket.settimeout(5.0)
        self.board_socket.connect((self.ip,self.port))

    def get_attenuator_value(self):
        """This method returns the current attenuation value (in dB) as a floating-point number.
           The attenuation value will be between 0 dB and 31.5 dB, with a 0.5 dB step size."""
        self.board_socket.send(bytearray.fromhex("10 00 01 00"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def set_attenuator_value(self, value):
        """Sets the attenuation value of both front-ends. The agrument should be a
        floating-point number representing the attenuation (in dB) between 0 dB and 31.5 dB, with a
        0.5 dB step size. Argument values other than these will be disconsidered."""
        if (value not in RFFEControllerBoard.ATT_VALID_VALUES):
            raise ValueError("Value must be between 0 dB and 31.5 dB, with a 0.5 dB step size")
        else:
            self.board_socket.send(bytearray.fromhex("20 00 09 00") + struct.pack("<d", value))
            temp = self.board_socket.recv(1024)


    def get_temp_ac(self):
        """This method returns the temperature measured by the sensor present in the A/C
        front-end. The value returned is a floating-point number."""
        self.board_socket.send(bytearray.fromhex("10 00 01 01"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def get_temp_bd(self):
        """This method returns the temperature measured by the sensor present in the B/D
        front-end. The value returned is a floating-point number."""
        self.board_socket.send(bytearray.fromhex("10 00 01 02"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def get_temp_ac_setpoint(self):
        """This method returns the temperature set-point for the A/C front-end temperature
        controller. The returned value is a floating-point number in the Celsius degrees scale."""
        self.board_socket.send(bytearray.fromhex("10 00 01 03"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def set_temp_ac_setpoint(self, value):
        """Sets the temperature set-point for the A/C front-end temperature controller. The value
        passed as the argument is a floating-point number."""
        self.board_socket.send(bytearray.fromhex("20 00 09 03") + struct.pack("<d", value))
        temp = self.board_socket.recv(1024)

    def get_temp_bd_setpoint(self):
        """This method returns the temperature set-point for the B/D front-end temperature
        controller. The returned value is a floating-point number in the Celsius degrees scale."""
        self.board_socket.send(bytearray.fromhex("10 00 01 04"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def set_temp_bd_setpoint(self, value):
        """Sets the temperature set-point for the B/D front-end temperature controller. The value
        passed as the argument is a floating-point number."""
        self.board_socket.send(bytearray.fromhex("20 00 09 04") + struct.pack("<d", value))
        temp = self.board_socket.recv(1024)

    def get_temperature_control_status(self):
        """This method returns the temperature controller status as an integer. If this integer
        equals 0, it's because the temperature controller is off. Otherwise, if the value returned
        equals 1, this means the temperature controller is on."""
        self.board_socket.send(bytearray.fromhex("10 00 01 05"))
        temp = self.board_socket.recv(1024)
        return(temp[3])

    def set_temperature_control_status(self, status):
        """Method used to turn on/off the temperature controller. For turning the controller on, the
        argument should be the integer 1. To turn the controller off, the argument should be 0."""
        if (status in (0, 1)):
            self.board_socket.send(bytearray.fromhex("20 00 02 05 0" + str(status)))
            temp = self.board_socket.recv(1024)

    def get_heater_ac_value(self):
        """This method returns the voltage signal to the heater in the A/C front-end as a
        floating-point number."""
        self.board_socket.send(bytearray.fromhex("10 00 01 06"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def set_heater_ac_value(self, value):
        """Sets the voltage level to the heater in the A/C front-end. The value passed as the
        argument, a floating-point number, is the intended voltage for the heater."""
        self.board_socket.send(bytearray.fromhex("20 00 09 06") + struct.pack("<d", value))
        temp = self.board_socket.recv(1024)

    def get_heater_bd_value(self):
        """This method returns the voltage signal to the heater in the B/D front-end as a
        floating-point number."""
        self.board_socket.send(bytearray.fromhex("10 00 01 07"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def set_heater_bd_value(self, value):
        """Sets the voltage level to the heater in the B/D front-end. The value passed as the
        argument, a floating-point number, is the intended voltage for the heater."""
        self.board_socket.send(bytearray.fromhex("20 00 09 07") + struct.pack("<d", value))
        temp = self.board_socket.recv(1024)

    def reset(self):
        """This method resets the board software."""
        self.board_socket.send(bytearray.fromhex("20 00 02 08 01"))
        temp = self.board_socket.recv(1024)

    def reprogram(self, file_path, version):
        """This method reprograms the mbed device on the RF front-end controller board. The
        first argument, a string, is the path to the binary file which corresponds to the mbed
        program will be loaded in the device. The second argument is the new firmware version
        formated as: x.y.z or x_y_z"""

        major, minor, patch = map(int,re.split('[., _]',version))

        with open(file_path, "rb") as f:
            msg = bytearray.fromhex("20 00 81 0A")
            #Send firmware new version
            msg.extend([major,minor,patch])
            #Pad
            msg.extend(b'\0'*(129+3-len(msg)))
            self.board_socket.send(msg)
            temp = self.board_socket.recv(1024)

            self.board_socket.send(bytearray.fromhex("20 00 02 09 01"))
            temp = self.board_socket.recv(1024)

            while True:
                data = f.read(128)
                if (not data):
                    break
                elif (len(data) < 128):
                    data = data + (b"\xFF" * (128 - len(data)))
                self.board_socket.send(bytearray.fromhex("20 00 81 0A") + data)
                temp = self.board_socket.recv(1024)

            self.board_socket.send(bytearray.fromhex("20 00 02 09 02"))
            temp = self.board_socket.recv(1024)

    def get_software_version(self):
        """This method returns the RF front-end controller software version as a binary
        string of characters."""
        self.board_socket.send(bytearray.fromhex("10 00 01 0B"))
        temp = self.board_socket.recv(1024)
        return(temp[3:10])

    def set_pid_ac_kc(self, value):
        """Sets the PID Kc parameter in the A/C front-end. The value is passed as a floating-point number."""
        self.board_socket.send(bytearray.fromhex("20 00 09 0C") + struct.pack("<d", value))
        temp = self.board_socket.recv(1024)

    def get_pid_ac_kc(self):
        """This method returns the Kc parameter of the PID in the A/C front-end as a
        floating-point number."""
        self.board_socket.send(bytearray.fromhex("10 00 01 0C"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def set_pid_ac_taui(self, value):
        """Sets the PID tauI parameter in the A/C front-end. The value is passed as a floating-point number."""
        self.board_socket.send(bytearray.fromhex("20 00 09 0D") + struct.pack("<d", value))
        temp = self.board_socket.recv(1024)

    def get_pid_ac_taui(self):
        """This method returns the tauI parameter of the PID in the A/C front-end as a
        floating-point number."""
        self.board_socket.send(bytearray.fromhex("10 00 01 0D"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def set_pid_ac_taud(self, value):
        """Sets the PID tauD parameter in the A/C front-end. The value is passed as a floating-point number."""
        self.board_socket.send(bytearray.fromhex("20 00 09 0E") + struct.pack("<d", value))
        temp = self.board_socket.recv(1024)

    def get_pid_ac_taud(self):
        """This method returns the tauD parameter of the PID in the A/C front-end as a
        floating-point number."""
        self.board_socket.send(bytearray.fromhex("10 00 01 0E"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def set_pid_bd_kc(self, value):
        """Sets the PID Kc parameter in the B/D front-end. The value is passed as a floating-point number."""
        self.board_socket.send(bytearray.fromhex("20 00 09 0F") + struct.pack("<d", value))
        temp = self.board_socket.recv(1024)

    def get_pid_bd_kc(self):
        """This method returns the Kc parameter of the PID in the B/D front-end as a
        floating-point number."""
        self.board_socket.send(bytearray.fromhex("10 00 01 0F"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def set_pid_bd_taui(self, value):
        """Sets the PID tauI parameter in the B/D front-end. The value is passed as a floating-point number."""
        self.board_socket.send(bytearray.fromhex("20 00 09 10") + struct.pack("<d", value))
        temp = self.board_socket.recv(1024)

    def get_pid_bd_taui(self):
        """This method returns the tauI parameter of the PID in the B/D front-end as a
        floating-point number."""
        self.board_socket.send(bytearray.fromhex("10 00 01 10"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def set_pid_bd_taud(self, value):
        """Sets the PID tauD parameter in the B/D front-end. The value is passed as a floating-point number."""
        self.board_socket.send(bytearray.fromhex("20 00 09 11") + struct.pack("<d", value))
        temp = self.board_socket.recv(1024)

    def get_pid_bd_taud(self):
        """This method returns the tauD parameter of the PID in the B/D front-end as a
        floating-point number."""
        self.board_socket.send(bytearray.fromhex("10 00 01 11"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def get_mac_address(self):
        """This method returns the MBED MAC_Address as a string"""
        self.board_socket.send(bytearray.fromhex("10 00 01 13"))
        temp = self.board_socket.recv(1024)
        return(temp[3:20])

    def set_ip(self, ip):
        """Sets the IP Address. The value is passed as a string."""
        ip_hex = ' '.join(x.encode('hex') for x in ip)
        self.board_socket.send(bytearray.fromhex("20 00 11 12 "+ip_hex+" 00"*(16-len(ip))))
        #self.board_socket.send(bytearray.fromhex("20 00 0C 12 "+ip_hex))
        temp = self.board_socket.recv(1024)
    def close(self):
        """Close the socket connection to the board."""
        self.board_socket.close()
