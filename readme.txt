# PlantPals 🌱

## Overview

Gardening enthusiasts often struggle to track and share their garden progress due to a lack of structured and engaging platforms. This problem affects home gardeners, hobbyists, and beginners who wish to document their gardening journey and connect with a like-minded community. **PlantPals** solves this by providing a platform where users can create virtual garden portfolios, engage with other gardeners, and share their progress.

### [Insert Video Prototype Here] 

*(Insert your project demonstration video here once available)*

## Features

### 🌿 Garden Portfolio
Users can create a virtual garden to reflect the plants they are growing in real life. Each plant or section can be updated with:
- Progress images
- Growth details
- Watering schedules
- Other notes

Users also have the option to share their virtual garden portfolio publicly or with selected individuals.

### 🌍 Social Network and Messaging
- Users can view other users' gardens and portfolios, leave comments, and interact.
- A **Direct Messaging** feature allows users to ask questions, give feedback, and socialize with other gardeners.

### 🌟 Community Sharing
- Featured portfolios of the week/month will be highlighted.
- Users can follow each other and build a gardening community.

## User Experience

Upon launching the application, users will be greeted by the **login page**. New users can sign up using the **signup page**, after which they will be automatically logged into their new account. Once logged in, users land on their **Garden Portfolio** page, which serves as their personal dashboard.

On the left-hand side, a consistent **navigation menu** allows users to access various options:
- Home
- Profile
- Settings
- View Other Profiles
- Create New Journal Post
- Logout

Within each garden journal, users can browse all their posts and updates, creating a visual timeline of their gardening progress.

## Technologies Used

- **Web Application Framework**: Flask (Python, HTML, CSS, Bootstrap, JavaScript)
- **Backend Services**: Firebase SDK
  - **Authentication**: Secure user login/signup
  - **Firestore Database**: User management, garden portfolio data storage

## How to Run

1. Clone the repository:
   git clone https://github.com/YourUsername/PlantPals.git

2. Create venv:
   python3 -m venv venv (linux)
   python -m venv venv (windows)

3. Activate venv::
   source venv/bin/activate (linux)
   .\venv\Scripts\Activate (windows)

4. Install dependencies:
   pip install -r requirements.txt

5. Run the app::
   python app.py
