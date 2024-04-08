from flask import Flask, render_template, request, redirect, url_for, jsonify,session
from flask_sqlalchemy import SQLAlchemy
import os
from wtforms import RadioField
from werkzeug.utils import secure_filename
from runner import process_single_job
from werkzeug.security import generate_password_hash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_login import LoginManager
from flask import flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from flask import send_from_directory
from openai import OpenAI 
import openai
from flask_migrate import Migrate
from flask_login import login_user


openai.api_key = 'sk-VvY8Z9DhB4DGugbfXt1ST3BlbkFJoQ0e1JqMd6DJnCeVuYOqy'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
db = SQLAlchemy(app)

migrate = Migrate(app, db)

app.config['SECRET_KEY'] = b'\xf60g\x1e\xd9K\x90\xdb.@\xad\xb9\x10\xbb\x1d\x08'
login_manager = LoginManager(app)
login_manager.init_app(app)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description_filename = db.Column(db.String(100), nullable=False)
    logo_filename = db.Column(db.String(100), nullable=False)
    job_url = db.Column(db.String(200), nullable=True)
    values_category = db.Column(db.String(50))  # Assuming URLs can be null
    vision_category = db.Column(db.String(50))
    culture_category = db.Column(db.String(50))


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    university = StringField('University', validators=[DataRequired()])
    degree_program = StringField('Degree Program', validators=[DataRequired()])
    year_of_graduation = StringField('Year of Graduation', validators=[DataRequired()])
    submit = SubmitField('Register')

class MyForm(FlaskForm):
    my_radio_field = RadioField('Label', choices=[('value1', 'Option 1'), ('value2', 'Option 2')])

class UserInfoForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    university = StringField('University', validators=[DataRequired()])
    degree_program = StringField('Degree Program', validators=[DataRequired()])
    year_of_graduation = StringField('Year of Graduation', validators=[DataRequired()])
    submit = SubmitField('Finish')



class VisionQuizForm(FlaskForm):
    question1 = RadioField('What is your primary goal for the future?', choices=[
        ('A', 'Becoming a market leader'),
        ('B', 'Innovating within my industry'),
        ('C', 'Expanding globally'),
        ('D', 'Focusing on sustainability')])
    question2 = RadioField('How do you define success?', choices=[
        ('A', 'Financial profitability'),
        ('B', 'Customer satisfaction'),
        ('C', 'Social impact'),
        ('D', 'Team happiness')])
    question3 = RadioField('What impact do you want to have on society?', choices=[
        ('A', 'Improve quality of life'),
        ('B', 'Drive technological advancement'),
        ('C', 'Promote environmental sustainability'),
        ('D', 'Enhance education and knowledge')])
    question4 = RadioField('Where do you see your industry heading?', choices=[
        ('A', 'Leading a niche market'),
        ('B', 'Pioneering new technologies'),
        ('C', 'Advocating for regulatory changes'),
        ('D', 'Fostering community and collaboration')])
    question5 = RadioField('How do you plan to innovate?', choices=[
        ('A', 'Adopting new technologies'),
        ('B', 'Through strategic partnerships'),
        ('C', 'Expanding our product line'),
        ('D', 'Focusing on customer feedback')])
    submit = SubmitField('Submit')

class CultureFitQuizForm(FlaskForm):
    question1 = RadioField('What word best describes your ideal work environment?', choices=[
        ('A', 'Collaborative'),
        ('B', 'Innovative'),
        ('C', 'Competitive'),
        ('D', 'Relaxed')])
    question2 = RadioField('How do you prefer decision-making to be handled?', choices=[
        ('A', 'Top-down leadership'),
        ('B', 'Team consensus'),
        ('C', 'Individual autonomy'),
        ('D', 'Data-driven analysis')])
    question3 = RadioField('What do you value most in team members?', choices=[
        ('A', 'Creativity and innovation'),
        ('B', 'Dedication and hard work'),
        ('C', 'Flexibility and adaptability'),
        ('D', 'Expertise and skill')])
    question4 = RadioField('How should work-life balance be promoted?', choices=[
        ('A', 'Flexible working hours'),
        ('B', 'Remote work options'),
        ('C', 'Mandatory time off'),
        ('D', 'Wellness programs')])
    question5 = RadioField('How do you approach failure?', choices=[
        ('A', 'As a learning opportunity'),
        ('B', 'As a setback to analyze'),
        ('C', 'As an inevitable part of innovation'),
        ('D', 'Something to minimize through planning')])
    submit = SubmitField('Submit')


