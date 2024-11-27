"""GUI entry point"""

import multiprocessing


def run():
    """
    Show the TaxiGui window and enter the main event loop.
    Imports are done locally to optimize multiprocessing.
    """

    import config
    from itaxotools.taxi_gui.app import Application, skin
    from itaxotools.taxi_gui.main import Main
    from tasks import translator

    config.tasks = [translator]

    app = Application()
    app.set_config(config)
    app.set_skin(skin)

    main = Main()
    main.widgets.header.toolLogo.setFixedWidth(188)
    main.resize(820, 580)
    main.show()

    app.exec()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    run()
