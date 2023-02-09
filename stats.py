def f():
    import tkinter
    import mysql.connector

    sqlobj = mysql.connector.connect(host="localhost", user="root", password="1234")
    pyobj = sqlobj.cursor()
    pyobj.execute('use zzap')
    pyobj.execute('select max(highscores) from zapping')
    higscore_count = pyobj.fetchall()
    pyobj.execute('select max(bomb) from zapping')
    bomb_count = pyobj.fetchall()
    pyobj.execute('select max(games) from zapping')
    games_count = pyobj.fetchall()
    pyobj.execute('select max(virus) from zapping')
    virus_count = pyobj.fetchall()
    pyobj.execute('select max(shots_fired) from zapping')
    shot_fired= pyobj.fetchall()
    pyobj.execute('select max(shots_hit) from zapping')
    shots_hit = pyobj.fetchall()

    # from tkinter import Tk
    root=tkinter.Tk()
    root.title("STATISTICS")
    width= root.winfo_screenwidth()
    height= root.winfo_screenheight()
    root.geometry("%dx%d" % (width,height))

    #CANVAS
    c=tkinter.Canvas(root,height=1000,width=1000,)

    #Games played box
    rect=c.create_rectangle(25,80,380,350,width=4)

    #Powerups box(es)
    rect1=c.create_rectangle(25,380,850,730,width=4)
    rect2=c.create_rectangle(35,445,230,720,width=2)
    rect3=c.create_rectangle(235,720,440,445,width=2)
    rect4=c.create_rectangle(640,720,445,445,width=2)
    rect5=c.create_rectangle(645,720,840,445,width=2)

    #Coins box
    rect=c.create_rectangle(465,350,850,80,width=4)

    #Games played
    games=c.create_text(195,105,text="GAMES",font=("Arial",26,"bold","underline"))
    bombi=c.create_text(195,170,text= str(games_count[0][0]),font=("Arial",50))

    #Coins
    coins=c.create_text(650,105,text="HIGSCORES",font=("Arial",26,"bold","underline"))
    bombz=c.create_text(650,170,text=str(higscore_count[0][0]),font=("Arial",50))

    #Powerups
    bomb=c.create_text(135,465,text="killed by bomb",font=("Arial",15,"bold","underline"))
    bomb_text=c.create_text(135,550,text=str(bomb_count[0][0]),font=("Arial",50))
    virus=c.create_text(340,465,text="killed by virus",font=("Arial",15,"bold","underline"))
    cirus_text=c.create_text(340,550,text=str(virus_count[0][0]),font=("Arial",50))
    speed_up=c.create_text(542,465,text="shots fired",font=("Arial",15,"bold","underline"))
    bomb_te=c.create_text(542,550,text=str(shot_fired[0][0]),font=("Arial",50))
    speed_down=c.create_text(743,465,text="shots hit asteroid",font=("Arial",15,"bold","underline"))
    bombo=c.create_text(743,550,text=str(shots_hit[0][0]),font=("Arial",50))

    c.pack()
    root.mainloop()






