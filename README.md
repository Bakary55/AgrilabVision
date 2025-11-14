#  AgrilabVision – Soil Analysis & Fertility App ### Developed by **Bakary Coulibaly** AgrilabVision is an intelligent mobile application that helps farmers analyze soil, determine crop suitability, receive fertilizer recommendations, and optimize irrigation using **AI-powered image analysis**.
This project aims to bring **affordable agricultural decision-making tools** to rural communities with limited access to laboratories and experts. 

📘 About the Project AgrilabVision uses: - **Computer Vision (TensorFlow Lite)** to analyze soil texture and moisture - **Weather APIs** to determine agricultural seasons - **Rule-based & AI-driven engines** to recommend crops, fertilizers, and irrigation - **Offline mode** for rural areas - **Cloud synchronization** when network becomes available 
 Features  Soil Analysis - Capture soil images using the smartphone camera - Detect texture: *clay, sand, silt* - Estimate organic matter and surface moisture
 
 Crop Recommendation Engine - Suggest crops adapted to season + soil + moisture - Intelligent scoring of crop suitability 
 Irrigation Advisory - Detect when the user should water their crops - Warnings for over-watering or drought risks �
 Fertilizer Recommendation Engine - Suggest optimal fertilizers for each crop - Warn users about over-fertilization 
 📡 Additional Features - Offline mode - History of analyses - Automatic sync - Simple UI adapted for rural users  
  Tech Stack | Layer | Technology | |-------|------------| | Frontend | Flutter (Dart) | | AI / ML | TensorFlow Lite | | Backend (optional) | Firebase / NodeJS | | Database | Firestore / SQLite | | Weather | OpenWeatherMap API | | Architecture | MVC + Service Layer | 
Project Architecture agrilabvision/ │ ├── lib/ │ ├── ui/ # User interface files │ ├── models/ # Data models (SoilAnalysis, FarmPlot...) │ ├── services/ # AI, Weather, Storage Services │ ├── controllers/ # Logic controllers │ ├── utils/ # Helpers, constants │ └── main.dart # App entry point │ ├── assets/ │ ├── images/ # Soil reference images │ ├── model/ # TensorFlow Lite model (.tflite) │ └── README.md # Project documentation
