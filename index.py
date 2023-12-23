from flask import *
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
import datetime
import pandas as pd


app = Flask(__name__)

app.secret_key = 'skmv'
app.config['upload_direct']="C:/upload/direct/"
app.config['upload_indirect']="C:/upload/indirect/"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '#shubhammmmm_01'
app.config['MYSQL_DB'] = 'shubham'

mysql = MySQL(app)


@app.route('/')
def index():
    cur = mysql.connection.cursor()
    clgs=cur.execute('select * from subadmin where verify="YES"')
    clgs=cur.fetchall()
    cou=cur.execute('select * from courses where field="subadmin"')
    cou=cur.fetchall()
    return render_template('index.html',clgs=len(clgs),cou=len(cou))


@app.route('/portfolio')
def portfolio():
    return render_template('portfolio-details.html')


@app.route('/advantages')
def advantages():
    return render_template('advantages.html')


@app.route('/colleges')
def colleges():
    cur = mysql.connection.cursor()
    colleges=cur.execute('select * from subadmin')
    colleges=cur.fetchall()
    mysql.connection.commit()
    return render_template('colleges.html',data=colleges)


@app.route('/streams/<string:clg>/<int:clg_sr>')
def streams(clg,clg_sr):
    session["college"]=clg
    session["col_sr"]=clg_sr
    cur = mysql.connection.cursor()
    streams=cur.execute('select * from streams where college=%s',(clg_sr,))
    streams=cur.fetchall()
    college_det=cur.execute('select * from subadmin where sr=%s',(clg_sr,))
    college_det=cur.fetchall()
    session["college_details"]=college_det
    mysql.connection.commit()
    if 'pos' in session:
        session.pop('pos')
    return render_template('stream.html',data=streams)

@app.route('/course/<string:stream>/<string:stream_sr>')
def course(stream,stream_sr):
    clg=session["col_sr"]
    session["stream_name"]=stream
    session["stream_sr"]=stream_sr
    print(clg)
    if 'pso' in session:
        session.pop('pso',None)
    cur = mysql.connection.cursor()
    data=cur.execute('select * from courses where stream="'+stream_sr+'" and field="subadmin" and college=%s',(clg,))
    data=cur.fetchall()
    print(data)
    year=cur.execute('select courses.year from courses where stream="'+stream_sr+'" and college=%s',(clg,))
    year=cur.fetchall()
    pos=cur.execute('select * from streams_pos where stream="'+stream_sr+'" and college=%s',(clg,))
    pos=cur.fetchall()
    session["pos"]=pos
    s=tuple((str(x[0])) for x in data)
    y=tuple((int(x[0])) for x in year)
    length=len(data)
    session["stream"]=stream
    return render_template('course.html',data=s,length=length,y=y,dt=data)

@app.route('/pass/<string:course>/<int:year>/<int:course_sr>')
def lol(course,year,course_sr):
    session['course'] = course
    session['year'] = year
    session["course_sr"]=course_sr
    print(session['year'])
    # cur = mysql.connection.cursor()
    # # psos=cur.execute('select * from course_psos where course="'+ course+'"')
    # # psos=cur.fetchall()
    # # session["psos"]=psos
    # imp
    return redirect('/checklogin')


@app.route('/year',methods=["POST","GET"])
def year():
    if 'yearop' not in session:
        session['yearop']="year"
    else :
        if request.method != "POST" and 'yearop' not in request.form:
            session['yearop']=session['yearop']
        elif request.method == "POST" and 'yearop' in request.form:
            session["yearop"]=request.form["yearop"]
        else:
            session['yearop']="year"
    if 'selectedyear' in session:
        session.pop('selectedyear' , None )    
    if "submsg" in session:
        session.pop("submsg",None)  
    print(session["yearop"])
    clg=session["col_sr"]
    today = datetime.date.today()
    cur_year=today.year
    stream=session['stream']
    cur_pso=''
    if request.method=="POST" and 'cur_pso' in request.form and 'course' in session:
        cur_pso=request.form.getlist('cur_pso')
        course=str(session["course_sr"])
        for i in range(0,len(cur_pso)):
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO course_psos(pso,course,year,college) VALUES ( % s, % s, %s ,%s)', (cur_pso[i],course,cur_year,clg))
            mysql.connection.commit()

        print(cur_pso)

    if 'course' in session :
        course=str(session["course_sr"])
        course_name=session["course"]
        cur = mysql.connection.cursor()
        psos=cur.execute('select * from course_psos where course="'+ course+'" and year="'+ str(int(cur_year)-1) +'" and college=%s',(clg,))
        psos=cur.fetchall()
        cur_pso=cur.execute('select * from course_psos where course="'+ course+'" and year="'+ str(cur_year) +'" and college=%s',(clg,))
        cur_pso=cur.fetchall()
        mysql.connection.commit()
        session["psos"]=cur_pso
        year=int(session['year'])
        stream=session["stream"]
        pos=session["pos"]
        if "dataremove" in session:
            course=str(session["course"])
            pyear=str(session["particularYear"])
            return redirect("/subcal/"+course+"/"+pyear+"")
        elif "dataupload" in session:
            course=str(session["course"])
            pyear=str(session["particularYear"])
            return redirect("/subcal/"+course+"/"+pyear+"")
        else:
            pass
        return render_template('year.html',course=course_name,year=year,stream=stream,po=pos,pso=psos,cur_pso=cur_pso,cur_year=cur_year)
    else:
        return redirect('/')

@app.route('/subcal/<string:course>/<string:year>')
def subcal(course,year):
    print(year)
    session["selectedYear"]=year
    today = datetime.date.today()
    cur_year=today.year
    print(cur_year)
    op=str(session['yearop'])
    print(op)
    tyear=session['year']
    print(cur_year+(int(tyear)-int(year)))
    course_sr=str(session["course_sr"])
    print(course_sr)
    cur = mysql.connection.cursor()
    sub=cur.execute('select * from subjects where course="'+course_sr+'" and year='+year)
    sub=cur.fetchall()
    if op=="year":
        green=cur.execute('select distinct(subject) from direct where course=%s and year=%s',(course_sr,(cur_year+(int(tyear)-int(year))),))
        green=cur.fetchall()
    elif op == "exyear":
        green=cur.execute('select distinct(subject) from direct where course=%s and exyear=%s',(course_sr,cur_year,))
        green=cur.fetchall()
    else:
        pass
   
    session["sub_det"]=sub
    # imp 
    session["particularYear"]=year
    session["course_name"]=course
    subjects=tuple((str(x[0])) for x in sub)
    session["sub"]=subjects
    greenn=tuple((int(x[0])) for x in green)
    print(greenn)
    session["green"]=greenn
    session['selectedyear']=year
    if "dataupload" in session:
        subject=session["subject"]
        return redirect("/particular/"+subject+"/"+str(session["sub_sr"])+"")
    elif "dataremove" in session:
        session.pop("dataremove", None)
        subject=session["subject"]
        return redirect("/particular/"+subject+"/"+str(session["sub_sr"])+"")
    else:
        pass
    return redirect('/subjects')

@app.route('/subjects')
def subjects():
    msg=""
    if "submsg" in session:
        msg=session["submsg"]
        session.pop("submsg",None)
    else:
        pass
    if 'sub' in session:
        subjects=session["sub_det"]
        green=session['green']
        if 'subject' in session:
            session.pop('subject',None)
            session.pop('cos',None)
        course=session["course_name"]
        return render_template('subject.html',subject=subjects,course=course,green=green,msg=msg)
    else:
        return redirect('/')
    
@app.route('/particular/<string:subject>/<int:sub_sr>')
def particular(subject,sub_sr):
    if "submsg" in session:
        session.pop("submsg",None)  
    # session["cos"]=cos
    # imp
    session["subject"]=subject
    session["sub_sr"] = sub_sr
    return redirect('/choice')

