import bitflipping.experiments.sudo
import bitflipping.uppaal.uppaal
import bitflipping.locator

locator = bitflipping.locator.Locator ("results")
uppaal = bitflipping.uppaal.uppaal.Uppaal ("/opt/uppaal")

sudo_experiments = bitflipping.experiments.sudo.Experiments(uppaal,locator)


sudo_experiments.run ()
