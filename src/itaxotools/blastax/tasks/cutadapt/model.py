import multiprocessing
from pathlib import Path

from itaxotools.common.bindings import Instance, Property
from itaxotools.taxi_gui.model.tasks import SubtaskModel

from ..common.model import BatchQueryModel, BlastTaskModel
from . import process, title
from .types import CutAdaptAction


class Model(BlastTaskModel):
    task_name = title

    input_paths = Property(BatchQueryModel, Instance)
    output_dir = Property(Path, Path())

    adapters_a_enabled = Property(bool, False)
    adapters_g_enabled = Property(bool, False)
    adapters_a_list = Property(str, "")
    adapters_g_list = Property(str, "")

    quality_trim_enabled = Property(bool, False)
    quality_trim_a = Property(int, 10)
    quality_trim_g = Property(int, 0)

    cutadapt_action = Property(CutAdaptAction, CutAdaptAction.trim)
    cutadapt_error_rate = Property(float, 0.1)
    cutadapt_overlap = Property(int, 3)
    cutadapt_num_threads = Property(int, 1)
    cutadapt_extra_args = Property(str, "")
    cutadapt_no_indels = Property(bool, False)
    cutadapt_reverse_complement = Property(bool, False)
    cutadapt_trim_poly_a = Property(bool, False)

    write_reports = Property(bool, False)

    append_timestamp = Property(bool, False)
    append_configuration = Property(bool, True)

    def __init__(self, name=None):
        super().__init__(name, daemon=False)
        self.can_open = True
        self.can_save = False

        self.input_paths.batch_mode = True
        self.input_paths.set_globs(["fa", "fas", "fasta", "fq", "fastq"])

        self._update_num_threads_default()
        self.binder.bind(self.input_paths.properties.parent_path, self.properties.output_dir)

        self.subtask_init = SubtaskModel(self, bind_busy=False)

        for handle in [
            self.input_paths.properties.ready,
            self.properties.output_dir,
            self.properties.adapters_a_enabled,
            self.properties.adapters_g_enabled,
            self.properties.adapters_a_list,
            self.properties.adapters_g_list,
            self.properties.quality_trim_enabled,
            self.properties.quality_trim_a,
            self.properties.quality_trim_g,
        ]:
            self.binder.bind(handle, self.checkReady)
        self.checkReady()

        self.subtask_init.autostart(process.initialize)

    def isReady(self):
        if not self.input_paths.ready:
            return False
        if self.output_dir == Path():
            return False
        if not (self.adapters_a_enabled or self.adapters_g_enabled or self.quality_trim_enabled):
            return False
        if self.adapters_a_enabled and not self.adapters_a_list.strip():
            return False
        if self.adapters_g_enabled and not self.adapters_g_list.strip():
            return False
        if self.quality_trim_enabled:
            if not (self.quality_trim_a or self.quality_trim_g):
                return False
        return True

    def start(self):
        super().start()
        self.exec(
            process.execute,
            input_paths=self.input_paths.get_all_paths(),
            output_dir=self.output_dir,
            adapters_a=self.adapters_a_list if self.adapters_a_enabled else "",
            adapters_g=self.adapters_g_list if self.adapters_g_enabled else "",
            quality_trim_enabled=self.quality_trim_enabled,
            quality_trim_a=self.quality_trim_a,
            quality_trim_g=self.quality_trim_g,
            cutadapt_action=self.cutadapt_action.action,
            cutadapt_error_rate=self.cutadapt_error_rate,
            cutadapt_overlap=self.cutadapt_overlap,
            cutadapt_num_threads=self.cutadapt_num_threads,
            cutadapt_extra_args=self.cutadapt_extra_args,
            cutadapt_no_indels=self.cutadapt_no_indels,
            cutadapt_reverse_complement=self.cutadapt_reverse_complement,
            cutadapt_trim_poly_a=self.cutadapt_trim_poly_a,
            write_reports=self.write_reports,
            append_timestamp=self.append_timestamp,
            append_configuration=self.append_configuration,
        )

    def _update_num_threads_default(self):
        cpus = multiprocessing.cpu_count()
        property = self.properties.cutadapt_num_threads
        setattr(property._parent, Property.key_default(property._key), cpus)
        property.set(cpus)

    def open(self, path: Path):
        self.input_paths.open(path)
