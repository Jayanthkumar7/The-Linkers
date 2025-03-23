from flask import Flask, render_template, url_for, request, redirect,jsonify,session,flash
from flask_login import login_user, LoginManager, UserMixin, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from sqlalchemy import and_


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/bloodconnect'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blood_donation.db'
app.config['SECRET_KEY'] = 'this is my secret key'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(UserMixin, db.Model):
    __tablename__ = 'user_details'
    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    ph_number = db.Column(db.String(15), nullable=False, unique=True)
    dob = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.Enum('Male','Female','others'), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    weight = db.Column(db.Integer)
    blood_type = db.Column(db.Enum('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', name='blood_types'), nullable=False)
    last_donation_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def get_id(self):
        return str(self.user_id)

class Bloodbank(UserMixin, db.Model):  
    __tablename__ = 'bloodbanks'
    bloodbank_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    registration_number = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.Enum('bloodbank', 'hospital', name='type_of_org'), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    email = db.Column(db.String(100), nullable=False)
    ph_number = db.Column(db.String(10), nullable=False)

    def get_id(self):
        return str(self.bloodbank_id)


class Bloodrequest(db.Model):
    __tablename__ = 'request_table'
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    requester_id = db.Column(db.Integer, db.ForeignKey('user_details.user_id'), nullable=False)
    requester_name = db.Column(db.String(100), nullable=False)
    rel_patient = db.Column(db.Enum('self', 'Family', 'other', name='patient_relation'))
    patient_name = db.Column(db.String(50), nullable=False)
    patient_age = db.Column(db.Integer, nullable=False)
    blood_type = db.Column(db.Enum('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', name='blood_types'), nullable=False)
    reason = db.Column(db.String(1000), nullable=True)
    urgency = db.Column(db.Enum('Emergency', 'Not Urgent', name='priority'))
    status = db.Column(db.Enum('pending', 'cancelled', 'success', name='blood_status'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    hospital_name = db.Column(db.String(200), nullable=False)


    request_blood = db.relationship('User', backref=db.backref('requests', lazy=True))
    
class BloodBankRequests(db.Model):
    __tablename__ = 'bloodbank_requests'
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    blood_bank_id = db.Column(db.Integer, db.ForeignKey('bloodbanks.bloodbank_id'), nullable=False)
    requested_blood_type = db.Column(db.Enum('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', name='blood_types'), nullable=False)
    urgency = db.Column(db.Enum('Emergency', 'Not Urgent', name='priority'))
    status = db.Column(db.Enum('pending', 'fulfilled', 'cancelled', name='request_status'), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relationship to Bloodbank
    bloodbank = db.relationship('Bloodbank', backref=db.backref('requests', lazy=True))



class DonationRequests(db.Model):
    __tablename__ = 'donation_requests'
    response_id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    request_id = db.Column(db.Integer, db.ForeignKey('request_table.request_id'), nullable=False)
    donor_id = db.Column(db.Integer, db.ForeignKey('user_details.user_id'), nullable=True)  
    blood_bank_id = db.Column(db.Integer, db.ForeignKey('bloodbanks.bloodbank_id'), nullable=True)  
    status = db.Column(db.Enum('pending', 'rejected', 'accepted', name='status_requests'), default='pending')


    request = db.relationship('Bloodrequest', backref=db.backref('donation_requests', lazy=True))
    
    donor = db.relationship('User', backref=db.backref('donation_requests', lazy=True), foreign_keys=[donor_id])
    bloodbank = db.relationship('Bloodbank', backref=db.backref('donation_requests', lazy=True), foreign_keys=[blood_bank_id])



class Donations(db.Model):
    __tablename__ = 'donations'
    donation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('user_details.user_id'), nullable=True)
    blood_bank_id = db.Column(db.Integer, db.ForeignKey('bloodbanks.bloodbank_id'), nullable=True)
    donation_date = db.Column(db.DateTime, default=datetime.now, nullable=True)
    blood_type = db.Column(db.Enum('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', name='blood_types'), nullable=False)
    status = db.Column(db.Enum('pending', 'completed', 'rejected', name='donation_status'), default='pending', nullable=False)
    
    donor = db.relationship("User", backref=db.backref("donations", lazy=True), foreign_keys=[donor_id])
    bloodbank = db.relationship("Bloodbank", backref=db.backref("donations", lazy=True), foreign_keys=[blood_bank_id])
    



login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    user_type = session.get("user_type")
    
    if user_type == "user":
        return User.query.get(int(user_id))
    elif user_type == "bloodbank":
        return Bloodbank.query.get(int(user_id))
    return None 


BLOOD_COMPATIBILITY = {
    "O+": ["O+", "A+", "B+", "AB+"],
    "O-": ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"],
    "A+": ["A+", "AB+"],
    "A-": ["A+", "A-", "AB+", "AB-"],
    "B+": ["B+", "AB+"],
    "B-": ["B+", "B-", "AB+", "AB-"],
    "AB+": ["AB+"],
    "AB-": ["AB+", "AB-"]
}

@app.route('/', methods=['GET', 'POST'])
def home():
    type_of_user = session.get('user_type')

    my_self_requests = None
    if current_user.is_authenticated:
        if type_of_user == 'user':
            my_self_requests = Bloodrequest.query.filter(
                and_(
                    Bloodrequest.request_id == current_user.user_id,
                    Bloodrequest.rel_patient == 'self'
                )
            ).first()

    return render_template('landingpage.html', current_user=current_user, type_of_user=type_of_user, my_self_requests=my_self_requests)

@app.route('/login_org')
def login_org():
    return render_template("organisationlogin.html",current_user= current_user)

@app.route('/check_org_details', methods=['POST'])
def check_org_details():
    try:
        data = request.json
        email_or_reg = data.get("email_or_reg")
        password = data.get("password")

        if not (email_or_reg and password):
            return jsonify({'status': 'error', 'message': 'All fields are required!'}), 400

        existing_org = Bloodbank.query.filter(
            (Bloodbank.email == email_or_reg) | (Bloodbank.registration_number == email_or_reg)
        ).first()
        
        if not existing_org:
            return jsonify({'status': 'error', 'message': 'Organization not registered!'}), 404

        if bcrypt.check_password_hash(existing_org.password, password):
            login_user(existing_org)
            session["user_type"] = "bloodbank"
            return jsonify({'status': 'success', 'message': 'Organization logged in successfully!', 'url': '/organisation_dashboard'})
        else:
            return jsonify({'status': 'error', 'message': 'Invalid password!'}), 401

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'status': 'error', 'message': 'Login failed!'}), 500
    
    

