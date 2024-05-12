"""Classes for Sensors in functional RC Models."""

import machine
import utime
import general

class Potentiometer(general.Sensor):
    """A Class to connect any potentiometer."""
    def __init__(self,pinnumber:int,name:str,unit:str,read_frequency:int=10,queue_length:int=0,broadcast:bool=False)->None:
        super().__init__(name,unit,read_frequency,queue_length,broadcast)
        self.PotentiometerIn=machine.ADC(machine.Pin(pinnumber))

    def read_raw(self)->float:
        """Raw reading at the input pin."""
        raw_value=self.PotentiometerIn.read_u16() # read input voltage as 0-65535 in range of 0-ARef
        return raw_value

class int_Potentiometer(general.int_Sensor):
    """A Potentiometer that returns integer values as readouts."""
    def __init__(self, pinnumber:int,name: str, unit: str, read_frequency: int = 10, queue_length: int = 0, broadcast: bool = False) -> None:
        super().__init__(name, unit, read_frequency, queue_length, broadcast)
        self.PotentiometerIn=machine.ADC(machine.Pin(pinnumber))

    def read_raw(self)->int:
        """Raw reading at the input pin."""
        raw_value=self.PotentiometerIn.read_u16() # read input voltage as 0-65535 in range of 0-ARef
        return raw_value
    
class TempSensor(general.Sensor):
    """A Class for all kinds of temperature sensors.
    Supported types:
    1 : Analog voltage on ADC"""
    def __init__(self,name:str,sensortype:int,pin:int,broadcast:bool=True):
        super().__init__(name,"°C",queue_length=50,broadcast=broadcast)
        self.sensor_type=sensortype #Define possible sensor types: 1=ADC
        if sensortype == 1:
            self.measure_pin=pin # Pin with actual connection to sensor
            self.ADCin=machine.ADC(machine.Pin(self.measure_pin))
            self.period:int=0
    def read_raw(self) -> float:
        """Reads raw value, overwrites parent method."""
        if self.sensor_type == 1: # Analog Sensor based on ADC voltage reading
            raw_value=self.ADCin.read_u16() # read input voltage as 0-65535 in range of 0-ARef
        else:
            raw_value=0
        if self.debug:
            print("Raw Readout: "+str(raw_value))
        return raw_value
    
class RPMSensor(general.Sensor):
    """A Class for all kinds of rpm sensors."""
    def __init__(self,name:str,sensortype:int,sensor_pin:int,impulses_per_rotation:int,broadcast:bool=True):
        super().__init__(name,"RPM",queue_length=50,broadcast=broadcast)
        self.sensor_type=sensortype
        if sensortype == 1: #Based on simple interrupt
            self.start_time_ticks:int=0
            self.interrupt_flag:bool=False
            self.sensor_pin=machine.Pin(22,mode=machine.Pin.IN,pull=machine.Pin.PULL_DOWN)
            self.sensor_pin.irq(trigger=self.sensor_pin.IRQ_RISING,handler=self.impuls_callback)
        self.impulses_per_rotation=impulses_per_rotation
        
    def impuls_callback(self,pin):
        self.interrupt_flag=True
        self.period=utime.ticks_diff(utime.ticks_ms(),self.start_time_ticks)
        self.start_time_ticks=utime.ticks_ms()
        self.interrupt_flag=False

    def read_raw(self)->float:
        """Takes a reading and stores the value, overwrites parent method."""
        #TO DO: Implement actual reading (check!!)
        while not self.interrupt_flag:
            utime.sleep_ms(1)
        raw_value=1/(self.period*self.impulses_per_rotation/60000)
        return raw_value

class PressureSensor(general.Sensor):
    """A Class for all kinds of pressure sensors."""
    def __init__(self, name: str, unit: str, read_frequency: int = 10, queue_length: int = 50, broadcast: bool = False) -> None:
        super().__init__(name, unit, read_frequency, queue_length, broadcast)
        
    def read_pressure(self):
        """Reads a pressure value and stores it. Overwrites parent method."""
        # TO DO: Implement sensor reading based on sensor type etc.
        raw_value=2 #Placeholder
        return raw_value
    def get_pressure(self)->float:
        """Returns the measured pressure."""
        return self.value

class VoltageMeter(general.Sensor):
    """Monitors voltage readouts."""
    def __init__(self, name: str, unit: str, read_frequency: int = 10, queue_length: int = 0, broadcast: bool = False) -> None:
        super().__init__(name, unit, read_frequency, queue_length, broadcast)
        
    def read_raw(self) -> float:
        """Reads raw value for voltage, overwrites parent method."""
        raw_value=1 #Placeholder
        return raw_value

