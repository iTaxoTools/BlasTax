from .resources import icons, pixmaps
from .tasks import (
    about,
    append,
    appendx,
    blast,
    create,
    decont,
    fastmerge,
    fastsplit,
    groupmerge,
    museo,
    prepare,
    removal,
    scafos,
    translator,
    trim,
)

title = "BlasTax"
icon = icons.blastax
pixmap = pixmaps.blastax

dashboard = "groups"

show_open = True
show_save = False

tasks = [
    ["BLAST tools", 2],
    [create, blast],
    [append, appendx],
    [decont, museo],
    ["FASTA tools", 2],
    [prepare, fastsplit],
    [fastmerge, groupmerge],
    [removal, trim],
    ["Extras", 2],
    [scafos, translator],
    [about],
]