@app.route('/checklogin')
def checklogin():
    if 'course' in session and 'stream' in session:
        if 'email' in session and 'course' in session and 'main' in session:
            main=session['main']
            course=session['course']
            if main == course:
                return redirect('/year')
            else:
                return redirect('/login')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    mesage = ''
    stream=session["stream"]
    if 'course' in session and 'stream' in session:
        course=session["course"]      
        if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
                email = request.form['email']
                password = request.form['password']
                course=session["course"]
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    'SELECT * FROM user WHERE email = % s AND password = % s AND course = % s', (email, password,course ))
                user = cursor.fetchone()
                if user:
                    if user["field"]=="subadmin" and user["course"] == session["course"]:
                        session['loggedin'] = True
                        session['userid'] = user['userid']
                        session['name'] = user['name']
                        session['email'] = user['email']
                        session['main']=user['course']
                        session["subadmin"]="subadmin"
                        return redirect('/year')
                    else:
                        mesage = 'Please enter correct email / password !'
                else:
                    mesage = 'Please enter correct email / password !'
        return render_template('login.html', mesage=mesage,stream=stream,course=course)

    else:
        return redirect('/')

@app.route('/logout')
def logout():
    if "stream_sr" in session:
        stream=session["stream"]
        stream_sr=str(session["stream_sr"])
    session.pop('subs', None)
    session.pop('course',None)
    session.pop('course_sr',None)
    session.pop('subadmin', None)
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    session.pop('subject', None)
    session.pop('sub', None)
    session.pop('sub_sr', None)
    session.pop('direct', None)
    session.pop('indirect', None)
    session.pop('pso',None)
    session.pop('cos',None)
    session.pop('main',None)
    session.pop('yearop',None)
    if 'user' in session and 'upass' in session:
        session.pop('user', None)
        session.pop('upass', None)
        return redirect('/')
    return redirect('/course/'+stream+'/'+stream_sr)
        


@app.route('/register', methods=['GET', 'POST'])
def register():
    stream=session["stream"]
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute(
                'INSERT INTO user VALUES (NULL, % s, % s, % s)', (userName, email, password, ))
            mysql.connection.commit()
            mesage = 'You have successfully registered !'
            return redirect('/login')
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage=mesage,stream=stream)


@app.route('/choice',methods=['POST','GET'])
def choice():
    if "dataremove" in session:
        session.pop("dataremove", None)
    elif "dataupload" in session:
        session.pop("dataupload", None)
    else:
        pass
    
    msg=""
    if "derror" in session:
        if session["derror"] == "yes":
            msg="Please upload valid format of Direct file...!!"
            session.pop("derror",None)
        else:
            pass
    elif "inderror" in session:
        if session["inderror"] == "yes":
            msg="Please upload valid format of Indirect file...!!"
            session.pop("inderror",None)
        else:
            pass
    else:
        pass
    cur_co=''
    today = datetime.date.today()
    year=today.year
    cur = mysql.connection.cursor()
    green=session['green']
    clg=session["col_sr"]
    if 'email' in session:
        if request.method=='POST' and 'cur_co' in request.form:
            cur_co=request.form.getlist('cur_co')
            subject=session['sub_sr']
            subject_name=session["subject"]
            course=session["course_sr"]
            co=session['cos']
            for i in range(0,len(cur_co)):
                cur = mysql.connection.cursor()
                cur.execute('INSERT INTO subjects_cos(co,subject,course,year,college) VALUES ( % s, % s, %s,%s,%s)', (cur_co[i],subject,course,year,str(clg)))
                mysql.connection.commit()
        if 'subject' in session:
            subject=session['sub_sr']
            subject_name=session["subject"]
            course=session["course_sr"]
            co=cur.execute('select * from subjects_cos where subject="'+str(subject)+'" and course="'+str(course)+'" and year="'+str(int(year)-1)+'" and college=%s ',(str(clg),))
            co=cur.fetchall()
            cur_co=cur.execute('select * from subjects_cos where subject="'+str(subject)+'" and course="'+str(course)+'" and year="'+str(year)+'" and college=%s ',(str(clg),))
            cur_co=cur.fetchall()
            session["cos"]=cur_co
            mysql.connection.commit()
            if 'direct' in session and 'indirect' in session:
                session.pop('direct')
                session.pop('indirect')
            else:
                return render_template('choice.html',s=subject_name,co=co,cur_co=cur_co,year=year,green=green,msg=msg)
            return render_template('choice.html',s=subject_name,co=co,cur_co=cur_co,year=year,green=green,msg=msg)
        else:
            return redirect('/year')    
    else:
        return redirect('/login')

@app.route('/cal', methods=["POST", "GET"])
def cal():

    isDir = os.path.isdir('C:/upload')
    isDirDi = os.path.isdir('C:/upload/direct')
    isDirIn = os.path.isdir('C:/upload/indirect')
    
    if isDir == True and isDirDi == True and isDirIn == True:
        print("all good")
        pass
    elif isDir == False and isDirDi == False and isDirIn == False:
        os.mkdir('C:/upload')
        os.mkdir('C:/upload/direct')
        os.mkdir('C:/upload/indirect')
        print("not all good")
    elif isDir == False and isDirIn == False:
        os.mkdir('C:/upload/indirect')
        print("indirect is not good")
    elif isDir == False and isDirDi == False:
        os.mkdir('C:/upload/direct')
        print("direct is not good")
    else:
        return "error"
    
    if request.method == "POST" and  request.files["direct"].filename!="" and  request.files["indirect"].filename!="" :
        d=request.files["direct"]
        i=request.files["indirect"]

        d.save(os.path.join(app.config["upload_direct"],(d.filename)))
        i.save(os.path.join(app.config["upload_indirect"],(i.filename)))


        # for direct data to making list of csv data
        ddata = pd.read_csv('C:/upload/direct/'+d.filename+'',skiprows=-1)
        dli=ddata.values.tolist()

        # for indirect data to making list of csv data
        idata = pd.read_csv('C:/upload/indirect/'+i.filename+'',skiprows=-1)
        ili=idata.values.tolist()

        session['direct'] = dli
        session['indirect'] = ili
        print(len(dli[0]))
        for dd in dli:
            if len(dd)==4:
                pass
            else:
                session["derror"]="yes"
                return redirect("/choice")
        for ind in ili:
            if len(ind)==12:
                pass
            else:
                session["inderror"]="yes"
                return redirect("/choice")
    
        resp1 = redirect('/matrix')
        return resp1
    else:
        return redirect('/choice')

@app.route('/<string:subject>/viewdata')
def viewdata(subject):
    mysql.connection.commit()
    cur = mysql.connection.cursor()
    today = datetime.date.today()
    year=today.year
    course=str(session['course_sr'])
    clg=session["col_sr"]
    co=session['cos']
    pos=session['pos']
    pso=session['psos']
    tt=len(session['pos'])+len(session['psos'])
    print(pos)
    print(course)
    if session['yearop'] == "year":
        nyear=(year+int(session["year"])-int(session['selectedYear']))
        direct=cur.execute("select * from direct where subject=%s and course=%s and year=%s and college=%s",(str(subject),str(course),nyear,clg,))
        direct=cur.fetchall()
        indirect=cur.execute("select * from indirect where subject=%s and course=%s and year=%s and college=%s",(str(subject),str(course),nyear,clg,))
        indirect=cur.fetchall()
        pe1=cur.execute("select po.val from po where subject='"+str(subject)+"' and course='"+str(course)+"' and year=%s and college=%s",(nyear,clg,))
        pe1=cur.fetchall()
        poe1 = list((int(x[0])) for x in pe1)
        resultTuple = list(poe1[i:i + tt] for i in range(0, len(poe1), tt))

    elif session['yearop'] == "exyear":
        direct=cur.execute("select * from direct where subject=%s and course=%s and exyear=%s and college=%s",(str(subject),str(course),year,clg,))
        direct=cur.fetchall()
        indirect=cur.execute("select * from indirect where subject=%s and course=%s and exyear=%s and college=%s",(str(subject),str(course),year,clg,))
        indirect=cur.fetchall()
        pe1=cur.execute("select po.val from po where subject='"+str(subject)+"' and course='"+str(course)+"' and exyear=%s",(year,))
        pe1=cur.fetchall()
        poe1 = list((int(x[0])) for x in pe1)
        resultTuple = list(poe1[i:i + tt] for i in range(0, len(poe1), tt))

    else:
        direct=''
        indirect=''
        pass
    print(resultTuple)
    mysql.connection.commit()
    return render_template("displaydata.html",direct=direct,indirect=indirect,po=resultTuple,pos=pos,pso=pso)


