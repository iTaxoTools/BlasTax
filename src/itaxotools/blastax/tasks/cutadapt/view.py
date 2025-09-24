from PySide6 import QtCore, QtGui, QtWidgets

from pathlib import Path

from itaxotools.common.utility import AttrDict
from itaxotools.taxi_gui import app
from itaxotools.taxi_gui.utility import human_readable_seconds
from itaxotools.taxi_gui.view.animations import VerticalRollAnimation
from itaxotools.taxi_gui.view.cards import Card
from itaxotools.taxi_gui.view.widgets import LongLabel

from ..common.view import (
    BatchProgressCard,
    BatchQuerySelector,
    BlastTaskView,
    GraphicTitleCard,
    OptionCard,
    OutputDirectorySelector,
)
from ..common.widgets import (
    ConsolePropertyLineEdit,
    FloatPropertyLineEdit,
    GrowingTextEdit,
    IntPropertyLineEdit,
)
from . import long_description, pixmap_medium, title
from .types import CutAdaptResults
from .widgets import CutAdaptActionCombobox


class AdapterSelector(OptionCard):
    title_text = "Title text"
    list_text = "List text."
    list_placeholder = "List placeholder..."

    def __init__(self, parent=None):
        super().__init__(self.title_text, "", parent)
        self.controls.title.setFixedWidth(300)
        self.draw_list()

    def draw_list(self):
        label = LongLabel(self.list_text)

        list = GrowingTextEdit()
        list.document().setDocumentMargin(8)
        list.setPlaceholderText(self.list_placeholder)
        fixed_font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        list.setFont(fixed_font)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(label)
        layout.addWidget(list, 1)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.roll = VerticalRollAnimation(widget)
        self.controls.options_widget = widget
        self.controls.list = list

        self.toggled.connect(self.set_options_visible)

        self.addWidget(widget)

    def set_options_visible(self, value: bool):
        self.controls.options_widget.roll.setAnimatedVisible(value)


class AdapterASelector(AdapterSelector):
    title_text = "Cut 3’ adapters (at sequence end)"
    list_text = (
        "Enter a list of 3’ adapters separated by new lines. "
        "A 3’ adapter is assumed to be ligated to the 3’ end of your sequences of interest. "
        "When such an adapter is found, the adapter sequence itself and the sequence following it (if there is any) are trimmed. "
        "You may use Cutadapt's syntax to define anchored, non-internal, linked adapters or adapter-specific parameters. "
        "In the examples below, replace 'ADAPTER' with the actual nucleotide sequence of your adapter. "
    )
    list_placeholder = (
        "ADAPTER  -> regular 3’ adapter, full or partial"
        "\n"
        "ADAPTER$ -> anchored 3’, must be at sequence end, full matches only"
        "\n"
        "ADAPTERX -> non-internal 3’, like anchored but can be partial"
        "\n"
        "ADAPTER1...ADAPTER2 -> linked adapters, ^ADAPTER1 and ADAPTER2$ make adapters mandatory"
        "\n"
        "ADAPTER;e=0.2;o=5 -> adapter with maximum error rate = 0.2 and minimum overlap = 5"
    )


class AdapterGSelector(AdapterSelector):
    title_text = "Cut 5’ adapters (at sequence start)"
    list_text = (
        "Enter a list of 5’ adapters separated by new lines. "
        "A 5’ adapter is assumed to be ligated to the 5’ end of your sequences of interest. "
        "When such an adapter is found, the adapter sequence itself and the sequence preceding it (if there is any) are trimmed. "
        "You may use Cutadapt's syntax to define anchored, non-internal adapters or adapter-specific parameters. "
        "In the examples below, replace 'ADAPTER' with the actual nucleotide sequence of your adapter. "
    )
    list_placeholder = (
        " ADAPTER -> regular 5’ adapter, full or partial"
        "\n"
        "^ADAPTER -> anchored 5’, must be at sequence start, full matches only"
        "\n"
        "XADAPTER -> non-internal 5’, like anchored but can be partial"
        "\n"
        " ADAPTER;e=0.2;o=5 -> adapter with maximum error rate = 0.2 and minimum overlap = 5"
    )


