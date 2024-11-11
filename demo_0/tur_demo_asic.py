#!/usr/bin/env python3

import sys
import argparse

sys.path.append(".") #python should have access to core scripts. I added this so you can give another path


from migen import *

from litex.gen import *

import tur_demo_platform # We need to import the platform for the project so builder can get the port/connections etc...

from litex.soc.cores.clock import *
from litex.soc.integration.soc import SoCRegion
from litex.soc.integration.soc_core import *
from litex.build.generic_platform import *

from litex.soc.integration.builder import *


from gpio import * # I imported the script of my custom core



# BaseSoC ------------------------------------------------------------------------------------------
class BaseSoC(SoCCore):
    def __init__(self, sys_clk_freq=int(50e6), **kwargs ):
        sys_clk_freq = int(50e6) # 50MHz clock for the system
        platform = tur_demo_platform.Platform() # I define the platform i will use for the SoC

        # CRG --------------------------------------------------------------------------------------
        #Clock Reset Generator. I will only create a core clk but i can create another clock domains too (TO DO)
        self.crg = crg = CRG(platform.request("core_clk"), rst=platform.request("core_rst"))
        # Here i have called core clock and core reset signals from the platform script
        
        self.mem_map = {
            "rom":      0x00000000,
            "iram":     0x01000000,
            "dram":     0x02000000,
        }
        # I created my custom memory map for the project. LiteX can handle it itself and there is defaults
        # But i wanted to make it custom as possible so we can stretch the design as we want.

        # SoC with CPU
        SoCCore.__init__(self, platform,
            cpu_type                 = "cv32e40p", # My choose of open-source CPU for my SoC
            cpu_variant              = "standard", # If there is a specific variant i want i can change it
            clk_freq                 = sys_clk_freq, # clock frequency of the system
            ident                    = "TURING Demo SoC with custom gpio core", ident_version=True,
            integrated_rom_size      = 0x200,
            integrated_main_ram_size = None, # i will disable the intagrated ram so i add my own iram and dram
            integrated_sram_size     = None,
            integrated_rom_init      = None,
            uart_name                = "serial", # I can add a serial uart to the system with 1 line of code :)
            with_uart                = True,     # If you don't want any uart you can disable it or use your own uart
            with_timer               = False,
            with_ctrl                = False,
        )
     
        # This is where we add our own ram as iram and dram
        # reason i do this is to be able to see them separately in the RTL
        # That may help us during the asic backend and rtl would be more clean
        self.add_ram("iram",
            origin  = self.mem_map["iram"],
            size    = 0x400,
        )
        
        self.add_ram("dram",
            origin  = self.mem_map["dram"],
            size    = 0x400,
        )
        

        # I will add my own GPIO core to the SoC and integrate it to the memory map so I can use it with C
        # GPIO -------------------------------------------------------------------------------------
        # This will call the gpio_controller from python and integrate it using the pins I specified 
        self.submodules.gpio = gpio_controller(platform, idr_pins=platform.request_all("user_sw"), odr_pins=platform.request_all("seg_disp"))
        self.bus.add_slave(name = "gpio", slave = self.gpio.bus, region=SoCRegion(
            origin = 0x80001000, # you can change the origin address based on your choice
            size   = 16, # you need to make sure your internal bus registers fits your address !!!
            cached = False
        ))

      

soc = BaseSoC() # And with that our SoC is done and ready to be build


# Build --------------------------------------------------------------------------------------------
# LiteX also can give you the software package for your SoC so you can easily test it with C (If you are using FPGA)
# In our case we can keep the compile_software False, and compile_gateware synthesizes your design with vivado so its False

builder = Builder(soc, output_dir="build", compile_software=False, compile_gateware=False)
builder.build(build_name="top")# Now SoC can be built using 