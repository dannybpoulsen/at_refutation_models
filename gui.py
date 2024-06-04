import argparse

import bitflipping.experiments.sudo
import bitflipping.uppaal.uppaal
import bitflipping.locator

parser = argparse.ArgumentParser(
    prog='Sudo Bitflip Model')

parser.add_argument ("--userpass",dest="user",default="1234")
parser.add_argument ("--stored",dest="stored",default="3234")
parser.add_argument ("--flips",dest="flips",default=5)
parser.add_argument ("--fixed",dest="new_version",action="store_true")

args = parser.parse_args()

locator = bitflipping.locator.Locator ("results")
uppaal = bitflipping.uppaal.uppaal.Uppaal ("/opt/uppaal")

sudo_experiments = bitflipping.experiments.sudo.GUI(uppaal)


sudo_experiments.runGUI (args.user.encode("'ascii'"),
                         args.stored.encode ('ascii'),
                         args.flips,
                         args.new_version)
