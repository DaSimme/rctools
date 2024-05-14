"""All general purpose classes and functions."""
import machine
import utime
import simple_queue

def convert(x:float, in_min:float, in_max:float, out_min:float, out_max:float):
    """A function to convert sensor values"""
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
    
class NoAvgValues(Exception):
    """Raises an error, if no avg values are present, but are requested."""
    pass

class Alarm(Exception):
    """Raises an Alarm when measured value is below minimum alarm or over maximum alarm value."""
    pass

class Sensor():
    """A class with general sensor attributes and methods, to be inherited by the specific
    sensor classes."""
    def __init__(self,name:str,unit:str,read_frequency:int=10,queue_length:int=0,broadcast:bool=False) -> None:
        self.name=name
        self.unit=unit
        self.error_state:str="Nominal."
        self.debug:bool=False
        self.min_raw_value:float=64000
        self.min_value:float=0
        self.max_raw_value:float=0
        self.max_value:float=0
        self.value:float=0
        self.min_read_value:float=64000
        self.max_read_value:float=0
        self.read_frequency=read_frequency #[Hz]
        self.TimerR=machine.Timer()
        self.broadcast=broadcast
        self.min_alarm_value:float=0
        self.check_min_alarm:bool=False
        self.max_alarm_value:float=64000
        self.check_max_alarm:bool=False
        self.avg_value:float=0
        if broadcast:
            self.TimerB=machine.Timer()
            self.broadcast_period:int=1000 #[ms]
        if queue_length>0:
            self.QueueValues=simple_queue.Queue(queue_length)
            self._avg_counter:int=0
            self.use_queue=True
        else:
            self.use_queue:bool=False
    
    def convert(self,x:float, in_min:float, in_max:float, out_min:float, out_max:float):
        """A method to convert sensor values"""
        if (in_max - in_min) ==0:
            return 0
        else:
            return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    def set_limits(self,min_value:float,max_value:float)->str:
        """Use this method to set upper and lower limits for this sensor."""
        self.min_value=min_value
        self.max_value=max_value
        return self.name+": New limits set to "+str(self.min_value)+" "+self.unit+" min and "+str(self.max_value)+" "+self.unit+" max."
    
    def set_min_alarm(self,min_alarm_value:float)->str:
        self.min_alarm_value=min_alarm_value
        self.check_min_alarm=True
        return "Min Alarm set to "+str(self.min_alarm_value)
    
    def set_max_alarm(self,max_alarm_value:float)->str:
        self.max_alarm_value=max_alarm_value
        self.check_max_alarm=True
        return "Max Alarm set to "+str(self.max_alarm_value)

    def read_raw(self)->float:
        """Raw reading. This method has to be overwritten by the Sensor specific child class."""
        raw_value=90 #Placeholder
        return raw_value

    def callback_read_value(self,timer)->None:
        """Read the raw value on the pin"""
        read_value=self.read_raw()
        # Adjust maximum and minimum values if necessary:
        if read_value<self.min_raw_value:
            self.min_raw_value=read_value
            if self.debug: 
                print("New minimum raw value set to "+str(self.min_raw_value))
        if read_value>self.max_raw_value:
            self.max_raw_value=read_value
            if self.debug: 
                print("New maximum raw value set to "+str(self.max_raw_value))
        if self.unit=="RPM":
            self.value=read_value
        else:
            self.value=self.convert(read_value,self.min_raw_value,self.max_raw_value,self.min_value,self.max_value)
        if self.value<self.min_read_value:
            self.min_read_value=self.value
        if self.value>self.max_read_value:
            self.max_read_value=self.value
        if self.use_queue:
            self.QueueValues.put(self.value)
        if self.check_min_alarm:
            if self.value<self.min_alarm_value:
                message=self.name+": measured value "+str(self.value)+" "+self.unit+"below set Alarm point of "+str(self.min_alarm_value)+" "+self.unit+"."
                raise Alarm(message)
        if self.check_max_alarm:
            if self.value>self.max_alarm_value:
                message=self.name+": measured value "+str(self.value)+" "+self.unit+"above set Alarm point of "+str(self.max_alarm_value)+" "+self.unit+"."
                raise Alarm(message)

    def start_reading(self)->str:
        """Starts timer and reads values regularly."""
        self.TimerR.init(mode=machine.Timer.PERIODIC,freq=self.read_frequency,callback=self.callback_read_value)
        return self.name+": Start reading values."

    def set_read_frequency(self,frequency:int):
        """Set the reading frequency"""
        self.TimerR.init(mode=machine.Timer.PERIODIC,freq=frequency,callback=self.callback_read_value)

    def stop_reading(self)->str:
        """Stops reading values."""
        self.TimerR.deinit()
        return self.name+": Reading stopped."

    def get_value(self)->float:
        """Returns the last saved value reading."""
        return self.value
    
    def callback_print_value(self,timer):
        """Prints value (later to given broadcast channel)."""
        if self.debug: 
            print("Here is the output:")
        print(self.name+": "+str(self.value)+' '+self.unit)
    
    def start_broadcasting(self)->str:
        """Starts to broadcast values"""
        self.TimerB.init(mode=machine.Timer.PERIODIC,period=self.broadcast_period,callback=self.callback_print_value)
        self.broadcast=True
        return self.name+": Start broadcasting values"
    
    def set_broadcast_period(self,period:int)->str:
        """Sets a new broadcast period [ms] and (re)-starts broadcast."""
        self.broadcast_period=period
        self.TimerB.init(mode=machine.Timer.PERIODIC,period=self.broadcast_period,callback=self.callback_print_value)
        self.broadcast=True
        return self.name+": Broadcast period set to "+str(self.broadcast_period)+"ms, broadcast restarted."

    def stop_broadcasting(self)->str:
        """Stops broadcasting position values."""
        self.TimerB.deinit()
        self.broadcast=False
        return self.name+": Stopped broadcasting."
    
    def get_avg_value(self):
        """Returns the average value stored, raises an exception if no queue is used."""
        if not self.use_queue:
            raise NoAvgValues()
        self.avg_value=self.QueueValues.get_avg()
        return self.avg_value
    
    def get_min_read_value(self)->float:
        """Returns the minimum measured value."""
        return self.min_read_value
    
    def get_max_read_value(self)->float:
        """Returns the maximum read value."""
        return self.max_read_value
    
    def start_debug(self)->str:
        """Starts debug mode of this sensor."""
        self.debug=True
        return self.name+": Start debug mode."
    
    def stop_debug(self)->str:
        """Stops debug mode of this sensor."""
        self.debug=False
        return self.name+": Stopped debug mode."
  
