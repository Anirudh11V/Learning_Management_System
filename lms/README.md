lms - A simple Learning Management System.


About the Project.

	lms is a minimalist Learning Management System (LMS) built with Django, designed to provide a foundational platform 
for managing online course, modules, lessons. It supports distinct user roles (students, instructor), course enrollment
and basic lesson content delivery and tracking.

	This project was developed as a learning exercise to solidify concepts in Django web development, including : 
-Custom user models and authentication,
-Model relationships,
-Function_based views,
-URL routing and namespacing,
-Djanfo forms and Form validations,
-Database management,
-Basic templates and user interface.


Features.

	-User authentication and roles-
		-Student registration and login,
		-Separate roles for students and instructor,
		-Instructor accounts are created by admin for security.
		
	-Course management-
		-Browse a list of available course,
		-view detailed course informations,
		-Courses can be published / unpublished.
		
	-Modules and lessons structure-
		-Courses are organized into modules,
		-Modules contains individual lessons.
		-Lessons can have various content type ( texts, videos, files ).
		
	-Enrollment System-
		-Logged_in student can enroll in course,
		-Prevents enroll in same course,
		
	-Lesson progress tracking-
		-Students can view lesson content,
		-Students can mark individual lesson as complete,
		-Track lesson completion status per student.
		
	-Django admin integrations-
		-Full adminstration interface for managing users, courses, modules, lessons and enrollment.


Technologies Used.

	-Backend-
		-Python 3.11
		-Django 5.2
		
	-Database-
		-sqlite3 
		
	-Frontend-
		-Html5,
		-CSS3


Getting Started.
	
	Follow this instruction to get a copy of the project up and running on your local machine for development and testing purpose.
	
	-Prerequisites-
		-python 3.8+
		-pyhton (pyhton package installer)
		
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
			

Usage.

	-Admin panel.
		-Access the admin panel at "http://127.0.0.1:8000/admin/",
		-Log in with your superuser credentials.
		
		-Create Courses: Go to courses -> Click add Courses, fill in details, set is_published= True.
		-Add modules and lessons: From a course detail page in the admin , you can add Modules (related to the Course) and
			then Lessons (related to Modules). Ensure lessons are is_published= True.
		-Create Instructor account: Go to Users -> ManageUsers. Add a new user or edit an existing one, and check the is_instructor checkbox.
		
	-Student user flow.
		1.Register: Go to http://127.0.0.1:8000/accounts/register/ to create a new student account.
		2.Login: login witn your new student credentials. http://127.0.0.1:8000/ .
		3.Browse Course: View the list of course on the homepage or via /courses/ .
		4.View course details: click on a course to see its description, modules, lessons.
		5.Enroll: on the course details page, if not already enrolled, click enroll now.
		6.Access lessons: once enrolled, click on any lesson within the course to view its content.
		7.Mark compelete: you can find a button within the lesson details to mark it as compelete.
		
	-Instructor user flow.
		1.Login: login with an instructor account at http://127.0.0.1:8000/.
		2.Browse course: instructor can view course details, but they cannot enroll in course.
		3.(future): dedicated instructor dashboard for managing their own courses.
		

Project Structure.

|--lms						#Main django project setting.
|	|--settings.py
|	|--urls.py
|	|--wsgi.py
|---manage.py	
|
|--courses/					#Django app for course, module, lesson.
|   |--migrations.py
|	|--templates/courses/
|		|--access_denied.html
|		|--course_list.html
|		|--course_detail.html
|		|--lesson_detail.html
|	|--admin.py
|	|--models.py
|	|--urls.py
|	|--views.py
|
|--users/					#Django app for Customuser model and authentication.
|   |--migrations.py
|	|--templates/users/
|		|--login.html
|		|--register.html
|		|--profile.html
|		|--stu_dashboard.html
|	|--admin.py
|	|--forms.py
|	|--models.py
|	|--urls.py
|	|--views.py
|
|--enrollments/				#Django app for handling course enrollment and lesson progress.
|   |--migrations.py
|	|--admin.py
|	|--models.py
|	|--urls.py
|	|--views.py
|
|--quiz/					#Django app for handling quiz.
|   |--migrations.py
|	|--admin.py
|	|--models.py
|	|--urls.py
|	|--views.py
|
|--core/					#for (future).
|   |--migrations.py
|	|--admin.py
|	|--models.py
|	|--urls.py
|	|--views.py
|
|--discussion/				# for (future).
|   |--migrations.py
|	|--admin.py
|	|--models.py
|	|--urls.py
|	|--views.py
|
|---static/
|	|--style.css
|
|---templates
|	|--main.html 
|
|---requirements.txt
|---README.md


Future Enhancements.
		
	-Dedicated instructor dashboard: A seperate interface for instructors to manage their courses, view student progress, and
		interact with students.
	
	-Payment gateway integrations: Implement a real payment gateway for paid course.
	
	-Quizzes & Assignments: Add functionality for quizzes, assignments, and grading.
	
	-Notifications: Email notification for enrollment, new lessons etc.
	
	-Search & filtering: Enhanced course action search and filtering options.
	
	-Rich text editor: For course/lesson descriptions.
	
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
	-project link: https://github.com/Anirudh11V/Learning_Management_System.git   .