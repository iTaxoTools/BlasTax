"""GUI entry point"""


def run():
    """
    Show the TaxiGui window and enter the main event loop.
    Imports are done locally to optimize multiprocessing.
    """

    import config
    from itaxotools.taxi_gui.app import Application, skin
    from itaxotools.taxi_gui.main import Main

    app = Application()
    app.set_config(config)
    app.set_skin(skin)

    main = Main()
    main.widgets.header.toolLogo.setFixedWidth(208)
    main.resize(780, 540)
    main.show()

    app.exec()


if __name__ == "__main__":
    run()
