# /model/model_retrievals.py

import json
from .json_utils import json_loadf
from collections import OrderedDict

from utils.mylogger import console_logger, file_logger


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
        """find the unterminated pid and lookup the start time and url then return timestamp, task_package, and pid"""
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
            """
            SELECT activity_hash FROM activity
            WHERE activityId = ? AND NOT EXISTS (
                SELECT 1 FROM activity_termination WHERE activity_termination.activityId = activity.activityId
            )
        """,
            (activity_id,),
        )
        result = cursor.fetchone()
        # cursor = self.model.connection.execute(
        #     "SELECT activity_hash FROM activity WHERE activityId = ?",
        #     (activity_id,),
        # )
        # result = cursor.fetchone()

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

    def get_payment_network(self):
        """determine the payment network if possible and return either mainnet or testnet or None"""
        payment_network = None
        if any(
            network in self.model.payment_networks
            for network in ["rinkeby", "mumbai", "goerli"]
        ):
            payment_network = "testnet"
        elif any(
            network in self.mdoel.payment_networks for network in ["mainnet", "polygon"]
        ):
            payment_network = "mainnet"
        return payment_network

    def get_payment_account_address_info_on_network(self, networks):
        # Convert the list of networks to a tuple, which can be used in a SQL query
        networks_tuple = tuple(networks)

        # Generate placeholders for each network in the list
        placeholders = ", ".join("?" for network in networks)

        # Execute the SQL query
        cursor = self.model.connection.execute(
            f"""
            SELECT address, token
            FROM initialized_payment_accounts
            WHERE network IN ({placeholders})
            ORDER BY initialized_account_id DESC
            LIMIT 1
            """,
            networks_tuple,
        )

        # Fetch the first (and only) row from the results
        result = cursor.fetchone()
        file_logger.debug(f"{result}")
        if result is None:
            # No matching record was found
            return None

        # Unpack the result into variables
        address, token = result

        # Return the address and token as a tuple
        return address, token
