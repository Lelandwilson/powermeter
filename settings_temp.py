@app.route('/settings', methods=['GET', 'POST'])
def settings():
    form1 = SettingsForm1()
    form_Nw = NetworkForm()

    if request.method == 'POST':
        if form1.S1.data == '': form1.S1.data = SensorLabels[1][1]
        if form1.S2.data == '': form1.S2.data = SensorLabels[1][2]
        if form1.S3.data == '': form1.S3.data = SensorLabels[1][3]
        if form1.S4.data == '': form1.S4.data = SensorLabels[1][4]
        if form1.S5.data == '': form1.S5.data = SensorLabels[1][5]
        if form1.S6.data == '': form1.S6.data = SensorLabels[1][6]

        if form_Nw.interface == '': form_Nw.interface.data = INTERFACE
        if form_Nw.ip == '': form_Nw.ip.data = IP
        if form_Nw.port == '': form_Nw.port.data = str(PORT)
        if form_Nw.router == '': form_Nw.router.data = ROUTER
        if form_Nw.DNS == '': form_Nw.DNS.data = DNS
        if form_Nw.SSID == '': form_Nw.SSID.data = SSID
        if form_Nw.password == '': form_Nw.password.data = PASSWORD

        if form1.validate() == False:
            flash('All fields are required.', 'danger')
            return render_template('settings3.html', form_1=form1, form_Nw=form_Nw)

        else:
            # if form completed correctly:
            SensorLabels[1][1] = str(form1.S1.data)
            SensorLabels[1][2] = str(form1.S2.data)
            SensorLabels[1][3] = str(form1.S3.data)
            SensorLabels[1][4] = str(form1.S4.data)
            SensorLabels[1][5] = str(form1.S5.data)
            SensorLabels[1][6] = str(form1.S6.data)

            # Interface = str(form_Nw.interface.data)
            # IPaddress = str(form_Nw.ip.data)
            # Port = int(form_Nw.port.data)
            # Router = str(form_Nw.router.data)
            # DNS = str(form_Nw.DNS.data)
            # SSID = str(form_Nw.SSID.data)
            # Password =  str(form_Nw.password.data)

            # print(SensorLabels)
            # return render_template('main3.html')

            # return redirect(url_for('index'))
            flash('Unit Names- Saved', 'success')
            # saveLables()
            return render_template('settings3.html', form_1=form1, form_Nw=form_Nw)
            # return redirect(url_for('index'))
    elif request.method == 'GET':

        form1.U1_S1.data = SensorLabels[1][1]
        form1.U1_S2.data = SensorLabels[1][2]
        form1.U1_S3.data = SensorLabels[1][3]
        form1.U1_S4.data = SensorLabels[1][4]
        form1.U1_S5.data = SensorLabels[1][5]
        form1.U1_S6.data = SensorLabels[1][6]

        form_Nw.interface.data = INTERFACE
        form_Nw.ip.data = IP
        form_Nw.port.data = str(PORT)
        form_Nw.router.data = ROUTER
        form_Nw.DNS.data = DNS
        form_Nw.SSID.data = SSID
        form_Nw.password.data = PASSWORD

        return render_template('settings3.html', form_1=form1, form_Nw=form_Nw)