@app.route('/<string:subject>/removedata')
def removedata(subject):
    session["dataremove"]="yes"
    mysql.connection.commit()
    cur = mysql.connection.cursor()
    today = datetime.date.today()
    tyear=str(today.year) 
    peryear=session["particularYear"]
    year=session['year']
    dif=(int(year)-int(peryear))
    course=str(session['course_sr'])
    print(year)
    if session['yearop'] == "year":
        cur.execute("delete from direct where subject="+subject+" and course=%s and year=%s",(course,str(int(tyear)+dif),))
        cur.execute("delete from indirect where subject="+subject+" and course=%s and year=%s",(course,str(int(tyear)+dif),))
        cur.execute("delete from po where subject="+subject+" and course=%s and year=%s",(course,str(int(tyear)+dif),))
        cur.execute("delete from poavg where subject="+subject+" and course=%s and year=%s",(course,str(int(tyear)+dif),))
    elif session['yearop'] == "exyear":
        cur.execute("delete from direct where subject="+subject+" and course=%s and exyear=%s",(course,tyear,))
        cur.execute("delete from indirect where subject="+subject+" and course=%s and exyear=%s",(course,tyear,))
        cur.execute("delete from po where subject="+subject+" and course=%s and exyear=%s",(course,tyear,))
        cur.execute("delete from poavg where subject="+subject+" and course=%s and exyear=%s",(course,tyear,))
    else:
        pass
    cur.connection.commit()
    return redirect("/year")


                            # for inserting direct and indirect data
                                                # for inserting matrix values

@app.route('/matrix')
def matrix():
    today = datetime.date.today()
    year=today.year
    if 'direct' in session != '' and 'indirect' in session != '' and 'name' in session:
        pos=session["pos"]
        psos=session['psos']
        cos=session['cos']
        return render_template('copo.html',po=pos,pso=psos,co=cos,year=year)
    elif 'name' in session:
        return redirect('/choice')
    else:
        return redirect('/')