class ValuesQuizForm(FlaskForm):
    question1 = RadioField('What drives you to work every day?', choices=[
        ('A', 'Personal achievement and recognition'),
        ('B', 'Making a difference in society'),
        ('C', 'Financial security and prosperity'),
        ('D', 'Continuous learning and personal growth')])
    question2 = RadioField('How important is work-life balance to you?', choices=[
        ('A', 'Essential - My personal life is as important as my career'),
        ('B', 'Important, but willing to sacrifice for career advancement'),
        ('C', 'I prioritize work over personal time'),
        ('D', 'Balance varies based on current work demands')])
    question3 = RadioField('What is your preferred way of contributing to a team?', choices=[
        ('A', 'By leading and making strategic decisions'),
        ('B', 'Through creative ideas and innovative solutions'),
        ('C', 'By supporting team members and fostering unity'),
        ('D', 'Through meticulous work and attention to detail')])
    question4 = RadioField('How do you view the role of ethics in your work?', choices=[
        ('A', 'Paramount - ethical considerations guide all my decisions'),
        ('B', 'Important, but must be balanced with business needs'),
        ('C', 'Secondary to achieving results and success'),
        ('D', 'As guidelines that can be adapted to the situation')])
    question5 = RadioField('What motivates you to achieve success?', choices=[
        ('A', 'Personal satisfaction and self-improvement'),
        ('B', 'Recognition from peers and industry'),
        ('C', 'The impact of my work on others and the world'),
        ('D', 'Financial rewards and job security')])
    submit = SubmitField('Submit')




class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    university = db.Column(db.String(100))
    degree_program = db.Column(db.String(100))
    year_of_graduation = db.Column(db.String(4))
    values_type = db.Column(db.String(50))
    vision_type = db.Column(db.String(50))
    culture_type = db.Column(db.String(50))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class StudentInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Assuming the User model's tablename is 'user'
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    university = db.Column(db.String(100), nullable=False)
    degree_program = db.Column(db.String(100), nullable=False)
    year_of_graduation = db.Column(db.String(4), nullable=False)



class Startup(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)  # Add this line
    password_hash = db.Column(db.String(200), nullable=False)  # Add this line
    name = db.Column(db.String(80), nullable=False)
    companyName = db.Column(db.String(120), nullable=False)
    size = db.Column(db.Integer)
    industry = db.Column(db.String(120))
    url = db.Column(db.String(120))
    vision = db.Column(db.String(500))
    values = db.Column(db.String(500))
    culture = db.Column(db.String(500))


    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return '<Startup %r>' % self.companyName
    


@login_manager.user_loader
def load_user(user_id):
    if session.get('user_type') == 'user':
        return User.query.get(int(user_id))
    elif session.get('user_type') == 'startup':
        return Startup.query.get(int(user_id))
    return None



@app.route('/debug/jobs')
def debug_jobs():
    jobs = Job.query.all()
    job_data = [{'id': job.id, 'description': job.description_filename, 'values_category': job.values_category} for job in jobs]
    return jsonify(job_data)



@app.route('/quiz-result/<type>')
def quiz_result(type):

   return render_template('quiz_result.html', type=type)

@app.route('/post-jobs')
def post_job():
    return render_template('startup.html')

@app.route('/delete_startup', methods=['POST'])
@login_required
def delete_startup():
    # Assuming you have access to current_user or similar
    startup_id = current_user.id  # or fetch the startup ID dynamically
    startup_to_delete = Startup.query.get(startup_id)
    if startup_to_delete:
        db.session.delete(startup_to_delete)
        db.session.commit()
        flash('Startup deleted successfully.')
        return redirect(url_for('login'))  # or any other page
    else:
        flash('Startup not found.')
        return redirect(url_for('home'))




def determine_values_type(answer1, answer2, answer3, answer4, answer5):
    # Initialize the OpenAI client
    client = openai.Client(api_key='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')
    

    try:
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Based on these answers, categorize the user into one of the following 4 values types(Drive for Excellence , Community and Impact , Stability and Reliability or Growth and Adabtability) , return only the name of the category and nothing else . here are the answers :\nAnswer 1: {answer1}\nAnswer 2: {answer2}\nAnswer 3: {answer3}\nAnswer 4: {answer4} Answer 5: {answer5}",
            temperature=0.6,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Extract and return the response text
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    

    