class int_Sensor(Sensor):
    def __init__(self, name: str, unit: str, read_frequency: int = 10, queue_length: int = 0, broadcast: bool = False) -> None:
        super().__init__(name, unit, read_frequency, queue_length, broadcast)
        self.min_raw_value:int=64000
        self.min_value:int=0
        self.max_raw_value:int=0
        self.max_value:int=0
        self.min_read_value:int=64000
        self.max_read_value:int=0
        self.min_alarm_value:int=0
        self.max_alarm_value:int=0
        self.avg_value:int=0
        self.value:int=0
        
    def convert(self, x:int, in_min:int, in_max:int, out_min:int, out_max:int):
        """A method to map values"""
        if (in_max - in_min) ==0:
            return 0
        else:
            return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def set_limits(self,min_value:int,max_value:int)->str:
        """Use this method to set upper and lower limits for this sensor."""
        self.min_value=min_value
        self.max_value=max_value
        return self.name+": New limits set to "+str(self.min_value)+" "+self.unit+" min and "+str(self.max_value)+" "+self.unit+" max."
    
    def set_min_alarm(self,min_alarm_value:int)->str:
        self.min_alarm_value=min_alarm_value
        self.check_min_alarm=True
        return "Min Alarm set to "+str(self.min_alarm_value)
    
    def set_max_alarm(self,max_alarm_value:int)->str:
        self.max_alarm_value=max_alarm_value
        self.check_max_alarm=True
        return "Max Alarm set to "+str(self.max_alarm_value)

    def read_raw(self)->int:
        """Raw reading. This method has to be overwritten by the Sensor specific child class."""
        raw_value=90 #Placeholder
        return raw_value
    
    def get_value(self)->int:
        """Returns the last saved value reading."""
        return self.value
    
    def get_min_read_value(self)->int:
        """Returns the minimum measured value."""
        return self.min_read_value
    
    def get_max_read_value(self)->int:
        """Returns the maximum read value."""
        return self.max_read_value
    
    
if __name__=="__main__":
    s1=Sensor("Rudder","°",read_frequency=100,queue_length=50,broadcast=True)
    out=s1.start_reading()
    print(out)
    utime.sleep_ms(1000)
    out=s1.start_broadcasting()
    print(out)
    utime.sleep_ms(1000)
    out=s1.stop_broadcasting()
    print(out)
    utime.sleep(1)
    out=s1.stop_reading()
    print(out)

        