EduNova - A simple Learning Management System.


About the Project.

	EduNova is a minimalist Learning Management System built with Django, designed to provide a foundational platform 
for managing online course, modules, lessons. It supports distinct user roles (students, instructor), course enrollment
and basic lesson content delivery and tracking.

	This project was developed as a learning exercise to solidify concepts in Django web development, including : 
	-Custom user models and authentication,
	-Model relationships,
	-Function_based views,
	-URL routing and namespacing,
	-Django forms and Form validations,
	-Database management,
	-Basic templates and user interface,
	-Rich text editor.

Project Status:
	This project is in active development. The core functionality is in place, allowing instructor to create courses and students to enroll and complete lessons.

	Core Feature : Fully functional.
	Quiz System : Fully functional.
	Discussion : Fully functional.
	Core apps : Scaffolding exists, but these app are planned for future implementations.


Features.

	-User authentication and roles-
		-Student registration and login system.
		-Separate permission based role for students and instructor.
		-Instructor Request Workflow: 
			Users can request to became an instructor during registration. An admin must approve the request before instructor privileges are granted.
		
	-Course & Content management-
		-Instructor can create, update and delete their course through a dedicated dashboard.
		-Courses are organized into modules, which in turn contain individual lessons.
		-Support for multiple lesson content type, including text, video urls, files.
		
	-Enrollment & Progress tracking-
		-Students can browse and enroll in published courses.
		-Prevents students from enrolling in the same course multiple times.
		-Students can mark individual lesson as complete to track their learning progress.

	-In App Notification-
		-Instructor receive a notification when a new student enroll in their course.
		-Student receive a notification when a new lesson added to a course they are enrolled in.
		-Admin are notified when a user request instructor privileges.
		
	-Lesson interaction-
		-A simple commenting system allows students to post comments on each lesson.
		
	-Django admin integrations-
		-Full adminstration interface for managing users, courses, modules, lessons and enrollment.

	-Discussion-
		-Instructor and Student can build conversation in their course.


Technologies Used.

	-Backend-
		-Python 3.11
		-Django 5.2
		
	-Database-
		-PostgreSQL 
		
	-Frontend-
		-Html5
		-CSS3
		-Bootstrap
	
	-Tool
		-Docker
		-TinyMCE


Getting Started.
	
	Follow this instruction to get a copy of the project up and running on your local machine for development and testing purpose.
	
	-Prerequisites-
		-python 3.8+
		-python (python package installer)
		-Docker (optional for containerized setup)
		
	-Installation-
		1. Clone the repository : bash
			git clone https://github.com/Anirudh11V/Learning_Management_System.git 
			cd lms
			
		2. Create and activate a virtual environment :
			-on windows : py -m venv venv 
					then, venv\acripts\activate
						  
			-on macos/linux : python -m venv venv
					then, source venv/bin/activate
				
		3. Install dependencies : 
			- pip install -r requirements.txt
			
		4. Apply database migrations : 
			- py manage.py makemigrations
			- py manage.py migrate
			
		5. Create superuser : 
			- py manage.py createsuperuser
			
		-Running Applications-
			1. Start Django development server.
				-py manage.py runserver
				
			2. Access the application.
				-Open your web browser and go to "http://127.0.0.1:8000/"

					(or)

		1. Clone the repository : bash
			git clone https://github.com/Anirudh11V/Learning_Management_System.git 
			cd lms
			
		2. Create a .env file in the root directory of the project. Add the necessary environment variables for django and postgresql
				(e.g., SECRET_KEY, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, etc).
				
		3. Build the docker container.
			docker-compose up --build
			
			* This command will build the images, create the services and start the application, database.
			
		4. Run database migrations.
			docker-compose exec web python manage.py makemigrations
			docker-compose exec web python manage.py migrate
			
			* Open new terminal and run the migrations inside the web container.
			

Usage.

	-Admin panel.
		-Access the admin panel at "http://127.0.0.1:8000/admin/",
		-Log in with your superuser credentials.

		-Approve Instructor Accounts:
			Go to Users -> Member users. Filter by Instructor Request. Select a user, check the is_instructor checkbox ans save.

		-Manage Content:
			Create Courses: Go to courses -> Click add Courses, fill in details, set is_published= True.
			Add modules and lessons: From a course detail page in the admin , you can add Modules (related to the Course) and then Lessons (related to Modules). Ensure lessons are is_published= True.
		
	-Student user flow.
		1.Register: Go to http://127.0.0.1:8000/accounts/register/ to create a new student account.
		2.Login: login witn your new student credentials. http://127.0.0.1:8000/ .
		3.Browse Course: View the list of course on the homepage or via /courses/ .
		4.View course details: click on a course to see its description, modules, lessons.
		5.Enroll: on the course details page, if not already enrolled, click enroll now.
		6.Access lessons: once enrolled, click on any lesson within the course to view its content.
		7.Mark compelete: you can find a button within the lesson details to mark it as compelete.
		8.My Learning Dashboard: Students can view their enrolled courses in here.
		9.Profile: Users details and user can reset their password from here. 
		
	-Instructor user flow.
		1.Login: login with an instructor account at http://127.0.0.1:8000/.
		2.Browse course: instructor can view course details, but they cannot enroll in course.
		3.My Dashboard: Dedicated instructor dashboard for managing their own courses and seperate interface for instructors to view student progress.
		4.Course create: click on Add new course in instructor dashboard and fill up details, set is_published= True.
		5.Module create: After creation of course now in course user can see a button to Add new module.
			After module created instructor have access to Edit/Delete/Add new lesson for every module.
		6.Lesson create: By clicking on Add new lesson button below module, can create lesson. Ensure lessons are is_published= True.
			After lesson created instructor have access to Edit/Delete/ for every lesson.
			Lesson content accepts text/file/video url.
		7.Profile: Users details and user can reset their password from here.
		

Project Structure.
	This project is organized into several Django apps:

	courses: Manages courses, modules, lessons.
	users: Handles the custom user model and authentication and profile.
	enrollment: Manage course enrollment and tracks lesson completion.
	quiz: Contains models of quizzes, questions and answers.
	discussion: In course, handles conversation of both instructor and student.
	core: placeholder app for future development.

Future Enhancements.
	
	-Payment gateway integrations: Implement a real payment gateway for paid course.
	
	-Assignments: Add functionality for assignments, and grading.

	-Certificate: Add functionality for certification after successfully completion of course.
	
	-Notifications: Advanced, email notification for enrollment, new lessons etc.
	
	-Improved UI\UX: A more polished and responsive frontend design using Css framework.
	
	-Media housting: Integration with cloud storage for media files.
	

Contributing.

	-Contributions are welcome! If you'd like to contribute, please follow these steps:
	1.Fork the repository.
	2.Create the new branch.
	3.Make your changes.
	4.Commit your changes.
	5.Push to the branch.
	6.Open a pull request.
	
	
License.

	-This project is licensed under the MIT License - see the [License] (License) file for details.
	
Contact.

	- Anirudh - anirudh11v@gmail.com .
	- project link: https://github.com/Anirudh11V/Learning_Management_System.git   .