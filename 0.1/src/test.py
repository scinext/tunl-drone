import minimaestro
mm = minimaestro.minimaestro('/dev/ttyACM0')
import acs709
acs = acs709.acs709(mm, 7)
acs.start()