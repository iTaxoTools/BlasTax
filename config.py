from resources import icons, pixmaps
from tasks import about, align, blast, create

title = "BLAST-Align"
icon = icons.blast
pixmap = pixmaps.blast

dashboard = "constrained"

show_open = True
show_save = False

tasks = [
    [
        create,
        blast,
        align,
    ],
    about,
]
