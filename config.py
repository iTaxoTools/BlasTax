from resources import icons, pixmaps
from tasks import about, append, appendx, blast, create, museo

title = "BlasTax"
icon = icons.blastax
pixmap = pixmaps.blastax

dashboard = "grid"

show_open = True
show_save = False

tasks = [
    [create, blast],
    [append, appendx],
    [museo, about],
]
