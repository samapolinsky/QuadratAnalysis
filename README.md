# Quadrat Analysis Application
## Project Overview
This application was developed by Samantha Apolinsky with the Center for Coastal Resource Management (CCRM) at the Virginia Institute of Marine Science.
The purpose of the application is to identify the percent cover of species in a quadrat -- a square frame used to isolate a unit of land. 
## Local Development Setup
1. Clone the repository
2. Create and activate a virtual environment
3. Download dependencies. Packages installed during initial implementation include:
   - Backend: `opencv-python`, `fastapi`, `python-multipart`, `openai`, `uvicorn`
   - Frontend: `React-data-grid`
4. Open two local terminals. In one, navigate to `/backend` and run `uvicorn main:app --reload`. In the other, navigate to `/quadrat_analysis` and run `npm run dev`.
5. On the browser, open 'http://localhost:5173/'