class QualityTrimmingSelector(OptionCard):
    help_text_a = (
        "Remove low-quality bases from the start or end of each read before adapter trimming. "
        "This option is available only for FASTQ files, since quality scores are required. "
        "Trimming is performed using the BWA-style algorithm, which evaluates read sequences "
        "and may retain bases slightly below the cutoff if they are surrounded by higher-quality bases."
    )

    help_text_b = (
        "Each cutoff value sets the quality threshold used by the algorithm to decide which bases to trim. "
        "Higher values lead to more aggressive trimming and improved overall read quality. "
        "For reference, a Phred score of 10 corresponds to 90% accuracy, a score of 20 corresponds to 99% accuracy, "
        "and a score of 30 corresponds to 99.9% accuracy."
    )

    def __init__(self, title: str, parent=None):
        super().__init__(title, "", parent)
        self.controls.title.setFixedWidth(300)
        self.draw_list()

    def draw_list(self):
        label_a = LongLabel(self.help_text_a)
        label_b = LongLabel(self.help_text_b)

        options_layout = QtWidgets.QGridLayout()
        options_layout.setColumnMinimumWidth(0, 16)
        options_layout.setColumnMinimumWidth(1, 94)
        options_layout.setColumnMinimumWidth(3, 16)
        options_layout.setColumnStretch(4, 1)
        options_layout.setHorizontalSpacing(16)
        options_layout.setVerticalSpacing(8)
        row = 0

        name = QtWidgets.QLabel("3’ cutoff:")
        field = IntPropertyLineEdit()
        description = QtWidgets.QLabel("Applied to the end of each read. Lower cutoff means more bases kept.")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(name, row, 1)
        options_layout.addWidget(field, row, 2)
        options_layout.addWidget(description, row, 4)
        self.controls.quality_trim_a = field
        row += 1

        name = QtWidgets.QLabel("5’ cutoff:")
        field = IntPropertyLineEdit()
        description = QtWidgets.QLabel("Applied to the start of each read. Often left at 0 for Illumina data.")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(name, row, 1)
        options_layout.addWidget(field, row, 2)
        options_layout.addWidget(description, row, 4)
        self.controls.quality_trim_g = field
        row += 1

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(label_a)
        layout.addLayout(options_layout, 1)
        layout.addWidget(label_b)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        widget.roll = VerticalRollAnimation(widget)
        self.controls.options_widget = widget
        self.controls.list = list

        self.toggled.connect(self.set_options_visible)

        self.addWidget(widget)

    def set_options_visible(self, value: bool):
        self.controls.options_widget.roll.setAnimatedVisible(value)


class CutadaptOptionSelector(Card):
    def __init__(self, parent=None):
        super().__init__(parent)
        label = QtWidgets.QLabel("Cutadapt options:")
        label.setStyleSheet("""font-size: 16px;""")
        label.setMinimumWidth(150)

        description = QtWidgets.QLabel("Parametrize the arguments passed to Cutadapt.")

        title_layout = QtWidgets.QHBoxLayout()
        title_layout.addWidget(label)
        title_layout.addWidget(description, 1)
        title_layout.setSpacing(16)

        options_layout = QtWidgets.QGridLayout()
        options_layout.setColumnMinimumWidth(0, 16)
        options_layout.setColumnMinimumWidth(1, 94)
        options_layout.setColumnMinimumWidth(3, 16)
        options_layout.setColumnStretch(4, 1)
        options_layout.setHorizontalSpacing(16)
        options_layout.setVerticalSpacing(8)
        row = 0

        name = QtWidgets.QLabel("Action:")
        field = CutAdaptActionCombobox()
        description = QtWidgets.QLabel("What to do when a match is found")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(name, row, 1)
        options_layout.addWidget(field, row, 2)
        options_layout.addWidget(description, row, 4)
        self.controls.cutadapt_action = field
        row += 1

        name = QtWidgets.QLabel("Error rate:")
        field = FloatPropertyLineEdit()
        description = QtWidgets.QLabel("Maximum allowed error rate (or absolute number of errors if greater than 1.0)")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(name, row, 1)
        options_layout.addWidget(field, row, 2)
        options_layout.addWidget(description, row, 4)
        self.controls.cutadapt_error_rate = field
        row += 1

        name = QtWidgets.QLabel("Overlap:")
        field = IntPropertyLineEdit()
        description = QtWidgets.QLabel("Minimum overlap between read and adapter for an adapter to be considered")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(name, row, 1)
        options_layout.addWidget(field, row, 2)
        options_layout.addWidget(description, row, 4)
        self.controls.cutadapt_overlap = field
        row += 1

        name = QtWidgets.QLabel("Threads:")
        field = IntPropertyLineEdit()
        description = QtWidgets.QLabel("Number of threads (CPUs) to use")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_layout.addWidget(name, row, 1)
        options_layout.addWidget(field, row, 2)
        options_layout.addWidget(description, row, 4)
        self.controls.cutadapt_num_threads = field
        row += 1

        options_long_layout = QtWidgets.QGridLayout()
        options_long_layout.setContentsMargins(0, 0, 0, 0)
        options_long_layout.setColumnMinimumWidth(0, 16)
        options_long_layout.setColumnMinimumWidth(1, 94)
        options_long_layout.setColumnStretch(2, 1)
        options_long_layout.setHorizontalSpacing(16)
        options_long_layout.setVerticalSpacing(8)
        row = 0

        name = QtWidgets.QLabel("Extras:")
        field = ConsolePropertyLineEdit()
        field.setPlaceholderText("Extra arguments to pass to the BLAST+ executable")
        description.setStyleSheet("QLabel { font-style: italic; }")
        options_long_layout.addWidget(name, row, 1)
        options_long_layout.addWidget(field, row, 2)
        self.controls.cutadapt_extra_args = field
        row += 1

        options_checks_layout = QtWidgets.QVBoxLayout()
        options_checks_layout.setContentsMargins(16, 4, 0, 8)
        options_checks_layout.setSpacing(8)

        field = QtWidgets.QCheckBox("Disallow indels in alignments (mismatches are always allowed).")
        self.controls.cutadapt_no_indels = field
        options_checks_layout.addWidget(field)

        field = QtWidgets.QCheckBox("Check both the read and its reverse complement for adapter matches.")
        self.controls.cutadapt_reverse_complement = field
        options_checks_layout.addWidget(field)

        field = QtWidgets.QCheckBox("Trim poly-A tails (done after adapter trimming).")
        self.controls.cutadapt_trim_poly_a = field
        options_checks_layout.addWidget(field)

        field = QtWidgets.QCheckBox("Write a report with adapter statistics for each input file.")
        self.controls.write_reports = field
        options_checks_layout.addWidget(field)

        self.addLayout(title_layout)
        self.addLayout(options_layout)
        self.addLayout(options_long_layout)
        self.addLayout(options_checks_layout)

    def set_outfmt_options_visible(self, value: bool):
        self.controls.blast_outfmt_options.setVisible(value)
        self.controls.blast_outfmt_options_label.setVisible(value)


