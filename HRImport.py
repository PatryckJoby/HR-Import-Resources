"""
HR Import module for processing and transforming HR data files.
Converts names to lowercase and separates Joby Germany users into tenant-specific files.
"""
import pandas

class HRImport:
    """
    Class to represent the HR import process. It takes a filename as input and performs the necessary transformations to ensure that all names are in lowercase and that Joby Germany users are split into a separate file with a tenantmember column for auto enrollment.
    """

    def __init__(self, filename: str) -> None:
        """
        Initialize the HRImport class with the given filename and read the data from the file.

        @param filename: The filename to read the data from
        """

        self.filename = filename
        try:
            self.data = pandas.read_csv(filename)
        except Exception as e:
            print(f"Error reading file: {e}")
            return


    def _split_tenant(self, business_unit_description: str, tenant_id: str) -> pandas.DataFrame:
        """
        Split the file at Joby Germany folks. Remove them from the main file and create a new one with just the Joby Germany users and add a tenantmember column for auto enrollment

        @param business_unit_description: The business unit to filter on (e.g., "joby germany gmbh")
        @param tenant_id: The tenant ID to assign to split records (e.g., "jbg")
        @return: The dataframe with the matching business unit records removed
        """

        # Create boolean mask: True where business unit matches (case-insensitive), False otherwise
        germany_mask = self.data["business unit description"].str.strip().str.lower() == business_unit_description.lower()
        # Extract rows matching the mask into separate dataframe
        germany_data = self.data[germany_mask].copy()
        # Keep rows that don't match the mask for main file
        remaining_data = self.data[~germany_mask]
        # If matching records found, write them to a separate CSV with tenant identifier
        if not germany_data.empty:
            germany_filename = self.filename.replace(".csv", f"_{tenant_id}.csv")
            germany_data["tenantmember"] = tenant_id
            germany_data.to_csv(germany_filename)
        return remaining_data


    def _job_assignments(self) -> None:
        """
        Perform the necessary transformations for the Job Assignments file
        """

        # Remove rows where useridnumber is missing or empty
        self.data = self.data[~(self.data["useridnumber"].isna() | (self.data["useridnumber"] == ""))]
        # Replace NaN values in Manager email with placeholder string for downstream processing
        self.data["Manager email"] = self.data["Manager email"].fillna("#N/A")
        # Convert manager email and userid to lowercase for consistency
        for name_index in self.data.index:
            self.data.loc[name_index, "Manager email"] = self.data["Manager email"][name_index].lower()
            self.data.loc[name_index, "useridnumber"] = self.data["useridnumber"][name_index].lower()
            if self.data.loc[name_index, "idnumber"] == "joeben@joby.aero" or self.data.loc[name_index, "idnumber"] == "patryck.chipman@joby.aero":
                self.data = self.data.drop(name_index)

        return

    def _users(self, tenants: list[dict[str, str]]) -> None:
        """
        Perform the necessary transformations for the Users file
        """
        # Remove rows where idnumber is missing or empty
        self.data = self.data[~(self.data["idnumber"].isna() | (self.data["idnumber"] == ""))]
        # Split the data for each tenant using its configured business unit description
        for tenant in tenants:
            self.data = self._split_tenant(tenant["business_unit_description"], tenant["tenant_id"])
        # Convert idnumber and email to lowercase for consistency
        for name_index in self.data.index:
            self.data.loc[name_index, "idnumber"] = self.data["idnumber"][name_index].lower()
            self.data.loc[name_index, "email"] = self.data["email"][name_index].lower()
            if self.data.loc[name_index, "idnumber"] == "joeben@joby.aero" or self.data.loc[name_index, "idnumber"] == "patryck.chipman@joby.aero":
                self.data = self.data.drop(name_index)

        return
    

    def run(self, tenants: list[dict[str, str]]) -> None:
        """
        Perform the necessary transformations and write the output back to the same file.
        """

        print("...working...")

        # Route to appropriate processing method based on filename keyword
        if "job assignments" in self.filename.lower():
            self._job_assignments()
        elif "users" in self.filename.lower():
            self._users(tenants)
        else:
            raise ValueError("Filename must contain either 'Job Assignments' or 'Users' to determine the type of file being processed.")

        self.data.to_csv(self.filename)

        # Print success message after potentially long-running operations complete
        print("Success!")

        return