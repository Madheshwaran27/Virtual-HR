from flask import Flask, render_template,send_file,Response,request, redirect, flash, url_for, session
from flask_mysqldb import MySQL
import os
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from Resume_Analyzer import Resume_Ranker


app = Flask(__name__)

app.config['SECRET_KEY'] = '123'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Replace 'username' with your MySQL username
app.config['MYSQL_PASSWORD'] = ''  # Replace 'password' with your MySQL password
app.config['MYSQL_DB'] = 'test'  # Replace 'registration' with your MySQL database name
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

# End of MySQL



# Login and Registration functions


@app.route('/')
def index():
    return render_template('Homepage.html')

@app.route('/Admin')
def admin():
    return render_template('Admin_Login.html')

@app.route('/Recruiter')
def recruiter():
    return render_template('Recruiter_Login.html')

@app.route('/User')
def user():
    return render_template('User_Login.html')

@app.route('/Recruiter-Reg')
def recruiter_reg():
    return render_template('Recruiter_Registration.html')

@app.route('/User-Reg')
def user_reg():
    return render_template('User_Registration.html')



@app.route('/register-recruiter', methods=['POST','GET'])
def register_recruiter():
    if request.method == 'POST':
        recruiterDetails = request.form
        name =recruiterDetails['name']
        email =recruiterDetails['email']
        password =recruiterDetails['password']
        mobile =recruiterDetails['mobile']
        company =recruiterDetails['company-name']
        city =recruiterDetails['city-name']
        street =recruiterDetails['street-name']
        landmark =recruiterDetails['landmark']

        try :
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO recruiter(r_name, r_email, password, r_mobile, c_name, city, street, landmark) VALUES(%s, %s, %s, %s, %s, %s,%s,%s)", (name, email, password, mobile, company, city, street, landmark))
            mysql.connection.commit()
            cur.close()
            flash("Recruiter Successfully Registered","success")
            return render_template('Recruiter_Registration.html')
        
        except mysql.connection.IntegrityError as e:
            if e :
                flash("Recruiter already Exist's","warning")
                return render_template('Recruiter_Registration.html')


    

@app.route('/register-user', methods=['POST','GET'])
def register_user():
    if request.method == 'POST':
        userDetails = request.form
        first_name = userDetails['f_name']
        last_name = userDetails['l_name']
        email = userDetails['email']
        password = userDetails['password']
        mobile = userDetails['mobile']

        

        try:
            cur = mysql.connection.cursor()
            if cur.execute("INSERT INTO user(f_name,l_name, u_email, u_pass, u_mobile) VALUES(%s, %s, %s, %s, %s)", (first_name, last_name , email, password, mobile)) :
                mysql.connection.commit()
                cur.close()
                flash("User Registered Successfully","success")
                return render_template('User_Registration.html')
        
        except mysql.connection.IntegrityError as e:
            if e :
                flash("User already Exist's","warning")
                return render_template('User_Registration.html')
                