def determine_vision_type(visionanswer1, visionanswer2, visionanswer3, visionanswer4, visionanswer5):
    # Initialize the OpenAI client
    client = openai.Client(api_key='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')
    

    try:
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Based on these answers, categorize the user into one of the following 4 values types ( Innovation-focused: Prioritizing breakthroughs and new solutions. Sustainability-driven: Committed to environmental and social responsibility. Growth-oriented: Focused on scaling and market expansion. Community-centric: Valuing social impact and community engagement.) , you should return only the name of the category and nothing else . here are the answers :\nAnswer 1: {visionanswer1}\nAnswer 2: {visionanswer2}\nAnswer 3: {visionanswer3}\nAnswer 4: {visionanswer4} Answer 5: {visionanswer5}",
            temperature=0.6,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Extract and return the response text
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None





def determine_culture_type(cultureanswer1, cultureanswer2, cultureanswer3, cultureanswer4, cultureanswer5):
    # Initialize the OpenAI client
    client = openai.Client(api_key='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')
    

    try:
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Based on these answers, categorize the user into one of the following 4 values types ( Collaborative: Emphasizing teamwork and shared goals. High-paced: Thriving in fast-moving and dynamic environments. Independent: Valuing autonomy and self-direction. Inclusive: Prioritizing diversity and open-mindedness.) , you should return only the name of the category and nothing else . here are the answers :\nAnswer 1: {cultureanswer1}\nAnswer 2: {cultureanswer2}\nAnswer 3: {cultureanswer3}\nAnswer 4: {cultureanswer4} Answer 5: {cultureanswer5}",
            temperature=0.6,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Extract and return the response text
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None




def categorize_company_profile(text, category_type):
    # Initialize the OpenAI client with your API key
    client = openai.Client(api_key='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')
    

    try:
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Based on this text, categorize the company's {category_type} into one of the following 4 types: (if you  are categorizing the comapanys values then choose one of the following 4 : (Drive for Excellence, Community and Impact , Stability and Reliability or Growth and Adaptability) else if the category type is vision then choose one of the following : (Innovation-focused , Sustainability-driven , Growth-oriented or Community-centric ) else if the category type is culture then choose one of the following :(Collaborative , High-Paced , Independent or inclusive) . you should only return the name of the category and nothing else . Text:\n{text}",
            temperature=0.6,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Extract and return the response text
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred while categorizing company {category_type}: {e}")
        return None


@app.route('/userinfo', methods=['GET', 'POST'])
@login_required
def userinfo():
    form = UserInfoForm()
    if form.validate_on_submit():
        # Create a new StudentInfo object and populate it with form data
        student_info = StudentInfo(
            user_id=current_user.id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            university=form.university.data,
            degree_program=form.degree_program.data,
            year_of_graduation=form.year_of_graduation.data
         
        )
        # Add to the database and commit
        db.session.add(student_info)
        db.session.commit()
        
        # Redirect to the student page or another success page
        return redirect(url_for('student'))
    
    # Render the template with the form object
    return render_template('userinfo.html', form=form)

# Ensure the directories for descriptions and logos exist
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'descriptions'), exist_ok=True)
os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'logos'), exist_ok=True)

@app.route('/choose')
def home():
    return render_template('choose.html')


@app.route('/student_home')
def student_home():
    return render_template('student.html' , user= current_user)

@app.route('/profile')
@login_required
def profile():
    # You don't need to query StudentInfo, as the additional fields are in the User model
    # Simply pass the current_user to the template
    return render_template('profile.html', user=current_user)



@app.route('/startup/dashboard')
@login_required
def startup_dashboard():
    # This route will display the startup's dashboard or profile information
    return render_template('startup_profile.html', startup=current_user)

@app.route('/values-quiz', methods=['GET', 'POST'])
@login_required
def values_quiz():
    form = ValuesQuizForm()
    category = None  # Initialize category as None
    if form.validate_on_submit():
        # Extract data from form and pass to determination function
        category = determine_values_type(
            form.question1.data, 
            form.question2.data, 
            form.question3.data, 
            form.question4.data,
            form.question5.data
        )
        current_user.value_type = category
        db.session.commit()
        # Proceed to show the c
    return render_template('values_quiz.html', form=form, category=category)




@app.route('/vision-quiz', methods=['GET', 'POST'])
@login_required
def vision_quiz():
    form = VisionQuizForm()
    category = None  # Initialize category as None
    if form.validate_on_submit():
        # Extract data from form and pass to determination function
        category = determine_vision_type(
            form.question1.data, 
            form.question2.data, 
            form.question3.data, 
            form.question4.data,
            form.question5.data
        )
        current_user.vision_type = category
        db.session.commit()
        # Proceed to show the category with an option to go to the next quiz
    return render_template('vision_quiz.html', form=form, category=category)