@app.route('/register_org')
def register_org():
    return render_template("registerasorganisation.html",current_user=current_user)

@app.route('/add_org_details', methods=['POST'])
def add_org_details():
    try:
        data = request.json  
        
        name = data.get("institution_name")
        registration_number = data.get("registration_number")
        email = data.get("email")
        phone = data.get("phone")
        location = data.get("location")
        address = data.get("address")
        city = data.get("city")
        pincode = data.get("pincode")
        org_type = data.get("org_type")  # hospital, blood bank, NGO
        password = data.get("password")
        
        
        if not all([name, registration_number, email, phone, location, address, city, pincode, org_type, password]):
            return jsonify({'status': 'error', 'message': 'All fields are required!'}), 400
        
        
        existing_org = Bloodbank.query.filter(
            (Bloodbank.registration_number == registration_number) | (Bloodbank.email == email)
        ).first()
        if existing_org:
            return jsonify({'status': 'error', 'message': 'Organization already registered with this email or registration number!'}), 409
        
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        
        new_org = Bloodbank(
            name=name,
            registration_number=registration_number,
            type=org_type,
            address=address,
            city=city,
            pincode=pincode,
            email=email,
            ph_number=phone,
            password = hashed_password
        )
        
        db.session.add(new_org)
        db.session.commit()
        login_user(new_org)
        session["user_type"] = "bloodbank"
        return jsonify({'status': 'success', 'message': 'Organization registered successfully!', 'url': '/organisation_dashboard'})

    except Exception as e:
        print("Error:", str(e))
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Registration failed!'}), 500


@app.route('/organisation_dashboard')
@login_required
def organisation_dashboard():
    # Fetch accepted requests with donor details
    accepted_requests = db.session.query(
        DonationRequests, User.full_name
    ).join(User, DonationRequests.donor_id == User.user_id).filter(
        DonationRequests.blood_bank_id == current_user.bloodbank_id,
        DonationRequests.status == 'accepted'
    ).all()

    # Create notifications with sample messages
    notifications = [
        {
            "name": donor_name,
            "status": request.status,
            "message": f"{donor_name}, please come at 9:00 AM."
        }
        for request, donor_name in accepted_requests
    ]

    return render_template(
        'organisationdashboard.html',
        current_user=current_user,
        notifications=notifications
    )


@app.route('/receiver_dashboard')
@login_required
def receiver_dashboard():

    
    # Fetch individual blood requests
    user_blood_requests = Bloodrequest.query.filter_by().all()

    # Fetch blood bank requests
    user_blood_bank_requests = BloodBankRequests.query.filter_by().all()

    # Combine both into a single list

    return render_template('receiverdashboard.html', 
                           current_user=current_user,
                           user_blood_bank_requests = user_blood_bank_requests,user_blood_requests=user_blood_requests)
    