@app.route('/admin-login', methods = ['POST','GET'])
def admin_login():
    if request.method == 'POST':
        adminDetails = request.form
        email = adminDetails['email']
        password = adminDetails['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT email, password FROM admin WHERE email = %s AND password = %s", (email,password))
        admin = cur.fetchone()
        cur.close()

        if admin:
            session['id'] = 'admin'
            return render_template('Dashboard_Admin.html')
        else :
            flash('Invalid username or password', 'danger')

    return redirect(url_for('dashboard_admin'))


@app.route('/recruiter-login', methods = ['POST','GET'])
def recruiter_login():
    if request.method == 'POST':
        recruiterDetails = request.form
        email = recruiterDetails['email']
        password = recruiterDetails['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT r_email, password FROM recruiter WHERE r_email = %s AND password = %s", (email,password))
        recruiter = cur.fetchone()
        cur.close()

        if recruiter:
            session['state'] = True
            session['recruiter_id'] = email
            return redirect(url_for('dashboard_recruiter'))
        else :
            flash('Invalid username or password', 'danger')

    return redirect(url_for('recruiter'))


@app.route('/user-login', methods = ['POST','GET'])
def user_login():
    if request.method == 'POST':
        userDetails = request.form
        email = userDetails['email']
        password = userDetails['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT u_email, u_pass FROM user WHERE u_email = %s AND u_pass = %s", (email,password))
        user = cur.fetchone()
        cur.close()

        if user:
            session['state'] = True
            session['candidate_id'] = email
            return redirect(url_for('dashboard_candidate'))
        else :
            flash('Invalid username or password', 'danger')

    return redirect(url_for('user'))




# End of Login and Registrations functions

# Dashboard Functionality of Admin
@app.route('/Dashboard-admin')
def dashboard_admin():
    return render_template('Dashboard_Admin.html')


@app.route('/Admin-home')
def admin_home():
    return render_template('Admin_Home.html')





@app.route('/User-Details')
def user_details():
    cur = mysql.connection.cursor()
    cur.execute("SELECT sno,f_name,l_name,u_mobile,u_email FROM user ")
    user = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return render_template('User_Details.html',users = user)

@app.route('/User-Delete/<string:user_email>', methods = ['POST','GET'])
def delete_user(user_email):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM user WHERE u_email = %s", (user_email,))
    cur.execute("DELETE FROM education WHERE email = %s", (user_email,))
    cur.execute("DELETE FROM experience_details WHERE email = %s", (user_email,))
    cur.execute("DELETE FROM personal_details WHERE email = %s", (user_email,))
    mysql.connection.commit()
    cur.close()
    flash("User Deleted Successfully","info")
    return redirect(url_for('user_details'))



@app.route('/Aptitude')
def aptitude():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM aptitude")
    Question = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return render_template('Aptitude.html',questions = Question)

@app.route('/Add-Aptitude', methods = ['POST','GET'])
def add_aptitude():
    if request.method == 'POST' :
        questionDetails = request.form
        ques = questionDetails['question']
        a = questionDetails['a']
        b = questionDetails['b']
        c = questionDetails['c']
        d = questionDetails['d']
        ans = questionDetails['ans']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO aptitude(ques,a,b,c,d,ans) VALUES (%s, %s, %s, %s, %s, %s)",(ques,a,b,c,d,ans))
        mysql.connection.commit()
        cur.close()

    return redirect(url_for('aptitude'))



@app.route('/Technical')
def technical():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM technical")
    Question = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    return render_template('Technical.html',questions = Question)

@app.route('/Add-Technical', methods = ['POST','GET'])
def add_technical():
    if request.method == 'POST' :
        questionDetails = request.form
        ques = questionDetails['question']
        a = questionDetails['a']
        b = questionDetails['b']
        c = questionDetails['c']
        d = questionDetails['d']
        ans = questionDetails['ans']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO technical(ques,a,b,c,d,ans) VALUES (%s, %s, %s, %s, %s, %s)",(ques,a,b,c,d,ans))
        mysql.connection.commit()
        cur.close()

    return redirect(url_for('technical'))







# End of Admin Dashboard



# Dashboard Functionality of Recruiter

@app.route('/Dashboard-Recruiter')
def dashboard_recruiter():
    session_state = session.get('state')
    if session_state == True :
        recruiter_id = session.get('recruiter_id')
        print(recruiter_id)
        cur = mysql.connection.cursor()
        cur.execute(" SELECT r_name FROM recruiter WHERE r_email = %s ",(recruiter_id,))
        name = cur.fetchone()
        recruiter_name = name[0]
        cur.close()

        return render_template('Dashboard_Recruiter.html',r_name = recruiter_name)
    
    return redirect(url_for('recruiter'))


@app.route('/recruiter-home')
def recruiter_home():
    return render_template('Recruiter_Home.html')

# End Of Recruiter dashboard


# Candidate dashboard

@app.route('/Dashboard-Candidate')
def dashboard_candidate():
    session_state = session.get('state')
    if session_state == True :
        candidate_id = session.get('candidate_id')
        cur = mysql.connection.cursor()
        cur.execute(" SELECT f_name,l_name FROM user WHERE u_email = %s ",(candidate_id,))
        name = cur.fetchone()
        first_name = name[0]
        last_name = name[1]
        candidate_name = first_name +" "+ last_name
        cur.close()

        return render_template('Dashboard_Candidate.html', c_name = candidate_name)
    
    return redirect(url_for('user'))


@app.route('/candidate-home')
def candidate_home():
    return render_template('Candidate_Home.html')

# End of Candidate dashboard

# Recruiter Funcionality

@app.route('/Jobposts', methods=['POST','GET'])
def job_post():
    r_id = session.get('recruiter_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT c_name FROM recruiter WHERE r_email = %s ",(r_id,))
    name = cur.fetchone()
    company_name = name[0]
    cur.close()


    if request.method == 'POST' :
        jobDetails = request.form
        job_role = jobDetails['role']
        job_skill = jobDetails['skills']
        job_exp = jobDetails['experience']
        job_salary = jobDetails['salary']
        school_rank = jobDetails['school_mark']
        college_rank = jobDetails['degree']

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO job_post(role,skills,experience,salary,school,college,c_name,r_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",(job_role,job_skill,job_exp,job_salary,school_rank,college_rank,company_name,r_id))
        mysql.connection.commit()
        cur.close()
        job_post_fetch()
    return redirect(url_for('job_post_fetch'))


@app.route('/Jobposts_Fetch')
def job_post_fetch():
    r_id = session.get('recruiter_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM job_post WHERE r_id = %s",(r_id,))
    job = cur.fetchall()
    return render_template('JobPost.html',jobs=job)

@app.route('/Job_Delete/<int:id>', methods=['POST'])
def job_delete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM job_post WHERE job_id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('job_post'))

@app.route('/Applied-Candidates')
def applied_candidates():
    recruiter_id = session.get('recruiter_id')
    cur = mysql.connection.cursor()
    if cur.execute("SELECT * FROM resume_path WHERE r_id = %s ",(recruiter_id,)) :
        applicant = cur.fetchall()
        mysql.connection.commit()
        cur.close()
       

        return render_template("Applied_Candidates.html",applicants = applicant, recruiter_email = recruiter_id )
    
    return redirect(url_for('applied_candidates'))

#End of recruiter Functionality

# Candidate Functionality

# Storing Personal Details

@app.route('/Personal-Details')
def personal_details():
    candidate_id = session.get('candidate_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT email from personal_details WHERE email = %s",(candidate_id,))
    if  not cur.fetchone():
        cur.execute(" SELECT f_name,l_name,u_mobile,u_email FROM user WHERE u_email = %s ",(candidate_id,))
        name = cur.fetchone()
        first_name = name[0]
        last_name = name[1]
        mobile = name[2]
        email = name[3]
        cur.close()
        return render_template("Personal_Details.html", 
            f_name = first_name,l_name = last_name, 
            mobile = mobile, email = email,)

    else :
        cur1 = mysql.connection.cursor()
        cur1.execute(" SELECT f_name,l_name,u_mobile,u_email FROM user WHERE u_email = %s ",(candidate_id,))
        user_details = cur1.fetchone()
        first_name = user_details[0]
        last_name = user_details[1]
        mobile = user_details[2]
        email = user_details[3]
        cur1.close()
        cur2 = mysql.connection.cursor()
        cur2.execute(" SELECT dob,gender,state,city,dist,street,pin_code FROM personal_details WHERE email = %s",(candidate_id,))
        user_details_2 = cur2.fetchone()
        print(user_details_2)
        dob = user_details_2[0]
        gender = user_details_2[1]
        state = user_details_2[2]
        city = user_details_2[3]
        dist = user_details_2[4]
        street = user_details_2[5]
        pin_code = user_details_2[6]
        cur2.close()

        
        return render_template("Show_Personal_Details.html",
                f_name = first_name, l_name = last_name, 
                mobile = mobile, email = email, dob = dob, 
                gender = gender, state = state, city = city, 
                dist = dist, street = street, pin_code = pin_code)

       


@app.route('/Personal-Details-Store', methods = ['POST','GET'])
def personal_details_store():
     
    candidate_id = session.get('candidate_id')

    if request.method == 'POST':
        fullDetails = request.form
        dob = fullDetails['d_o_b']
        gender = fullDetails['gender']
        state = fullDetails['state']
        city = fullDetails['city']
        dist = fullDetails['dist']
        street = fullDetails['street']
        pin_code = fullDetails['pin_code']
        cur = mysql.connection.cursor()
        if cur.execute("INSERT INTO personal_details(email, dob, gender, state, city, dist, street, pin_code) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)", (candidate_id, dob, gender, state, city, dist, street, pin_code)) :
            mysql.connection.commit()
            cur.close()
            flash("Personal Details Registered Successfully","success")
        
    return redirect(url_for('personal_details')) 




@app.route('/Personal-Details-Update', methods=['POST','GET'])
def personal_details_update():
    candidate_id = session.get('candidate_id')
    cur1 = mysql.connection.cursor()
    cur1.execute(" SELECT f_name,l_name,u_mobile,u_email FROM user WHERE u_email = %s ",(candidate_id,))
    user_details = cur1.fetchone()
    first_name = user_details[0]
    last_name = user_details[1]
    mobile = user_details[2]
    email = user_details[3]
    cur1.close()

    cur2 = mysql.connection.cursor()
    cur2.execute(" SELECT dob,gender,state,city,dist,street,pin_code FROM personal_details WHERE email = %s",(candidate_id,))
    user_details_2 = cur2.fetchone()
    dob = user_details_2[0]
    gender = user_details_2[1]
    state = user_details_2[2]
    city = user_details_2[3]
    dist = user_details_2[4]
    street = user_details_2[5]
    pin_code = user_details_2[6]
    cur2.close()

        
    return render_template("Update_Personal_Details.html",
                f_name = first_name, l_name = last_name, 
                mobile = mobile, email = email, dob = dob, 
                gender = gender, state = state, city = city, 
                dist = dist, street = street, pin_code = pin_code)



@app.route('/Personal-Details-Update-Complete', methods=['POST','GET'])
def full_details_update_complete():
    candidate_id = session.get('candidate_id')
    if request.method == 'POST':
        fullDetails = request.form
        f_name = fullDetails['f_name']
        l_name = fullDetails['l_name']
        mobile = fullDetails['mobile']
        dob = fullDetails['d_o_b']
        gender = fullDetails['gender']
        state = fullDetails['state']
        city = fullDetails['city']
        dist = fullDetails['dist']
        street = fullDetails['street']
        pin_code = fullDetails['pin_code']
        cur = mysql.connection.cursor()
        cur2 = mysql.connection.cursor()
        query1 = cur.execute("UPDATE personal_details SET dob=%s, gender=%s, state=%s, city=%s, dist=%s, street=%s, pin_code=%s WHERE email = %s",
            (dob, gender, state, city, dist, street, pin_code,candidate_id))
        mysql.connection.commit()
        cur.close()
        query2 = cur2.execute("UPDATE user SET f_name = %s, l_name = %s, u_mobile = %s WHERE u_email = %s",(f_name,l_name,mobile,candidate_id))
        mysql.connection.commit()
        cur2.close()
        if query1<=1 and query2<=1 :
            flash("Updated Successfully","success")

        else:
            flash("Not Updated","danger")

    return redirect(url_for('personal_details'))

# end of Personal Details


@app.route('/Education-Details')
def education_details():
    candidate_id = session.get('candidate_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM education WHERE email = %s ",(candidate_id,))
    if cur.fetchone() :
        cur.close()
        cur2 = mysql.connection.cursor()
        cur2.execute("""SELECT hsc,hsc_school,hsc_year,
                     sslc,sslc_school,sslc_year,stream,
                     college_name,percentage,year FROM education WHERE email = %s""",(candidate_id,))
        education = cur2.fetchone()
        hsc = education[0]
        hsc_school = education[1]
        hsc_year = education[2]
        sslc = education[3]
        sslc_school = education[4]
        sslc_year = education[5]
        stream = education[6]
        college_name = education[7]
        percentage = education[8]
        year = education[9]
        cur.close()
        return render_template("Show_Education_Details.html",hsc = hsc,
                               hsc_school = hsc_school, hsc_year = hsc_year,
                               sslc = sslc, sslc_school = sslc_school, sslc_year = sslc_year,
                               stream = stream, college_name = college_name, percentage = percentage,
                               year = year)
    else :
        return render_template("Education_Details.html")


@app.route('/Education-Details-Store', methods = ['POST','GET'])
def education_details_store():
    candidate_id = session.get('candidate_id')
    
    if request.method == 'POST' :
        degree = "B.E / B.TECH"
        educationDetails = request.form
        hsc = educationDetails['hsc'] 
        hsc_name = educationDetails['hsc_name'] 
        hsc_year = educationDetails['hsc_year'] 
        sslc = educationDetails['sslc'] 
        sslc_name = educationDetails['sslc_name'] 
        sslc_year = educationDetails['sslc_year']  
        stream = educationDetails['stream'] 
        college_name = educationDetails['college_name'] 
        percentage = educationDetails['percentage'] 
        y_o_p = educationDetails['y_o_p']

        cur = mysql.connection.cursor()
        if cur.execute ("""INSERT INTO education
         (email,hsc,hsc_school,hsc_year,
         sslc,sslc_school,sslc_year,
         degree,stream,college_name,percentage,year) 
         VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
         (candidate_id,hsc,hsc_name,hsc_year,sslc,sslc_name,sslc_year,
          degree,stream,college_name,percentage,y_o_p)) :
            mysql.connection.commit()
            cur.close()
            flash("Education Details Updated ","success")

        else :
            flash("Failed","danger")

    return redirect(url_for('education_details'))


@app.route('/Education-Details-Update', methods = ['POST','GET'])
def education_details_update():
    candidate_id = session.get('candidate_id')
    cur2 = mysql.connection.cursor()
    cur2.execute("""SELECT hsc,hsc_school,hsc_year,
                     sslc,sslc_school,sslc_year,stream,
                     college_name,percentage,year FROM education WHERE email = %s""",(candidate_id,))
    education = cur2.fetchone()
    hsc = education[0]
    hsc_school = education[1]
    hsc_year = education[2]
    sslc = education[3]
    sslc_school = education[4]
    sslc_year = education[5]
    stream = education[6]
    college_name = education[7]
    percentage = education[8]
    year = education[9]
        
    return render_template("Update_Education_Details.html",hsc = hsc,
                               hsc_school = hsc_school, hsc_year = hsc_year,
                               sslc = sslc, sslc_school = sslc_school, sslc_year = sslc_year,
                               stream = stream, college_name = college_name, percentage = percentage,
                               year = year)


@app.route('/Education-Details-Update-Complete', methods = ['POST','GET'])
def personal_details_update_complete():
    candidate_id = session.get('candidate_id')
    cur = mysql.connection.cursor()
    if request.method == 'POST' :
        degree = "B.E / B.TECH"
        educationDetails = request.form
        hsc = educationDetails['hsc'] 
        hsc_name = educationDetails['hsc_name'] 
        hsc_year = educationDetails['hsc_year'] 
        sslc = educationDetails['sslc'] 
        sslc_name = educationDetails['sslc_name'] 
        sslc_year = educationDetails['sslc_year']  
        stream = educationDetails['stream'] 
        college_name = educationDetails['college_name'] 
        percentage = educationDetails['percentage'] 
        y_o_p = educationDetails['y_o_p']

        query = cur.execute("""UPDATE education SET hsc = %s, hsc_school = %s, hsc_year = %s,
                    sslc = %s, sslc_school = %s, sslc_year = %s, stream = %s, college_name = %s,
                    percentage = %s,year = %s WHERE email = %s""",(hsc, hsc_name, hsc_year, sslc, sslc_name, sslc_year,
                    stream, college_name, percentage, y_o_p, candidate_id,))
        mysql.connection.commit()
        cur.close()
        if query == 1 :
            flash("Education Details Update Successfully","success")

        else:
            flash("Update Failed","danger")
    return redirect(url_for('education_details'))


@app.route('/Experience-Details', methods = ['POST','GET'])
def experience_details():
    candidate_id = session.get('candidate_id')

    cur = mysql.connection.cursor()
    cur.execute("SELECT email FROM experience_details WHERE email = %s",(candidate_id,))

    if cur.fetchone() :
        mysql.connection.commit()
        cur.close()
        cur2 = mysql.connection.cursor()
        cur2.execute("SELECT experience,designation,company,location,year,month FROM experience_details WHERE email = %s",(candidate_id,))
        experienceDetails = cur2.fetchone()
        experience = experienceDetails[0]
        designation = experienceDetails[1]
        company = experienceDetails[2]
        location = experienceDetails[3]
        year = experienceDetails[4]
        month = experienceDetails[5]
        mysql.connection.commit()
        cur2.close()

        return render_template("Show_Experience_Details.html",
                               experience = experience, designation = designation,
                               company = company ,location = location, year = year, month = month )
    else :
        return render_template("Experience_Details.html")
    


@app.route('/Experience-Details-Store', methods = ['POST','GET'])
def experience_details_store():

    candidate_id = session.get('candidate_id')
    if request.method == 'POST':

        experienceDetails = request.form
        experience = experienceDetails['experience']
        designation = experienceDetails['designation']
        company = experienceDetails['company']
        location = experienceDetails['location']
        year = experienceDetails['year']
        month = experienceDetails['month']

        cur = mysql.connection.cursor()
        if cur.execute("""INSERT INTO experience_details(email,experience,designation,
                    company,location,year,month) VALUES (%s, %s, %s, %s, %s, %s, %s)""",(candidate_id,
                    experience,designation,company,location,year,month)) :
            mysql.connection.commit()
            cur.close()
            flash("Experience Details Stored","success")

    return redirect(url_for('experience_details'))

@app.route('/Experience-Details-Update', methods = ['POST','GET'])
def experience_details_update():
    candidate_id = session.get('candidate_id')
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT experience,designation,company,location,year,month FROM experience_details WHERE email = %s",(candidate_id,))
    experienceDetails = cur2.fetchone()
    experience = experienceDetails[0]
    designation = experienceDetails[1]
    company = experienceDetails[2]
    location = experienceDetails[3]
    year = experienceDetails[4]
    month = experienceDetails[5]
    mysql.connection.commit()
    cur2.close()

    return render_template("Update_Experience_Details.html",
                               experience = experience, designation = designation,company = company,
                               location = location, year = year, month = month )

@app.route('/Experience-Details-Update-Complete', methods = ['POST','GET'])
def experience_details_update_complete():
    candidate_id = session.get('candidate_id')
    if request.method == 'POST':

        experienceDetails = request.form
        experience = experienceDetails['experience']
        designation = experienceDetails['designation']
        company = experienceDetails['company']
        location = experienceDetails['location']
        year = experienceDetails['year']
        month = experienceDetails['month']

        cur = mysql.connection.cursor()
        query = cur.execute("""UPDATE experience_details SET experience = %s, designation = %s,company = %s, location = %s,
                    year = %s, month = %s WHERE email = %s""",(experience, designation,company, location, year, month, candidate_id,))
        
        mysql.connection.commit()
        cur.close()
        if query == 1 :
            flash("Experience Details Updated Successfully","success")

        else:
            flash("Update Failed","danger")
    return redirect(url_for('experience_details'))


@app.route('/Job-Show',methods = ['POST','GET'])
def job_show():
    candidate_id = session.get('candidate_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM job_post")
    job = cur.fetchall()
    mysql.connection.commit()
    cur.close()
    cur2 = mysql.connection.cursor()
    cur2.execute("SELECT * FROM user WHERE u_email = %s",(candidate_id,))
    detail = cur2.fetchone()
    mysql.connection.cursor()
    cur2.close()
    print(detail)

    return render_template('Job_Show.html',jobs=job, details=detail)




@app.route('/Upload-Resume', methods=['POST','GET'])
def upload_photo():
    # Folder to store uploaded files
    venv_dir = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(venv_dir, 'User_Resume')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    if request.method == 'POST' :
        file = request.files['resume']
        resumeDetails = request.form
        role = resumeDetails['role']
        recruiter_id = resumeDetails['recruiter_id']
        skills = resumeDetails['skills']
        if file:
        # Save the file to the Photos folder
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            candidate_id = session.get('candidate_id')
            cur = mysql.connection.cursor()
            cur.execute("SELECT f_name,l_name,u_mobile FROM user WHERE u_email = %s",(candidate_id,))
            user = cur.fetchone()
            f_name = user[0].upper()
            l_name = user[1].upper()
            u_mobile = user[2]
            full_name = f_name + " "+ l_name
            mysql.connection.commit()
            cur.close()
            score = Resume_Ranker(skills,file_path,full_name)
            cur2 = mysql.connection.cursor()
            if cur2.execute("INSERT INTO resume_path(email,file_name,role,r_id,score,name,mobile) VALUES(%s, %s, %s, %s, %s, %s, %s)",(candidate_id,file_path,role,recruiter_id,score,full_name,u_mobile)):
                mysql.connection.commit()
                cur2.close()
                flash("Resume Uploaded Sucessfully","success")
            else :
                flash("Upload Failed","danger")
        
    return redirect(url_for('job_show'))    

# End of candidate Functionality


@app.route('/Quiz')
def quiz():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM aptitude")
    Question = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM aptitude")
    Count = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    print(Count) 

    return render_template('Quiz.html',questions = Question,count = Count)


@app.route('/show_resume')
def show_resume():
    resume_path = request.args.get('path')
    print(resume_path)
    return send_file(resume_path, mimetype='application/pdf')

# Email Sending

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from send_mail import send_Email

@app.route('/Send-Email',methods = ['POST','GET'])
def send_email():
    email_send_status = ''
    if request.method == 'POST' :
        emails = request.form.getlist('email')
        recruiter_email = request.form['recruiter_email']
        print(emails)
        for email in emails :
            email_list = email.split(',')
            candidate_email = email_list[1]
            candidate_name = email_list[0]
            candidate_role = email_list[2]
            test_link_status = "Yes"
            email_send_status = send_Email(candidate_email,candidate_role,candidate_name)
            cur = mysql.connection.cursor()
            cur.execute("UPDATE resume_path SET link_shared = %s WHERE email = %s",(test_link_status,candidate_email,))
            cur.execute("INSERT INTO test_user (c_email) VALUES (%s)",(candidate_email,))
            mysql.connection.commit()
            cur.close()
            print(email_send_status)
    if email_send_status == 'sent' :
        flash("Email Sent Successfully","success")        
    return redirect(url_for('applied_candidates'))

@app.route('/Test_App')
def test_app():
    test_session = session.get('test_state')
    print(test_session)
    if test_session == True :
        return render_template('Test_App.html')
    
    return redirect(url_for('test_login'))


@app.route('/Capture_Image')
def capture_image():
    return render_template('Face_Capture.html')


@app.route('/Save_Image',methods=['POST','GET'])
def save_image():
    # venv_dir = os.path.dirname(os.path.abspath(__file__))
    # UPLOAD_PHOTO = os.path.join(venv_dir, 'User_Photo')
    # os.makedirs(UPLOAD_PHOTO, exist_ok=True)
    UPLOAD_PHOTO = 'D:\\Madhesh\\venv\\static\\images'
    app.config['UPLOAD_PHOTO'] = UPLOAD_PHOTO
    if request.method == 'POST' :
        file = request.files['userImage']
        if file:
        # Save the file to the Photos folder
            file_path = os.path.join(app.config['UPLOAD_PHOTO'], file.filename)
            img_path = file.save(file_path)
            print(file_path)

    return render_template('Test_App.html',image_path = img_path)
    


@app.route('/Test_Login')
def test_login():
    return render_template('Test_Login.html')


@app.route('/Test_Login_Check', methods=['POST','GET'])
def test_login_check():
    if request.method == 'POST':
        userDetails = request.form
        email = userDetails['email']
        password = userDetails['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT u_email, u_pass FROM user WHERE u_email = %s AND u_pass = %s", (email,password))
        user = cur.fetchone()
        cur.execute("SELECT c_email FROM test_user WHERE c_email = %s",(email,))
        test_uesr = cur.fetchone()
        mysql.connection.commit()
        cur.close()


        if user and test_uesr:
            session['test_state'] = True
            session['candidate_id'] = email
            return redirect(url_for('instructions'))
        else :
            flash('Invalid username or password', 'danger')

    return redirect(url_for('test_login'))





@app.route('/Instructions')
def instructions():
    test_session = session.get('test_state')
    if test_session == True :
        return render_template('Instructions.html')

    else:
        return redirect(url_for('test_login'))


@app.route('/Aptitude-Check',methods = ['POST','GET'])
def aptitude_check():
    if request.method == 'POST' :
        score = 0
        aptitudeAnswers = request.form
        ans1 = aptitudeAnswers['ans1']
        ans2 = aptitudeAnswers['ans2']
        ans3 = aptitudeAnswers['ans3']
        ans4 = aptitudeAnswers['ans4']
        ans5 = aptitudeAnswers['ans5']
        print(ans1,ans2,ans3,ans4,ans5)

        cur = mysql.connection.cursor()
        cur.execute("SELECT ans FROM aptitude ")
        answers = cur.fetchall()
        if ans1 == answers[0][0]:
            score+=1

        if ans2 == answers[1][0]:
            score+=1
        
        if ans3 == answers[2][0]:
            score+=1
       
        if ans4 == answers[3][0]:
            score+=1
       
        if ans5 == answers[4][0]:
            score+=1

        user_id = session.get('candidate_id')
        cur = mysql.connection.cursor()
        cur.execute("SELECT name,mobile,r_id FROM resume_path WHERE email = %s",(user_id,))
        userDetails = cur.fetchone()
        user_name = userDetails[0]
        user_mobile = userDetails[1]
        r_id = userDetails[2]
        if cur.execute("INSERT INTO assesment (user_id,r_id,name,mobile) VALUES (%s,%s,%s,%s)",(user_id,r_id,user_name,user_mobile)) :
            cur.execute("UPDATE assesment SET aptitude = %s WHERE user_id = %s",(score,user_id))
        mysql.connection.commit()
        cur.close()
        
       
        
    # return "<h1>Aptitude Complted </h1>"
    return redirect(url_for('test_app'))




@app.route('/Technical_Test')
def technical_test():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM technical")
    Question = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM technical")
    Count = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return render_template('Technical_Test.html',questions = Question,count = Count)


@app.route('/Technical-check',methods = ['POST','GET'])
def technical_check():
     if request.method == 'POST' :
        score = 0
        technicalAnswers = request.form
        ans1 = technicalAnswers['ans1']
        ans2 = technicalAnswers['ans2']
        ans3 = technicalAnswers['ans3']
        print(ans1,ans2,ans3)

        cur = mysql.connection.cursor()
        cur.execute("SELECT ans FROM aptitude ")
        answers = cur.fetchall()
        if ans1 == answers[0][0]:
            score+=1

        if ans2 == answers[1][0]:
            score+=1
        
        if ans3 == answers[2][0]:
            score+=1
       
       
    
    

@app.route('/Chatbot')
def chatbot():
    return render_template('chat.html')


original_score = 0

@app.route('/Chat-msg',methods = ['POST','GET'])
def chat_response():
    global original_score
    user_id = "peter@gmail.com"
    if request.method == 'POST':
        msg = request.form
        message = msg['msg']
        counter = msg['counter']
        if counter == '6' :
            sentiment = Analyze_User_Message(message)
            score = sentiment['communication_skills']
            end_response = "Well Done !! you can now finish the assessment"
            original_score += score
            corrected_score = int((original_score/400)*100)
            cur = mysql.connection.cursor()
            cur.execute("UPDATE assesment SET interview = %s WHERE user_id = %s",(corrected_score,user_id))
            mysql.connection.commit()
            cur.close()
            print(corrected_score)
            return end_response
        else :
            score,res = Analyze_Msg(message,counter)
            original_score += score 
        return res


import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from Sentiment import Analyze_User_Message

def Analyze_Msg(msg,counter):
    if counter == '1' :
        responses = "Are you ready for the interview"
        score = 0
        return score,responses
    elif counter == '2':
        score = 0
        responses = "Tell me about yourself ?"
        return score,responses
    elif counter == '3':
        self_intro_score = self_intro(msg)
        self_intro_score = self_intro_score
        responses = "Explain about your any one project in 3-4 lines"
        return self_intro_score,responses
    elif counter == '4':
        sentiment = Analyze_User_Message(msg)
        score = sentiment['communication_skills']
        responses = "What are your short term and long term goals "
        return score,responses
    else:
        sentiment = Analyze_User_Message(msg)
        score = sentiment['communication_skills']
        responses = "What motivates you to perform at your best?"
        return score,responses
    
    
def self_intro(msg):
    score = 0
    #user_id = session.get('candidate_id')
    user_id = 'peter@gmail.com'
    cur = mysql.connection.cursor()
    cur.execute("SELECT f_name FROM user WHERE u_email = %s",(user_id,))
    userDetails = cur.fetchone()
    f_name = userDetails[0].lower()
    # f_name = f_name.lower()
    cur.execute("SELECT city FROM personal_details WHERE email = %s",(user_id,))
    Details = cur.fetchone()
    city = Details[0]
    city = city.lower()
    cur.execute("SELECT hsc_school,college_name,stream FROM education WHERE email = %s",(user_id,))
    Edu_Details = cur.fetchone()
    hsc_school = Edu_Details[0].lower()
    college_name = Edu_Details[1].lower()
    stream = Edu_Details[2].lower()
    mysql.connection.commit()
    cur.close()
    msg = msg.lower()
    score += 10 if f_name in msg  else 0
    score += 10 if city in msg  else 0
    score += 10 if hsc_school in msg  else 0
    score += 10 if college_name in msg  else 0
    score += 10 if stream in msg  else 0

    return score





























if __name__ == '__main__':
    app.run(debug=True)