@app.route('/culture-fit-quiz', methods=['GET', 'POST'])
@login_required
def culture_fit_quiz():
    form = CultureFitQuizForm()
    category = None  # Initialize category as None
    if form.validate_on_submit():
        # Extract data from form and pass to determination function
        category = determine_culture_type(
            form.question1.data, 
            form.question2.data, 
            form.question3.data, 
            form.question4.data,
            form.question5.data
        )
        current_user.culture_fit_type = category
        db.session.commit()
        return redirect(url_for('start_matching'))
    return render_template('culture_fit_quiz.html', form=form, category=category)

    






def get_job_name(filename):
    # Remove the '.txt' extension to get the job title
    job_title = os.path.splitext(filename)[0]
    return job_title

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Check if user exists
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
           login_user(user, remember=True)
           session['user_type'] = 'user'  # Set user type for students
           return redirect(url_for('student'))
        else:
            # Query for a startup instead of using an undefined variable
            startup = Startup.query.filter_by(email=form.email.data).first()
            if startup and startup.check_password(form.password.data):
                login_user(startup, remember=True)
                session['user_type'] = 'startup' 
                session['startup_id'] = startup.id # Set user type for startups
                return redirect(url_for('startup_home'))
    
    return render_template('login.html', form=form)




@app.route('/process_info', methods=['POST'])
def process_info():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    university = request.form.get('university')
    degree_program = request.form.get('degree_program')
    year_of_graduation = request.form.get('year_of_graduation')

    # Validation logic here if necessary, e.g., check if the year of graduation is a number

    # Create an instance of the StudentInfo
    student_info = StudentInfo(
        first_name=first_name,
        last_name=last_name,
        university=university,
        degree_program=degree_program,
        year_of_graduation=year_of_graduation
    )

    # Add to the session and commit to the database
    db.session.add(student_info)
    db.session.commit()

    # Redirect to the student page or another success page
    return redirect(url_for('student'))




def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create a new User instance with all form data
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            university=form.university.data,
            degree_program=form.degree_program.data,
            year_of_graduation=form.year_of_graduation.data
        )
        user.set_password(form.password.data)  # Set the password

        # Add to the database and commit
        db.session.add(user)
        db.session.commit()

        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))  # Redirect to login page after registration

    return render_template('register.html', title='Register', form=form)


@app.route('/signup/startup', methods=['GET', 'POST'])
def signup_startup():
    if request.method == 'POST':
        data = request.json  # Access JSON data sent from the client
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        companyName = data.get('companyName')
        size = data.get('size')
        industry = data.get('industry')
        url = data.get('url')
        values = data.get('values')  # New field
        vision = data.get('vision')  # New field
        culture = data.get('culture')  # New field

        categorized_values = categorize_company_profile(values, "values")
        categorized_vision = categorize_company_profile(vision, "vision")
        categorized_culture = categorize_company_profile(culture, "culture")


        if not email or not password:  # Basic validation
            flash('Email and password are required.')
            return redirect(url_for('signup_startup'))

        hashed_password = generate_password_hash(password)
        new_startup = Startup(email=email, password_hash=hashed_password, name=name, companyName=companyName,
                               size=size, industry=industry, url=url,values=categorized_values,  # Use the categorized values
                      vision=categorized_vision,  # Use the categorized vision
                      culture=categorized_culture)
        db.session.add(new_startup)
        try:
            db.session.commit()
            login_user(new_startup)  # Log in the new startup
            return redirect('/startup/home')  # Adjust this to your startup home page's route
        except Exception as e:
            db.session.rollback()  # Rollback the session in case of error
            print(e)  # For debugging, better to log this in a real application
            flash('An error occurred. Please try again.')
            return redirect(url_for('signup_startup'))

    return render_template('signup_startup.html')



@app.route('/startup/home')
def startup_home():
    if 'startup_id' not in session:
        # Example: Redirect to a welcome or info page instead of login
        return redirect('/login')
    return render_template('startup_home.html' , startup= current_user)


def categorize_job_description(job_desc_content):
    client = openai.Client(api_key='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')
    try:
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Categorize this job description into one of the following types: The Strategist, The Innovator, The Diplomat, The Leader. you should return only the name of the category and nothing else. here is the job description:\n\n{job_desc_content}",
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Extract and return the response text
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

