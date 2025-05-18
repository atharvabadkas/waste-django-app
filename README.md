
# 🗑️ Waste Django App

The **Waste Django App** is a web-based platform designed to manage and analyze waste data efficiently. Built using Django, this application integrates machine learning models to classify waste images and provides an interface for users to interact with the system seamlessly.

---

## 🚀 Features

- **Image Classification**: Utilize pre-trained EfficientNetB0 model to classify waste images.
- **Data Management**: Store and manage waste-related data effectively.
- **Modular Structure**: Organized into multiple Django apps for scalability and maintainability.
- **API Integration**: Potential for RESTful API integration for external services.

---

## 🛠️ Tech Stack

- **Backend Framework**: Django
- **Machine Learning**: TensorFlow/Keras with EfficientNetB0
- **Database**: SQLite (default, can be configured for others)
- **Frontend**: HTML, CSS, JavaScript (via Django templates)

---

## 📁 Project Structure

```
waste-django-app/
├── drive_app/                 # Handles interactions with external storage or APIs
├── models/                    # Contains machine learning models and related code
├── myapp/                     # Core application logic and views
├── verandah_prep/             # Preprocessing scripts and utilities
├── verandah_waste/            # Waste data management and processing
├── manage.py                  # Django's command-line utility
├── requirements.txt           # Python dependencies
├── names.txt                  # Labels or class names for classification
├── efficientnetb0_weights.h5  # Pre-trained model weights
├── README.md                  # Project documentation
```

---

## ⚙️ Installation & Setup

1. **Clone the Repository**:

```bash
git clone https://github.com/atharvabadkas/waste-django-app.git
cd waste-django-app
```

2. **Create a Virtual Environment**:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**:

```bash
pip install -r requirements.txt
```

4. **Apply Migrations**:

```bash
python manage.py migrate
```

5. **Run the Development Server**:

```bash
python manage.py runserver
```
