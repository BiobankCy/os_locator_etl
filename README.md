# OpenSpecimen Locator ETL

> **WARNING**  
> This project is currently under development. Please use with caution.

## Overview

The OpenSpecimen Locator ETL is a flexible pipeline designed for 
biobanks utilizing OpenSpecimen as their BIMS (Biobanking 
Information Management System). Its primary purpose is to 
streamline integration with the 
[BBMRI-ERIC Sample Locator](https://locator.bbmri-eric.eu/) 
project.

## Key Features

* **Multiple Configurations:** Allows for integration with 
multiple OpenSpecimen sources and offers the flexibility to 
target multiple FHIR destinations.
* **Scheduling:** Enables the setup of periodic runs for 
specific configurations, enhancing automation and efficiency.
* **History Tracking:** Provides a comprehensive history 
of past runs, complete with statistical data and status updates.

## Technical Insight

* This project utilizes the OpenSpecimen API to extract data 
from the biobank repository. To facilitate this, it requires 
the creation of a read-only Robot user in OpenSpecimen.
* Data extraction from OpenSpecimen relies on the presence of 
a predefined query containing all the data destined for the 
Locator project.
* The Bridgehead component must run on a separate virtual 
machine, necessitating the provision of appropriate 
credentials (username/password) during the load step.
* The ETL project is a customized Django Admin application 
integrated with Celery for efficient scheduling and task 
management.

## Setup Guidelines

* A Dockerfile is available to simplify the setup and 
execution of this project.
* Ensure the availability of a persistent directory 
for `/app/data` to retain configuration details and 
historical run statistics.
* For additional assistance, please feel free to contact [myerou02@ucy.ac.cy](mailto:myerou02@ucy.ac.cy).

## Future Enhancements and Limitations

While we have strived to make the ETL process highly 
configurable, we acknowledge that it may not cater to every 
unique biobank's requirements. We encourage you to reach out to 
us or actively contribute to the project if you require greater 
flexibility or have specific needs. Your feedback and 
involvement are highly valued.
