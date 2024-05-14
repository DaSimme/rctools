# Classes for systems in functional RC-Models
import sensors
import actuators
import machine
import utime

class SetupError(Exception):
    """Error class for invalid setup."""
    pass

class WaterCoolingSystem:
    """A water cooling system for any other system."""
    def __init__(self):
        #Example:
        self.WatertempInSensor=sensors.TempSensor("Cooling water inlet temperature",1,0)
        self.WatertempOutSensor=sensors.TempSensor("Cooling water outlet temperature",1,0)
        self.waterpressure_in:float=0
        self.max_watertemp_in:float=30
        self.max_watertemp_out:float=60
        self.min_waterpressure_in:float=0.5
    pass

class FireFightingMonitor:
    """A fire fighting monitor with servos / gimbal, optional stabilisation"""
    pass

class BilgeSystem:
    """A system to monitor a compartment for water in bilge, operates bilge pump and gives appropriate feedback."""
    def __init__(self,compartment_name:str,pin_water,pin_pump) -> None:
        self.name=compartment_name
        self.status_operational:bool=False # If set True, system is up and running with automatic bilge pumps.
        name_wd=compartment_name+" bilge alarm"
        self.WaterSensor=sensors.WaterDetector(pin_water,name_wd)
        name_bp=compartment_name+" bilge pump"
        self.BilgePump=actuators.Pump(pin_pump,name_bp)
        self.check_period:int=1 # How many seconds pass until system checks status
        self.Timer=machine.Timer()
        self.last_water_detected=0
        self.has_water_in_bilge:bool=False
        self.bilge_pump_running:bool=False
        self.additional_runtime:int=5000 # ms additional runtime of pump after last water was detected.

    def callback_timer(self,timer):
        if self.WaterSensor.check_for_water():
            self.last_water_detected=utime.ticks_ms()
            self.BilgePump.switch_on()
            self.has_water_in_bilge=True
            self.bilge_pump_running=True
        else:
            if self.bilge_pump_running:
                self.has_water_in_bilge=False
                now=utime.ticks_ms()
                if utime.ticks_diff(now,self.last_water_detected)>self.additional_runtime:
                    self.BilgePump.switch_off()
                    self.bilge_pump_running=False

    def start_system(self):
        """Starts monitoring the bilge and operates pump as needed."""
        self.WaterSensor.start_reading()
        utime.sleep_ms(500)
        self.Timer.init(mode=machine.Timer.PERIODIC,period=self.check_period,callback=self.callback_timer)
        self.status_operational=True

    def stop_system(self):
        """Stops automatic operation of the system.
        Only possible when bilge pump is not running!"""
        if not self.bilge_pump_running:
            self.Timer.deinit()
            self.WaterSensor.stop_reading()
            self.status_operational=False

    def in_operation(self):
        """Returns True if system is running, False if in standby."""
        return self.status_operational

class Propulsion:
    """A class for a propulsion system, e.g. Controller, Motor, Sensors and water cooling system"""
    def __init__(self,number_of_motors:int=1) -> None:
        self.motors=[]
        for motor in range(1,number_of_motors):
            motor=actuators.Motor(1)
            self.motors.append(motor)

class FireFightingSystem:
    """A class for a fire fighting system, consisting e.g. of a pump, valves and a fire fighting monitor."""
    pass

class AnchorWinch:
    """A modular class for anchor winches, with chain brake, winch motor etc."""
    pass

class GeneralWinch:
    """A class for all other winches on deck, consisting e.g. of motor, sensors, and encoder"""
    pass

