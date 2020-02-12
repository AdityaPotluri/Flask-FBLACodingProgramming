from flask import Flask,render_template, request, redirect, url_for,jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta

Month = datetime.today()-timedelta(30)
Week=datetime.today()-timedelta(30)
app=Flask(__name__)


ENV='dev'

if ENV=='dev':
    app.debug=True
    app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:Ap237033!@localhost/FBLA'
    
else:
    app.debug=False
    app.config['SQLALCHEMY_DATABASE_URI']=''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)

class FormResults(db.Model):
    __tablename__='FormResults'
    id=db.Column(db.Integer(),primary_key=True)
    Grade=db.Column(db.String(4))
    StudentNumber=db.Column(db.String())
    Hours=db.Column(db.Integer())
    Name=db.Column(db.String(200))
    Date=db.Column(db.DateTime,default=datetime.utcnow())
    Unique_Name=db.Column(db.String(200), default=Name+'||'+StudentNumber)

    def __init__(self,Grade,StudentNumber,Hours,Name):
        self.Grade=Grade
        self.StudentNumber=StudentNumber
        self.Hours=Hours
        self.Name=Name
        self.Unique_Name=self.Name+'||'+self.StudentNumber
        
        
    
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit',methods=['POST'])
def submit():
    if request.method=='POST':
        Name=request.form['Name']
        Grade=request.form['Grade']
        StudentNumber=request.form['StudentNumber']
        Hours=request.form['Hours']
        if Name=='' or Grade=='' or StudentNumber=='':
            return render_template('index.html',message='Please enter in all fields correctly')
        else:
            data= FormResults(Grade,StudentNumber,Hours,Name)
            db.session.add(data)
            db.session.commit()
            return redirect(url_for('index'))

@app.route('/EditandView',methods=['GET'])
def EditView():
    Students=FormResults.query.order_by(FormResults.Date).all()
    return render_template('Edit.html',Students=Students)

@app.route('/delete/<int:id>')
def delete(id):
    Student_to_delete=FormResults.query.get_or_404(id)
    try:
        db.session.delete(Student_to_delete)
        db.session.commit()
        return redirect(url_for('EditView'))
    except:
        return 'problem deleting task'

@app.route('/update/<int:id>', methods=['POST','GET'])
def update(id):
    Student=FormResults.query.get_or_404(id)
    if request.method=='POST':
        Student.Name=request.form['Name']
        Student.Grade=request.form['Grade']
        Student.StudentNumber=request.form['StudentNumber']
        Student.Hours=request.form['Hours']

        try:
            db.session.commit()
            return redirect(url_for('EditView'))
        except:
            return 'There was an issue updating your task'
    else:
        return render_template('update.html',Student=Student)

@app.route('/Analytics',methods=['GET','POST'])
def Analytics():
    Students=FormResults.query.order_by(FormResults.Date).all()

    studentToHours=dict()
    
    for student in Students:
        if student.Unique_Name in studentToHours:
            studentToHours[student.Unique_Name]=studentToHours[student.Unique_Name]+student.Hours
        else:
            studentToHours[student.Unique_Name]=student.Hours
    CSA_Community=0
    CSA_Service=0
    CSA_Achievement=0
    total_hours=0
    for vals in studentToHours.keys():
        if studentToHours[vals]>=500:
            CSA_Achievement+=1
        elif studentToHours[vals]>=200:
            CSA_Service+=1
        elif studentToHours[vals]>=50:
            CSA_Community+=1
    data=[CSA_Community,CSA_Service,CSA_Achievement]  
    
    
    Students = FormResults.query.filter(FormResults.Date >= Month).all()
    Month_hours=sum([student.Hours for student in Students])
    
    Students = FormResults.query.filter(FormResults.Date >= Week).all()
    Week_hours=sum([student.Hours for student in Students])
    

    return render_template("Analytics.html",data=data,Month_hours=Month_hours,Week_hours=Week_hours)

    


@app.route('/HelpMenu',methods=['GET','POST'])
def HelpMenu():
    render_template('HelpMenu.html')

if __name__=="__main__":
    
    app.run()