class View(BlastTaskView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.draw_cards()

    def draw_cards(self):
        self.cards = AttrDict()
        self.cards.title = GraphicTitleCard(title, long_description, pixmap_medium.resource, self)
        self.cards.progress = BatchProgressCard(self)
        self.cards.input = BatchQuerySelector("Input sequences", self)
        self.cards.output = OutputDirectorySelector("\u25C0  Output folder", self)
        self.cards.adapters_a = AdapterASelector(self)
        self.cards.adapters_g = AdapterGSelector(self)
        self.cards.trimming = QualityTrimmingSelector("Quality trimming", self)
        self.cards.cutadapt_options = CutadaptOptionSelector(self)

        self.cards.input.set_batch_only(True)

        self.cards.input.set_placeholder_text("Sequences that will be processed")
        self.cards.output.set_placeholder_text("Folder that will contain all output files")

        layout = QtWidgets.QVBoxLayout()
        for card in self.cards:
            layout.addWidget(card)
        layout.addStretch(1)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)

        self.setLayout(layout)

    def setObject(self, object):
        self.object = object
        self.binder.unbind_all()

        self.binder.bind(object.notification, self.showNotification)
        self.binder.bind(object.report_results, self.report_results)
        self.binder.bind(object.request_confirmation, self.request_confirmation)
        self.binder.bind(object.progression, self.cards.progress.showProgress)

        self.binder.bind(object.properties.name, self.cards.title.setTitle)
        self.binder.bind(object.properties.busy, self.cards.progress.setVisible)

        self.cards.input.bind_batch_model(self.binder, object.input_paths)

        self.binder.bind(object.properties.output_dir, self.cards.output.set_path)
        self.binder.bind(self.cards.output.selectedPath, object.properties.output_dir)

        self.binder.bind(
            object.properties.append_configuration, self.cards.output.controls.append_configuration.setChecked
        )
        self.binder.bind(
            self.cards.output.controls.append_configuration.toggled, object.properties.append_configuration
        )

        self.binder.bind(object.properties.adapters_a_enabled, self.cards.adapters_a.setChecked)
        self.binder.bind(self.cards.adapters_a.toggled, object.properties.adapters_a_enabled)
        self.cards.adapters_a.set_options_visible(object.adapters_a_enabled)

        self.binder.bind(object.properties.adapters_g_enabled, self.cards.adapters_g.setChecked)
        self.binder.bind(self.cards.adapters_g.toggled, object.properties.adapters_g_enabled)
        self.cards.adapters_g.set_options_visible(object.adapters_g_enabled)

        self.binder.bind(object.properties.adapters_a_list, self.cards.adapters_a.controls.list.setText)
        self.binder.bind(self.cards.adapters_a.controls.list.textEditedSafe, object.properties.adapters_a_list)

        self.binder.bind(object.properties.adapters_g_list, self.cards.adapters_g.controls.list.setText)
        self.binder.bind(self.cards.adapters_g.controls.list.textEditedSafe, object.properties.adapters_g_list)

        self.binder.bind(object.properties.quality_trim_enabled, self.cards.trimming.setChecked)
        self.binder.bind(self.cards.trimming.toggled, object.properties.quality_trim_enabled)
        self.cards.trimming.set_options_visible(object.quality_trim_enabled)

        self.cards.trimming.controls.quality_trim_a.bind_property(object.properties.quality_trim_a)
        self.cards.trimming.controls.quality_trim_g.bind_property(object.properties.quality_trim_g)

        self.binder.bind(
            object.properties.cutadapt_action, self.cards.cutadapt_options.controls.cutadapt_action.setValue
        )
        self.binder.bind(
            self.cards.cutadapt_options.controls.cutadapt_action.valueChanged, object.properties.cutadapt_action
        )

        self.cards.cutadapt_options.controls.cutadapt_error_rate.bind_property(object.properties.cutadapt_error_rate)
        self.cards.cutadapt_options.controls.cutadapt_overlap.bind_property(object.properties.cutadapt_overlap)
        self.cards.cutadapt_options.controls.cutadapt_num_threads.bind_property(object.properties.cutadapt_num_threads)
        self.cards.cutadapt_options.controls.cutadapt_extra_args.bind_property(object.properties.cutadapt_extra_args)

        self.binder.bind(
            object.properties.cutadapt_no_indels, self.cards.cutadapt_options.controls.cutadapt_no_indels.setChecked
        )
        self.binder.bind(
            self.cards.cutadapt_options.controls.cutadapt_no_indels.toggled, object.properties.cutadapt_no_indels
        )

        self.binder.bind(
            object.properties.cutadapt_reverse_complement,
            self.cards.cutadapt_options.controls.cutadapt_reverse_complement.setChecked,
        )
        self.binder.bind(
            self.cards.cutadapt_options.controls.cutadapt_reverse_complement.toggled,
            object.properties.cutadapt_reverse_complement,
        )

        self.binder.bind(
            object.properties.cutadapt_trim_poly_a, self.cards.cutadapt_options.controls.cutadapt_trim_poly_a.setChecked
        )
        self.binder.bind(
            self.cards.cutadapt_options.controls.cutadapt_trim_poly_a.toggled, object.properties.cutadapt_trim_poly_a
        )

        self.binder.bind(object.properties.write_reports, self.cards.cutadapt_options.controls.write_reports.setChecked)
        self.binder.bind(self.cards.cutadapt_options.controls.write_reports.toggled, object.properties.write_reports)

        self.binder.bind(object.properties.editable, self.setEditable)

    def report_results(self, task_name: str, results: CutAdaptResults):
        msg_info = f"Total reads processed: {results.total_reads}"
        if results.quality_trimmed >= 0:
            msg_info += f"\nQuality trimmed: {results.quality_trimmed} bp ({results.trimmed_percent:.2f}%)"
        if results.reads_with_adapters >= 0:
            msg_info += f"\nReads with adapters: {results.reads_with_adapters} ({results.adapters_percent:.2f}%)"
        msg_info += f"\nTime taken: {human_readable_seconds(results.seconds_taken)}."

        if results.failed:
            msg_icon = QtWidgets.QMessageBox.Warning
            msg_text = f"{task_name} completed with errors!"
            msg_info = f"Files with errors: {len(results.failed)}\n" + msg_info
            msg_details = (
                "Error logs were written for the following files:\n"
                + "\n".join(f"- {path.name}" for path in results.failed)
                + "\n"
            )
        else:
            msg_icon = QtWidgets.QMessageBox.Information
            msg_text = f"{task_name} completed successfully!"
            msg_details = ""

        msgBox = QtWidgets.QMessageBox(self.window())
        msgBox.setWindowTitle(app.config.title)
        msgBox.setIcon(msg_icon)
        msgBox.setText(msg_text.ljust(50))
        msgBox.setInformativeText(msg_info)
        msgBox.setDetailedText(msg_details)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Open)
        button = self.window().msgShow(msgBox)
        if button == QtWidgets.QMessageBox.Open:
            url = QtCore.QUrl.fromLocalFile(str(results.output_path.absolute()))
            QtGui.QDesktopServices.openUrl(url)

    def setEditable(self, editable: bool):
        for card in self.cards:
            card.setEnabled(editable)
        self.cards.title.setEnabled(True)
        self.cards.progress.setEnabled(True)

    def open(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent=self.window(),
            caption=f"{app.config.title} - Open file",
        )
        if not filename:
            return
        self.object.open(Path(filename))
