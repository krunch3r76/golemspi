# /model/model_retrievals.py

import json
from .json_utils import json_loadf
from collections import OrderedDict


class ModelRetrievals:
    def __init__(self, model):
        self.model = model
        self.conn = model.connection

    def get_agreement_json_by_activity_hash(self, activity_hash):
        cursor = self.conn.execute(
            """
            SELECT task.path_to_agreement_json_file
            FROM task
            JOIN activity ON task.agreementId = activity.agreementId
            WHERE activity.activity_hash = ?
            """,
            (activity_hash,),
        )
        result = cursor.fetchone()

        if result is None:
            raise Exception("Activity not found")

        agreement_json_file = result[0]

        # Load the JSON file
        agreement_data = json_loadf(agreement_json_file)

        return agreement_data

    def get_coeffs_for_activity(self, activity_hash):
        """given an activity hash extract associated agreement coefficients into a dictionary
        in the order defined by the agreement

        returns dictionary keyed to:
            'golem.usage.cpu_sec',
            'golem.usage.duration_sec',
            'start'
        """
        data = self.get_agreement_json_by_activity_hash(activity_hash)

        usage_vector = (
            data.get("offer", {})
            .get("properties", {})
            .get("golem", {})
            .get("com", {})
            .get("usage", {})
            .get("vector")
        )

        coeffs = (
            data.get("offer", {})
            .get("properties", {})
            .get("golem", {})
            .get("com", {})
            .get("pricing", {})
            .get("model", {})
            .get("linear", {})
            .get("coeffs")
        )

        result = OrderedDict(zip(usage_vector, coeffs[: len(usage_vector)]))
        result["start"] = coeffs[2]
        return result

    def get_current_exeunit_info(self):
        """find the last pid and lookup the start time and url then return timestamp, task_package, and pid"""
        cursor = self.model.connection.execute(
            "SELECT timestamp, activityId, pid FROM activity_pid ORDER BY activityPidId DESC LIMIT 1"
        )
        result = cursor.fetchone()

        if result is None:
            return None, None, None
        time_start = result[0]
        activity_id = result[1]
        pid = result[2]

        cursor = self.model.connection.execute(
            "SELECT activity_hash FROM activity WHERE activityId = ?",
            (activity_id,),
        )
        result = cursor.fetchone()

        if result is None:
            return None, None, None

        activity_hash = result[0]
        agreement_details = self.get_agreement_json_by_activity_hash(activity_hash)
        try:
            task_package = agreement_details["demand"]["properties"]["golem"]["srv"][
                "comp"
            ]["task_package"]
        except:
            task_package = None

        return time_start, task_package, pid
