import pandas

# Get filename for active accounts through stdin
filenname_active = input().strip('"')
data_active = pandas.read_csv(filenname_active)
active_emails = data_active["idnumber"]

# Get filename for suspended accounts through stdin
filenname_suspended = input().strip('"')
data_suspened = pandas.read_csv(filenname_suspended)
suspended_emails = data_suspened["idnumber"]

# New series of only the values in both active and suspended accounts
# Quantum accounts?
in_both = data_active["idnumber"].isin(data_suspened["idnumber"])

# Create a new table of the values from in_both
result = data_active[in_both]

print(result)