# /model/model_updates.py

from .time_utils import convert_to_unix_time

from decimal import Decimal


class ModelUpdates:
    def __init__(self, model):
        self.model = model
        self.conn = self.model.connection

    def update_cost_information(self, timestamp, activity_hash, cost, usage_vector):
        # Update the model with cost information
        usage_vector = list(map(Decimal, map(str, usage_vector)))
        timestamp = convert_to_unix_time(timestamp)
        agreement_coeffs = self.model.retrievals.get_coeffs_for_activity(activity_hash)
        usage_keys = list(agreement_coeffs.keys())
        usages = dict(zip(usage_keys[0:2], usage_vector))

        duration_sec = usages["golem.usage.duration_sec"]
        cpu_sec = usages["golem.usage.cpu_sec"]

        # Insert a new row into the activity_metric table
        self.conn.execute(
            """
            INSERT INTO activity_metric (timestamp, activityId, duration_sec, cpu_sec)
            SELECT ?, activityId, ?, ?
            FROM activity
            WHERE activity_hash = ?
            """,
            (timestamp, duration_sec, cpu_sec, activity_hash),
        )

    def update_exeunit_termination(self, timestamp, activity_hash):
        # Update the model with the termination of an exeunit/activity

        # Insert a new row into the activity_termination table
        self.conn.execute(
            """
            INSERT INTO activity_termination (activityId, timestamp)
            SELECT activityId, ? FROM activity WHERE activity_hash = ?
            """,
            (timestamp, activity_hash),
        )
        self.model.view_update_flags["exeunit terminated"] = True

    def update_exeunit_exit(
        self,
        timestamp,
        exit_status_str,
        exit_status_code,
        agreement_hash,
        activity_hash,
    ):
        # Update the model with the exit status of an exeunit/activity
        timestamp = convert_to_unix_time(timestamp)

        # Insert a new row into the activity_exit table
        self.conn.execute(
            """
            INSERT INTO activity_exit (activityId, timestamp, exit_status_str, exit_status_code)
            SELECT activityId, ?, ?, ?
            FROM activity
            WHERE activity_hash = ?
            """,
            (timestamp, exit_status_str, exit_status_code, activity_hash),
        )

    def update_final_cost_for_activity_information(
        self, timestamp, activity_hash, final_cost
    ):
        # Update the model with the final cost information for an activity
        timestamp = convert_to_unix_time(timestamp)

        self.conn.execute(
            """
            INSERT INTO activity_final_cost (activityId, timestamp, final_cost)
            SELECT activityId, ?, ? FROM activity WHERE activity_hash = ?
            """,
            (timestamp, final_cost, activity_hash),
        )
