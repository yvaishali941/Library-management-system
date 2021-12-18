import datetime

from flask import Flask,render_template,request,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user,UserMixin,logout_user
from datetime import date


app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SECRET_KEY'] = 'secret@123'
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)

class Admin(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    uname=db.Column(db.String(50),unique=True,nullable=False)
    password=db.Column(db.String(80),unique=True,nullable=False)

    def __repr__(self):
        return '<User % r>' % self.uname


class Book(db.Model):
    book_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)
    author=db.Column(db.String(50),nullable=False)
    isbn = db.Column(db.String(50),nullable=False)
    publisher = db.Column(db.String(50), nullable=False)
    edition=db.Column(db.String(5), nullable=False)
    avail=db.Column(db.String,default='Yes')
    entry_date=db.Column(db.DateTime(),default=datetime.datetime.utcnow)
    issued_to=db.Column(db.String(50),default='')

    def __repr__(self):
        return '<Book % r>' % self.isbn



class Student(db.Model):
    student_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)
    branch=db.Column(db.String(50),nullable=False)
    year=db.Column(db.String(4),nullable=False)
    roll_no = db.Column(db.String(50), unique=True, nullable=False)
    address = db.Column(db.String(100),  nullable=False)
    ph_no = db.Column(db.String(10),  nullable=False)
    max_issue=db.Column(db.Integer,default=3)
    issued_book_id=db.Column(db.String(50),default=' ')


    def __repr__(self):
        return '<Student % r>' % self.roll_no

class Borrow(db.Model):
    borrow_id=db.Column(db.Integer,primary_key=True)
    st_id=db.Column(db.Integer,nullable=False)
    b_id=db.Column(db.Integer,nullable=False)
    loan_date=db.Column(db.DateTime(),default=datetime.datetime.utcnow)
    loan_days=db.Column(db.Integer,default=15)
    expiry_date=db.Column(db.DateTime(),default=datetime.datetime.today()+datetime.timedelta(days=15))

    def __repr__(self):
        return '<Borrow % r>' % self.borrow_id


class Submit(db.Model):
    submit_id=db.Column(db.Integer,primary_key=True)
    st_id=db.Column(db.Integer,nullable=False)
    b_id=db.Column(db.Integer,nullable=False)
    submit_date=db.Column(db.DateTime(),default=datetime.datetime.utcnow)
    penalty = db.Column(db.Integer,default=0)

    def __repr__(self):
        return '<Submit % r>' % self.submit_id




@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@app.route("/")
def home():
    return render_template('home1.html')


