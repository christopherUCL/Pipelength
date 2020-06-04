# 1. API call to fluid properties website
def calculatePipeLength():
    from selenium import webdriver
    from selenium.webdriver.support.ui import Select
    from flask import request
    import math
    import os    
    WaterTemperature = "42.5"
    AtmosphericPressure = "100"
    url = 'https://preview.irc.wisc.edu/properties/'

    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")

    driver=webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),chrome_options=chrome_options)

    #driver = webdriver.Chrome(executable_path="chromedriver.exe")

    #Select radiobutton
    driver.get(url)
    driver.find_element_by_id('International').click()

    #select drop down
    select = Select(driver.find_element_by_name('fluid'))
    select.select_by_visible_text('Water')

    #Select temperature and abs pressure dropdowns
    select = Select(driver.find_element_by_name('parameter1')) #temperature
    select.select_by_visible_text('Temperature')

    select = Select(driver.find_element_by_name('parameter2')) #pressure
    select.select_by_visible_text('Abs. Pressure')

    #Enter values for temperature and pressure
    driver.find_element_by_name("state1").send_keys(WaterTemperature)
    driver.find_element_by_name("state2").send_keys(AtmosphericPressure)

    #click the "calculate properties" button
    driver.find_element_by_name("calculate").click()


    table1 = driver.find_element_by_xpath("//table/tbody/tr/td/form/table/tbody/tr[3]/td[2]/table/tbody/tr[2]/td[2]").text
    table2 = driver.find_element_by_xpath("//table/tbody/tr/td/form/table/tbody/tr[3]/td[2]/table/tbody/tr[4]/td").text
    table3 = driver.find_element_by_xpath("//table/tbody/tr/td/form/table/tbody/tr[3]/td[2]/table/tbody/tr[4]/td[2]").text


    # 2. Retrieve response of water properties

    print(table1)
    f = table1.split('\n')
    f[0].split(': ')[1].strip(' ')

    print(table2)
    f = table2.split('\n')
    density = f[2].split(': ')[1].split(' ')[0].strip(' ')
    heat_capacity = f[9].split(': ')[1].split(' ')[0].strip(' ')
    print(density)
    print(heat_capacity)

    print(table3)
    f = table3.split('\n')
    viscosity = f[3].split(': ')[1].split(' ')[0].strip(' ')
    thermal_conductivity = f[4].split(': ')[1].split(' ')[0].strip(' ')
    prandtl = f[5].split(': ')[1].split(' ')[0].strip(' ')
    print(viscosity)
    print(thermal_conductivity)
    print(prandtl)

    density = int(density)
    heat_capacity = int(heat_capacity)
    viscosity = int(viscosity)


    thermal_conductivity = float(thermal_conductivity)
    prandtl = float(prandtl)

    density_per_L = density/1000
    dynamic_viscosity = (viscosity/1000000)/(density)

    foul_i = 0.0004
    foul_o = 0.0008

    # 3. Request user input for other parameters

    pipe_inner_dia = float(request.form['pipe_inner_dia'])
    pipe_outer_dia = float(request.form['pipe_outer_dia'])
    Q_dot_watts =    float(request.form['Q_dot_watts'])
    h_out =          float(request.form['h_out'])
    K_wall =         float(request.form['K_wall'])
    V_dot_LtrPerMin =        float(request.form['V_dot_LtrPerMin'])
    Boiler_hotWater_temp =   float(request.form['Boiler_hotWater_temp'])
    Finaltemp_of_coldFluid = float(request.form['Finaltemp_of_coldFluid'])
    init_coldFluidTemp =     float(request.form['init_coldFluidTemp'])


    V_dot_LPS = V_dot_LtrPerMin/60
    inner_pipeArea = 3.142*pipe_inner_dia*pipe_inner_dia*0.25
    mass_dot = V_dot_LPS*density_per_L
    velocity = mass_dot/(density*inner_pipeArea)
    reynold = velocity*pipe_inner_dia/dynamic_viscosity
    deltaT_coldFluid = Finaltemp_of_coldFluid - init_coldFluidTemp

    UFH_deltaT = Q_dot_watts/(mass_dot*heat_capacity)
    exitTempofBoilerwater = Boiler_hotWater_temp - UFH_deltaT

    if ((deltaT_coldFluid < 0)|(exitTempofBoilerwater<=Finaltemp_of_coldFluid)):
        print("temperature errors")
        pipelength = 0
        return pipelength
        

    deltaT1 = Boiler_hotWater_temp - Finaltemp_of_coldFluid
    deltaT2 = exitTempofBoilerwater - init_coldFluidTemp
    delta_T_lmcf = ((deltaT1-deltaT2)/(math.log(deltaT1/deltaT2)))

    if reynold >= 4000:
        nusselt = 0.023*(reynold**0.8)*(prandtl**0.4)
    else:
        nusselt = 4.36
    h_i = nusselt*thermal_conductivity/(pipe_inner_dia)

    UAs = Q_dot_watts/(0.85*delta_T_lmcf)

    R_tot = 1/UAs

    R_i = 1/(h_i*(math.pi)*pipe_inner_dia)
    R_foul_i = foul_i/((math.pi)*pipe_inner_dia)
    R_wall = (math.log(pipe_outer_dia/pipe_inner_dia))/(2*(math.pi)*K_wall)
    R_foul_o = foul_o/((math.pi)*pipe_outer_dia)
    R_o = 1/(h_out*(math.pi)*pipe_outer_dia)

    R_all = R_i+R_foul_i+R_wall+R_foul_o+R_o

    pipelength = R_all/R_tot
    print("Pipe length is {}".format(pipelength))
    return pipelength