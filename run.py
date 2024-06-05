import bitflipping.experiments.sudo
import bitflipping.uppaal.uppaal
import bitflipping.locator
import sys

if len(sys.argv) > 1:
    seed = sys.argv[1]
else:
    import datetime
    seed = datetime.datetime.now().timestamp()

locator = bitflipping.locator.Locator ("results")
uppaal = bitflipping.uppaal.uppaal.Uppaal ("/opt/uppaal",seed)

sudo_experiments = bitflipping.experiments.sudo.Experiments(uppaal,locator)


sudo_experiments.run ()
