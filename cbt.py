import sys
from time import time, sleep
from threading import Thread
import json
import os


from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton,QRadioButton, QVBoxLayout,\
                               QDesktopWidget, QButtonGroup, QHBoxLayout, QGroupBox, QGridLayout, QLineEdit, \
                                       QCheckBox, QMessageBox, QTextEdit)
from PyQt5.QtCore import (Qt, QUrl, QVariant)
from  PyQt5.QtGui import (QFont, QPixmap, QTextCursor, QTextImageFormat, QImage, QCursor, QImageReader, QTextDocument)

from make_question import Question

with open ('cbt.css', 'r') as obj:
    style_sheet =obj.read()


class CBT(QWidget):
        def __init__(self):
                super().__init__()

                self.prepareQuestions()
                self.initializeUi()
                
                     
        def initializeUi(self):
                #create a list of several QWidget items
                self.qwidgets = []
                for i in range(len(self.prepared_questions)+1):
                        obj = QWidget()
                        obj.setMinimumSize(1080, 750)
                        obj.setMaximumSize(1080, 750)
                        self.qwidgets.append(obj)


                #Question interface
                self.interface = QWidget()
                self.interface.setObjectName('main1')

                #Proceed interface
                self.proceed = QWidget()
                self.proceed.setObjectName('main')



                # generate empty list of all the options chosen by the user
                self.choices = ['null' for i in range(len(self.prepared_questions))] 
                
                '''
                qindex is like a counter that i use to flip to frames, questions, options and user choices
                '''
                self.qindex = 0

                self.attempted = True

                #fix window dimensions
                self.setFixedSize(1100,800)
                self.setWindowFlags(Qt.FramelessWindowHint)
                #position app to be at center of the desktop screen
                desktop = QDesktopWidget().screenGeometry()
                screen_width = desktop.width()
                screen_height = desktop.height()
                x = (screen_width - self.width())/2
                y = (screen_height - self.height())/2
                self.move(x,y)

                #set the window default layout
                self.layout = QVBoxLayout()
                self.setLayout(self.layout)

                #set a state to control timer
                self.state = True

                self.test_over = False
                

                self.login()

                #make window visible
                self.show()


        def prepareQuestions(self):
                filepath1 = 'questions.txt'
                filepath2 = 'options.txt'
                data = Question(filepath1, filepath2)

                self.prepared_questions = data.sortQuestion()
                self.prepared_options = data.sortOption()


        def setUpProceed(self):
                self.finish = False
                frame = self.qindex

                #Label for showing time counter
                self.time_display = QLabel("00:00:00")
                self.time_display.setFont(QFont('Ariel', 20))
                self.time_display.setMaximumHeight(30)
                self.time_display.setMinimumHeight(30)
                self.time_display.setMinimumWidth(160)
                self.time_display.setMaximumWidth(160)
                self.time_display.setObjectName('main')
                
                #text on screen
                title = QLabel()
                title.setText("COMPUTER BASED TEST")
                title.setFont(QFont('Cambria', 40))
                title.setAlignment(Qt.AlignCenter)
                title.setObjectName('main')

                button = QPushButton('PROCEED')
                button.setFont(QFont('Ariel', 17))
                button.resize(10,4)
                button.clicked.connect(self.navigateToNextTest)

                #creat home widget layout
                h_widget = QVBoxLayout()
                h_widget.setSpacing(30)

                #add widgets to home widget layout
                h_widget.addStretch(6)
                h_widget.addWidget(title)
                h_widget.addStretch()
                h_widget.addWidget(button, alignment= Qt.AlignCenter)
                h_widget.addStretch(8)

                #assihn layout to home widget
                self.qwidgets[self.qindex].setLayout(h_widget)

                self.info_screen.hide()
                #add the widget to the window default layout
                self.layout.addWidget(self.qwidgets[self.qindex])
                self.qindex += 1


        def login(self):
                if self.test_over:
                        self.finish_screen.hide()
                self.text = ''
                self.login_screen = QWidget()
                self.login_screen.setObjectName('main')
                self.login_screen.setMaximumHeight(750)
                self.login_screen.setMinimumHeight(750)
                self.login_screen.setMinimumWidth(1050)
                self.login_screen.setMaximumWidth(1050)

                title = QLabel()
                title.setText("LOGIN")
                title.setFont(QFont('Cambria', 40))

                self.username_entry = QLineEdit(self)
                self.username_entry.resize(150,70)
                self.username_entry.setPlaceholderText('User Name')
                self.username_entry.setObjectName('login')

                self.password_entry = QLineEdit(self)
                self.password_entry.resize(150,70)
                self.password_entry.setPlaceholderText('Password')
                self.password_entry.setEchoMode(QLineEdit.Password)
                self.password_entry.setObjectName('login')

                self.password_cb = QCheckBox(self)
                self.password_cb.setText('Show Password')

                self.login_button = QPushButton('Login')
                self.login_button.clicked.connect(self.verify_login)
                
                frame = QGroupBox()
                frame.setObjectName('question')
                frame.setMaximumHeight(400)
                frame.setMinimumHeight(400)
                frame.setMinimumWidth(400)
                frame.setMaximumWidth(400)
                frame_layout = QVBoxLayout()
                frame_layout.addWidget(title, alignment=Qt.AlignCenter)
                frame_layout.addStretch()
                frame_layout.addWidget(self.username_entry)
                frame_layout.addWidget(self.password_entry)
                frame_layout.addWidget(self.password_cb)
                frame_layout.addStretch()
                frame_layout.addWidget(self.login_button , alignment=Qt.AlignCenter)

                frame.setLayout(frame_layout)

                login_screen_layout = QVBoxLayout()
                login_screen_layout.addWidget(frame, alignment=Qt.AlignCenter)

                self.login_screen.setLayout(login_screen_layout)
                
                
                self.layout.addWidget(self.login_screen, alignment= Qt.AlignCenter)


        def verify_login(self):
                username = self.username_entry.text()
                password = self.password_entry.text()
                with open('login.json', 'r') as obj:
                        check = json.load(obj)
                if (username, password) in check.items():
                        self.userInformation()
                else:
                        QMessageBox.warning(self.login_screen, "Error", "Username or password incorrect", QMessageBox.Close, QMessageBox.Close)
                        self.password_entry.clear()
                        self.username_entry.clear()
                        self.username_entry.setFocus()


        def navigateToNextTest(self):
                if self.state:
                        self.tr =Thread(target = self.timer)
                        self.tr.start()
                        self.state = False
                if self.text:
                        self.qwidgets[self.qindex].hide()
                        self.testOver()
                        return None
                try:
                        if self.attempted:
                                self.frame = self.qindex
                                pick = self.prepared_questions[self.qindex]
                                question_no = QLabel()
                                question_no.setFont(QFont('Ariel', 15))
                                question_no.setText(pick[0].strip('\n'))
                                question_no.setObjectName('q_number')
                                question_no.setMaximumHeight(30)

                                question = QTextEdit()
                                question.setObjectName('question')
                                question_text = self.arrangeText(pick[1])
                                question.setText(question_text)
                                question.setFont(QFont('Ariel', 15))
                                #question.setWordWrap(True)
                                question.setReadOnly(True)
                                question.setMaximumSize(720, 350)
                                question.setMinimumSize(720, 350)
                                
                                

                                option_group = QButtonGroup(self)
                                
                                question_gb = QGroupBox()
                                question_gb.setObjectName('question')
                                question_gb.setTitle('')
                                question_gb.setFont(QFont('Ariel', 15))
                                question_gb.resize(500,500)
                                question_gb.setMaximumSize(750,400)
                                question_gb.setMinimumSize(750, 400)
                                
                                question_layout = QVBoxLayout()
                                #question_layout.addWidget(question, alignment=Qt.AlignTop)
                                if len(pick) == 3:
                                        file_path = pick[2]
                                        image_url = QUrl(file_path)
                                        image = QImage(QImageReader(file_path).read())

                                        question.document().addResource(QTextDocument.ImageResource,image_url,QVariant(image))

                                        image_format = QTextImageFormat()
                                        image_format.setWidth(image.width())
                                        image_format.setHeight(image.height())
                                        image_format.setName(image_url.toString())

                                        text_cursor = question.textCursor()
                                        text_cursor.movePosition(QTextCursor.End,QTextCursor.MoveAnchor)
                                        text_cursor.insertImage(image_format)

                                question_layout.addWidget(question, alignment=Qt.AlignTop)       

                                question_gb.setLayout(question_layout)
                                
                                rb_box = QVBoxLayout()
                                rb_box.setSpacing(2)
                                rb_box.setObjectName('options')
                                rb_box.setAlignment(Qt.AlignCenter)
                                


                                options = self.prepared_options[self.qindex]
                                
                                for items in options:
                                        rb = QRadioButton(items.strip('\n'), self)
                                        rb.setFont(QFont('Ariel', 15))
                                        rb.setObjectName('options')
                                        rb_box.addWidget(rb)
                                        option_group.addButton(rb)
                                option_group.buttonClicked.connect(self.getChoice)
                                
                                
                                
                                button_next = QPushButton('Next')
                                button_next.setObjectName('next')
                                button_next.resize(10,5)
                                button_next.clicked.connect(self.navigateToNextTest)

                                button_previous = QPushButton('Previous')
                                button_previous.setObjectName('next')
                                button_previous.resize(10,5)
                                button_previous.clicked.connect(self.navigateToPreviousTest)
                        

                                container = QGridLayout()
                                container.setContentsMargins(5,5,5,5)
                                #container.setSpacing(2)


                                container.addWidget(question_no, 0, 0,alignment=Qt.AlignLeft  )
                                container.addWidget(self.time_display,0,4, alignment=Qt.AlignRight)
                                container.addWidget(question_gb, 1 , 1, 1, 3,)
                                container.addLayout(rb_box, 3, 2)
                                container.addWidget(button_next, 4, 4, 1, 1)
                                if (self.qindex == 1):
                                        pass
                                else:
                                        container.addWidget(button_previous, 4, 0, 1, 1)
                                if self.qindex == (len(self.prepared_questions)- 1):
                                        button_next.setText('Submit')

                                self.qwidgets[self.qindex].setLayout(container)
                                self.qwidgets[self.qindex].setObjectName('main')
                                
                                self.qwidgets[self.qindex-1].hide()
                                self.layout.addWidget(self.qwidgets[self.qindex])
                                
                                
                                self.qindex +=1
                                
                                self.check = self.qindex
                                
                        else:
                                if self.qindex == self.check-1:
                                        self.attempted = True
                                else:
                                        self.attempted = False
                                self.qwidgets[self.qindex-1].hide()
                                self.qwidgets[self.qindex].show()
                                self.qindex += 1
                                self.frame += 1
                                

                except IndexError:
                        print("Questions Exhausted")
                        done = QMessageBox.question(self.qwidgets[self.qindex],"Submit Test?", "Are you sure you want to submit the test?", QMessageBox.No | QMessageBox.Yes, QMessageBox.No)
                        if done == QMessageBox.Yes:
                                self.testOver()
                        else:
                                pass


        def navigateToPreviousTest(self):
                
                try:
                        self.attempted = False
                        self.qwidgets[self.qindex-1].hide()
                        self.qwidgets[self.qindex-2].show()
                        self.qindex -= 1
                        self.frame -= 1
                        print(self.qindex)
                        
                except IndexError:
                        print("Questions Exhausted")
                        self.testOver()

        
        def getChoice(self, obj):
                choice = obj.text()
                self.choices[self.frame] = choice
                print(self.choices)


        def timer(self):
                #h, m, s = 0, 0, 0
                for m in range(59, -1, -1):
                        for s in range(59, -1, -1):
                                text = '00:{0}:{1}'.format(m,s)
                                if text == "00:0:0":
                                        self.text = text
                                        self.time_display.setText("Time Elapsed")
                                        break
                                if self.finish:
                                        break
                                else:
                                        self.time_display.setText(text)
                                sleep(1)
                

        def testOver(self):
                self.finish_screen = QWidget()
                self.finish_screen.setObjectName('main')
                self.finish_screen.setMaximumHeight(650)
                self.finish_screen.setMinimumHeight(650)
                self.finish_screen.setMinimumWidth(950)
                self.finish_screen.setMaximumWidth(950)

                finish_scr_layout = QVBoxLayout()

                title = QLabel("Test Completed")
                title.setFont(QFont('Cambria', 40))
                title.setObjectName('main')

                info = QLabel("Your Response Has Been Submitted")
                info.setFont(QFont('Cambria', 30))
                info.setObjectName('main')

                button = QPushButton("RETURN HOME")
                button.clicked.connect(self.login)

                finish_scr_layout.addWidget(title, alignment= Qt.AlignCenter)
                finish_scr_layout.addWidget(info, alignment= Qt.AlignCenter)
                finish_scr_layout.addWidget(button)

                self.finish_screen.setLayout(finish_scr_layout)
                self.index = -2
                self.qwidgets[self.index].hide()
                self.layout.addWidget(self.finish_screen, alignment= Qt.AlignCenter)

                self.qindex = 0

                self.test_over = True

                self.state = True
                
                self.finish = True
                self.tr.join()
                self.sendResponse()
                #create a list of several QWidget items
                self.qwidgets = []
                for i in range(len(self.prepared_questions)+1):
                        obj = QWidget()
                        self.qwidgets.append(obj)
                
                # generate empty list of all the options chosen by the user
                self.choices = ['null' for i in range(len(self.prepared_questions))] 


        def userInformation(self):
                self.info_screen = QWidget()
                self.info_screen.setObjectName('main')
                self.info_screen.setMaximumHeight(750)
                self.info_screen.setMinimumHeight(750)
                self.info_screen.setMinimumWidth(1050)
                self.info_screen.setMaximumWidth(1050)
                
                title = QLabel()
                title.setText("WELCOME TO CARINA COMMON ENTRANCE EXAMINATION")
                title.setFont(QFont('Cambria', 25))
                title.setObjectName('main')
                
                school_logo = self.loadImage('carina.png')
                title1 = QLabel()
                title1.setText("SUBMIT YOUR DETAILS")
                title1.setFont(QFont('Cambria', 20))
                title1.setObjectName('q_number')

                self.surname_entry = QLineEdit(self)
                self.surname_entry.resize(150,70)
                self.surname_entry.setPlaceholderText('Surname Name')
                self.surname_entry.setObjectName('login')


                self.firstname_entry = QLineEdit(self)
                self.firstname_entry.resize(150,70)
                self.firstname_entry.setPlaceholderText('First Name')
                self.firstname_entry.setObjectName('login')

                self.middlename_entry = QLineEdit(self)
                self.middlename_entry.resize(150,70)
                self.middlename_entry.setPlaceholderText('Middle Name')
                self.middlename_entry.setObjectName('login')



                submit_button = QPushButton('Submit')
                submit_button.clicked.connect(self.verifySaveUserInfo)
                
                frame = QGroupBox()
                frame.setObjectName('question')
                frame.setMaximumHeight(400)
                frame.setMinimumHeight(400)
                frame.setMinimumWidth(400)
                frame.setMaximumWidth(400)
                frame_layout = QVBoxLayout()
                frame_layout.addWidget(title1, alignment=Qt.AlignCenter)
                frame_layout.addStretch()
                frame_layout.addWidget(self.surname_entry)
                frame_layout.addWidget(self.firstname_entry)
                frame_layout.addWidget(self.middlename_entry)
                frame_layout.addStretch()
                frame_layout.addWidget(submit_button, alignment=Qt.AlignCenter)
                
                frame.setLayout(frame_layout)

                info_screen_layout = QVBoxLayout()
                info_screen_layout.addWidget(school_logo, alignment=Qt.AlignCenter | Qt.AlignTop )
                info_screen_layout.addWidget(title, alignment=Qt.AlignCenter | Qt.AlignTop)
                info_screen_layout.addWidget(frame, alignment=Qt.AlignCenter)

                self.info_screen.setLayout(info_screen_layout)

                self.login_screen.hide()
                
                
                self.layout.addWidget(self.info_screen, alignment= Qt.AlignCenter)
                
        
        def loadImage(self, image_path):
                try:
                        with open(image_path):
                                image = QLabel(self)
                                pixmap = QPixmap(image_path)
                                image.setPixmap(pixmap.scaled(100,100, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))
                                return image
                except FileNotFoundError:
                        print('image not found')
        

        def verifySaveUserInfo(self):
                surname = self.surname_entry.text()
                firstname = self.firstname_entry.text()
                lastname = self.middlename_entry.text()

                if surname and firstname and lastname:
                        name = '{} {} {}'.format(surname, firstname, lastname)
                        self.choices[0] = name
                        self.setUpProceed()

                else:
                        QMessageBox.warning(self.info_screen, 'Incomplete!','You must fill all the fields!', QMessageBox.Ok)


        def sendResponse(self):
                #file_name = r'C:\Users\{}'.format(self.choices[0].strip(' '))
                file_name = os.getcwd()
                file_name = file_name + r'\results.txt'
                responses = ''
                
                try:
                        with open(file_name, 'r') as obj:
                                old_response = obj.readlines()
                        for i in range(len(self.choices)):
                                responses = responses + old_response[i].strip('\n') +','+self.choices[i] + '\n'
                        with open(file_name, 'w') as obj:
                                obj.write(responses)
                                print('file saved!')
                except FileNotFoundError:
                        for i in self.choices:
                                responses = responses + i +'\n'
                        with open(file_name, 'w') as obj:
                                obj.write(responses)
                                print('file saved!')


        def arrangeText(self, text):
                if '&' in text:
                        return text.replace('&','\n')
                else:
                        return text
                
                
         
if __name__ == "__main__":
        app = QApplication(sys.argv)
        app.setStyleSheet(style_sheet)
        window = CBT()
        sys.exit(app.exec_())