P_TX = 0.084  # Watts
P_RX = 0.073  # Watts

E_INIT = 2.0  # Joules
E_MIN = 0.5   # Joules  to operate

# charging  rate
P_CHARGING = 0.0005  # Watts

# idle discharge rate
P_IDLE = 0.001  # Watts

# transmission rate
TR_RATE = 128   # kbps

def decrease_transfer_energy(connectionDuration, energy):
    energy_dec = P_TX * connectionDuration/1000
    energy -= energy_dec
    return energy

def decrease_idle_time_energy(energy, discharging_rate=None, discharging_time=1):
        energy_dec = (discharging_rate or P_IDLE) * discharging_time
        energy -= energy_dec
        return energy

def increase_energy(energy, charging_time=1):
        energy += P_CHARGING * charging_time/1000
        return energy