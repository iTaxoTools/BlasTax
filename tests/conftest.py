import multiprocessing

import pytest

# This is a workaround, fixed by TaxiGui commit @54897f1
# to be removed later


@pytest.fixture(autouse=True)
def terminate_child_processes():
    yield
    for child in multiprocessing.active_children():
        child.terminate()
        child.join(timeout=1)
