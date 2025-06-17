import os 


class Constants:
    ZOHO_QUERY_PARAMS = (
            "fields=First_Name,Last_Name,Company,Lead_Source,Lead_Status,Industry,"
            "Annual_Revenue,Phone,Mobile,Email,Secondary_Email,Skype_ID,Website,Rating,"
            "No_of_Employees,Email_Opt_out,Street,City,State,Zip_Code,Country,Created_By,"
            "Modified_By,Created_Time,Modified_Time,Owner,Lead_Owner,Twitter,Secondary_URL,"
            "Address&sort_by=Created_Time&sort_order=desc&per_page=200&page=1"
    )

    ZOHO_MODULE = "Leads"
    ZOHO_API_URL = f"https://www.zohoapis.com/crm/v8/{ZOHO_MODULE}"
    