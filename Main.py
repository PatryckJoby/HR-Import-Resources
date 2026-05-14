import sys
import Tenants
import HRImport

def main() -> None:
    """
    Main entry point: loads tenants, validates CLI arguments, then repeatedly prompts for CSV filenames.
    
    CLI Usage:
        python HRImport.py [tenant_id ...]  (optional tenant IDs to filter)
        Then enter CSV filenames to process (enter 'q' to quit)
    
    If tenant_id(s) provided: only those tenants are used for splitting.
    If no tenant_id(s) provided: no tenants are used.
    """

    # Load all available tenants from configuration file
    tenants = Tenants.load_tenants()
    use_tenants: list[dict[str, str]] = []
    
    # Parse CLI arguments to select specific tenants for processing
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            # Normalize argument to lowercase for case-insensitive matching against tenant_id
            normalized_arg = arg.lower()
            
            # Search for tenant(s) matching the provided ID (supports ID filtering/validation)
            matches = [tenant for tenant in tenants if tenant["tenant_id"] == normalized_arg]
            
            # If tenant ID found, add all matching configurations; otherwise raise error
            if matches:
                for tenant in matches:
                    use_tenants.append(tenant)
            else:
                raise ValueError(f"Tenant ID '{arg}' not found")

    # Get filename through stdin, removing surrounding quotes if present
    # Users often copy filenames with quotes from file explorer; strip them for clean paths
    filename = input().strip('"').strip("'")

    # Loop until user enters 'q' to quit, processing each CSV file with the selected tenants
    while (filename != 'q'):
        hr_import = HRImport.HRImport(filename)
        hr_import.run(use_tenants)
        filename = input().strip('"').strip("'")


if __name__ == "__main__":
    main()