@app.route("/register",methods=['GET','POST'])
def register():
    if request.method=='POST':
        uname = request.form.get('uname')
        password =request.form.get('password')
        user = Admin(uname=uname,password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/')
    return render_template('register.html')


@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        uname = request.form.get('uname')
        password = request.form.get('password')
        user = Admin.query.filter_by(uname=uname).first()
        if user and uname == user.uname and password == user.password:
            login_user(user)
            return redirect("/")

        else:
            flash('Invalid Credentials','warning')
            return redirect('/login')

    return render_template("login.html")



@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')

@app.route("/book_add",methods=['GET','POST'])
def book_add():
    if request.method == 'POST':
        name=request.form.get('name')
        author=request.form.get('author')
        isbn = request.form.get('isbn')
        publisher = request.form.get('publisher')
        edition = request.form.get('edition')

        qty=request.form.get('qty')
        #q=int(qty)
        #print(type(q))
        for i in range(int(qty)):
            book = Book(name=name, author=author, isbn=isbn, publisher=publisher ,edition=edition)
            db.session.add(book)
            db.session.commit()
        return redirect('/')

    return render_template('book.html')


@app.route("/student_add",methods=['GET','POST'])
def student_add():
    if request.method == 'POST':
        name=request.form.get('name')
        branch=request.form.get('branch')
        year=request.form.get('year')
        roll_no=request.form.get('roll_no')
        address=request.form.get('address')
        ph_no=request.form.get('ph_no')
        st=Student(name=name,branch=branch,year=year,roll_no=roll_no,address=address,ph_no=ph_no)
        db.session.add(st)
        db.session.commit()
        return redirect('/')
    return render_template('student.html')

@app.route("/display_st")
def display_student_list():
    all_student=Student.query.all()
    return render_template('display_st.html' ,all_student=all_student)

@app.route("/display_book")
def display_book_list():
    all_book=Book.query.all()
    return render_template('display_book.html' ,all_book=all_book)

@app.route("/issue",methods=['GET','POST'])
def issue():
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        student_id = request.form.get('student_id')
        book=Book.query.filter_by(book_id=book_id).first()
        student=Student.query.filter_by(student_id=student_id).first()
        #submit = Submit.query.filter_by(st_id=student_id).all()

        if book and book.avail=='Yes':
            #print(type(submit))
            if student and student.max_issue!=0:
                print('book issue')
                book.avail = 'No'
                book.issued_to = student.student_id
                db.session.commit()
                student.max_issue = student.max_issue - 1
                if student.max_issue == 2:
                    student.issued_book_id = student.issued_book_id + str(book.book_id)
                else:
                    student.issued_book_id = student.issued_book_id + ',' + str(book.book_id)
                db.session.commit()
                borrow = Borrow(st_id=student.student_id, b_id=book.book_id)
                db.session.add(borrow)
                db.session.commit()
                return redirect('/')

            else:
                print('Student is not available in directory')
        else:
            print('Book is not available in directory')
    return render_template('issue.html')



@app.route("/submit",methods=['GET','POST'])
def submit():
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        student_id = request.form.get('student_id')
        book=Book.query.filter_by(book_id=book_id).first()
        student=Student.query.filter_by(student_id=student_id).first()
        borrow = Borrow.query.filter_by(b_id=book_id).first()

        #print(book)
        #print(student)
        if book and book.avail=='No':
            if student and student.max_issue <= 3:
                print('book issue')
                book.avail='Yes'
                book.issued_to=''
                db.session.commit()
                student.max_issue=student.max_issue+1
                if len(student.issued_book_id)>2:
                    if str(book.book_id) == student.issued_book_id[1]:
                        student.issued_book_id = student.issued_book_id.replace(str(book.book_id)+',', '')
                    else:
                        student.issued_book_id = student.issued_book_id.replace(',' + str(book.book_id), '')
                else:
                    student.issued_book_id = student.issued_book_id.replace(str(book.book_id) , '')

                db.session.commit()
                if borrow.expiry_date<datetime.datetime.today():
                    d=borrow.expiry_date-datetime.datetime.today()
                    p=(d.days)*5
                else:
                    p=0
                submit= Submit(st_id=student.student_id, b_id=book.book_id,penalty=p)
                db.session.add(submit)
                db.session.commit()
                db.session.delete(borrow)
                db.session.commit()
                return redirect('/')
            else:
                print('Student is not available in directory')
        else:
            print('Book is not available in directory')
    return render_template('submit.html')

@app.route("/borrow_record")
def borrow_record():
    all_borrow=Borrow.query.all()
    return render_template('borrow.html',all_borrow=all_borrow)

@app.route("/deposit_record")
def deposit_record():
    all_deposit=Submit.query.all()
    return render_template('deposit.html',all_deposit=all_deposit)


@app.route("/st_detail/<int:id>")
def student_detail(id):
    st=Student.query.get(id)


    return render_template('st_detail.html',student=st)

@app.route("/st_update/<int:id>",methods=['GET','POST'])
def st_update(id):
    st=Student.query.get(id)
    #db.session.delete(blog)
    #db.session.commit()
    #flash('Post has been deleted successfully', 'success')
    return render_template('st_update.html',student=st)

@app.route("/st_delete/<int:id>",methods=['GET','POST'])
def st_delete(id):
    st=Student.query.get(id)
    db.session.delete(st)
    db.session.commit()
    #flash('Post has been deleted successfully', 'success')
    return redirect("/")

@app.route("/book_update/<int:id>",methods=['GET','POST'])
def book_update(id):
    book=Book.query.get(id)
    print(book)
    if request.method == 'POST':
        print('hi')
        book.name=request.form.get('name')
        book.author = request.form.get('author')
        book.isbn = request.form.get('isbn')
        book.publisher = request.form.get('publisher')
        book.edition = request.form.get('edition')
        qty=request.form.get('qty')
        db.session.commit()
        return redirect('/display_book')
    #flash('Post has been deleted successfully', 'success')
    return render_template('book_update.html',book=book)

@app.route("/book_delete/<int:id>",methods=['GET','POST'])
def book_delete(id):
    book=Book.query.get(id)
    db.session.delete(book)
    db.session.commit()
    #flash('Post has been deleted successfully', 'success')
    return redirect("/")

if __name__=="__main__":
    app.run(debug=True, port=2000)