class AmpereMeter(general.Sensor):
    """Monitors current mneasurements."""
    def __init__(self, name: str, unit: str, read_frequency: int = 10, queue_length: int = 0, broadcast: bool = False) -> None:
        super().__init__(name, unit, read_frequency, queue_length, broadcast)
    
    def read_raw(self) -> float:
        """Reads raw value, overwrites parent method."""
        raw_value=1 #Placeholder
        return raw_value

class PowerMeter(general.Sensor):
    """A class for voltage and current measurements."""
    def __init__(self, name: str="Power", unit: str="W", read_frequency: int = 1, queue_length: int = 10, broadcast: bool = False) -> None:
        super().__init__(name, unit, read_frequency, queue_length, broadcast)
        self.voltage:float=0
        self.current:float=0
        self.power:float=0
        self.VoltageSensor=VoltageMeter("Voltage","V",10,50)
        self.CurrentSensor=AmpereMeter("Current","A",10,50)

    def read_raw(self):
        """Take actual readings, overwrites parent method."""
        #TO DO: Implement actual measurement.
        self.voltage=self.VoltageSensor.get_value()
        self.current=self.CurrentSensor.get_value()
        self.power=self.current*self.voltage
        self.QueueValues.put(self.power)
        
    def get_voltage(self)->float:
        """Return voltage reading [Volts]"""
        return self.voltage
    
    def get_max_voltage(self)->float:
        """Return max measured voltage"""
        return self.VoltageSensor.get_max_read_value()
    
    def get_avg_voltage(self)->float:
        """Return the average voltage measured in the amount of values, that are stored in the queue."""
        return self.VoltageSensor.get_avg_value()
    
    def get_current(self)->float:
        """Return current reading [Amps]"""
        return self.current
    
    def get_max_current(self)->float:
        """Return max measured current (Amps)"""
        return self.CurrentSensor.get_max_read_value()
    
    def get_avg_current(self)->float:
        """Return the average current measured in the amount of values, that are stored in the queue."""
        return self.CurrentSensor.get_avg_value()

    def get_power(self)->float:
        """Return power reading [Watt]"""
        return self.power
    
    def get_max_power(self)->float:
        """Return max measured power (Watt)"""
        return self.max_read_value
    
    def get_avg_power(self)->float:
        """Return the average power measured in the amount of values, that are stored in the queue."""
        return self.min_read_value

class WaterSensor:
    """A class for a water detection or water level measurement sensor."""
    pass

class BrightnessSensor:
    """A sensor to measure ambient brightness, to trigger navigation lights."""
    pass

if __name__=="__main__":
    #CoolingWaterSensor=TempSensor
    #Ruderservo=Potentiometer("Rudder",1)
    #out=Ruderservo.start_reading()
    #print(out)
    #utime.sleep_ms(5000)
    #out=Ruderservo.start_broadcasting()
    #print(out)
    #utime.sleep_ms(5000)
    #out=Ruderservo.stop_broadcasting()
    #print(out)
    #utime.sleep_ms(5000)
    #out=Ruderservo.stop_reading()
    #print(out)
    #R1=RPMSensor("Antriebswelle",1,2,1,True)
    #out=R1.start_reading()
    #print(out)
    #out=R1.start_broadcasting()
    #print(out)
    #utime.sleep(30)

    P1=Potentiometer(26,"Rudder","°",broadcast=True)
    out=P1.set_limits(-45.0,45.0)
    print(out)
    P1.set_read_frequency(100)
    out=P1.set_broadcast_period(250)
    print(out)
    out=P1.start_reading()
    print(out)
    out=P1.start_broadcasting()
    print(out)
    utime.sleep(30)
    
    T1=TempSensor("Motor temperature",1,27)
    out=T1.set_limits(0,150)
    print(out)
    out=T1.start_reading()
    print(out)
    out=T1.start_broadcasting()
    print(out)
    utime.sleep(20)
    out=T1.stop_broadcasting()
    print(out)
    out=T1.stop_reading()
    print(out)

    out=P1.stop_broadcasting()
    print(out)
    out=P1.stop_reading()
    print(out)
    out=P1.stop_debug()
    print(out)

    #out=R1.stop_broadcasting()
    #print(out)
    #out=R1.stop_reading()
    #print(out)