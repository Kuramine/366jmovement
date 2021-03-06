def get_distance():

    if GPIO.input (GPIO_ECHO):                                          # If the 'Echo' pin is already high
        return (1000)                                                   # then exit with 1000 (sensor fault)

    distance = 0                                                        # Set initial distance to zero

    GPIO.output (GPIO_TRIGGER,False)                                    # Ensure the 'Trig' pin is low for at
    time.sleep (0.05)                                                   # least 50mS (recommended re-sample time)

    GPIO.output (GPIO_TRIGGER,True)                                     # Turn on the 'Trig' pin for 10uS (ish!)
    dummy_variable = 0                                                  # No need to use the 'time' module here,
    dummy_variable = 0                                                  # a couple of 'dummy' statements will do fine
    
    GPIO.output (GPIO_TRIGGER,False)                                    # Turn off the 'Trig' pin
    time1, time2 = time.time(), time.time()                             # Set inital time values to current time
    
    while not GPIO.input (GPIO_ECHO):                                   # Wait for the start of the 'Echo' pulse
        time1 = time.time()                                             # Get the time the 'Echo' pin goes high
        if time1 - time2 > 0.02:                                        # If the 'Echo' pin doesn't go high after 20mS
            distance = 1000                                             # then set 'distance' to 1000
            break                                                       # and break out of the loop
        
    if distance == 1000:                                                # If a sensor error has occurred
        return (distance)                                               # then exit with 1000 (sensor fault)
    
    while GPIO.input (GPIO_ECHO):                                       # Otherwise, wait for the 'Echo' pin to go low
        time2 = time.time()                                             # Get the time the 'Echo' pin goes low
        if time2 - time1 > 0.02:                                        # If the 'Echo' pin doesn't go low after 20mS
            distance = 1000                                             # then ignore it and set 'distance' to 1000
            break                                                       # and break out of the loop
        
    if distance == 1000:                                                # If a sensor error has occurred
        return (distance)                                               # then exit with 100 (sensor fault)
        
                                                                        # Sound travels at approximately 2.95uS per mm
                                                                        # and the reflected sound has travelled twice
                                                                        # the distance we need to measure (sound out,
                                                                        # bounced off object, sound returned)
                                                                        
    distance = (time2 - time1) / 0.00000295 / 2 / 10                    # Convert the timer values into centimetres
    return (distance)                                                   # Exit with the distance in centimetres