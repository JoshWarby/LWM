import tkinter as tk
import tkinter.scrolledtext as tkst
import tkinter.ttk as ttk
import datetime
import sqlite3
import re
from passlib.hash import sha256_crypt

# Regular expressions used in validating.
dateregex="""(^(((0[1-9]|1[0-9]|2[0-8])[\/](0[1-9]|1[012]))|((29|30|31)[\/](0[13578]|1[02]))|((29|30)[\/](0[4,6,9]|11)))[\/](19|[2-9][0-9])\d\d$)|(^29[\/]02[\/](19|[2-9][0-9])(00|0408||12|16|20|24|28|32|36|40|44|48|52|56|60|64|68|72|76|80|84|88|92|96)$)"""

emailregex="""[^@]+@[^@]+\.[^@]+"""
# Creating database and tables.
conn = sqlite3.connect("data\LWDB.db")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS Events (
    EventID     INTEGER  PRIMARY KEY ASC AUTOINCREMENT,
    Name        VARCHAR,
    Date        VARCHAR,
    VenueID     INTEGER  REFERENCES Venues ( VenueID ),
    TrainerID   INTEGER  REFERENCES Trainers ( TrainerID ),
    TrainerPaid REAL
);
""")
cursor.execute("""CREATE TABLE IF NOT EXISTS Trainers (
    TrainerID    INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    FName        VARCHAR,
    LName        VARCHAR,
    ContactNo    VARCHAR,
    ContactEmail VARCHAR,
    TotalPaid    REAL,
    TotalEvents  INT
);
""")
cursor.execute("""CREATE TABLE IF NOT EXISTS Venues (
    VenueID   INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    Name      VARCHAR,
    Capacity  INTEGER,
    ContactNo VARCHAR
);
""")
cursor.execute("""CREATE TABLE IF NOT EXISTS EventTasks (
    TasksID           INTEGER PRIMARY KEY ASC AUTOINCREMENT
                              REFERENCES Events ( EventID ),
    DeligateListSent  BOOLEAN,
    PaperWorkRecorded BOOLEAN,
    CertificatesSent  BOOLEAN,
    ClientInvoiced    BOOLEAN,
    PayReceived       BOOLEAN
);
""")
conn.commit()

#Tkinter Necessities
class Application(tk.Frame):

    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)

        # Main function foir displaying data into all tables.
        def DisplayData():
        #   HOME PAGE OVERVIEW

            for row in EventTable.get_children():
                EventTable.delete(row)

            cursor.execute(
                "SELECT EventID, Name,Date,VenueID,TrainerID FROM Events")
            EventPulledData = cursor.fetchall()
            for row in EventPulledData:
                EventTable.insert(
                    "", 0, text="Row", values=(row[0], row[1], row[2], row[3], row[4]))

            for row in TrainerTable.get_children():
                TrainerTable.delete(row)

            cursor.execute(
                "SELECT TrainerID, FName,ContactNo,ContactEmail FROM Trainers")
            TrainerPulledData = cursor.fetchall()
            for row in TrainerPulledData:
                TrainerTable.insert(
                    "", 0, text="Row", values=(row[0], row[1], row[2], row[3]))

            for row in VenueTable.get_children():
                VenueTable.delete(row)

            cursor.execute(
                "SELECT VenueID, Name, ContactNo FROM Venues")
            VenuePulledData = cursor.fetchall()
            for row in VenuePulledData:
                VenueTable.insert(
                    "", 0, text="Row", values=(row[0], row[1], row[2]))

            # CountDowns
            for row in TimeTable.get_children():
                TimeTable.delete(row)

            cursor.execute(
                "SELECT EventID,Date FROM Events")
            IDandDate = cursor.fetchall()
            lizt = []
            for i in IDandDate:
                maths = str(datetime.datetime.strptime(
                    i[1], '%d/%m/%Y').date() - datetime.datetime.now().date())[:-9]
                lizt += [(str(i[0]), maths)]

            for row in lizt:
                TimeTable.insert(
                    "", 0, text="Row", values=(row[0], row[1]))

        # MAIN PAGES
            for row in TaskBigTable.get_children():
                TaskBigTable.delete(row)

            cursor.execute(
                "SELECT TasksID,DeligateListSent,PaperWorkRecorded,CertificatesSent,ClientInvoiced,PayReceived FROM EventTasks")
            TasksPulledData = cursor.fetchall()
            TaskList=list(map(list, TasksPulledData))

            lookup = {0: "Incomplete", 1: "Complete"}
            for i, j in enumerate(TaskList):
                for k, l in enumerate(j):
                    if k == 0:
                        continue
                    TaskList[i][k] = lookup[TaskList[i][k]]

            for row in TaskList:
                TaskBigTable.insert(
                    "", 0, text="Row", values=(row[0], row[1], row[2], row[3], row[4], row[5]))

            for row in TrainerBigTable.get_children():
                TrainerBigTable.delete(row)

            cursor.execute(
                "SELECT TrainerID, FName,LName,ContactNo,ContactEmail,TotalPaid,TotalEvents FROM Trainers")
            TrainerPulledData = cursor.fetchall()
            for row in TrainerPulledData:
                TrainerBigTable.insert("", 0, text="Row", values=(
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6]))

            for row in VenueBigTable.get_children():
                VenueBigTable.delete(row)

            cursor.execute(
                "SELECT VenueID, Name, Capacity, ContactNo FROM Venues")
            VenuePulledData = cursor.fetchall()
            for row in VenuePulledData:
                VenueBigTable.insert(
                    "", 0, text="Row", values=(row[0], row[1], row[2], row[3]))

        # Main function for inserting data into the database.
        def InsertData(whichlist):

            for i in TrainerIDEntry_H.get() + VenueIDEntry_H.get():
                if i  not in "0123456789":
                    PopupMessage("ID Wrong Format")
                    return


            if DateEntry.get() != "":
                if not re.match(dateregex, DateEntry.get()):
                    PopupMessage("Date Wrong Format")
                    return

            if ContactEEntry.get() != "":
                if not re.match(emailregex, ContactEEntry.get()):
                    PopupMessage("Email Wrong Format")
                    return

            if TrainerPaidEntry.get() != "":
                try:
                    float(TrainerPaidEntry.get())
                except:
                    PopupMessage("Paid Wrong Format")
                    return


            zero = 0
            dics = {"EventEntryList":
                     [NameEntry, DateEntry, VenueIDEntry_H,
                         TrainerIDEntry_H, TrainerPaidEntry],
                     "TrainerEntryList":
                     [FNameEntry, LNameEntry, ContactNoEntry,
                         ContactEEntry, PaidEntry, zero],
                     "TaskEntryList":
                     [DelVar, PapVar, CertVar, InvVar, PayVar],
                     "VenueEntryList":
                     [VNameEntry, CapacityEntry, ContactVEntry]}
            if whichlist == "EventEntryList":
                Table = "Events"
                DML = "INSERT INTO EventTasks VALUES (NULL,0,0,0,0,0);"
                cursor.execute(DML)
                conn.commit()

            if whichlist == "TrainerEntryList":
                Table = "Trainers"
            if whichlist == "VenueEntryList":
                Table = "Venues"

            DML = "INSERT INTO %s VALUES (NULL" % Table
            for i in dics[whichlist]:
                if i in(NameEntry, FNameEntry, LNameEntry, ContactNoEntry, ContactEEntry, VNameEntry, ContactVEntry, DateEntry):
                    x = '"' + str(i.get()) + '"'
                else:
                    try:
                        x = str(i.get())
                    except:
                        x = str(0)
                DML += "," + x
            DML += ");"

            cursor.execute(DML)
            conn.commit()

            if whichlist == "EventEntryList":
                DML = "UPDATE Trainers SET TotalPaid = TotalPaid + {} WHERE TrainerID = {}".format(
                    TrainerPaidEntry.get(), TrainerIDEntry_H.get())
                cursor.execute(DML)
                conn.commit()
                DML = "UPDATE Trainers SET TotalEvents = TotalEvents + 1 WHERE TrainerID = {}".format(
                    TrainerIDEntry_H.get())
                cursor.execute(DML)
                conn.commit()

            DisplayData()

        # Function for updating tix box values within the database.
        def TickBoxUpdate(ID,Del,Pap,Cert,Inv,Pay):
            if ID != "":
                try:
                    int(ID)
                except:
                    PopupMessage("TaskID Wrong Format")
                    return

            DML = "UPDATE EventTasks SET DeligateListSent ="+str(Del)+", PaperWorkRecorded = "+str(Pap)+", CertificatesSent = "+str(Cert)+",ClientInvoiced = "+str(Inv)+", PayReceived = "+str(Pay)+" WHERE TasksID = "+str(ID)
            cursor.execute(DML)
            conn.commit()
            DisplayData()

        # Function for editing the event table.
        def EditEventTable(ID,Name,Date,VenID,TrainID,TrainPaid):
            if ID != "":
                try:
                    int(ID)
                except:
                    PopupMessage("EventID Wrong Format")
                    return
            DML = "UPDATE Events SET Name = {}, Date = {}, VenueID = {},TrainerID = {},TrainerPaid = {} WHERE EventID = {}".format(('"'+Name+'"'),('"'+Date+'"'),('"'+VenID+'"'),('"'+TrainID+'"'),('"'+TrainPaid+'"'),('"'+ID+'"'),)
            cursor.execute(DML)
            conn.commit()
            DisplayData()
        # Function for editing the venue table.
        def EditVenueTable(ID,Name,Cap,Contact):
            print(ID)
            if ID != "":
                try:
                    int(ID)
                except:
                    PopupMessage("TaskID Wrong Format")
                    return
            DML = "UPDATE Venues SET Name = {}, Capacity = {}, ContactNo = {} WHERE VenueID = {}".format(('"'+Name+'"'),('"'+Cap+'"'),('"'+Contact+'"'),('"'+ID+'"'))
            cursor.execute(DML)
            conn.commit()
            DisplayData()
        # Function for editing the trainer table.
        def EditTrainerTable(ID,FName,LName,ContactE,ContactNo,Paid):
            print(ID)
            if ID != "":
                try:
                    int(ID)
                except:
                    PopupMessage("TrainerID Wrong Format")
                    return
            DML = "UPDATE Trainers SET FName = {}, LName = {}, ContactNo = {}, ContactEmail = {} , TotalPaid = {} WHERE TrainerID = {}".format(('"'+FName+'"'),('"'+LName+'"'),('"'+ContactE+'"'),('"'+ContactNo+'"'),('"'+Paid+'"'),('"'+ID+'"'))
            cursor.execute(DML)
            conn.commit()
            DisplayData()
        # Deletes any data from database.
        def DeleteField(Table,ID):
            if Table == "Events":
                tableID = "EventID"
            if Table == "Trainers":
                tableID = "TrainerID"
            if Table == "Venues":
                tableID = "VenueID"
            DML = "DELETE FROM {} WHERE {} = {}".format(Table,tableID,ID)
            cursor.execute(DML)
            conn.commit()
            if Table == "Events":
                Table = "EventTasks"
                tableID = "TasksID"
                DML = "DELETE FROM {} WHERE {} = {}".format(Table,tableID,ID)
                cursor.execute(DML)
                conn.commit()
            DisplayData()
        # "Forwards" pressing enter to checking password.
        def passcheckenter():
            passcheck(PE1)
        # Used to switch between "Pages"
        def switchto(frame):
            frame.tkraise()
        # Used to create popup messsages, used for errors.
        def PopupMessage(message):
            PopupMessage = tk.Tk()
            PopupMessage.wm_title("ERROR!")
            PopupMessage.configure(background="Yellow4")
            label = tk.Label(
                PopupMessage, bg="Yellow4", text=message, font=("Verdana", 12))
            label.pack(side="top", fill="x", pady=10)
            button1 = ttk.Button(
                PopupMessage, text="Okay", command=lambda: PopupMessage.destroy())
            button1.pack(padx=20, pady=10, side="bottom", fill="x")
            PopupMessage.resizable(width=False, height=False)
            PopupMessage.mainloop()

        # Checks password against encryped password.
        def passcheck(PE1):
            if sha256_crypt.verify( PE1.get(), "$5$rounds=535000$A13jp7js0fJDN97x$fZ9gRkQoRKtreWl/WGa2Bc.eYXYf3aKcnydcll445fB"):
                switchto(HomeFrame)
                TopFrame.grid(row=0, column=0, sticky='news')
            else:
                PopupMessage("Password Incorrect")


        # Colours
        topbarcolour = "white"
        textboxcolour = "#CCFFCC"
        regbgcolour = "#0099CC"
        loginbgcolour = "gray5"

        # Create Frames
        TopFrame = tk.Frame(self, bg=topbarcolour)
        LoginFrame = tk.Frame(
            self, width=875, height=600, bg=loginbgcolour, padx=320, pady=250)
        HomeFrame = tk.Frame(
            self, width=875, height=600, bg=regbgcolour, padx=20, pady=10)
        TasksFrame = tk.Frame(
            self, width=875, height=600, bg=regbgcolour, padx=20, pady=10)
        TrainerFrame = tk.Frame(
            self, width=875, height=600, bg=regbgcolour, padx=20, pady=10)
        VenueFrame = tk.Frame(
            self, width=875, height=600, bg=regbgcolour, padx=20, pady=10)

        # Top Frame Buttons
        ttk.Button(TopFrame,
                   text="Home",
                   command=lambda: switchto(HomeFrame)
                   ).grid(row=0, column=0, sticky='w')
        ttk.Button(TopFrame,
                   text="Tasks",
                   command=lambda: switchto(TasksFrame)
                   ).grid(row=0, column=1, sticky='w')
        ttk.Button(TopFrame,
                   text="Trainers",
                   command=lambda: switchto(TrainerFrame)
                   ).grid(row=0, column=2, sticky='w')
        ttk.Button(TopFrame,
                   text="Venues",
                   command=lambda: switchto(VenueFrame)
                   ).grid(row=0, column=3, sticky='w')

        # Login Frame
        PL1 = tk.Label(LoginFrame, text="Password :")
        PL1.grid(row=1, column=0, sticky="w")
        PE1 = tk.Entry(LoginFrame, bd=2, show="*")
        PE1.focus_set()
        PE1.bind('<Return>', lambda event: passcheck(PE1))
        PE1.grid(row=1, column=1,)

        PassButton1 = ttk.Button(
            LoginFrame, text="Submit", width=10,
            command=lambda: passcheck(PE1))
        PassButton1.grid(row=3, column=1, sticky="s")

        # Home Page


        photo = tk.PhotoImage(file="data\logo.png")
        w = tk.Label(HomeFrame, image=photo, bg=regbgcolour)
        w.photo = photo
        w.place(x=250, y=0)

        EventTable = ttk.Treeview(HomeFrame)
        EventTable['show'] = 'headings'
        EventTable["columns"]=("E ID","Name","Date","V ID","T ID")
        EventTable.column("E ID", width=30)
        EventTable.column("Name", width=60)
        EventTable.column("Date", width=60)
        EventTable.column("V ID", width=30)
        EventTable.column("T ID", width=30)
        EventTable.heading("E ID", text="ID")
        EventTable.heading("Name", text="Name")
        EventTable.heading("Date", text="Date")
        EventTable.heading("V ID", text="V ID")
        EventTable.heading("T ID", text="T ID")
        EventTable.place(x=10, y=110)


        TrainerTable = ttk.Treeview(HomeFrame)
        TrainerTable['show'] = 'headings'
        TrainerTable["columns"]=("T ID","First Name","Mob No",)
        TrainerTable.column("T ID", width=30)
        TrainerTable.column("First Name", width=120)
        TrainerTable.column("Mob No", width=120)
        TrainerTable.heading("T ID", text="ID")
        TrainerTable.heading("First Name", text="First Name")
        TrainerTable.heading("Mob No", text="Mob No")
        TrainerTable.place(x=250, y=110)

        VenueTable = ttk.Treeview(HomeFrame)
        VenueTable['show'] = 'headings'
        VenueTable["columns"]=("V ID","Name","Mob No",)
        VenueTable.column("V ID", width=30)
        VenueTable.column("Name", width=120)
        VenueTable.column("Mob No", width=120)
        VenueTable.heading("V ID", text="V ID")
        VenueTable.heading("Name", text="Name")
        VenueTable.heading("Mob No", text="Mob No")
        VenueTable.place(x=550, y=110)

        TimeTable = ttk.Treeview(HomeFrame, height=8)
        TimeTable['show'] = 'headings'
        TimeTable["columns"]=("Event ID","Time Until",)
        TimeTable.column("Event ID", width=100)
        TimeTable.column("Time Until", width=150)
        TimeTable.heading("Event ID", text="Event ID")
        TimeTable.heading("Time Until", text="Time Until")
        TimeTable.place(x=275, y=400)


        VenueL1 = tk.Label(HomeFrame, text="Venue :", bg=regbgcolour)
        VenueL1.place(x=660, y=90)
        TrainerL1 = tk.Label(HomeFrame, text="Trainer :", bg=regbgcolour)
        TrainerL1.place(x=370, y=90)
        EventL1 = tk.Label(HomeFrame, text="Event :", bg=regbgcolour)
        EventL1.place(x=100, y=90)

        EventIDLabel = tk.Label(
            HomeFrame, text="Event ID (Edits Only)", bg=regbgcolour)
        NameLabel = tk.Label(HomeFrame, text="Event Name", bg=regbgcolour)
        DateLabel = tk.Label(HomeFrame, text="Date (DD/MM/YYYY)", bg=regbgcolour)
        VenueIDLabel = tk.Label(HomeFrame, text="VenueID", bg=regbgcolour)
        TrainerIDLabel = tk.Label(HomeFrame, text="TrainerID", bg=regbgcolour)
        TrainerPaidLabel = tk.Label(
            HomeFrame, text="Trainer Paid (£)", bg=regbgcolour)

        EventIDEntry = tk.Entry(HomeFrame, bd=2, bg=textboxcolour)
        NameEntry = tk.Entry(HomeFrame, bd=2, bg=textboxcolour)
        DateEntry = tk.Entry(HomeFrame, bd=2, bg=textboxcolour)
        VenueIDEntry_H = tk.Entry(HomeFrame, bd=2, bg=textboxcolour)
        TrainerIDEntry_H = tk.Entry(HomeFrame, bd=2, bg=textboxcolour)
        TrainerPaidEntry = tk.Entry(HomeFrame, bd=2, bg=textboxcolour)

        EventIDEntry.place(x=0, y=370)
        NameEntry.place(x=140, y=370)
        DateEntry.place(x=280, y=370)
        VenueIDEntry_H .place(x=420, y=370)
        TrainerIDEntry_H.place(x=560, y=370)
        TrainerPaidEntry.place(x=700, y=370)

        EventIDLabel.place(x=0, y=340)
        NameLabel.place(x=140, y=340)
        DateLabel.place(x=280, y=340)
        VenueIDLabel.place(x=420, y=340)
        TrainerIDLabel.place(x=560, y=340)
        TrainerPaidLabel.place(x=700, y=340)

        EventSubmitButton = ttk.Button(HomeFrame,
                                       text="Submit New Event",
                                       command=lambda: InsertData(
                                           "EventEntryList")
                                       )
        EventSubmitButton.place(x=0, y=400)

        DeleteLabel = tk.Label(HomeFrame, text="Delete Event", bg=regbgcolour)
        DeleteEventEntry = tk.Entry(HomeFrame, bd=2, bg=textboxcolour)
        DeleteEventButon = ttk.Button(HomeFrame, text="Delete Event", command=lambda: DeleteField("Events", DeleteEventEntry.get()))
        DeleteLabel.place(x=0, y=450)
        DeleteEventEntry.place(x=0, y=480)
        DeleteEventButon.place(x=140, y=480)

        EditEventButon = ttk.Button(HomeFrame, text="Edit", command=lambda: EditEventTable(EventIDEntry.get(), NameEntry.get(), DateEntry.get(), VenueIDEntry_H.get(), TrainerIDEntry_H.get(), TrainerPaidEntry.get()))
        EditEventButon.place(x=120, y=400)

        # Trainer Page

        TrainerPageLabel = tk.Label(
            TrainerFrame, text="Trainers", bg=regbgcolour, font=("Helvetica", 30))
        TrainerPageLabel.place(x=300, y=0)

        TrainerIDLabel = tk.Label(
            TrainerFrame, text="Trainer ID (Edits Only)", bg=regbgcolour)
        FNameLabel = tk.Label(TrainerFrame, text="First Name", bg=regbgcolour)
        LNameLabel = tk.Label(TrainerFrame, text="Last Name", bg=regbgcolour)
        ContactNoIDLabel = tk.Label(
            TrainerFrame, text="Contact No", bg=regbgcolour)
        ContactEIDLabel = tk.Label(
            TrainerFrame, text="Contact Email", bg=regbgcolour)
        Paid = tk.Label(
            TrainerFrame, text="Trainer Total Paid (£)", bg=regbgcolour)

        TrainerIDEntry = tk.Entry(TrainerFrame, bd=2, bg=textboxcolour)
        FNameEntry = tk.Entry(TrainerFrame, bd=2, bg=textboxcolour)
        LNameEntry = tk.Entry(TrainerFrame, bd=2, bg=textboxcolour)
        ContactNoEntry = tk.Entry(TrainerFrame, bd=2, bg=textboxcolour)
        ContactEEntry = tk.Entry(TrainerFrame, bd=2, bg=textboxcolour)
        PaidEntry = tk.Entry(TrainerFrame, bd=2, bg=textboxcolour)

        TrainerIDEntry.place(x=0, y=370)
        FNameEntry.place(x=140, y=370)
        LNameEntry.place(x=280, y=370)
        ContactNoEntry.place(x=420, y=370)
        ContactEEntry.place(x=560, y=370)
        PaidEntry.place(x=700, y=370)

        TrainerIDLabel.place(x=0, y=340)
        FNameLabel.place(x=140, y=340)
        LNameLabel.place(x=280, y=340)
        ContactNoIDLabel.place(x=420, y=340)
        ContactEIDLabel.place(x=560, y=340)
        Paid.place(x=700, y=340)

        TrainerSubmitButton = ttk.Button(TrainerFrame,
                                         text="Submit New Trainer",
                                         command=lambda: InsertData(
                                             "TrainerEntryList")
                                         )
        TrainerSubmitButton.place(x=0, y=400)

        DeleteLabelTrainer = tk.Label(
            TrainerFrame, text="Delete Trainer", bg=regbgcolour)
        DeleteTrainerEntry = tk.Entry(TrainerFrame, bd=2, bg=textboxcolour)
        DeleteTrainerButon = ttk.Button(
            TrainerFrame, text = "Delete Trainer", command=lambda: DeleteField("Trainers",DeleteTrainerEntry.get()))
        DeleteLabelTrainer.place(x=0, y=450)
        DeleteTrainerEntry.place(x=0, y=480)
        DeleteTrainerButon.place(x=140, y=480)

        TrainerBigTable = ttk.Treeview(TrainerFrame)
        TrainerBigTable['show'] = 'headings'
        TrainerBigTable["columns"]=("T ID","FName","LName","Contact No","Contact Email","TotalPaid","TotalEvents")

        TrainerBigTable.column("T ID", width=60)
        TrainerBigTable.heading("T ID", text="T ID")
        TrainerBigTable.column("FName", width=120)
        TrainerBigTable.heading("FName", text="FName")
        TrainerBigTable.column("LName", width=120)
        TrainerBigTable.heading("LName", text="LName")
        TrainerBigTable.column("Contact No", width=120)
        TrainerBigTable.heading("Contact No", text="Contact No")
        TrainerBigTable.column("Contact Email", width=120)
        TrainerBigTable.heading("Contact Email", text="Contact Email")
        TrainerBigTable.column("TotalPaid", width=120)
        TrainerBigTable.heading("TotalPaid", text="TotalPaid")
        TrainerBigTable.column("TotalEvents", width=120)
        TrainerBigTable.heading("TotalEvents", text="TotalEvents")
        TrainerBigTable.place(x=0, y=50)


        TrainerEventButon = ttk.Button(TrainerFrame, text="Edit", command=lambda: EditTrainerTable(TrainerIDEntry.get(),FNameEntry.get(),LNameEntry.get(),ContactNoEntry.get(),ContactEEntry.get(),PaidEntry.get()))
        TrainerEventButon.place(x=120, y=400)

        #Tasks Page

        TasksPageLabel = tk.Label(
            TasksFrame, text="Tasks", bg=regbgcolour, font=("Helvetica", 30))
        TasksPageLabel.place(x=300, y=0)

        DelVar = tk.IntVar()
        PapVar = tk.IntVar()
        CertVar = tk.IntVar()
        InvVar = tk.IntVar()
        PayVar = tk.IntVar()

        TaskIDEntry = tk.Entry(TasksFrame, bd=2, bg=textboxcolour)
        DelCheck = tk.Checkbutton(TasksFrame, text="Deligate List", variable=DelVar,
                                  onvalue=1, offvalue=0, height=5,
                                  width=20, bg=regbgcolour, activebackground=textboxcolour)
        PapCheck = tk.Checkbutton(TasksFrame, text="Paper Work", variable=PapVar,
                                  onvalue=1, offvalue=0, height=5,
                                  width=20, bg=regbgcolour, activebackground=textboxcolour)
        CertCheck = tk.Checkbutton(TasksFrame, text="Certificates", variable=CertVar,
                                   onvalue=1, offvalue=0, height=5,
                                   width=20, bg=regbgcolour, activebackground=textboxcolour)
        InvCheck = tk.Checkbutton(TasksFrame, text="Invoice", variable=InvVar,
                                  onvalue=1, offvalue=0, height=5,
                                  width=20, bg=regbgcolour, activebackground=textboxcolour)
        PayCheck = tk.Checkbutton(TasksFrame, text="Payed", variable=PayVar,
                                  onvalue=1, offvalue=0, height=5,
                                  width=20, bg=regbgcolour, activebackground=textboxcolour)

        TaskIDLabel = tk.Label(TasksFrame, text="Event ID", bg=regbgcolour)
        TaskIDLabel.place(x=0, y=375)

        TaskIDEntry.place(x=0, y=400)
        DelCheck.place(x=140, y=370)
        PapCheck.place(x=280, y=370)
        CertCheck.place(x=420, y=370)
        InvCheck.place(x=560, y=370)
        PayCheck .place(x=700, y=370)

        TaskSubmitButton = ttk.Button(TasksFrame,
                                      text="Update Task",
                                      command=lambda: TickBoxUpdate(TaskIDEntry.get(),DelVar.get(), PapVar.get(), CertVar.get(), InvVar.get(), PayVar.get())
                                      )
        TaskSubmitButton.place(x=0, y=450)

        TaskBigTable = ttk.Treeview(TasksFrame)
        TaskBigTable['show'] = 'headings'
        TaskBigTable["columns"]=("E ID","Deligate List","Paper Work","Certificates","Invoiced","Payed")

        TaskBigTable.column("E ID", width=60)
        TaskBigTable.heading("E ID", text="E ID")
        TaskBigTable.column("Deligate List", width=120)
        TaskBigTable.heading("Deligate List", text="Deligate List")
        TaskBigTable.column("Paper Work", width=120)
        TaskBigTable.heading("Paper Work", text="Paper Work")
        TaskBigTable.column("Certificates", width=120)
        TaskBigTable.heading("Certificates", text="Certificates Sent")
        TaskBigTable.column("Invoiced", width=120)
        TaskBigTable.heading("Invoiced", text="Invoiced")
        TaskBigTable.column("Payed", width=120)
        TaskBigTable.heading("Payed", text="Payed")

        TaskBigTable.place(x=75, y=50)


        #Venue Page

        VenuePageLabel = tk.Label(
            VenueFrame, text="Venue", bg=regbgcolour, font=("Helvetica", 30))
        VenuePageLabel.place(x=300, y=0)

        VenueIDLabel = tk.Label(
            VenueFrame, text="Venue ID (Edits Only)", bg=regbgcolour)
        VNameLabel = tk.Label(VenueFrame, text="Venue Name", bg=regbgcolour)
        CapacityLabel = tk.Label(VenueFrame, text="Capacity", bg=regbgcolour)
        VContactNoIDLabel = tk.Label(
            VenueFrame, text="Contact No", bg=regbgcolour)

        VenueIDEntry = tk.Entry(VenueFrame, bd=2, bg=textboxcolour)
        VNameEntry = tk.Entry(VenueFrame, bd=2, bg=textboxcolour)
        CapacityEntry = tk.Entry(VenueFrame, bd=2, bg=textboxcolour)
        ContactVEntry = tk.Entry(VenueFrame, bd=2, bg=textboxcolour)

        VenueIDEntry.place(x=0, y=370)
        VNameEntry.place(x=140, y=370)
        CapacityEntry.place(x=280, y=370)
        ContactVEntry.place(x=420, y=370)

        VenueIDLabel.place(x=0, y=340)
        VNameLabel.place(x=140, y=340)
        CapacityLabel.place(x=280, y=340)
        VContactNoIDLabel.place(x=420, y=340)

        VenueSubmitButton = ttk.Button(VenueFrame,
                                       text="Submit New Venue",
                                       command=lambda: InsertData(
                                           "VenueEntryList")
                                       )
        VenueSubmitButton.place(x=0, y=400)

        DeleteLabelVenue = tk.Label(
            VenueFrame, text="Delete Venue", bg=regbgcolour)
        DeleteVenueEntry = tk.Entry(VenueFrame, bd=2, bg=textboxcolour)
        DeleteVenueButon = ttk.Button(VenueFrame, text="Delete Venue", command=lambda: DeleteField("Venues", DeleteVenueEntry.get()))
        DeleteLabelVenue.place(x=0, y=450)
        DeleteVenueEntry.place(x=0, y=480)
        DeleteVenueButon.place(x=140, y=480)

        VenueBigTable = ttk.Treeview(VenueFrame)
        VenueBigTable['show'] = 'headings'
        VenueBigTable["columns"] = ("V ID", "Name", "Capacity", "ContactNo")

        VenueBigTable.column("V ID", width=60)
        VenueBigTable.heading("V ID", text="V ID")
        VenueBigTable.column("Name", width=120)
        VenueBigTable.heading("Name", text="Name")
        VenueBigTable.column("Capacity", width=120)
        VenueBigTable.heading("Capacity", text="Capacity")
        VenueBigTable.column("ContactNo", width=120)
        VenueBigTable.heading("ContactNo", text="ContactNo")

        VenueBigTable.place(x=175, y=50)

        VenueEventButon = ttk.Button(VenueFrame, text="Edit", command=lambda: EditVenueTable(VenueIDEntry.get(), VNameEntry.get(), CapacityEntry.get(), ContactVEntry.get()))
        VenueEventButon.place(x=120, y=400)

        #Setup

        LoginFrame.grid(row=1, column=0, sticky='news')
        HomeFrame.grid(row=1, column=0, sticky='news')
        TasksFrame.grid(row=1, column=0, sticky='news')
        TrainerFrame.grid(row=1, column=0, sticky='news')
        VenueFrame.grid(row=1, column=0, sticky='news')
        self.grid()

        switchto(LoginFrame)
        DisplayData()

#Tkinter Necessities
root = tk.Tk()
root.title("LW Manager")
root.iconbitmap('data\LWicon.ico')
root.resizable(width=False, height=False)
Application(root).mainloop()
root.destroy
