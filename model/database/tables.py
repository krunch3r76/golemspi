from . import connection


def create_tables():
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS agreement (
            agreementId INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INT NOT NULL,
            hash TEXT UNIQUE NOT NULL,
            address TEXT NOT NULL,
            subscription TEXT NOT NULL
        )
    """
    )

    connection.execute(
        """
            CREATE TABLE IF NOT EXISTS task (
                taskId INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                agreementId INTEGER NOT NULL,
                activityId INTEGER NOT NULL,
                path_to_work_dir TEXT NOT NULL,
                path_to_agreement_dir TEXT NOT NULL,
                path_to_agreement_json_file TEXT NOT NULL,
                path_to_activity_dir TEXT NOT NULL,
                path_to_deployment_json_file TEXT NOT NULL,
                FOREIGN KEY (agreementId) REFERENCES agreement (agreementId),
                FOREIGN KEY (activityId) REFERENCES activity (activityId)
            )
        """
    )

    connection.execute(
        """
            CREATE TABLE IF NOT EXISTS activity (
                activityId INTEGER PRIMARY KEY AUTOINCREMENT,
                agreementId INTEGER NOT NULL,
                activity_hash TEXT NOT NULL,
                FOREIGN KEY (agreementId) REFERENCES agreement (agreementId)
            )
        """
    )
    connection.execute(
        """
            CREATE TABLE IF NOT EXISTS activity_logs_directory (
                logsdirId INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                activityId INTEGER NOT NULL,
                logs_directory TEXT NOT NULL,
                FOREIGN KEY (activityId) REFERENCES activity (activityId)
            )
        """
    )

    connection.execute(
        """
            CREATE TABLE IF NOT EXISTS activity_pid (
                activityPidId INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                activityId INTEGER NOT NULL,
                pid INTEGER NOT NULL,
                FOREIGN KEY (activityId) REFERENCES activity (activityId)
            )
        """
    )

    connection.execute(
        """
        CREATE TABLE activity_metric (
            metric_id INTEGER PRIMARY KEY AUTOINCREMENT,
            activityId INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            duration_sec DECIMAL NOT NULL,
            cpu_sec DECIMAL NOT NULL,
            FOREIGN KEY (activityId) REFERENCES activity (activityId)
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS activity_termination (
            terminationId INTEGER PRIMARY KEY AUTOINCREMENT,
            activityId INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            FOREIGN KEY (activityId) REFERENCES activity (activityId)
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS activity_exit (
            activityExitId INTEGER PRIMARY KEY AUTOINCREMENT,
            activityId INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            exit_status_str TEXT NOT NULL,
            exit_status_code INTEGER NOT NULL,
            FOREIGN KEY (activityId) REFERENCES activity (activityId)
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS activity_final_cost (
            finalCostId INTEGER PRIMARY KEY AUTOINCREMENT,
            activityId INTEGER NOT NULL,
            timestamp INTEGER NOT NULL,
            final_cost DECIMAL NOT NULL,
            FOREIGN KEY (activityId) REFERENCES activity (activityId)
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS initialized_payment_accounts (
            initialized_account_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp INTEGER NOT NULL,
            mode TEXT NOT NULL,
            address TEXT NOT NULL,
            driver TEXT NOT NULL,
            network TEXT NOT NULL,
            token TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
            CREATE TABLE IF NOT EXISTS payment_account (
                payment_account_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER NOT NULL,
                address TEXT NOT NULL,
                network TEXT NOT NULL,
                platform TEXT NOT NULL
            )
        """
    )
