from resources import icons, pixmaps
from tasks import about, align, alignx, blast, create, museo

title = "BLAST-Align"
icon = icons.blast
pixmap = pixmaps.blast

dashboard = "grid"

show_open = True
show_save = False

tasks = [
    [create, blast],
    [align, alignx],
    [museo, about],
]
