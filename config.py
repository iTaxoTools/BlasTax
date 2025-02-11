from resources import icons, pixmaps
from tasks import (
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
    rename,
    scafos,
    translator,
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
    [fastmerge, fastsplit],
    [groupmerge, rename],
    ["Extras", 2],
    [scafos, translator],
    [about],
]