@app.route('/poInsert/<int:row>/<int:col>/<int:pso>', methods=['POST', 'GET'])
def poInsert(row,col,pso):
    college=str(session["col_sr"])
    subject=str(session["sub_sr"])
    course=str(session["course_sr"])
    session["row"]=row
    session["col"]=col
    session["pso"]=pso
    peryear=session["particularYear"]
    year=session['year']
    today = datetime.date.today()
    tyear=today.year
    dif=(int(year)-int(peryear))
    
    direct=session["direct"]
    indirect=session["indirect"]
    print(indirect)
    cur = mysql.connection.cursor()
        
    for i in range(0,len(direct)):
        cur.execute("insert into direct(sr,name,cie1,ca1,subject,course,college) values(%s,%s,%s,%s,%s,%s,%s)",(direct[i][0],direct[i][1],direct[i][2],direct[i][3],subject,str(course),college))

    for i in range(0,len(indirect)):
        cur.execute("insert into indirect(sr,name,Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8,Q9,Q10,subject,course,college) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(indirect[i][0],indirect[i][1],indirect[i][2],indirect[i][3],indirect[i][4],indirect[i][5],indirect[i][6],indirect[i][7],indirect[i][8],indirect[i][9],indirect[i][10],indirect[i][11],subject,str(course),college))


    mysql.connection.commit()
    cur = mysql.connection.cursor()
    session["dataupload"]="yes"

    comb0 = ["co1/po1", "co1/po2", "co1/po3", "co1/po4", "co1/po5", "co1/po6", "co1/po7", "co1/po8", "co1/po9", "co1/po10", "co1/po11", "co1/po12"]
    comb1 = ["co2/po1", "co2/po2", "co2/po3", "co2/po4", "co2/po5", "co2/po6", "co2/po7", "co2/po8", "co2/po9", "co2/po10", "co2/po11", "co2/po12"]
    comb2 = ["co3/po1", "co3/po2", "co3/po3", "co3/po4", "co3/po5", "co3/po6", "co3/po7", "co3/po8", "co3/po9", "co3/po10", "co3/po11", "co3/po12"]
    comb3 = ["co4/po1", "co4/po2", "co4/po3", "co4/po4", "co4/po5", "co4/po6", "co4/po7", "co4/po8", "co4/po9", "co4/po10", "co4/po11", "co4/po12"]
    comb4 = ["co5/po1", "co5/po2", "co5/po3", "co5/po4", "co5/po5", "co5/po6", "co5/po7", "co5/po8", "co5/po9", "co5/po10", "co5/po11", "co5/po12"]
    comb5 = ["co6/po1", "co6/po2", "co6/po3", "co6/po4", "co6/po5", "co6/po6", "co6/po7", "co6/po8", "co6/po9", "co6/po10", "co6/po11", "co6/po12"]
    comb6 = ["co7/po1", "co7/po2", "co7/po3", "co7/po4", "co7/po5", "co7/po6", "co7/po7", "co7/po8", "co7/po9", "co7/po10", "co7/po11", "co7/po12"]
    comb7 = ["co8/po1", "co8/po2", "co8/po3", "co8/po4", "co8/po5", "co8/po6", "co8/po7", "co8/po8", "co8/po9", "co8/po10", "co8/po11", "co8/po12"]
    comb8 = ["co9/po1", "co9/po2", "co9/po3", "co9/po4", "co9/po5", "co9/po6", "co9/po7", "co9/po8", "co9/po9", "co9/po10", "co9/po11", "co9/po12"]
    comb9 = ["co10/po1", "co10/po2", "co10/po3", "co10/po4", "co10/po5", "co10/po6", "co10/po7", "co10/po8", "co10/po9", "co10/po10", "co10/po11", "co10/po12"]
    main = [comb0,comb1,comb2,comb3,comb4,comb5,comb6,comb7,comb8,comb9]
    last=[]

    comb00 = ["co1/po1", "co1/po2", "co1/po3", "co1/po4", "co1/po5", "co1/po6", "co1/po7", "co1/po8", "co1/po9", "co1/po10", "co1/po11", "co1/po12"]
    comb10 = ["co2/po1", "co2/po2", "co2/po3", "co2/po4", "co2/po5", "co2/po6", "co2/po7", "co2/po8", "co2/po9", "co2/po10", "co2/po11", "co2/po12"]
    comb20 = ["co3/po1", "co3/po2", "co3/po3", "co3/po4", "co3/po5", "co3/po6", "co3/po7", "co3/po8", "co3/po9", "co3/po10", "co3/po11", "co3/po12"]
    comb30 = ["co4/po1", "co4/po2", "co4/po3", "co4/po4", "co4/po5", "co4/po6", "co4/po7", "co4/po8", "co4/po9", "co4/po10", "co4/po11", "co4/po12"]
    comb40 = ["co5/po1", "co5/po2", "co5/po3", "co5/po4", "co5/po5", "co5/po6", "co5/po7", "co5/po8", "co5/po9", "co5/po10", "co5/po11", "co5/po12"]
    comb50 = ["co6/po1", "co6/po2", "co6/po3", "co6/po4", "co6/po5", "co6/po6", "co6/po7", "co6/po8", "co6/po9", "co6/po10", "co6/po11", "co6/po12"]
    comb60 = ["co7/po1", "co7/po2", "co7/po3", "co7/po4", "co7/po5", "co7/po6", "co7/po7", "co7/po8", "co7/po9", "co7/po10", "co7/po11", "co7/po12"]
    comb70 = ["co8/po1", "co8/po2", "co8/po3", "co8/po4", "co8/po5", "co8/po6", "co8/po7", "co8/po8", "co8/po9", "co8/po10", "co8/po11", "co8/po12"]
    comb80 = ["co9/po1", "co9/po2", "co9/po3", "co9/po4", "co9/po5", "co9/po6", "co9/po7", "co9/po8", "co9/po9", "co9/po10", "co9/po11", "co9/po12"]
    comb90 = ["co10/po1", "co10/po2", "co10/po3", "co10/po4", "co10/po5", "co10/po6", "co10/po7", "co10/po8", "co10/po9", "co10/po10", "co10/po11", "co10/po12"]
    main0 = [comb00,comb10,comb20,comb30,comb40,comb50,comb60,comb70,comb80,comb90]
    last0=[]

    
    comb000 = ["co1/pSo1", "co1/pSo2", "co1/pSo3", "co1/pSo4", "co1/pSo5", "co1/pSo6", "co1/pSo7", "co1/pSo8", "co1/pSo9", "co1/pSo10"]
    comb100 = ["co2/pSo1", "co2/pSo2", "co2/pSo3", "co2/pSo4", "co2/pSo5", "co2/pSo6", "co2/pSo7", "co2/pSo8", "co2/pSo9", "co2/pSo10"]
    comb200 = ["co3/pSo1", "co3/pSo2", "co3/pSo3", "co3/pSo4", "co3/pSo5", "co3/pSo6", "co3/pSo7", "co3/pSo8", "co3/pSo9", "co3/pSo10"]
    comb300 = ["co4/pSo1", "co4/pSo2", "co4/pSo3", "co4/pSo4", "co4/pSo5", "co4/pSo6", "co4/pSo7", "co4/pSo8", "co4/pSo9", "co4/pSo10"]
    comb400 = ["co5/pSo1", "co5/pSo2", "co5/pSo3", "co5/pSo4", "co5/pSo5", "co5/pSo6", "co5/pSo7", "co5/pSo8", "co5/pSo9", "co5/pSo10"]
    comb500 = ["co6/pSo1", "co6/pSo2", "co6/pSo3", "co6/pSo4", "co6/pSo5", "co6/pSo6", "co6/pSo7", "co6/pSo8", "co6/pSo9", "co6/pSo10"]
    comb600 = ["co7/pSo1", "co7/pSo2", "co7/pSo3", "co7/pSo4", "co7/pSo5", "co7/pSo6", "co7/pSo7", "co7/pSo8", "co7/pSo9", "co7/pSo10"]
    comb700 = ["co8/pSo1", "co8/pSo2", "co8/pSo3", "co8/pSo4", "co8/pSo5", "co8/pSo6", "co8/pSo7", "co8/pSo8", "co8/pSo9", "co8/pSo10"]
    comb800 = ["co9/pSo1", "co9/pSo2", "co9/pSo3", "co9/pSo4", "co9/pSo5", "co9/pSo6", "co9/pSo7", "co9/pSo8", "co9/pSo9", "co9/pSo10"]
    comb900 = ["co10/pSo1", "co10/pSo2", "co10/pSo3", "co10/pSo4", "co10/pSo5", "co10/pSo6", "co10/pSo7", "co10/pSo8", "co10/pSo9", "co10/pSo10"]
    main00 = [comb000,comb100,comb200,comb300,comb400,comb500,comb600,comb700,comb800,comb900]
    last00=[]

    comb0000 = ["co1/pSo1", "co1/pSo2", "co1/pSo3", "co1/pSo4", "co1/pSo5", "co1/pSo6", "co1/pSo7", "co1/pSo8", "co1/pSo9", "co1/pSo10"]
    comb1000 = ["co2/pSo1", "co2/pSo2", "co2/pSo3", "co2/pSo4", "co2/pSo5", "co2/pSo6", "co2/pSo7", "co2/pSo8", "co2/pSo9", "co2/pSo10"]
    comb2000 = ["co3/pSo1", "co3/pSo2", "co3/pSo3", "co3/pSo4", "co3/pSo5", "co3/pSo6", "co3/pSo7", "co3/pSo8", "co3/pSo9", "co3/pSo10"]
    comb3000 = ["co4/pSo1", "co4/pSo2", "co4/pSo3", "co4/pSo4", "co4/pSo5", "co4/pSo6", "co4/pSo7", "co4/pSo8", "co4/pSo9", "co4/pSo10"]
    comb4000 = ["co5/pSo1", "co5/pSo2", "co5/pSo3", "co5/pSo4", "co5/pSo5", "co5/pSo6", "co5/pSo7", "co5/pSo8", "co5/pSo9", "co5/pSo10"]
    comb5000 = ["co6/pSo1", "co6/pSo2", "co6/pSo3", "co6/pSo4", "co6/pSo5", "co6/pSo6", "co6/pSo7", "co6/pSo8", "co6/pSo9", "co6/pSo10"]
    comb6000 = ["co7/pSo1", "co7/pSo2", "co7/pSo3", "co7/pSo4", "co7/pSo5", "co7/pSo6", "co7/pSo7", "co7/pSo8", "co7/pSo9", "co7/pSo10"]
    comb7000 = ["co8/pSo1", "co8/pSo2", "co8/pSo3", "co8/pSo4", "co8/pSo5", "co8/pSo6", "co8/pSo7", "co8/pSo8", "co8/pSo9", "co8/pSo10"]
    comb8000 = ["co9/pSo1", "co9/pSo2", "co9/pSo3", "co9/pSo4", "co9/pSo5", "co9/pSo6", "co9/pSo7", "co9/pSo8", "co9/pSo9", "co9/pSo10"]
    comb9000 = ["co10/pSo1", "co10/pSo2", "co10/pSo3", "co10/pSo4", "co10/pSo5", "co10/pSo6", "co10/pSo7", "co10/pSo8", "co10/pSo9", "co10/pSo10"]
    main000 = [comb0000,comb1000,comb2000,comb3000,comb4000,comb5000,comb6000,comb7000,comb8000,comb9000]
    last000=[]

    for i in range(0,row):
        for j in range(0,col):
            last=main[i]
            last0=main0[i]
            last[j]= request.form[""+last[j]+""]
            cur.execute('INSERT INTO  po(field,val,subject,course,college) VALUES (% s, % s, % s, % s,%s)',(last0[j],last[j],subject,course,college))
        for j in range(0,pso):
            last00=main00[i]
            last000=main000[i]
            last00[j]= request.form[""+last00[j]+""]
            cur.execute('INSERT INTO  po(field,val,subject,course,college) VALUES (% s, % s, % s , % s,%s)',(last000[j],last00[j],subject,course,college))

    


    
                                            # for calculating average of po's and store it in database

    # important
    po=[]
    ps=[]


    valuepo=[]
    a=0
    valuepso=[]
    b=0
    avgpo=["po1","po2","po3","po4","po5","po6","po7","po8","po9","po10","po11","po12"]
    avgpso=["pso1","pso2","pso3","pso4","pso5","pso6","pso7","pso8","pso9","pso10"]

    polist=["po1","po2","po3","po4","po5","po6","po7","po8","po9","po10","po11","po12"]
    session["polist"]=polist
    psolist=["pso1","pso2","pso3","pso4","pso5","pso6","pso7","pso8","pso9","pso10"]
    for i in range(0,col):
        for j in range(0,row):
            valuepo=main[j]
            a=a+int(valuepo[i])
        avgpo[i]=a/row 
        a=0
        po.append(round(avgpo[i],2))
    
    for i in range(0,pso):
        for j in range(0,row):
            valuepso=main00[j]
            b=b+int(valuepso[i])
        avgpso[i]=b/row 
        b=0
        ps.append(round(avgpso[i],2))

    for i in range(0,col):
        cur.execute('INSERT INTO  poavg(field,val,subject,course,college) VALUES (% s, % s, % s, % s,%s)',(polist[i],po[i],subject,course,college))
        cur.fetchall()
    for i in range(0,pso):
        cur.execute('INSERT INTO  poavg(field,val,subject,course,college) VALUES (% s, % s, % s, % s,%s)',(psolist[i],ps[i],subject,course,college))
        cur.fetchall()

        
    if session['yearop'] == 'year':
        cur.execute("update direct set year=%s where subject=%s and year =%s and course =%s and exyear='Empty' ",((tyear+dif),subject,"Empty",course))
        cur.execute("update indirect set year=%s where subject=%s and year =%s and course =%s and exyear='Empty' ",((tyear+dif),subject,"Empty",course))
        cur.execute("update po set year=%s where subject=%s and year =%s and course =%s and exyear='Empty' ",((tyear+dif),subject,"Empty",course))
        cur.execute("update poavg set year=%s where subject=%s and year =%s and course =%s and exyear='Empty' ",((tyear+dif),subject,"Empty",course))
    elif session['yearop'] == 'exyear':
        cur.execute("update direct set exyear=%s where subject=%s and year =%s and course =%s and year='Empty' ",(tyear,subject,"Empty",course))
        cur.execute("update indirect set exyear=%s where subject=%s and year =%s and course =%s and year='Empty' ",(tyear,subject,"Empty",course))
        cur.execute("update po set exyear=%s where subject=%s and year =%s and course =%s and year='Empty' ",(tyear,subject,"Empty",course))
        cur.execute("update poavg set exyear=%s where subject=%s and year =%s and course =%s and year='Empty' ",(tyear,subject,"Empty",course))
    else:
        pass

    mysql.connection.commit()
        
    return redirect('/year')


                                        #for subAdmin profile 

@app.route('/subadminyear')
def subadminyear():
    if 'subadmin' in session:
        course=str(session["course_sr"])
        return redirect('/sub/'+course+'')
    else:
        return redirect('/year')

@app.route('/sub/<string:course>')
def sub(course):
    if 'subadmin' in session:
        cur = mysql.connection.cursor()
        sub=cur.execute('select * from subjects where course="'+course+'"')
        sub=cur.fetchall()
        subjects=tuple((str(x[0])) for x in sub)
        sub_sr_det=tuple((str(x[4])) for x in sub)
        session["sub_sr_det"]=sub_sr_det
        session["subs"]=subjects
        if len(subjects) == 0:
            return '<script type="text/javascript"> alert("There are No Subjects in your Course !! Please add atleast 1 Subject."); window.location.href = "/year"; </script>'
        return redirect('/subadmin')
    else:
        return redirect('/year')

@app.route('/subadmin')
def subadmin():
    clg=session["col_sr"]
    today = datetime.date.today()
    year=today.year
    yearop=session['yearop']
    if 'subs' in session:
        if len(session["subs"])== 0 :
            return redirect('/subadminyear')
    # important for subject
        elif 'subs' in session and 'subadmin' in session:
            sub = []
            sub=session["sub_sr_det"]
            print(sub)
            course=str(session["course_sr"])
            cur = mysql.connection.cursor()
            cur.execute("delete from direct where cie1='' or ca1='' and course=%s",(course,))

            q = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q8", "Q9", "Q10"]
            e = ["Q1e", "Q2e", "Q3e", "Q4e", "Q5e", "Q6e", "Q7e", "Q8e", "Q9e", "Q10e"]
            v = ["Q1v", "Q2v", "Q3v", "Q4v", "Q5v", "Q6v", "Q7v", "Q8v", "Q9v", "Q10v"]
            g = ["Q1g", "Q2g", "Q3g", "Q4g", "Q5g", "Q6g", "Q7g", "Q8g", "Q9g", "Q10g"]
            a = ["Q1a", "Q2a", "Q3a", "Q4a", "Q5a", "Q6a", "Q7a", "Q8a", "Q9a", "Q10a"]
            p = ["Q1p", "Q2p", "Q3p", "Q4p", "Q5p", "Q6p", "Q7p", "Q8p", "Q9p", "Q10p"]
            abavg = ["q1aba", "q2aba", "q3aba", "q4aba", "q5aba","q6aba", "q7aba", "q8aba", "q9aba", "q10aba"]
            avg = ['ab','bc','cd','de','ef','fg','gh','hi','ij','jk']



            per = []
            perc = 0
            print(sub)
            if session['yearop'] == 'year':
                for j in range(0, len(sub)):
                    t=cur.execute("SELECT * FROM indirect WHERE subject='"+sub[j]+"'  and course='"+course+"' and year=%s and college=%s",(year,clg,))
                    t=cur.fetchall()
                    print(t)
                    print(year)
                    for i in range(0, 10):
                        e[i] = cur.execute(
                            "SELECT * FROM indirect WHERE subject='"+sub[j]+"'  and course='"+course+"' and "+q[i]+" = 'Excellent' and year=%s and college=%s",(year,clg,))
                        e[i] = cur.fetchall()
                        v[i] = cur.execute(
                            "SELECT * FROM indirect WHERE subject='"+sub[j]+"'  and course='"+course+"' and "+q[i]+" = 'Very Good' and year=%s and college=%s",(year,clg,))
                        v[i] = cur.fetchall()
                        g[i] = cur.execute(
                            "SELECT * FROM indirect WHERE subject='"+sub[j]+"'  and course='"+course+"' and "+q[i]+" = 'Good' and year=%s and college=%s",(year,clg,))
                        g[i] = cur.fetchall()
                        a[i] = cur.execute(
                            "SELECT * FROM indirect WHERE subject='"+sub[j]+"'  and course='"+course+"' and "+q[i]+" = 'Average' and year=%s and college=%s",(year,clg,))
                        a[i] = cur.fetchall()
                        p[i] = cur.execute(
                            "SELECT * FROM indirect WHERE subject='"+sub[j]+"'  and course='"+course+"' and "+q[i]+" = 'Poor' and year=%s and college=%s",(year,clg,))
                        p[i] = cur.fetchall()

                        check=(5 * len(e[i]) + 4 * len(v[i]) + 3 * len(g[i]) + 2 * len(a[i]) + len(p[i]))
                        if check == 0:
                            print(sub[j])
                            cur.execute("select year from subjects where subject=%s and course=%s",(sub[j],course,))
                            dif=cur.fetchone()
                            print(dif)
                            if dif == None:
                                dif = year
                            else:
                                dif=year-int(dif[0])
                            return "<h1>You Have Entered Invalid Data...Or Less Amount Of Data!! of subject <h1>"+sub[j]+" for year "+str(dif) +"</h1> </h1> <a href='/year'>back</a>"
                        avg[i]=((5 * len(e[i]) + 4 * len(v[i]) + 3 * len(g[i]) + 2 * len(a[i]) + len(p[i]))/len(t))
                        abavg[i] = 0
                        if 5 >= avg[i]:
                            abavg[i] = abavg[i]+len(e[i])
                        if 4 >= avg[i]:
                            abavg[i] = abavg[i]+len(v[i])
                        if 3 >= avg[i]:
                            abavg[i] = abavg[i]+len(g[i])
                        if 2 >= avg[i]:
                            abavg[i] = abavg[i]+len(a[i])
                        if 1 >= avg[i]:
                            abavg[i] = abavg[i]+len(p[i])
                        perc = perc+(abavg[i]*100/len(t))

                        # avg[i]=avg[i]*0

                        e[i]=e[i]*0
                        v[i]=v[i]*0
                        g[i]=g[i]*0
                        a[i]=a[i]*0
                        p[i]=p[i]*0
                    per.append(round(perc/10,2))
                    perc = 0

            elif session['yearop'] == "exyear":
                for j in range(0, len(sub)):
                    t=cur.execute("SELECT * FROM indirect WHERE subject='"+sub[j]+"'  and course='"+course+"' and exyear=%s and college=%s",(year,clg,))
                    t=cur.fetchall()
                    for i in range(0, 10):
                        e[i] = cur.execute(
                            "SELECT * FROM indirect WHERE subject='"+sub[j]+"'  and course='"+course+"' and "+q[i]+" = 'Excellent' and exyear=%s and college=%s",(year,clg,))
                        e[i] = cur.fetchall()
                        v[i] = cur.execute(
                            "SELECT * FROM indirect WHERE subject='"+sub[j]+"'  and course='"+course+"' and "+q[i]+" = 'Very Good' and exyear=%s and college=%s",(year,clg,))
                        v[i] = cur.fetchall()
                        g[i] = cur.execute(
                            "SELECT * FROM indirect WHERE subject='"+sub[j]+"'  and course='"+course+"' and "+q[i]+" = 'Good' and exyear=%s and college=%s",(year,clg,))
                        g[i] = cur.fetchall()
                        a[i] = cur.execute(
                            "SELECT * FROM indirect WHERE subject='"+sub[j]+"'  and course='"+course+"' and "+q[i]+" = 'Average' and exyear=%s and college=%s",(year,clg,))
                        a[i] = cur.fetchall()
                        p[i] = cur.execute(
                            "SELECT * FROM indirect WHERE subject='"+sub[j]+"'  and course='"+course+"' and "+q[i]+" = 'Poor' and exyear=%s and college=%s",(year,clg,))
                        p[i] = cur.fetchall()

                        check=(5 * len(e[i]) + 4 * len(v[i]) + 3 * len(g[i]) + 2 * len(a[i]) + len(p[i]))
                        if check == 0:
                            return "<h1>You Have Entered Invalid Data...Or Less Amount Of Data!! of subject <h1>"+sub[j]+" for year "+ str(year)+"</h1> </h1> <a href='/year'>back</a>"
                        avg[i]=((5 * len(e[i]) + 4 * len(v[i]) + 3 * len(g[i]) + 2 * len(a[i]) + len(p[i]))/len(t))
                        abavg[i] = 0
                        if 5 >= avg[i]:
                            abavg[i] = abavg[i]+len(e[i])
                        if 4 >= avg[i]:
                            abavg[i] = abavg[i]+len(v[i])
                        if 3 >= avg[i]:
                            abavg[i] = abavg[i]+len(g[i])
                        if 2 >= avg[i]:
                            abavg[i] = abavg[i]+len(a[i])
                        if 1 >= avg[i]:
                            abavg[i] = abavg[i]+len(p[i])
                        perc = perc+(abavg[i]*100/len(t))

                        # avg[i]=avg[i]*0

                        e[i]=e[i]*0
                        v[i]=v[i]*0
                        g[i]=g[i]*0
                        a[i]=a[i]*0
                        p[i]=p[i]*0
                    per.append(round(perc/10,2))
                    perc = 0
                else:
                    pass
                
            session["inper"]=per
            mysql.connection.commit()
            return redirect('/direct')
        else:
            return redirect('/year')
    else:
         return redirect('/year')



@app.route('/direct')
def coAttainment():
    today = datetime.date.today()
    year=today.year
    if 'subs' in session and 'subadmin' in session:
        cur = mysql.connection.cursor()
        sub = []
        clg=session["col_sr"]
        sub=session["sub_sr_det"]
        course=str(session["course_sr"])

        # important
        percie = []
        perca = []


        if session['yearop'] == "year":
            for i in range(0, len(sub)):
                t=cur.execute("SELECT * FROM direct WHERE subject='"+str(sub[i])+"' and course='"+course+"' and year=%s and college=%s",(year,clg,))
                t=cur.fetchall()
                a= cur.execute("SELECT * FROM direct WHERE subject='"+str(sub[i]) +
                                   "'  and course='"+course+"' and cie1 >= (SELECT AVG(cie1) FROM direct  WHERE subject='"+str(sub[i])+"'  and course='"+course+"') and year=%s and college=%s",(year,clg,))
                a= cur.fetchall()
                b= cur.execute("SELECT * FROM direct WHERE subject='"+str(sub[i]) +
                                   "'  and course='"+course+"' and ca1 >= (SELECT AVG(ca1) FROM direct  WHERE subject='"+str(sub[i])+"'  and course='"+course+"') and year=%s and college=%s",(year,clg,))
                b = cur.fetchall()
                percie.append(round((len(a)*100)/len(t),2))
                perca.append(round((len(b)*100)/len(t),2))
        elif session['yearop'] == "exyear":
            for i in range(0, len(sub)):
                t=cur.execute("SELECT * FROM direct WHERE subject='"+str(sub[i])+"' and course='"+course+"' and exyear=%s and college=%s",(year,clg,))
                t=cur.fetchall()
                a= cur.execute("SELECT * FROM direct WHERE subject='"+str(sub[i]) +
                                   "'  and course='"+course+"' and cie1 >= (SELECT AVG(cie1) FROM direct  WHERE subject='"+sub[i]+"'  and course='"+course+"') and exyear=%s and college=%s",(year,clg,))
                a= cur.fetchall()
                b= cur.execute("SELECT * FROM direct WHERE subject='"+str(sub[i]) +
                                   "'  and course='"+course+"' and ca1 >= (SELECT AVG(ca1) FROM direct  WHERE subject='"+str(sub[i])+"'  and course='"+course+"') and exyear=%s and college=%s",(year,clg,))
                b = cur.fetchall()
                percie.append(round((len(a)*100)/len(t),2))
                perca.append(round((len(b)*100)/len(t),2))
                print((len(a)*100)/len(t))
        session['percie']=percie
        session['perca']=perca
        mysql.connection.commit()
        return redirect('/admin')
    else:
        return redirect('/year')
import numpy as np
@app.route('/admin')
def nobita():
    clg=session["col_sr"]
    today = datetime.date.today()
    year=today.year
    course=str(session["course_sr"])
    if 'subs' in session and 'subadmin' in session:
        # important
        percie=session["percie"]
        perca=session["perca"]
        inper=session["inper"]
        sub=session["sub_sr_det"]

        directLevel=[]
        indirectLevel=[]
        cie_ca=[]

        # it contain coAttainment levels
        coAttainment=[]

        for i in range(0,len(sub)):
            a=(percie[i]+perca[i])/2
            cie_ca.append(round(a,2))

        for i in range(0,len(sub)):
            a=(percie[i]+perca[i])/2
            if a >= 41 and a < 51:
                directLevel.append(1)
            elif a >= 51 and a < 61:
                directLevel.append(2)
            elif a >= 61 :
                directLevel.append(3)
            else:
                directLevel.append(0)

        for i in range(0,len(sub)):
            a=inper[i]
            if a >= 41 and a < 51:
                indirectLevel.append(1)
            elif a >= 51 and a < 61:
                indirectLevel.append(2)
            elif a >= 61 :
                indirectLevel.append(3)
            else:
                indirectLevel.append(0)

        for i in range(0,len(sub)):
            a=((directLevel[i]*80)/100)+((indirectLevel[i]*20)/100)
            coAttainment.append(round(a,2))



        polist=["po1","po2","po3","po4","po5","po6","po7","po8","po9","po10","po11","po12"]
        psolist=["pso1","pso2","pso3","pso4","pso5","pso6","pso7","pso8","pso9","pso10"]
        poe1=[]
        poavg=[]
        cur = mysql.connection.cursor()
        subject_name=cur.execute("select * from subjects where course=%s",(course,))
        subject_name=cur.fetchall()
        print(subject_name)
        print("hi")
        course=str(session["course_sr"])
        if session['yearop'] == 'year':
            for i in range(0,len(sub)):
                pe1=cur.execute("select poavg.val from poavg where subject="+str(sub[i])+" and course="+course+" and year=%s and college=%s",(year,clg,))
                pe1=cur.fetchall()
                poe1 = tuple((float(x[0])) for x in pe1)
                poavg.append(poe1)
        elif session['yearop'] == 'exyear':
            for i in range(0,len(sub)):
                pe1=cur.execute("select poavg.val from poavg where subject="+str(sub[i])+" and course="+course+" and exyear=%s and college=%s",(year,clg,))
                pe1=cur.fetchall()
                poe1 = tuple((float(x[0])) for x in pe1)
                poavg.append(poe1)
        else:
            pass
        print(sub)
        # matrix values of po and pso
        poval=[]
        tt=len(session['pos'])+len(session['psos'])
        if session['yearop'] == 'year':
            for i in range(0,len(sub)):
                pe1=cur.execute("select po.val from po where subject='"+str(sub[i])+"' and course='"+course+"' and year=%s and college=%s",(year,clg,))
                pe1=cur.fetchall()
                co=cur.execute("select * from subjects_cos where subject='"+str(sub[i])+"' and course='"+course+"' and year=%s and college=%s",(year,clg,))
                co=cur.fetchall()
                poe1 = list((int(x[0])) for x in pe1)

                resultTuple = list(poe1[i:i + tt] for i in range(0, len(poe1), tt))
                
                print(poe1)
                poval.append(resultTuple)
        elif session['yearop'] == 'exyear':
            for i in range(0,len(sub)):
                pe1=cur.execute("select po.val from po where subject='"+sub[i]+"' and course='"+course+"' and exyear=%s and college=%s",(year,clg,))
                pe1=cur.fetchall()
                co=cur.execute("select * from subjects_cos where subject='"+sub[i]+"' and course='"+course+"' and year=%s and college=%s",(year,clg,))
                co=cur.fetchall()
                poe1 = list((int(x[0])) for x in pe1)
                resultTuple = list(poe1[i:i + tt] for i in range(0, len(poe1), tt))
                
                print(list[poe1])
                poval.append(resultTuple)
        else:
            pass

        pos=session["pos"]
        psos=session['psos']
        cos=[]
        for i in range(0,len(sub)):
            cur_co=cur.execute('select * from subjects_cos where subject="'+sub[i]+'" and course="'+course+'" and year="'+str(year)+'" and college=%s',(clg,))
            cur_co=cur.fetchall()
            cos.append(cur_co)
        # cos=session['cos']

        a=0
        b=0
        # it contain poAttainment levels
        poAttainment=[]  
        po=session["pos"]
        pso=session["psos"]
        column=len(po)+len(pso)
        for i in range(0,column):
            for j in range(0,len(sub)):
                b=b+poavg[j][i]
                a=a+poavg[j][i]*coAttainment[j]
            if a==0 and b==0:
                c=0.0
            else:
                c=a/b
            poAttainment.append(round(c,2))
            a=0
            b=0
        mysql.connection.commit()
        pocount=len(po)
        psocount=len(pso)
        allForCoAttainment=[sub,perca,percie,cie_ca,directLevel,inper,indirectLevel,coAttainment,subject_name]
        allForPoAttainment=[polist,psolist,poavg,poAttainment,pocount,psocount]
        alldata=[pos,psos,cos,course,year]

        return render_template('copoattainment.html', all=allForCoAttainment,all2=allForPoAttainment,alldata=alldata,poval=poval)
    else:
        return redirect('/year')




    

@app.route('/add_student', methods =['POST'])
def add_student():
    clg=str(session["col_sr"])
    today = datetime.date.today()
    year=today.year
    if request.method=='POST':
        name = request.form['pso']
        course=str(session["course_sr"])
        cursor = mysql.connection.cursor()
        query='INSERT INTO course_psos (pso,course,year,college) VALUES ( %s, %s,%s,%s)'
        val=( name, course ,year ,clg )
        cursor.execute(query,val)
        mysql.connection.commit()
        flash('pso added successufully')
        return redirect(url_for('year'))

@app.route('/add_students', methods =['POST'])
def add_students():
    clg=str(session["col_sr"])
    today = datetime.date.today()
    year=today.year
    if request.method=='POST':
        name = request.form['co']
        course=str(session["course_sr"])
        subject=str(session["sub_sr"])
        cursor = mysql.connection.cursor()
        query='INSERT INTO subjects_cos (co,subject,course,year,college) VALUES ( %s, %s, %s,%s,%s)'
        val=( name, subject, course ,year ,clg )
        cursor.execute(query,val)
        mysql.connection.commit()
        flash('pso added successufully')
        return redirect(url_for('choice'))


@app.route('/delete/<string:nid>')
def delete_student(nid):
    today = datetime.date.today()
    year=today.year
    course=str(session["course_sr"])
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM course_psos WHERE course="'+course+'" and sr ="'+nid+'" and year ="'+str(year)+'"')
    #query='DELETE FROM clg.studentdata WHERE sid = %s'
    #cursor.execute(query,(nid))
    mysql.connection.commit()
    flash('Student Removed Successfully')
    return redirect(url_for('year'))

@app.route('/deletes/<string:nid>')
def delete_students(nid):
    today = datetime.date.today()
    year=today.year
    course=str(session["course_sr"])
    subject=str(session["sub_sr"])
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM subjects_cos WHERE course="'+course+'" and subject="'+subject+'" and sr ="'+nid+'"  and year ="'+str(year)+'"')
    mysql.connection.commit()
    flash('Student Removed Successfully')
    return redirect(url_for('choice'))
    


# @app.route('/delete')
# def delete():
#     cur = mysql.connection.cursor()

#     cur.execute("delete from direct")
#     cur.execute("delete from indirect")
#     cur.execute("delete from po")
#     cur.execute("delete from poavg")
#     mysql.connection.commit()
#     return "<h1>Data has been Deleted</h1> <a href='/'>Home</a>"

    


# @app.route('/indirecte2')
# def ie1():
#     cur = mysql.connection.cursor()
#     # subject=session['subject']
#     subject="f2"
#     table= cur.execute("SELECT * FROM indirect where subject='"+subject+"'")
#     if table > 0:
#         table = cur.fetchall()
#     return render_template('indirect_data.html',tablee=table,subject=subject)

@app.route('/reg')
def reg():
    msg=""
    clg=session["col_sr"]
    if 'pwdmsg' in session:
        msg=session["pwdmsg"]
        session.pop("pwdmsg",None)
    cur = mysql.connection.cursor()
    streams=cur.execute('select * from streams where college=%s',(clg,))
    streams=cur.fetchall()
    mysql.connection.commit()
    return render_template('new_staff.html',streams=streams,msg=msg)

@app.route('/add_course', methods =['POST'])
def add_course():
    msg=""
    clg=session["col_sr"]
    clgname=session["college"]
    if request.method=='POST' and str(request.form["stream"]) != "error":
        stream=str(request.form["stream"])
        course_name = request.form['course_name']
        mail=request.form["mail"]
        user = request.form['user']
        pwd=request.form["pwd"]
        pwdd =request.form["pwdd"]
        no_year=request.form["no_year"]
        if pwd != pwdd :
            session["pwdmsg"]="Password doesn't match"
            return redirect("/reg")

        # subjects=request.form["subjects"]
        field="NULL"
        cursor = mysql.connection.cursor()

        query1='INSERT INTO user (name,email,password,course,field,college) VALUES (%s, %s, %s, %s,%s,%s)'
        val1=(user, mail, pwd, course_name,field ,clg)
        cursor.execute(query1,val1)

        query2='INSERT INTO courses (course,stream,year,field,college) VALUES (%s, %s, %s,%s,%s)'
        val2=(course_name,stream,no_year,field,clg)
        cursor.execute(query2,val2)

        mysql.connection.commit()

        return redirect('/streams/'+clgname+'/'+str(clg)+'')
    else:
        session["pwdmsg"]="please select the Stream"
        return redirect("/reg")

@app.route('/add_subject', methods =['POST'])
def add_user():
    if request.method=='POST':
        cursor = mysql.connection.cursor()
        sub_name = request.form['sub_name']
        sub_code = request.form['sub_code']
        particularYear = session['particularYear']
        course=str(session["course_sr"])
        # stream=session["stream_name"]
        college=str(session["col_sr"])
        subjects=cursor.execute("select subjectcode from subjects where course=%s and college=%s",(course,college))
        subjects=cursor.fetchall()
        subjectcode=tuple((str(x[0])) for x in subjects)
        if sub_code in subjectcode:
            session["submsg"]="Subject Code is already used...!!!"
            return redirect('/subcal/'+course+'/'+particularYear+'')
        query='INSERT INTO subjects (subjectcode,subject,year,course,college) VALUES (%s,%s, %s, %s,%s)'
        val=(sub_code,sub_name,particularYear,course ,college)
        cursor.execute(query,val)
        mysql.connection.commit()
        session["submsg"]="Subject is added successfully...!!!"
        return redirect('/subcal/'+course+'/'+particularYear+'')

@app.route('/adminhome')
def adminhome():
    cur = mysql.connection.cursor()
    streams=cur.execute('select * from streams')
    streams=cur.fetchall()
    mysql.connection.commit()
    return render_template('adminstream.html',data=streams)


@app.route('/adminpo/<string:stream>')
def adminuser(stream):
    session["adminstream"]=stream
    return redirect('/fun/'+stream+'')



# dashboard template
@app.route('/dashboard',methods=['POST','GET'])
def dashboard():
    csr=""
    if "uu" in session and 'csr' in session:
        uu=session["uu"]
        csr=session["csr"]
    else:
        uu=""
    if 'user' in session and session['user'] == uu:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user where field="subadmin" and college=%s',(csr,))
        user = cursor.fetchall()
        cursor.execute('SELECT * FROM user where field="NULL" and college=%s',(csr,))
        notification = cursor.fetchall()
        cursor.execute('SELECT * FROM streams_pos where college=%s',(csr,))
        po = cursor.fetchall()
        cursor.execute('SELECT * FROM streams where college=%s',(csr,))
        streams = cursor.fetchall()
        # cursor.execute('SELECT * FROM streams_pos where stream=%s',(cat,))
        # po = cursor.fetchall()
        
        return render_template('dashboard1.html',user=user,noti=notification,all=po,streams=streams)
    if request.method=='POST':
        username = request.form['uname']
        userpass = request.form['pass']
        cursor = mysql.connection.cursor()
        subadmin_user=cursor.execute('select * from subadmin where email=%s and pass=%s',(username,userpass,))
        subadmin_user = cursor.fetchall()
        if len(subadmin_user) > 0:
            session['user'] = username
            session['upass'] = userpass
            session["uu"]=session['user']
            session["csr"]=subadmin_user[0][0]
            cursor.execute('SELECT * FROM user where field="subadmin" and college=%s',(subadmin_user[0][0],))
            user = cursor.fetchall()
            cursor.execute('SELECT * FROM user where field="NULL" and college=%s',(subadmin_user[0][0],))
            notification = cursor.fetchall()
            cursor.execute('SELECT * FROM streams_pos where college=%s',(subadmin_user[0][0],))
            po = cursor.fetchall()
            cursor.execute('SELECT * FROM streams where college=%s',(subadmin_user[0][0],))
            streams = cursor.fetchall()
            return render_template('dashboard1.html',user=user,noti=notification,all=po,streams=streams)
        else:
            return render_template('error404.html')
    else:
        return render_template('adminlogin.html')

@app.route('/fun/<string:cat>',methods=['POST','GET'])
def fun(cat):
    session['option']=cat
    # if 'user' in session and session['user'] == 'skmv' and cat=="user":
    #     cursor = mysql.connection.cursor()
    #     cursor.execute('SELECT * FROM user where field="subadmin"')
    #     skills = cursor.fetchall()
    #     # print(list(skills))
    #     mysql.connection.commit()
        
    #     return render_template('b6index.html',data=skills,name=cat)

    # if 'user' in session and session['user']=="skmv" and cat=="notification":
    #     cursor = mysql.connection.cursor()
    #     cursor.execute('SELECT * FROM user where field="NULL"')
    #     user = cursor.fetchall()
    #     mysql.connection.commit()
    #     return render_template('b6index.html',data=user,name=cat)
    
    # if 'user' in session and session['user'] == 'skmv' and session["adminstream"] == cat:
    #     cursor = mysql.connection.cursor()
    #     cursor.execute('SELECT * FROM streams_pos where stream=%s',(cat,))
    #     skills = cursor.fetchall()
    #     # print(list(skills))
    #     mysql.connection.commit()
    #     return render_template('b6index.html',data=skills,name=cat)
    return render_template('adminlogin.html')


@app.route('/courseadmin/<int:sr>')
def courseadmin(sr):
    # option=session["option"]
    if session["user"]== "skmv":
        cursor = mysql.connection.cursor()
        cursor.execute("update courses set field='subadmin' where sr=%s",(sr,))
        cursor.execute("update user set field='subadmin' where userid=%s",(sr,))
        # cursor.execute(query)
        mysql.connection.commit()
        flash('User added successfully')
        return redirect('/dashboard')
    else:
        return render_template('adminlogin.html')
    
@app.route('/courseadminreject/<int:sr>')
def courseadminreject(sr):
    # option=session["option"]
    if session["user"]== "skmv":
        cursor = mysql.connection.cursor()
        cursor.execute("delete from courses where sr=%s",(sr,))
        cursor.execute("delete from user where userid=%s",(sr,))
        # cursor.execute(query)
        mysql.connection.commit()
        flash('User added successfully')
        return redirect('/dashboard')
    else:
        return render_template('adminlogin.html')
    


@app.route('/add_userorpo', methods =['POST'])
def add_userorpo():
    # option=session["option"]
    # stream=session["adminstream"]
    if request.method=='POST' and session["option"] == "user":
        name = request.form['name']
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO user () VALUES ( %s)",(name,))
        # cursor.execute(query)
        mysql.connection.commit()
        flash('User added successfully')
        return redirect('/dashboard')

    # if request.method=='POST' and session["option"] == stream:
    #     name = request.form['name']
    #     cursor = mysql.connection.cursor()
    #     cursor.execute("INSERT INTO streams_pos (po,stream) VALUES ( %s,%s)",(name,stream,))
    #     # cursor.execute(query)
    #     mysql.connection.commit()
    #     flash('Pso added successfully')
    #     return redirect('/fun/'+option+'')
    else:
        return render_template('adminlogin.html')



@app.route('/edit_userorpo/<option>/<sid>', methods = ['POST', 'GET'])
def edit_userorpo(option,sid):
    if 'adminstream' in session:
        stream=session["adminstream"]
    if option=="user":
        cursor = mysql.connection.cursor()
        query='SELECT * FROM user WHERE userid = %s'
        cursor.execute(query,(sid,))
        data = cursor.fetchall()
        cursor.close()
        print(data[0])
        return render_template('b6edit.html', student = data,cat=option)

    # if session["adminstream"]== option:
    #     cursor = mysql.connection.cursor()
    #     query='SELECT * FROM streams_pos WHERE sr = %s and stream=%s'
    #     cursor.execute(query,(sid,stream))
    #     data = cursor.fetchall()
    #     cursor.close()
    #     print(data[0])
    #     return render_template('b6edit.html', student = data,cat=option)
    else:
        return render_template('adminlogin.html')
 
@app.route('/update_userorpo/<option>/<nid>', methods=['POST'])
def update_userorpo(option,nid):
    # option=session["option"]
    if 'adminstream' in session:
        stream=session["adminstream"]
    if request.method == 'POST' and option == "user":
        name = request.form['name']
        cursor = mysql.connection.cursor()
        query='UPDATE user SET password=%s where userid=%s '
        cursor.execute(query,(name,nid))
        flash('Password Updated Successfully')
        mysql.connection.commit()
        return redirect('/dashboard')

    # if request.method == 'POST' and session["option"] == stream:
    #     name = request.form['name']
    #     cursor = mysql.connection.cursor()
    #     query='UPDATE streams_pos SET po=%s where sr=%s and stream=%s'
    #     cursor.execute(query,(name,nid,stream))
    #     flash('Pso Updated Successfully')
    #     mysql.connection.commit()
    #     return redirect('/fun/'+option+'')
    else:
        return render_template('adminlogin.html')

@app.route('/delete_userorpo/<option>/<nid>', methods = ['POST','GET'])
def delete_userorpo(option,nid):
    if option == "user":
        cursor = mysql.connection.cursor()
        cursor.execute('DELETE FROM user WHERE userid = %s',(nid,))
        cursor.execute('DELETE FROM courses WHERE sr = %s',(nid,))

        #query='DELETE FROM clg.studentdata WHERE sid = %s'
        #cursor.execute(query,(nid))
        mysql.connection.commit()
        flash('User Removed Successfully')
        return redirect('/dashboard')
    else:
        return redirect('/')
    
    # if session["option"] == stream:
    #     cursor = mysql.connection.cursor()
    #     cursor.execute('DELETE FROM streams_pos WHERE sr = %s and stream=%s',(nid,stream))
    #     #query='DELETE FROM clg.studentdata WHERE sid = %s'
    #     #cursor.execute(query,(nid))
    #     mysql.connection.commit()
    #     flash('Pso Removed Successfully')
    #     return redirect('/fun/'+option+'')

@app.route('/insertpo', methods = ['POST','GET'])
def insertpo():
    if request.method == "POST" and 'po' in request.form and request.form['stream']  != '':
        po = request.form['po']
        stream = request.form['stream']
        print(stream)
        college=session["csr"]
        print(college)
        cursor = mysql.connection.cursor()
        cursor.execute('insert into streams_pos(po,stream,college) values(%s,%s,%s)',(po,stream,college))
        mysql.connection.commit()
        return redirect('/dashboard')
    else:
        return redirect('/dashboard')

@app.route('/userpdf/<choice>')
def userpdf(choice):
    if choice == "user":
        cursor = mysql.connection.cursor()
        cursor.execute('select * from user where field="subadmin"')
        data=cursor.fetchall()
        mysql.connection.commit()
        return render_template('userpdf.html',data=data)
    if choice == "request":
        cursor = mysql.connection.cursor()
        cursor.execute('select * from user where field=""')
        data=cursor.fetchall()
        mysql.connection.commit()
        return render_template('userpdf.html',data=data)
    else:
        return redirect('/dashboard')


@app.route('/admindashboard')
def adminprofile():
    cursor = mysql.connection.cursor()
    verified=cursor.execute('select * from subadmin where verify="YES"')
    # verified
    # =cursor.fetchall()
    mysql.connection.commit()
    return render_template('admindashboard.html')
if __name__ == "__main__":
    app.run(debug=True)