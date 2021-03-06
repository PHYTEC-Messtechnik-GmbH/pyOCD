"""
 mbed CMSIS-DAP debugger
 Copyright (c) 2006-2015 ARM Limited

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import sys, os
import logging, array

from time import sleep
from board import Board
from pyOCD.pyDAPAccess import DAPAccess

class BoardInfo(object):
    def __init__(self, name, target, binary):
        self.name = name
        self.target = target
        self.binary = binary

BOARD_ID_TO_INFO = {
              # Note: please keep board list sorted by ID!
              #
              # Board ID            Board Name              Target              Test Binary
                "0200": BoardInfo(  "FRDM-KL25Z",           "kl25z",            "l1_kl25z.bin"          ),
                "0201": BoardInfo(  "FRDM-KW41Z",           "kw41z4",           "l1_kw41z4.bin"         ),
                "0202": BoardInfo(  "USB-KW41Z",            "kw41z4",           "l1_kw41z4.bin"         ),
                "0203": BoardInfo(  "TWR-KL28Z72M",         "kl28z",            "l1_kl28z.bin",         ),
                "0204": BoardInfo(  "FRDM-KL02Z",           "kl02z",            "l1_kl02z.bin",         ),
                "0205": BoardInfo(  "FRDM-KL28Z",           "kl28z",            "l1_kl28z.bin",         ),
                "0215": BoardInfo(  "FRDM-KL28ZEM",         "kl28z",            "l1_kl28z.bin",         ),
                "0206": BoardInfo(  "TWR-KE18F",            "ke18f16",          "l1_ke18f16.bin",       ),
                "0210": BoardInfo(  "FRDM-KL05Z",           "kl05z",            "l1_kl05z.bin",         ),
                "0213": BoardInfo(  "FRDM-KE15Z",           "ke15z7",           "l1_ke15z7.bin",        ),
                "0214": BoardInfo(  "Hexiwear",             "k64f",             "l1_k64f.bin",          ),
                "0216": BoardInfo(  "HVP-KE18F",            "ke18f16",          "l1_ke18f16.bin",       ),
                "0217": BoardInfo(  "FRDM-K82F",            "k82f25615",        "l1_k82f.bin",          ),
                "0218": BoardInfo(  "FRDM-KL82Z",           "kl82z7",           "l1_kl82z.bin",         ),
                "0220": BoardInfo(  "FRDM-KL46Z",           "kl46z",            "l1_kl46z.bin",         ),
                "0224": BoardInfo(  "FRDM-K28F",            "k28f15",           "l1_k28f.bin",          ),
                "0230": BoardInfo(  "FRDM-K20D50M",         "k20d50m",          "l1_k20d50m.bin",       ),
                "0231": BoardInfo(  "FRDM-K22F",            "k22f",             "l1_k22f.bin",          ),
                "0240": BoardInfo(  "FRDM-K64F",            "k64f",             "l1_k64f.bin",          ),
                "0260": BoardInfo(  "FRDM-KL26Z",           "kl26z",            "l1_kl26z.bin",         ),
                "0261": BoardInfo(  "FRDM-KL27Z",           "kl27z4",            "l1_kl27z.bin",         ),
                "0262": BoardInfo(  "FRDM-KL43Z",           "kl43z4",           "l1_kl26z.bin",         ),
                "0290": BoardInfo(  "FRDM-KW40Z",           "kw40z4",           "l1_kw40z.bin",         ),
                "0298": BoardInfo(  "FRDM-KV10Z",           "kv10z7",           "l1_kl25z.bin"          ),
                "0300": BoardInfo(  "TWR-KV11Z75M",         "kv11z7",           "l1_kl25z.bin"          ),
                "0311": BoardInfo(  "FRDM-K66F",            "k66f18",           "l1_k66f.bin",          ),
                "0320": BoardInfo(  "FRDM-KW01Z9032",       "kw01z4",           "l1_kl26z.bin"          ),
                "0321": BoardInfo(  "USB-KW01Z",            "kw01z4",           "l1_kl25z.bin"          ),
                "0324": BoardInfo(  "USB-KW40Z",            "kw40z4",           "l1_kl25z.bin"          ),
                "0400": BoardInfo(  "maxwsnenv",            "maxwsnenv",        "l1_maxwsnenv.bin",     ),
                "0405": BoardInfo(  "max32600mbed",         "max32600mbed",     "l1_max32600mbed.bin",  ),
                "0824": BoardInfo(  "LPCXpresso824-MAX",    "lpc824",           "l1_lpc824.bin",        ),
                "1054": BoardInfo(  "LPCXpresso54114-MAX",  "lpc54114",         "l1_lpc54114.bin",      ),
                "1010": BoardInfo(  "mbed NXP LPC1768",     "lpc1768",          "l1_lpc1768.bin",       ),
                "1017": BoardInfo(  "mbed HRM1017",         "nrf51",            "l1_nrf51.bin",         ),
                "1018": BoardInfo(  "Switch-Science-mbed-LPC824", "lpc824",     "l1_lpc824.bin",        ),
                "1019": BoardInfo(  "mbed TY51822r3",       "nrf51",            "l1_nrf51.bin",         ),
                "1040": BoardInfo(  "mbed NXP LPC11U24",    "lpc11u24",         "l1_lpc11u24.bin",      ),
                "1050": BoardInfo(  "NXP LPC800-MAX",       "lpc800",           "l1_lpc800.bin",        ),
                "1060": BoardInfo(  "EA-LPC4088",           "lpc4088qsb",       "l1_lpc4088qsb.bin",    ),
                "1062": BoardInfo(  "EA-LPC4088-Display-Module", "lpc4088dm",   "l1_lpc4088dm.bin",     ),
                "1070": BoardInfo(  "nRF51822-mKIT",        "nrf51",            "l1_nrf51.bin",         ),
                "1080": BoardInfo(  "DT01 + MB2001",        "stm32f103rc",      "l1_stm32f103rc.bin",   ),
                "1090": BoardInfo(  "DT01 + MB00xx",        "stm32f051",        "l1_stm32f051.bin",     ),
                "1090": BoardInfo(  "RedBearLab-nRF51822",  "nrf51",            "l1_nrf51.bin",         ),
                "1095": BoardInfo(  "RedBearLab-BLE-Nano",  "nrf51",            "l1_nrf51.bin",         ),
                "1100": BoardInfo(  "nRF51-DK",             "nrf51",            "l1_nrf51-dk.bin",      ),
                "1101": BoardInfo(  "nRF52-DK",             "nrf52",            "l1_nrf52-dk.bin",      ),
                "1200": BoardInfo(  "NCS36510-EVK",         "ncs36510",         "l1_ncs36510-evk.bin",  ),
                "1114": BoardInfo(  "mbed LPC1114FN28",     "lpc11xx_32",       "l1_mbed_LPC1114FN28.bin",),
                "1120": BoardInfo(  "nRF51-Dongle",         "nrf51",            "l1_nrf51.bin",         ),
                "1234": BoardInfo(  "u-blox-C027",          "lpc1768",          "l1_lpc1768.bin",       ),
                "1600": BoardInfo(  "Bambino 210",          "lpc4330",          "l1_lpc4330.bin",       ),
                "1605": BoardInfo(  "Bambino 210E",         "lpc4330",          "l1_lpc4330.bin",       ),
                "2201": BoardInfo(  "WIZwik_W7500",         "w7500",            "l1_w7500mbed.bin",     ),
                "4600": BoardInfo(  "Realtek RTL8195AM",    "rtl8195am",        "l1_rtl8195am.bin",     ),
                "7402": BoardInfo(  "mbed 6LoWPAN Border Router HAT", "k64f",   "l1_k64f.bin",          ),
                "9004": BoardInfo(  "Arch Pro",             "lpc1768",          "l1_lpc1768.bin",       ),
                "9009": BoardInfo(  "Arch BLE",             "nrf51",            "l1_nrf51.bin",         ),
                "9012": BoardInfo(  "Seeed Tiny BLE",       "nrf51",            "l1_nrf51.bin",         ),
                "9900": BoardInfo(  "Microbit",             "nrf51",            "l1_microbit.bin",      ),
                "C004": BoardInfo(  "tinyK20",              "k20d50m",          "l1_k20d50m.bin",       ),
                "C006": BoardInfo(  "VBLUno51",             "nrf51",            "l1_nrf51.bin",         ),
              }

mbed_vid = 0x0d28
mbed_pid = 0x0204

class MbedBoard(Board):
    """
    This class inherits from Board and is specific to mbed boards.
    Particularly, this class allows you to dynamically determine
    the type of all boards connected based on the id board
    """
    def __init__(self, link, target=None, frequency=1000000):
        """
        Init the board
        """
        self.native_target = None
        self.test_binary = None
        unique_id = link.get_unique_id()
        board_id = unique_id[0:4]
        self.name = "Unknown Board"
        if board_id in BOARD_ID_TO_INFO:
            board_info = BOARD_ID_TO_INFO[board_id]
            self.name = board_info.name
            self.native_target = board_info.target
            self.test_binary = board_info.binary

        # Unless overridden use the native target
        if target is None:
            target = self.native_target

        if target is None:
            logging.warning("Unsupported board found %s", board_id)
            target = "cortex_m"

        super(MbedBoard, self).__init__(target, link, frequency)
        self.unique_id = unique_id
        self.target_type = target

    def getUniqueID(self):
        """
        Return the unique id of the board
        """
        return self.unique_id

    def getTargetType(self):
        """
        Return the type of the board
        """
        return self.target_type

    def getTestBinary(self):
        """
        Return name of test binary file
        """
        return self.test_binary

    def getBoardName(self):
        """
        Return board name
        """
        return self.name

    def getInfo(self):
        """
        Return info on the board
        """
        return self.name + " [" + self.target_type + "]"

    @staticmethod
    def listConnectedBoards(dap_class=DAPAccess):
        """
        List the connected board info
        """
        all_mbeds = MbedBoard.getAllConnectedBoards(dap_class, close=True,
                                                    blocking=False)
        index = 0
        if len(all_mbeds) > 0:
            for mbed in all_mbeds:
                print("%d => %s boardId => %s" % (index, mbed.getInfo().encode('ascii', 'ignore'), mbed.unique_id))
                index += 1
        else:
            print("No available boards are connected")

    @staticmethod
    def getAllConnectedBoards(dap_class=DAPAccess, close=False, blocking=True,
                              target_override=None, frequency=1000000):
        """
        Return an array of all mbed boards connected
        """

        mbed_list = []
        while True:

            connected_daps = dap_class.get_connected_devices()
            for dap_access in connected_daps:
                new_mbed = MbedBoard(dap_access, target_override, frequency)
                mbed_list.append(new_mbed)

            #TODO - handle exception on open
            if not close:
                for dap_access in connected_daps:
                    dap_access.open()

            if not blocking:
                break
            elif len(mbed_list) > 0:
                break
            else:
                sleep(0.01)
            assert len(mbed_list) == 0

        return mbed_list

    @staticmethod
    def chooseBoard(dap_class=DAPAccess, blocking=True, return_first=False,
                    board_id=None, target_override=None, frequency=1000000,
                    init_board=True):
        """
        Allow you to select a board among all boards connected
        """
        all_mbeds = MbedBoard.getAllConnectedBoards(dap_class, True, blocking,
                                                    target_override, frequency)

        # If a board ID is specified remove all other boards
        if board_id != None:
            new_mbed_list = []
            for mbed in all_mbeds:
                if mbed.unique_id == (board_id):
                    new_mbed_list.append(mbed)
            assert len(new_mbed_list) <= 1
            all_mbeds = new_mbed_list

        # Return if no boards are connected
        if all_mbeds == None or len(all_mbeds) <= 0:
            if board_id is None:
                print("No connected boards")
            else:
                print("Board %s is not connected" % board_id)
            return None # No boards to close so it is safe to return

        # Select first board
        if return_first:
            all_mbeds = all_mbeds[0:1]

        # Ask use to select boards if there is more than 1 left
        if len(all_mbeds) > 1:
            index = 0
            print "id => usbinfo | boardname"
            for mbed in all_mbeds:
                print "%d => %s" % (index, mbed.getInfo().encode('ascii', 'ignore'))
                index += 1
            while True:
                print "input id num to choice your board want to connect"
                line = sys.stdin.readline()
                valid = False
                try:
                    ch = int(line)
                    valid = 0 <= ch < len(all_mbeds)
                except ValueError:
                    pass
                if not valid:
                    logging.info("BAD CHOICE: %s", line)
                    index = 0
                    for mbed in all_mbeds:
                        print "%d => %s" % (index, mbed.getInfo())
                        index += 1
                else:
                    break
            all_mbeds = all_mbeds[ch:ch + 1]

        assert len(all_mbeds) == 1
        mbed = all_mbeds[0]
        mbed.link.open()
        if init_board:
            try:
                mbed.init()
            except:
                mbed.link.close()
                raise
        return mbed
