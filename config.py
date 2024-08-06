from resources import icons, pixmaps
from tasks import about, append, appendx, blast, create, museo

title = "BLAST-Align"
icon = icons.blast
pixmap = pixmaps.blast

dashboard = "grid"

show_open = True
show_save = False

tasks = [
    [create, blast],
    [append, appendx],
    [museo, about],
]
