"""Main file for the ship management system on RP2040 (Rasperry Pico)
Operational states:
0 - Bench mode: All systems functional, except propulsion and water pumps.
1 - Docked in port: All systems functional, except propulsion, anchor
2 - Navigation: All systems operational, navigation lights / signs set
3 - At anchor: Propulsion and steering in standby, all other systems operational. Anchor lights / sign set.
4 - Towing: All systems operational, towing lights / sign set.
5 - Fire Fighting: All systems operational, restricted maneuverability indicated.
"""
import lib.systems as systems
import utime

class Ship:
    """Main class to include all systems."""
    def __init__(self) -> None:
        #ToDo: Read settings for subsystems from file, initialize all systems.
        self.ship_length=30 # [m]
        self.Propulsion=systems.Propulsion()
        self.NavSignals=systems.NavigationSignals(self.ship_length)
        self.NavSignals.setup_position_lights(13,2,3,6)
        self.NavSignals.setup_restricted_menueverability(7,8,9)
        self.NavSignals.setup_towlights(10,11)
        
if __name__=="__main__":
    Schlepper=Ship()
    Schlepper.NavSignals.setup_dim_poti(26)
    utime.sleep(10)
    Schlepper.NavSignals.debug=True
    for counter in range(1,3):
        Schlepper.NavSignals.start_moving()
        Schlepper.NavSignals.set_darkness()
        print(str(Schlepper.NavSignals.DimPotentiometer.get_value()))
        utime.sleep(10)
        val=Schlepper.NavSignals.DimPotentiometer.get_value()
        Schlepper.NavSignals.start_towing()
        Schlepper.NavSignals.set_dimmer(val)
        utime.sleep(10)
        val=Schlepper.NavSignals.DimPotentiometer.get_value()
        Schlepper.NavSignals.set_dimmer(val)
        Schlepper.NavSignals.stop_towing()
        utime.sleep(10)
        val=Schlepper.NavSignals.DimPotentiometer.get_value()
        Schlepper.NavSignals.start_restricted_movement()
        utime.sleep(10)
        Schlepper.NavSignals.stop_restricted_movement()
        utime.sleep(10)
        Schlepper.NavSignals.stop_moving()
        utime.sleep(10)