@app.route('/connect_request', methods=['POST'])
@login_required
def connect_request():
    data = request.get_json()
    request_id = data.get('request_id')
    blood_bank_id = data.get('blood_bank_id')

    st = 'pending'
    
    if blood_bank_id:
        st = 'accepted'
    
    if not request_id:
        return jsonify({'success': False, 'message': 'Invalid request data'}), 400

    new_donation_request = DonationRequests(
        request_id=request_id,
        donor_id=current_user.user_id,
        blood_bank_id=blood_bank_id if blood_bank_id else None,
        status=st
    )

    db.session.add(new_donation_request)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Request stored successfully'}),200


@app.route('/add_org_request', methods=['POST'])
@login_required
def add_org_request():
    try:
        data = request.get_json()
        blood_type = data.get("blood_type")
        is_emergency = data.get("emergency", False)
        if is_emergency:
            x = 'Emergency'
        else:
            x = 'Not Urgent'

        if not blood_type:
            return jsonify({"success": False, "error": "Blood type is required!"}), 400

        # Create a new blood request entry
        new_request = BloodBankRequests(
            blood_bank_id=current_user.bloodbank_id,  # Assuming org ID is stored in current_user
            requested_blood_type=blood_type,
            urgency=x,
            status = 'pending' 
        )

        # Add to DB
        db.session.add(new_request)
        db.session.commit()

        return jsonify({"success": True, "message": "Blood request submitted successfully!"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500



@app.route('/find_donor',methods=['GET','POST'])
@login_required
def find_donor():
    return render_template('requestblood.html',current_user = current_user)

@app.route('/login')
def login():
    return render_template('userlogin.html', current_user=current_user)

@app.route('/signup_user')
def signup_user():
    return render_template('usersignup.html',current_user = current_user)

@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        data = request.json

        full_name = data.get("fullName")
        email = data.get("email")
        phone = data.get("phone")
        dob = data.get("dob")
        gender = data.get("gender")
        blood_group = data.get("bloodGroup")
        address = data.get("address")
        city = data.get("city")
        state = data.get("state")
        pin = data.get("pin")
        password = data.get("password")

        # ✅ Ensure all required fields are provided
        if not all([full_name, email, phone, dob, gender, blood_group, address, city, state, pin, password]):
            return jsonify({'status': 'error', 'message': 'All fields are required!'}), 400

        # ✅ Fix: Use 'ph_number' instead of 'phone' in User model
        existing_user = User.query.filter((User.email == email) | (User.ph_number == phone)).first()
        if existing_user:
            return jsonify({'status': 'error', 'message': 'User already exists with this email or phone number!'}), 409

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        new_user = User(
            full_name=full_name,
            email=email,
            ph_number=phone,  # ✅ Fix: Use 'ph_number' here
            dob=dob,
            gender=gender,
            blood_type=blood_group,
            address=address,
            city=city,
            state=state,
            pincode=pin,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        session["user_type"] = "user"

        return jsonify({'status': 'success', 'message': 'User registered successfully!', 'url': '/'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Registration failed: {str(e)}'}), 500

    
@app.route('/login_user',methods=['POST','GET'])
def user_login():
    try:
        data = request.json
        print(data)
        email = data.get('email')
        password = data.get('password')
        
        if not (email and password):
            return jsonify({'status': 'error', 'message': 'All fields are required!'}), 400
        
        existing_user = User.query.filter((User.email == email) | (User.ph_number == email)).first()
        if not existing_user:
            return jsonify({'status': 'error', 'message': 'User is not registered'}), 409
        
        if existing_user :
            user_pass_check = bcrypt.check_password_hash(existing_user.password , password)
            if user_pass_check :
                login_user(existing_user)
                session["user_type"] = "user"
                return jsonify({'status':'success','message':'User successfully logged in !','url':'/'})
            
    except Exception as e:
        print("Error:", str(e))
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Registration failed!'}), 500

@app.route('/request_blood_details', methods=['POST', 'GET'])
@login_required
def request_blood_details():
    try:
        data = request.json
        
        new_request = Bloodrequest(
            requester_id=current_user.user_id or current_user.bloodbank_id,
            requester_name=data.get('requester_name'),
            rel_patient=data.get('rel_patient'),
            patient_name=data.get('patient_name'),
            patient_age=data.get('patient_age'),
            blood_type=data.get('blood_type'),
            reason=data.get('reason'),
            urgency='Emergency' if data.get('is_emergency') else 'Not Urgent',
            status='pending',
            created_at=datetime.now(),
            hospital_name=data.get('hospital_name'),
        )
        
        db.session.add(new_request)
        db.session.commit()

        # **Find Donors with the Same Blood Type**
        matching_donors = User.query.filter_by(blood_type=new_request.blood_type).all()
        
        for donor in matching_donors:
            donation_request = DonationRequests(
                request_id=new_request.request_id,
                donor_id=donor.user_id,
                status='pending'
            )
            db.session.add(donation_request)

        db.session.commit()

        return jsonify({"message": "Blood request submitted successfully and donors notified!", "request_id": new_request.request_id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


BLOOD_COMPATIBILITY = {
    "O-": ["O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+"],
    "O+": ["O+", "A+", "B+", "AB+"],
    "A-": ["A-", "A+", "AB-", "AB+"],
    "A+": ["A+", "AB+"],
    "B-": ["B-", "B+", "AB-", "AB+"],
    "B+": ["B+", "AB+"],
    "AB-": ["AB-", "AB+"],
    "AB+": ["AB+"]
}

@app.route('/donor_dashboard')
@login_required
def donor_dashboard():
    # Check blood donation eligibility
    eligible = "Yes"
    next_eligible_date = None
    if current_user.last_donation_date:
        min_gap = timedelta(days=90)  # 3-month gap
        next_eligible_date = current_user.last_donation_date + min_gap
        if datetime.now().date() < next_eligible_date:
            eligible = "No"

    # Get donor's blood type
    donor_blood_type = current_user.blood_type

    # Find compatible blood requests that haven't been accepted
    blood_requests = Bloodrequest.query.filter(
        Bloodrequest.status == 'pending',
        Bloodrequest.blood_type.in_(BLOOD_COMPATIBILITY.get(donor_blood_type, [])),
        ~Bloodrequest.request_id.in_(
            db.session.query(DonationRequests.request_id).filter(DonationRequests.status == "accepted")
        )
    ).all()

    # Find compatible blood bank requests that haven't been accepted
    blood_bank_requests = BloodBankRequests.query.filter(
        BloodBankRequests.status == 'pending',
        BloodBankRequests.requested_blood_type.in_(BLOOD_COMPATIBILITY.get(donor_blood_type, [])),
        ~BloodBankRequests.request_id.in_(
            db.session.query(DonationRequests.request_id).filter(DonationRequests.status == "accepted")
        )
    ).all()

    # Combine all compatible requests
    all_requests = blood_requests + blood_bank_requests

    # Fetch past donations
    past_donations = Donations.query.filter_by(donor_id=current_user.user_id, status='completed').all()

    # Mock upcoming donation drives (can be replaced with DB queries)
    upcoming_drives = [
        {"event_name": "Red Cross Blood Drive", "date": "2025-04-10", "location": "City Hall"},
        {"event_name": "Health Camp", "date": "2025-05-15", "location": "Community Center"}
    ]

    return render_template('donordashboard.html',
                           eligible=eligible,
                           next_eligible_date=next_eligible_date,
                           all_requests=all_requests,
                           past_donations=past_donations,
                           upcoming_drives=upcoming_drives)


@app.route('/accept_donation_request/<int:request_id>', methods=['POST', 'GET'])
@login_required
def accept_donation_request(request_id):
    """Accept a blood request and notify the requester"""
    blood_request = Bloodrequest.query.get(request_id)
    
    # Check if the donor has already responded
    existing_request = DonationRequests.query.filter_by(
        request_id=request_id, donor_id=current_user.user_id
    ).first()

    if existing_request:
        existing_request.status = "accepted"
        db.session.commit()
        
        print(f"🩸 Blood Type: {blood_request.blood_type}")  

    # Insert into Donations table
        donation_details = Donations(
        donor_id=current_user.user_id,
        blood_bank_id=None,  # Ensure this can be NULL
        donation_date=datetime.now(),  # Ensure date is not None
        blood_type=blood_request.blood_type,
        status='pending'
    )
        db.session.add(donation_details)
        db.session.commit()
        flash("You have already responded to this request.", "info")
        print(f"✅ Successfully inserted donation with ID: {donation_details.donation_id}")
        return redirect(url_for("donor_dashboard"))




    return redirect(url_for("donor_dashboard"))



@app.route('/decline_donation_request/<int:request_id>', methods=['POST', 'GET'])
@login_required
def decline_donation_request(request_id):
    """Decline a blood request"""
    # Check if the donor has already responded
    existing_request = DonationRequests.query.filter_by(
        request_id=request_id, donor_id=current_user.user_id
    ).first()

    if existing_request:
        existing_request.status = "rejected"  # Update the status
        db.session.commit()  # Commit the change
    else:
        new_donation_request = DonationRequests(
            request_id=request_id,
            donor_id=current_user.user_id,
            status="rejected"
        )
        db.session.add(new_donation_request)
        db.session.commit()

    flash("You have declined the request.", "warning")
    return redirect(url_for("donor_dashboard"))



@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
