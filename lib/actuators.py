"""All classes for actuators and outputs.
    """

import machine
import utime
import sensors

def convert(x:float, in_min:float, in_max:float, out_min:float, out_max:float):
    """A function to map values"""
    if (in_max - in_min) ==0:
        return 0
    else:
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
def convert_int(x:int, in_min:int, in_max:int, out_min:int, out_max:int):
    """A function to map values"""
    if (in_max - in_min) ==0:
        return 0
    else:
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

class PWMOut():
    def __init__(self,pin_number:int,name:str,frequency:int=10000) -> None:
        if pin_number==0: #Class initialized without actual output, can be to control remote (I2C etc) PWM.
            pin_number=25 #Set pin to built-in LED (Raspi Pico)
        else:
            self.PWM=machine.PWM(machine.Pin(pin_number))
        self.name=name
        self.PWM.freq(frequency) #[Hz]
        self.PWM.duty_u16(0) # 0-65535 
        self.min_pwm=0
        self.max_pwm=65535
        self.raw_duty:int

    def set_raw_duty_cycle(self,raw_duty:int)->None:
        self.raw_duty=raw_duty
        self.PWM.duty_u16(raw_duty)

    def set_min_pwm(self,min_pwm:int)->None:
        self.min_pwm=min_pwm

    def set_max_pwm(self,max_pwm:int)->None:
        self.max_pwm=max_pwm

    def set_duty_percent(self,duty_percent:int)->None:
        raw_duty=convert_int(duty_percent,0,100,self.min_pwm,self.max_pwm)
        self.set_raw_duty_cycle(raw_duty)
        print(str(raw_duty)+", "+str(duty_percent)+"%")

class Light(PWMOut):
    def __init__(self, pin_number: int, name:str, frequency: int = 100) -> None:
        super().__init__(pin_number, name, frequency)
        self.on_state:bool=False  # If light is currently on or off.
        self.dim_value=0  #Dimmer Value
        self.name=name

    def set_dim_value(self,dim_value:int)->None:
        self.dim_value=dim_value
        if self.on_state:
            duty=self.max_pwm-dim_value
            self.set_raw_duty_cycle(duty)

    def switch_on(self)->None:
        duty=self.max_pwm-self.dim_value
        self.set_raw_duty_cycle(duty)
        self.on_state=True

    def switch_off(self)->None:
        self.set_raw_duty_cycle(self.min_pwm)
        self.on_state=False

    def is_on(self)->bool:
        return self.on_state

class Motor:
    """XXXXXXXXXXXXXXXXXXXXXXXX
    ÜBERARBEITEN, basierend auf PWM!
    XXXXXXXXXXXXXXXXXXXXXXXXXXX
    A class for all motor types"""
    def __init__(self,mode:int):
        self.modes=mode #Possible modes: 1=pwm control one direction,2=pwm control two direction, 3 rpm control
        self.has_MotorTemp=False
        self.has_ControllerTemp=False
        self.has_watercooling=False     
        self.requested_rpm:int=0
        self.measured_rpm:int=0
        self.min_rpm:int=0
        self.max_rpm:int=0
        self.voltage:float=0
        self.current:float=0
        self.stop_current:float=0
        self.pwm_value:int=0
        self.direction:int=0 # 0=forwards, 1=backwards if motor bidirectional
        self.error_state:str="Nominal"
        self.pin_pwm_in:int=0
        self.pin_pwm_out:int=0
            
    def create_motor_temperature_sensor(self,sensortype:int,pin:int,max_temp_alarm:float=60)->str:
        """Creates a temperature sensor for the motor"""
        self.MotorTemp=sensors.TempSensor(name="Motor Temperature",sensortype=sensortype,pin=pin)
        # Take a first reading to check for valid results:
        self.MotorTemp.start_reading()
        self.MotorTemp.start_broadcasting()
        self.has_MotorTemp=True
        self.MotorTemp.set_max_alarm(max_temp_alarm)
        return "Motor temperature sensor created and alarm set."
        
    def create_controller_temperature_sensor(self,sensortype:int,pin:int,max_temp_alarm:float=70)->str:
        """Creates a temperature sensor for the controller."""
        self.ControllerTemp=sensors.TempSensor(name="Controller Temperature",sensortype=sensortype,pin=pin)
        # Take a first reading to check for valid results:
        self.ControllerTemp.start_reading()
        self.ControllerTemp.start_broadcasting()
        self.has_ControllerTemp=True
        self.ControllerTemp.set_max_alarm(max_temp_alarm)
        return "Controller temperature sensor created and alarm set."
        
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
            
    def get_rpm(self)->float:
        """Method returns the actual speed."""
        return self.measured_rpm
                    
    def measure_rpm(self):
        """Method to measure the rpm from the measurement buffer"""
        # TO DO: Implement sensors and measurements!
        self.measured_rpm=200
    
class Valve:
    """A valve to control hydraulic systems."""
    pass

class Pump(PWMOut):
    """A class for a pump"""
    def __init__(self, pin_number: int, name:str, frequency: int = 10000) -> None:
        super().__init__(pin_number, name, frequency)
        self.on_pwm:int=65535 # PWM value when switched on (default=maximum)
        self.on_state:bool=False  #Is pump running?

    def switch_on(self):
        """Start pump."""
        self.set_raw_duty_cycle(self.on_pwm)
        self.on_state=True

    def switch_off(self):
        """Stops the pump."""
        self.set_raw_duty_cycle(0)
        self.on_state=False

    def is_running(self):
        """Returns true if pump is running."""
        return self.on_state



if __name__=="__main__":
    #Test on build-in led
    #LED=PWMOut(25)
    #LED.set_duty_percent(10)
    #utime.sleep(10)
    #LED.set_duty_percent(50)
    #utime.sleep(10)
    #LED.set_duty_percent(100)
    #utime.sleep(10)
    #LED.set_duty_percent(50)
    #utime.sleep(10)
    LED=Light(25,"Testlight.")
    LED.switch_on()
    utime.sleep(15)
    LED.switch_off()
    utime.sleep(19)
    LED.set_max_pwm(32000)
    LED.switch_on()
    utime.sleep(10)
    LED.switch_off()