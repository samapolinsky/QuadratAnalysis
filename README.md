# AI-powered Quadrat Land Cover Analysis App
## Project Overview
The purpose of the application is to identify the percent cover of species in a quadrat -- a square frame used to isolate a unit of land. The application uses the OpenAI API and Python's OpenCV library to crop and analyze the quadrat image.

This application was developed by Samantha Apolinsky with the help of members of the Center for Coastal Resource Management (CCRM) at the Virginia Institute of Marine Science (VIMS).
## Local Development Setup
1. Clone the repository
2. Create and activate a virtual environment
3. Download dependencies. Packages installed during initial implementation include:
   - Backend: `opencv-python`, `fastapi`, `python-multipart`, `openai`, `uvicorn`
   - Frontend: `React-data-grid`
4. Open two local terminals. In one, navigate to `/backend` and run `uvicorn main:app --reload`. In the other, navigate to `/quadrat_analysis` and run `npm run dev`.
5. On the browser, open 'http://localhost:5173/'