class NavigationSignals:
    """This class manages all navigation lights and shapes.
    Possible states: 
    0 - docked. All lights and shapes available for manual operation
    1 - moving. Navigation lights switched on (manual, brightness sensor or sunset / sunrise data)
    2 - restricted maneuverability. If dark, navigation lights and restricted maneuverability lights lightened, during daylight shapes of ball rhomb and ball are set.
    3 - towing. 
    4 - At anchor.
    Other states / setups to be includes, as per https://de.wikipedia.org/wiki/Lichterf%C3%BChrung"""

    def __init__(self,ship_length:float) -> None:
        self.ship_length=ship_length
        self.is_dark=False # Indicates if it is dark or daylight
        self.towing=False  # Trigger for towing signals
        self.restricted_maneuver=False 
        self.anchored=False
        self.moving=True
        self.all_lights=[]
        self.dimmer:int=0
        self.has_dim_potentiometer:bool=False
        self.debug=False
    
    def setup_position_lights(self,Pin_Toplight,Pin_PSLight,Pin_SBLight,Pin_RearLight,Pin_Toplight2=0):
        self.PSLight=actuators.Light(Pin_PSLight,"Port side navigation light")
        self.SBLight=actuators.Light(Pin_SBLight,"Starboard side navigation light")
        self.RearLight=actuators.Light(Pin_RearLight,"Rear navigation light")
        self.Toplight=actuators.Light(Pin_Toplight,"Navigation Toplight")
        self.Position_Lights=[self.PSLight,self.SBLight,self.RearLight,self.Toplight]
        if self.ship_length>50:
            if Pin_Toplight2 == 0:
                raise SetupError("Ship is longer than 50m, second top light required!")
            self.Toplight2=actuators.Light(Pin_Toplight2,"Second Toplight for navigation")
            self.Position_Lights.append(self.Toplight2)
        self.all_lights.extend(self.Position_Lights)

    def setup_towlights(self,Pin_Towlight1,Pin_Towlight2,Pin_Towlight3=0):
        self.Towlight1=actuators.Light(Pin_Towlight1,"First towlight")
        self.Towlight2=actuators.Light(Pin_Towlight2,"Second towlight")
        self.towlights=[self.Towlight1,self.Towlight2]
        if Pin_Towlight3>0:
            self.Towlight3=actuators.Light(Pin_Towlight3,"Third towlight")
            self.towlights.append(self.Towlight3)
        self.all_lights.extend(self.towlights)
        self.rhomb="Placeholder for a servo / winch to pull up the rhomb signal."

    def setup_restricted_manueverability(self,Pin_RM1,Pin_RM2,Pin_RM3):
        self.RMLight1=actuators.Light(Pin_RM1,"First light for reduced maneuverability")
        self.RMLight2=actuators.Light(Pin_RM2,"Second light for reduced maneuverability")
        self.RMLight3=actuators.Light(Pin_RM3,"Third light for reduced maneuverability")
        self.rm_lights=[self.RMLight1,self.RMLight2,self.RMLight3]
        self.all_lights.extend(self.rm_lights)
        self.BallRhombBall="Placeholder for a ball rhomb ball shape to be set"

    def dim_pot_callback(self,timer):
        raw_value=self.DimPotentiometer.get_value()
        if ((raw_value<self.dimmer-100) or (raw_value>self.dimmer+100)):
            self.dimmer=raw_value
            self.set_dimmer(self.dimmer)
            if self.debug:
                print(self.dimmer)

    def setup_dim_poti(self,pin_dim_poti):
        self.DimPotentiometer=sensors.int_Potentiometer(pin_dim_poti,"Navigation Light Dimmer"," ")
        self.DimPotentiometer.set_read_frequency(100)
        self.DimPotentiometer.start_reading()
        self.TimerR=machine.Timer()
        self.TimerR.init(mode=machine.Timer.PERIODIC,freq=10,callback=self.dim_pot_callback)
        self.has_dim_potentiometer=True

    def setup_anchor_lights(self,Pin_AL1,Pin_AL2=0):
        self.AnchorLight1=actuators.Light(Pin_AL1,"Anchorlight")
        self.anchor_lights=[self.AnchorLight1]
        if self.ship_length>50:  # Ships < 50m need only one anchor light.
            if Pin_AL2==0:
                raise SetupError("Ship is longer than 50m, second anchor light is required.")
            self.AnchorLight2=actuators.Light(Pin_AL2,"Second anchorlight")
            self.anchor_lights.append(self.AnchorLight2)
        self.all_lights.extend(self.anchor_lights)
        self.BallShape="Placeholder for ball shape in daylight anchoring."

    def set_daylight(self):
        self.is_dark=False
        #Switch off lights
        for light in self.all_lights:
            light.switch_off()
        #set shapes, if necessary
        if self.towing:
            print("Placeholder, towing shape to be set.")
        if self.restricted_maneuver:
            print("Placeholder, signs for restricted maneuver to be set.")
        if self.anchored:
            print("Placeholder, signs for anchor to be set.")

    def set_darkness(self):
        self.is_dark=True
        #switch lights on, as necessary
        if self.moving:
            for light in self.Position_Lights:
                light.switch_on()
        if self.anchored:
            for light in self.anchor_lights:
                light.switch_on()
            print("Placeholder, anchor shape to be taken down.")
        if self.towing:
            for light in self.towlights:
                light.switch_on()
            print("Placeholder, towing shape to be taken down.")
        if self.restricted_maneuver:
            for light in self.rm_lights:
                light.switch_on()
            print("Placeholder, shape for restricted maneuver to be taken in.")

    def start_moving(self):
        if self.is_dark:
            for light in self.Position_Lights:
                light.switch_on()
        self.moving=True

    def stop_moving(self):
        if self.is_dark:
            for light in self.Position_Lights:
                light.switch_off()
        self.moving=False

    def start_anchor(self):
        if self.is_dark:
            for light in self.anchor_lights:
                light.switch_on()
        else:
            print("Placeholder, anchor sign to be set.")
        self.anchored=True

    def stop_anchor(self):
        if self.is_dark:
            for light in self.anchor_lights:
                light.switch_off()
        else:
            print("Placeholder, anchor shape to be taken in.")
        self.anchored=False

    def start_towing(self):
        if self.is_dark:
            for light in self.towlights:
                light.switch_on()
        else:
            print("Placeholder, twing shape to be set.")
        self.towing=True

    def stop_towing(self):
        if self.is_dark:
            for light in self.towlights:
                light.switch_off()
        else:
            print("Placeholder, towing shape to be taken in.")
        self.towing=False

    def start_restricted_movement(self):
        if self.is_dark:
            for light in self.rm_lights:
                light.switch_on()
        else:
            print("Placeholder, ball rhomb ball to be set.")

    def stop_restricted_movement(self):
        if self.is_dark:
            for light in self.rm_lights:
                light.switch_off()
        else:
            print("Placeholder, shapes to be taken down.")

    def set_dimmer(self,dim_value:int):
        self.dimmer=dim_value
        for light in self.all_lights:
            light.set_dim_value(dim_value)
            if self.debug:
                print(light.name+" dimmed, value "+str(dim_value)+".")
    
class ShipSafetySystem:
    """This class handles water ingress detection, bilge pumps and emergency signals."""
    pass


if __name__=="__main__":
    WTC1=BilgeSystem("Compartment 1",27,25)
    WTC1.start_system()
    utime.sleep(60)
    WTC1.stop_system()
