# Classes for functional CAN-Nodes in RC Models
class temp_sensor:
    """A Class for all kinds of temperature sensors."""
    def __init__(self,type,pin):
        self.adress=None
        self.sensor_type=type #Define possible sensor types
        self.measure_pin=pin # Pin with actual connection to sensor
        self.temperature=None
        self.error_state=None
        
    def read_temp(self):
        """Reads a temperature value and stores it."""
        # TO DO: Implement sensor reading based on sensor type etc.
        self.temperature=20
        
    def get_temp(self):
        """Returns the measured temperature."""
        return self.temperature
    
class rpm_sensor:
    """A Class for all kinds of rpm sensors."""
    def __init__(self):
        self.adress=None
        self.sensor_type=None
        self.measure_pin=None
        self.impulses_per_rotation=None
        self.rpm=None
        self.error_state=None
        
    def measure_rpm(self):
        """Takes a reading and stores the value"""
        #TO DO: Implement actual reading
        self.rpm=400
        
    def get_rpm(self):
        return self.rpm

class pressure_sensor:
    """A Class for all kinds of pressure sensors."""
    def __init__(self):
        self.adress=None
        self.sensor_type=None
        self.measure_pin=None
        self.pressure=None
        self.error_state=None
        
    def read_pressure(self):
        """Reads a pressure value and stores it."""
        # TO DO: Implement sensor reading based on sensor type etc.
        self.pressure=2
        
    def get_pressure(self):
        """Returns the measured pressure."""
        return self.pressure

class powermeter:
    """A class for voltage and current measurements."""
    def __init__(self):
        self.voltage=None
        self.current=None
        self.power=None
        
    def measure(self):
        """Take actual reading and store variables"""
        self.voltage=13.1 #Volts
        self.current=2.4  #Amps
        self.power=self.voltage*self.current #Watt
        
    def get_voltage(self):
        return self.voltage
    
    def get_current(self):
        return self.current
    
    def get_power(self):
        return self.power
        
class motor:
    """A class for all motor types"""
    def __init__(self,mode):
        self.modes=mode #Possible modes: 1=pwm control one direction,2=pwm control two direction, 3 rpm control
        self.has_motor_temp=False
        self.has_controller_temp=False
        self.has_watercooling=False       
        self.requested_rpm=None
        self.min_rpm=None
        self.max_rpm=None
        self.voltage=None
        self.current=None
        self.stop_current=None
        self.pwm_value=None
        self.error_state=None
        self.pin_pwm_in=None
        self.pin_pwm_out=None
        # In case motor has temperature sensor:
        self.motor_temp=None
        self.max_motor_temp=60
        # In case controller has temperature sensor:
        self.controller_temp=None
        self.max_controller_temp=80
        # In case motor has water cooling:
        self.watertemp_in=None
        self.watertemp_out=None
        self.waterpressure_in=None
        self.max_watertemp_in=30
        self.max_watertemp_out=60
        self.min_waterpressure_in=0.5
    
    def create_motor_temperature_sensor(self,type,pin):
        """Creates a temperature sensor for the motor"""
        self.motor_temp=temp_sensor(type,pin)
        # Take a first reading to check for valid results:
        self.motor_temp.read_temp()
        self.has_motor_temp=True
        
    def create_controller_temperature_sensor(self,type,pin):
        """Creates a temperature sensor for the controller."""
        self.controller_temp=temp_sensor(type,pin)
        # Take a first reading to check for valid results:
        self.controller_temp.read_temp()
        self.has_controller_temp=True
        
        
    def set_rpm(self,rpm_in):
        """Method to set a target speed"""
        if rpm_in>self.min_rpm:
            if rpm_in<self.max_rpm:
                self.requested_rpm=rpm_in
                print("RPM set to "+str(rpm_in)+".")
            else:
                print("Requested RPM more than max_rpm!")
        else:
            print("Requested RPM below min_rpm!")
            
    def get_rpm(self):
        """Method returns the actual speed."""
        return self.measured_rpm
                    
    def measure_rpm(self):
        """Method to measure the rpm from the measurement buffer"""
        # TO DO: Implement sensors and measurements!
        self.measured_rpm=200
        
    
        
# debugging:
if __name__=='__main__':
    print('Start debugging mode')
    andimot=motor(2)
    print(andimot.modes)
    andimot.min_rpm=10
    andimot.max_rpm=3500
    andimot.set_rpm(300)
    andimot.measure_rpm()
    rpm=andimot.get_rpm()
    print("RPM="+str(rpm))
    andimot.create_motor_temperature_sensor(1,10)
    tmp=andimot.motor_temp.get_temp()
    print("Motor temperature: "+str(tmp))
    andimot.create_controller_temperature_sensor(1,11)
    tmp=andimot.controller_temp.get_temp()
    print("Controller temperature: "+str(tmp))
    
    
