"""GUI entry point"""

import multiprocessing


def run():
    """
    Show the TaxiGui window and enter the main event loop.
    Imports are done locally to optimize multiprocessing.
    """

    from itaxotools.taxi_gui.app import Application, skin

    from . import config
    from .main import Main

    app = Application()
    app.set_config(config)
    app.set_skin(skin)

    main = Main()
    main.widgets.header.toolLogo.setFixedWidth(188)
    main.resize(880, 554)
    main.setMinimumWidth(820)
    main.show()

    app.exec()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    run()
