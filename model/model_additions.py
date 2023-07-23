# /model/model_additions.py

from .time_utils import convert_to_unix_time
from .objects import VersionInfo, HardwareResourceInfo

from utils.mylogger import console_logger, file_logger


class ModelAdditions:
    def __init__(self, model):
        self.model = model
        self.conn = model.connection

    def add_hardware_cap_info(self, timestamp, cpu_threads, mem_gib, storage_gib):
        unix_timestamp = convert_to_unix_time(timestamp)
        self.model.hardware_resource_cap_info = {
            "timestamp": unix_timestamp,
            "cpu_threads": cpu_threads,
            "mem_gib": mem_gib,
            "storage_gib": storage_gib,
        }
        self.model.view_update_flags["hardware_resource_cap_info"] = True

    def add_subnet_utilized(self, timestamp, subnet):
        self.model.subnet = subnet
        self.model.view_update_flags["subnet"] = True

    def add_agreement(self, timestamp, agreement_hash, requestor_address, subscription):
        # Update model on new agreement
        unixtimestamp = convert_to_unix_time(timestamp)
        # Insert a new row into the agreement table
        query = """
            INSERT INTO agreement (timestamp, hash, address, subscription) VALUES (?, ?, ?, ?)
        """
        values = (unixtimestamp, agreement_hash, requestor_address, subscription)

        self.model.connection.execute(query, values)

        # Optional: Update the model or perform any additional logic

        # Example: Update the model with the newly added agreement
        # self.model.update_agreement(agreement_hash, requestor_address, subscription)

    def add_task(
        self,
        timestamp,
        agreement_hash,
        activity_hash,
        path_to_work_dir,
        path_to_agreement_dir,
        path_to_agreement_json_file,
        path_to_activity_dir,
        path_to_deployment_json_file,
    ):
        unixtimestamp = convert_to_unix_time(timestamp)
        # Lookup the agreementId based on the agreement_hash
        cursor = self.conn.execute(
            "SELECT agreementId FROM agreement WHERE hash = ?", (agreement_hash,)
        )
        result = cursor.fetchone()

        if result is None:
            raise Exception("agreement with the given hash not found")

        agreement_id = result[0]

        # Insert a new row into the activity table
        self.conn.execute(
            """
            INSERT INTO activity (agreementId, activity_hash) VALUES (?, ?)
            """,
            (agreement_id, activity_hash),
        )

        # Retrieve the activityId of the inserted row
        cursor = self.conn.execute("SELECT last_insert_rowid()")
        activity_id = cursor.fetchone()[0]

        # Insert a new row into the task table
        self.conn.execute(
            """
            INSERT INTO task (
                timestamp,
                agreementId,
                activityId,
                path_to_work_dir,
                path_to_agreement_dir,
                path_to_agreement_json_file,
                path_to_activity_dir,
                path_to_deployment_json_file
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                unixtimestamp,
                agreement_id,
                activity_id,
                path_to_work_dir,
                path_to_agreement_dir,
                path_to_agreement_json_file,
                path_to_activity_dir,
                path_to_deployment_json_file,
            ),
        )

    # Other add methods...

    def add_exeunit_logs_dir(self, timestamp, path_to_logs_dir, activity_hash):
        unixtimestamp = convert_to_unix_time(timestamp)
        # Lookup the activityId based on the activity hash
        cursor = self.model.connection.execute(
            "SELECT activityId FROM activity WHERE activity_hash = ?",
            (activity_hash,),
        )
        result = cursor.fetchone()

        if result is None:
            raise Exception("Activity with the given hash not found")

        activity_id = result[0]

        # Insert a new row into the activity_logs_directory table
        self.model.connection.execute(
            """
            INSERT INTO activity_logs_directory (timestamp, activityId, logs_directory) VALUES (?, ?, ?)
            """,
            (unixtimestamp, activity_id, path_to_logs_dir),
        )

    #    self.model.log_directory = path_to_logs_dir

    def add_exeunit_pid(self, timestamp, pid):
        """
        by implication the pid corresponds to the last exeunit/activity added to the model
        """
        unixtimestamp = convert_to_unix_time(timestamp)

        from datetime import datetime

        dt = datetime.fromtimestamp(unixtimestamp)

        # Retrieve the last inserted activityId
        cursor = self.model.connection.execute(
            "SELECT activityId FROM activity ORDER BY activityId DESC LIMIT 1"
        )
        result = cursor.fetchone()

        if result is None:
            raise Exception("No activities found")

        activity_id = result[0]

        # Insert a new row into the activity_pid table
        self.model.connection.execute(
            """
            INSERT INTO activity_pid (timestamp, activityId, pid) VALUES (?, ?, ?)
            """,
            (unixtimestamp, activity_id, pid),
        )
        self.model.view_update_flags["pid"] = True

    def add_version_info(self, timestamp, version, commit, build_date, build_number):
        timestamp = convert_to_unix_time(timestamp)
        self.model.version_info = VersionInfo(
            timestamp, version, commit, build_date, build_number
        )

    def add_initialized_payment_account_info(
        self, timestamp, mode, address, driver, network, token
    ):
        unixtimestamp = convert_to_unix_time(timestamp)
        query = """
            INSERT INTO initialized_payment_accounts (timestamp, mode, address, driver, network, token)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        values = (unixtimestamp, mode, address, driver, network, token)
        self.conn.execute(query, values)

    def add_payment_accounts(self, timestamp, accounts):
        # Convert the timestamp to UNIX timestamp
        unix_timestamp = convert_to_unix_time(timestamp)
        # Iterate over the accounts list
        for account in accounts:
            # Extract the account details
            address = account["address"]
            network = account["network"]
            platform = account["platform"]

            # Insert the account details into the payment_account table
            self.conn.execute(
                """
                INSERT INTO payment_account (timestamp, address, network, platform)
                VALUES (?, ?, ?, ?)
                """,
                (unix_timestamp, address, network, platform),
            )

    def add_payment_network(self, timestamp, payment_network):
        self.model.payment_networks.append(payment_network)
