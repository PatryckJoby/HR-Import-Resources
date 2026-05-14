import pandas

class HRImport:
    """
    Class to represent the HR import process. It takes a filename as input and performs the necessary transformations to ensure that all names are in lowercase and that Joby Germany users are split into a separate file with a tenantmember column for auto enrollment.
    """

    def __init__(self, filename) -> None:
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


    def split_germany(self) -> pandas.DataFrame:
        """
        Split the file at Joby Germany folks. Remove them from the main file and create a new one with just the Joby Germany users and add a tenantmember column for auto enrollment

        @param data: The dataframe to split
        @param filename: The filename to use for the new file
        @return: The dataframe with the Joby Germany users removed
        """
        germany_mask = self.data["business unit description"].str.strip().str.lower() == "joby germany gmbh"
        germany_data = self.data[germany_mask].copy()
        remaining_data = self.data[~germany_mask]
        if not germany_data.empty:
            germany_filename = self.filename.replace(".csv", "_JobyGermany.csv")
            germany_data["tenantmember"] = "jbg"
            germany_data.to_csv(germany_filename)
        return remaining_data
    

    def run(self) -> None:
        """
        Perform the necessary transformations and write the output back to the same file.
        """

        print("...working...")

        if "job assignments" in self.filename.lower(): # Job Assignments file
            self._job_assignments()
        elif "users" in self.filename.lower(): # Users file
            self._users()
        else:
            raise ValueError("Filename must contain either 'Job Assignments' or 'Users' to determine the type of file being processed.")

        self.data.to_csv(self.filename)

        print("Success!") # Can take a while to perform above tasks, so input is ready after this message is displayed

        return


    def _job_assignments(self) -> None:
        """
        Perform the necessary transformations for the Job Assignments file
        """

        self.data = self.data[~(self.data["useridnumber"].isna() | (self.data["useridnumber"] == ""))]
        self.data = self.split_germany()
        self.data["Manager email"] = self.data["Manager email"].fillna("#N/A")
        for name_index in self.data.index:
            self.data.loc[name_index, "Manager email"] = self.data["Manager email"][name_index].lower()
            self.data.loc[name_index, "useridnumber"] = self.data["useridnumber"][name_index].lower()

        return

    def _users(self) -> None:
        """
        Perform the necessary transformations for the Users file
        """

        self.data = self.data[~(self.data["idnumber"].isna() | (self.data["idnumber"] == ""))]
        self.data = self.split_germany()
        for name_index in self.data.index:
            self.data.loc[name_index, "idnumber"] = self.data["idnumber"][name_index].lower()
            self.data.loc[name_index, "email"] = self.data["email"][name_index].lower()

        return
    

def main():
    # Get filename through stdin
    filenname = input().strip('"').strip("'")

    while (filenname != 'q'):
        hr_import = HRImport(filenname)
        hr_import.run()
        filenname = input().strip('"').strip("'")


if __name__ == "__main__":
    main()