@app.route('/startup_profile', methods=['GET', 'POST'])
def startup_profile():
    if request.method == 'POST':
        # Get the uploaded files
        job_description = request.files['job_description']
        company_logo = request.files['company_logo']
        job_url = request.form.get('job_url') 
        if job_description and company_logo:
            description_filename = secure_filename(job_description.filename)
            logo_filename = secure_filename(company_logo.filename)

            # Save files in their respective folders
            job_description_path = os.path.join(app.config['UPLOAD_FOLDER'], 'descriptions', description_filename)
            company_logo_path = os.path.join(app.config['UPLOAD_FOLDER'], 'logos', logo_filename)
            
            # Ensure the directories exist
            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'descriptions'), exist_ok=True)
            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'logos'), exist_ok=True)

            # Save the files
            job_description.save(job_description_path)
            company_logo.save(company_logo_path)


            with open(job_description_path, 'r') as file:
                job_desc_content = file.read()

            values_category = categorize_job_description(job_desc_content)

            # Create a new Job entry in the database
            new_job = Job(description_filename=description_filename, logo_filename=logo_filename, job_url=job_url , values_category=values_category)
            db.session.add(new_job)
            db.session.commit()

            return "<h1>Job Description and Logo Uploaded Successfully</h1>"
    return render_template('startup.html')



@app.route('/student')
@login_required
def student():
    return render_template('student.html', user=current_user)

@app.route('/start-matching', methods=['GET'])
def start_matching():
    return render_template('resume-upload.html')

@app.route('/job-board')
def job_board():
    # List all job description files from the UPLOAD_FOLDER
    job_files = [f for f in os.listdir('uploads') if os.path.isfile(os.path.join('uploads', f))]
    # Process filenames to more readable job names
    job_names = [os.path.splitext(f)[0].replace('_', ' ') for f in job_files]
    return render_template('job_board.html', job_names=job_names)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/job/<job_name>')
def job_details(job_name):
    # Convert the job name back to the filename format
    filename = job_name.replace(' ', '_') + '.txt'
    file_path = os.path.join('UPLOAD_FOLDER', filename)
    job_desc_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.isfile(file_path):
      with open(job_desc_path, 'r') as file:
        job_desc_content = file.read()
        return render_template('job_details.html', job_name=job_name, job_description=job_desc_content)
    else:
        return "<h1>Job description not found.</h1>"

@app.route('/upload-resume', methods=['POST'])
def upload_resume():
    # Check if the post request has the file part
    if 'resume' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    file = request.files['resume']

    # If the user does not select a file, the browser submits an
    # empty file without a filename.
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200

@app.route('/match-results', methods=['POST'])
def match_results():
    resume_file = request.files['resume']
    if resume_file and allowed_file(resume_file.filename):
        resume_filename = secure_filename(resume_file.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
        resume_file.save(resume_path)

        # Assume the function to get the user's vision and culture type is similar to getting values type
        current_user_values_type = current_user.values_type
        current_user_vision_type = current_user.vision_type
        current_user_culture_type = current_user.culture_type

        jobs = Job.query.all()
        match_results = []

        for job in jobs:
            job_desc_path = os.path.join(app.config['UPLOAD_FOLDER'], job.description_filename)
            similarity = process_single_job(resume_path, job_desc_path)
            
            # Adjust similarity based on values, vision, and culture alignment
            if job.values_category == current_user_values_type:
                similarity *= 1.5  # Weight for values alignment
            if job.vision_category == current_user_vision_type:
                similarity *= 1.2  # Weight for vision alignment
            if job.culture_category == current_user_culture_type:
                similarity *= 1.2  # Weight for culture alignment
            
            match_results.append((job, similarity))

        match_results.sort(key=lambda x: x[1], reverse=True)
        top_matches = match_results[:3]

        # Prepare matches for rendering
        matches = [{
            'job_name': get_job_name(job.description_filename), 
            'similarity': similarity,
            'logo_url': url_for('uploaded_file', filename=job.logo_filename),
            'job_url': job.job_url,
            'value_category': job.values_category,
            'vision_category': job.vision_category,
            'culture_category': job.culture_category,
            'student_type': current_user_values_type
        } for job, similarity in top_matches]

        return render_template('match_results.html', matches=matches)

    return redirect(url_for('start_matching'))







@app.route('/uploads/logos/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'] + '/logos/', filename)



def allowed_file(filename):
    # Your logic to check allowed file types
    pass


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf', 'docx', 'txt'}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables within the application context
    app.run(debug=True)