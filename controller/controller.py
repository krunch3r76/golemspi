# ./controller
# golemspi controller
# interact with the model and the view
# from utils.colors import Colors
import queue
import time
from .events import determine_event_type_and_data
from .events import parse_log_line
from .events.log_events import *

from model import Model
from utils.mylogger import console_logger, file_logger
from .model_queries import perform_view_updates


class Controller:
    def __init__(self, model: Model, view, log_queue):
        self.model = model
        self.view = view
        self.current_message = log_queue
        self.subprocess_start_time = None
        self.queue_read_start_time = None

    def read_next_message(self):
        try:
            log_line = self.current_message.get_nowait()
        except queue.Empty:
            log_line = None
        return log_line

    def determine_event_type_and_data(self, log_line):
        # logic to determine event type and associated data
        parsed_log_line = parse_log_line(log_line)
        if parsed_log_line.namespace is None:
            # later handle non conforming messages
            log_event = None
        else:
            log_event = determine_event_type_and_data(parsed_log_line)
        return log_event

    def process_log_event(self, log_event):
        if isinstance(log_event, YagnaServiceStartedEvent):
            self.model.additions.add_version_info(**log_event.asdict())
        elif isinstance(log_event, InitializedPaymentAccountEvent):
            self.model.additions.add_initialized_payment_account_info(
                **log_event.asdict()
            )
        elif isinstance(log_event, PaymentAccountsEvent):
            self.model.additions.add_payment_accounts(**log_event.asdict())
        elif isinstance(log_event, PaymentNetworkEvent):
            self.model.additions.add_payment_network(**log_event.asdict())
        elif isinstance(log_event, HardwareResourcesCapEvent):
            self.model.additions.add_hardware_cap_info(**log_event.asdict())
            # file_logger.debug(self.model.hardware_resource_cap_info)
        elif isinstance(log_event, UsingSubnetEvent):
            self.model.additions.add_subnet_utilized(**log_event.asdict())
        elif isinstance(log_event, UsageCoeffsEvent):
            self.model.additions.update_usage_coeffs(**log_event.as_dict())
        elif isinstance(log_event, NewAgreementEvent):
            self.model.additions.add_agreement(**log_event.asdict())
        elif isinstance(log_event, NewTaskEvent):
            self.model.additions.add_task(**log_event.asdict())
        elif isinstance(log_event, NewExeUnitLogsDirEvent):
            self.model.additions.add_exeunit_logs_dir(**log_event.asdict())
        elif isinstance(log_event, NewExeUnitPidEvent):
            self.model.additions.add_exeunit_pid(**log_event.asdict())
        elif isinstance(log_event, NewCostInformationEvent):
            self.model.updates.update_cost_information(**log_event.asdict())
        elif isinstance(log_event, ExeUnitTerminatedEvent):
            self.model.updates.update_exeunit_termination(**log_event.asdict())
        elif isinstance(log_event, ExeUnitExitedEvent):
            self.model.updates.update_exeunit_exit(**log_event.asdict())
        elif isinstance(log_event, FinalCostForActivityEvent):
            self.model.updates.update_final_cost_for_activity_information(
                **log_event.asdict()
            )
        elif isinstance(log_event, IdentityEvent):
            file_logger.debug(log_event.asdict())

    def __call__(self):
        # Colors.print_color(
        #     "Controller started, reading log messages", color=Colors.RED_BG
        # )
        k_log_line_read_limit = 10
        while True:
            # use a performance counter to give time for queue to fill
            if self.queue_read_start_time is None:
                self.queue_read_start_time = time.perf_counter()

            if time.perf_counter() - self.queue_read_start_time > 0.05:
                log_line = self.read_next_message()
                log_line_count = 0
                while log_line is not None and log_line_count < k_log_line_read_limit:
                    # read a bunch of log lines before processing
                    log_line_count += 1
                    # handle multi line log message (always a list)
                    if log_line.endswith("["):
                        while not log_line.endswith("]"):
                            inner_line = self.read_next_message()
                            if inner_line is not None:
                                log_line += self.read_next_message()
                    self.view.add_log_line(log_line)
                    log_event = self.determine_event_type_and_data(log_line)
                    if log_event is not None:
                        self.process_log_event(log_event)  # add to model
                    if log_line_count < k_log_line_read_limit:
                        log_line = self.read_next_message()

                # reset read queue timer
                self.queue_read_start_time = None

                # refer back to model
                # to perform any updates based on active_flags
                active_flags = self.model.get_active_flags()
                perform_view_updates(self, active_flags)
                self.model.reset_view_update_flags()

                # refresh view
                self.view.update()

            time.sleep(0.002)
