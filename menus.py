import pygame
import sys
import utils
import databases
import bcrypt # used for hashing/ dehashing passwords

# each ui will have it's own game loop
def access(display, clock, assets, game):
    running = True
    clicked = False
    font = pygame.font.Font('font.ttf', 28) # gets the font stored in the game files

    pygame.display.set_caption("Shadowspire")
    while running:
        display.fill((0,0,0)) # refreshes the screen
        display.blit(assets['menu'], (0,0)) # adds the menu background 
        display.blit(assets['logo'], (130, 50))# adds the logo

        mx, my = pygame.mouse.get_pos() # gets the x coordinate and y coordinate of the mouses position

        buttons = [[pygame.Rect(220, 180, 208, 80), (220,180), 'SIGN UP'], [pygame.Rect(220, 300, 208, 80), (220,300), 'SIGN IN']]
        # we go through each button in our buttons list, check if it has been clicked and if it has, we give an appropaite response
        for button in buttons:
            colour = (204,85,0)
            if button[0].collidepoint(mx,my): # checks if the mouse is hovering over a button
                colour = (255, 153, 51)
                if clicked and button[2] == 'SIGN IN':
                    login(display, clock, assets, game) # UI changes to login
                if clicked and button[2] == 'SIGN UP':
                    create(display, clock, assets) # UI changes to account creation

            text = font.render(button[2], True, 'white')
                    
            pygame.draw.rect(display, colour, button[0])
            pygame.draw.rect(display, (139, 64, 0), button[0], 4) # this adds an outline to each button
 
            display.blit(text, (button[1][0] + 45, button[1][1] + 20)) # adds text to the button

        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
    
        pygame.display.update() #updates the display
        clock.tick(60)
 
def login(display, clock, assets, game):
    running = True
    clicked = False
    mode = [''] # system will know what mode we are in

    display_username = ''
    display_password = ''

    username = '' #actual username we will use for account creation
    password = '' #actual password we will use for account creation

    font = pygame.font.Font('font.ttf', 20)
    user_text = font.render(display_username, True, 'white')
    pass_text = font.render(display_password, True, 'white')

    connection_check = databases.check_connection()

    while running:
        display.fill((0,0,0)) # refreshes screen
        display.blit(assets['login/create_menu'], (0,0)) # adds specific background image to the screen
        
        pygame.draw.rect(display, (0, 49, 83), pygame.Rect(0,0, 360, 480))
        pygame.draw.rect(display, (0, 33, 71), pygame.Rect(0,0, 360, 480), 6)
        display.blit(pygame.transform.scale_by(assets['logo'], 0.9), (5, 10))

        mx, my = pygame.mouse.get_pos() # gets mouse position

        buttons = [[pygame.Rect(30, 150, 300, 64), (30,150), 'USERNAME'], [pygame.Rect(30, 250, 300, 64), (30,250), 'PASSWORD'], 
                   [pygame.Rect(100, 350, 150, 64), (100,350), 'LOGIN'], [pygame.Rect(450, 420, 100, 48), (450,420), 'EXIT']]
        
        for button in buttons:
            #we check if the mouse is hovering over a button and change the colour according to 'type' of button
            if button[2] == 'USERNAME' or button[2] == 'PASSWORD':
                if button[0].collidepoint(mx,my):
                    colour = (108, 142, 206)
                else:
                    colour = (43, 87, 151)
                border = (31, 56, 100) 
            elif (button[2] == 'LOGIN' or button[2] == 'EXIT') and button[0].collidepoint(mx,my):
                colour = (135, 206, 235)
                border = (46, 78, 126)
            else:
                colour = (30, 144, 255)
                border = (46, 78, 126)

            if button[0].collidepoint(mx,my) and clicked:
                #if we have clicked the button, we change the mode accordingly 
                mode = [button[2]]

            if (button[0].collidepoint(mx, my) and button[2] == 'EXIT') and clicked:
                #exits out of the login UI
                running = False

            pygame.draw.rect(display, colour, button[0])
            pygame.draw.rect(display, border, button[0], 4)

            text = font.render(button[2], True, 'white')
            #renders the appropiate text for the button
            if button[2] == 'LOGIN':
                display.blit(text, (button[0][0] + 40, button[0][1] + 20))
            elif button[2] == 'EXIT':
                display.blit(text, (button[0][0] + 25, button[0][1] + 10))
            else:
                display.blit(text, (button[0][0] + 5, button[0][1] - 25))

        clicked = False

        if display_username:
            #if display_username is not empty, we display it
            user_text = font.render(display_username, True, 'white')
            display.blit(user_text, (40, 165))
            
        if display_password:
            #if display_password is not empty, we display it
            pass_text = font.render(display_password, True, 'white')
            display.blit(pass_text, (40, 275))

        #we check if the system is in login mode and check whether the username is an existing one
        if connection_check:
            if mode[0] == 'LOGIN' and databases.check_valid_username(username):
                pass_check = databases.retrieve_password(username) # we retrieve the stored hashed password from the database
                if (bcrypt.checkpw(password.encode('utf-8'), pass_check.encode('utf-8'))):
                    #checks whether the stored password and the entered password are the same
                    running = False # stops the game loop
                    game.username = username
                    main_menu(display, clock, assets, game, username) # we transition into the main menu screen
                else:
                    error_text = font.render('Incorrect password', True, 'white') #we display an error message to the user
                    display.blit(error_text, (10, 450))

            elif mode[0] == 'LOGIN' and not(databases.check_valid_username(username)):
                #user has entered an incorrect username so we display a corresponding error message for that
                error_text = font.render('Incorrect username', True, 'white')
                display.blit(error_text, (10, 450))

        else:
            error_text = font.render('Connection failed ', True, 'white')
            display.blit(error_text, (10, 450))
          
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    #removes one character from the end of either password or username depending on mode
                    if mode[0] == 'USERNAME':
                        display_username = display_username[:-1]
                        username = username[:-1]
                    elif mode[0] == 'PASSWORD':
                        display_password = display_password[:-1]
                        password = password[:-1]
                else:
                    if mode[0] == 'USERNAME':
                        if user_text.get_width() < 275: #we check how long the text is so that the text doesnt go beyond the input box
                            display_username = display_username + event.unicode #adds a character that the user inputted
                            username = username + event.unicode
                        else:
                            #if the text is now longer than the input box, we only add character to username, not display_username
                            username = username + event.unicode 
                    elif mode[0] == 'PASSWORD':
                        #exact same logic as how we handle usernames
                        if pass_text.get_width() < 275:
                            display_password = display_password + '*' #we add astericks for privacy instead of actual character
                            password = password + event.unicode
                        else:
                            password = password + event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
        
        pygame.display.update()
        clock.tick(60)

def create(display, clock, assets):
    #very similar to login page but with the addition of emails
    running = True
    clicked = False
    mode = ['']

    display_username = ''
    display_password = ''
    display_email = ''

    username = ''
    password = ''
    email = ''

    logged = False

    font = pygame.font.Font('font.ttf', 20)
    user_text = font.render(display_username, True, 'white')
    pass_text = font.render(display_password, True, 'white')
    email_text = font.render(display_email, True, 'white')

    connection_check = databases.check_connection()

    while running:
        display.fill((0,0,0)) #refreshes screen
        display.blit(assets['login/create_menu'], (0,0)) #adds background image 

        pygame.draw.rect(display, (0, 49, 83), pygame.Rect(0,0, 360, 480))
        pygame.draw.rect(display, (0, 33, 71), pygame.Rect(0,0, 360, 480), 6)
        display.blit(pygame.transform.scale_by(assets['logo'], 0.7), (40, 10)) #adds logo

        mx, my = pygame.mouse.get_pos() #gets mouse position

        buttons = [[pygame.Rect(30, 130, 300, 64), (30,130), 'USERNAME'], [pygame.Rect(30, 230, 300, 64), (30,230), 'PASSWORD'], 
                  [pygame.Rect(30, 330, 300, 64), (30,330), 'EMAIL'], [pygame.Rect(100, 405, 150, 64), (100,405), 'CREATE'], 
                   [pygame.Rect(450, 410, 100, 48), (450,410), 'EXIT']]
        
        for button in buttons:
            #go through each button in buttons list and check if mouse is hovering over it
            #if it is, we change colour of button
            if button[2] == 'USERNAME' or button[2] == 'PASSWORD' or button[2] == 'EMAIL':
                if button[0].collidepoint(mx,my):
                    colour = (108, 142, 206)
                else:
                    colour = (43, 87, 151)
                border = (31, 56, 100) 
            elif (button[2] == 'CREATE' or button[2] == 'EXIT') and button[0].collidepoint(mx,my):
                colour = (135, 206, 235)
                border = (46, 78, 126)
            else:
                colour = (30, 144, 255)
                border = (46, 78, 126)

            if button[0].collidepoint(mx,my) and clicked:
                #changes mode to the button we clicked
                mode = [button[2]]

            if (button[0].collidepoint(mx, my) and button[2] == 'EXIT') and clicked:
                #we end menu game loop
                running = False

            if (button[0].collidepoint(mx, my) and button[2] == 'CREATE') and clicked:
                if logged:
                    #if we have already created an account (logged is true), logged will be set to false
                    logged = False

            pygame.draw.rect(display, colour, button[0])
            pygame.draw.rect(display, border, button[0], 4)

            text = font.render(button[2], True, 'white')
            #adds the relevant text to each button
            if button[2] == 'CREATE':
                display.blit(text, (button[0][0] + 30, button[0][1] + 20))
            elif button[2] == 'EXIT':
                display.blit(text, (button[0][0] + 25, button[0][1] + 10))
            else:
                display.blit(text, (button[0][0] + 5, button[0][1] - 25))

        clicked = False

        #renders the username, password and email
        if display_username:
            user_text = font.render(display_username, True, 'white')
            display.blit(user_text, (40, 145))
            
        if display_password:
            pass_text = font.render(display_password, True, 'white')
            display.blit(pass_text, (40, 255))
        
        if display_email:
            email_text = font.render(display_email, True, 'white')
            display.blit(email_text, (40, 345))

        if connection_check:
            if mode[0] == 'CREATE' and not(logged):
                if not(databases.check_valid_username(username)) and utils.valid_account(username, password, email):
                    #we check if the username is a unique one and whether the detials are valid
                    databases.sign_up(username, password, email) #if they are, we add the account to accounts database
                    #we reset the values listed below
                    username = ''
                    password = ''
                    email = ''
                    display_username = ''   
                    display_password = ''
                    display_email = ''

                    logged = True
                else:
                    #if the account is not valid, we display an error text to the user
                    pygame.draw.rect(display, (43, 87, 151), (380, 130, 238, 64))
                    pygame.draw.rect(display, (31, 56, 100), (380, 130, 238, 64), 6)
                    error_text = font.render('Incorrect details', True, 'white')
                    display.blit(error_text, (393,150))
        else:
            pygame.draw.rect(display, (43, 87, 151), (380, 130, 238, 64))
            pygame.draw.rect(display, (31, 56, 100), (380, 130, 238, 64), 6)
            error_text = font.render('Connection failed', True, 'white')
            display.blit(error_text, (393,150))


        if logged and mode[0] == 'CREATE':
            #we display a confirmation that the user's account has been successfully created 
            pygame.draw.rect(display, (43, 87, 151), (380, 130, 238, 64))
            pygame.draw.rect(display, (31, 56, 100), (380, 130, 238, 64), 6)
            success_text = font.render('Account created', True, 'white')
            display.blit(success_text, (393,150))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if mode[0] == 'USERNAME':
                        display_username = display_username[:-1]
                        username = username[:-1]
                    elif mode[0] == 'PASSWORD':
                        display_password = display_password[:-1]
                        password = password[:-1]
                    elif mode[0] == 'EMAIL':
                        display_email = display_email[:-1]
                        email = email[:-1]
                else:
                    if mode[0] == 'USERNAME':
                        if user_text.get_width() < 275:
                            display_username = display_username + event.unicode
                            username = username + event.unicode
                        else:
                            username = username + event.unicode
                    elif mode[0] == 'PASSWORD':
                        if pass_text.get_width() < 275:
                            display_password = display_password + '*'
                            password = password + event.unicode
                        else:
                            password = password + event.unicode
                    elif mode[0] == 'EMAIL':
                        if email_text.get_width() < 275:
                            display_email = display_email + event.unicode
                            email = email + event.unicode
                        else:
                            email = email + event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
        
        pygame.display.update() #updates display
        clock.tick(60)

def main_menu(display, clock, assets, game, username):
    running = True
    clicked = False
    font = pygame.font.Font('font.ttf', 28)

    rankings = databases.retrieve_leaderboard_data() #we get the top 5 players from the leaderboard database
    user_data = databases.retrieve_userdata(username) #we retrieve the relevant account details from the accounts database
    account_record = utils.PlayerDetails(user_data[0], user_data[1], user_data[2]) #we create a record with those account details
    game.account_record = account_record

    #loads in music that will play
    pygame.mixer.music.load('audio/main_menu_music.wav')
    pygame.mixer.music.set_volume(0.6)
    pygame.mixer.music.play(-1) #ensures the music will loop

    while running:
        display.fill((0,0,0))
        display.blit(assets['menu'], (0,0))

        display.blit(assets['logo'], (130, 20))

        mx, my = pygame.mouse.get_pos() #gets mouse position

        buttons = [[pygame.Rect(147, 160, 360, 80), (180,160), 'PLAY'], [pygame.Rect(147, 260, 360, 80), (180,260), 'QUIT'],
                   [pygame.Rect(147, 360, 170, 80), (147,360), 'INSTRUCTIONS'], [pygame.Rect(337, 360, 170, 80), (337,360), 'LEADERBOARD']]

        for button in buttons:
            colour = (204,85,0)
            if button[0].collidepoint(mx,my):
                colour = (255, 153, 51)
                if clicked and button[2] == 'PLAY': #checks if user has clicked play button
                    game.reset() #resets the game         
                    pygame.mixer.music.stop() #we stop the music
                    game.run()
                    pygame.mixer.music.play(-1)
                if clicked and button[2] == 'QUIT': #checks if user has clicked quit button
                    pygame.quit()
                    sys.exit()
                if clicked and button[2] == 'INSTRUCTIONS': #checks if user has clicked instructions button
                    instructions(display, clock, assets) #transitions to instructions interface
                if clicked and button[2] == 'LEADERBOARD': #checks if user has clicked leaderboard button
                    leaderboard(display, clock, assets, account_record, rankings) #transitions to leaderboard interface                  

            if button[2] == 'INSTRUCTIONS' or button[2] == 'LEADERBOARD': #leaderboard/ instructions buttons are smaller
                font = pygame.font.Font('font.ttf', 18) #we use different size fonts for instructions/ leaderboard text
            else:
                font = pygame.font.Font('font.ttf', 28)

            text = font.render(button[2], True, 'white')
                    
            pygame.draw.rect(display, colour, button[0])
            pygame.draw.rect(display, (139, 64, 0), button[0], 4)

            if button[2] == 'INSTRUCTIONS' or button[2] == 'LEADERBOARD':
                display.blit(text, (button[1][0] + 9, button[1][1] + 25))
            else:
                display.blit(text, (button[1][0] + 100, button[1][1] + 20))

        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
    
        pygame.display.update()
        clock.tick(60)

def instructions(display, clock, assets):
    running = True
    clicked = False
    font = pygame.font.Font('font.ttf', 18)
    
    while running:
        display.fill((0,0,0)) #refreshes screen
        display.blit(assets['instructions'], (0,0)) #we add the instructions image to our screen

        mx, my = pygame.mouse.get_pos() #get mouse position
        button = [pygame.Rect(230, 320, 120, 60), 'EXIT']

        colour = (43, 87, 151)
        if button[0].collidepoint(mx,my):
            colour = (108, 142, 206)
            if clicked:
                #if player has clicked exit button, we end the game loop and go back to main menu
                running = False

        text = font.render(button[1], True, 'white')
        pygame.draw.rect(display, colour, button[0])
        pygame.draw.rect(display, (31, 56, 100), button[0], 4)
        display.blit(text, (265,340))

        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
    
        pygame.display.update()
        clock.tick(60)

def leaderboard(display, clock, assets, account_data, rankings):
    running = True
    clicked = False
    font = pygame.font.Font('font.ttf', 16)

    while running:
        display.fill((0,0,0)) #refreshes screen
        display.blit(assets['leaderboard'], (0,0))
        display.blit(pygame.transform.scale_by(assets['leaderboard_logo'], 0.6), (140, -30))

        mx, my = pygame.mouse.get_pos()
        button = [pygame.Rect(420, 400, 120, 60), 'EXIT']

        colour = (30, 144, 255)
        if button[0].collidepoint(mx,my):
            colour = (135, 206, 235)
            if clicked:
                #if user has pressed exit button, we exit out of the leaderboard interface and go back to main menu
                running = False

        
        pygame.draw.rect(display, (43, 87, 151), pygame.Rect(80, 150, 460, 80))
        pygame.draw.rect(display, (31, 56, 100), pygame.Rect(80, 150, 460, 80), 4)

        display.blit(font.render('Username', True, 'white'), (160,160))
        display.blit(font.render('Levels beaten', True, 'white'), (360,160))
        
        #this adds the user's own high score
        display.blit(font.render(account_data.username, True, 'white'), (160,195))
        display.blit(font.render(str(account_data.high_score), True, 'white'), (420,195))       

        text = font.render(button[1], True, 'white')
        pygame.draw.rect(display, colour, button[0])
        pygame.draw.rect(display, (46, 78, 126), button[0], 4)
        display.blit(text, (460, 432))

        pygame.draw.rect(display, (43, 87, 151), pygame.Rect(80, 250, 460, 180))
        pygame.draw.rect(display, (31, 56, 100), pygame.Rect(80, 250, 460, 180), 4)
        
        #rankings is a list containing lists that have a username and corresponding high score
        for x in range(len(rankings)):
            #we add the actual rankings to the screen
            display.blit(font.render(str(x + 1) + '.', True, 'white'), (110, 240 + ((x+1) * 30)))
            display.blit(font.render(rankings[x][0], True, 'white'), (160, 240 + ((x+1) * 30)))
            display.blit(font.render(str(rankings[x][1]), True, 'white'), (420, 240 + ((x+1) * 30)))

        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
    
        pygame.display.update()
        clock.tick(60)

def death(display, clock, assets, game):
    running = True
    clicked = False
    font = pygame.font.Font('font.ttf', 20)

    #we play our death music
    pygame.mixer.music.load('audio/death_music.wav')
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1) #ensures the music loops

    while running:
        display.fill((0,0,0)) #refreshes screen
        display.blit(assets['death'], (0,0))

        mx, my = pygame.mouse.get_pos()

        buttons = [[pygame.Rect(230, 340, 180, 60), (230,340), 'RESPAWN'], [pygame.Rect(230, 410, 180, 60), (230,410), 'MENU']]

        for button in buttons:
            colour = (20, 20, 20)
            if button[0].collidepoint(mx,my):
                colour = (50, 50, 50)

                if button[2] == 'RESPAWN' and clicked:
                    #we stop death music and death sound effect
                    game.sfx['death'].stop()
                    pygame.mixer.music.stop()
                    running = False #we go back to the game
                    game.reset() #resets game

                if button[2] == 'MENU' and clicked:
                    #we stop the death music and load the main menu music
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load('audio/main_menu_music.wav')

                    game.sfx['death'].stop() #stop death sfx
                    running = False #ends the loop for this menu
                    game.running = False #ends the game loop so we go back to main menu

            text = font.render(button[2], True, 'white')
                    
            pygame.draw.rect(display, colour, button[0])
            pygame.draw.rect(display, (138, 3, 3), button[0], 4)
 
            if button[2] == 'MENU':
                display.blit(text, (button[1][0] + 60, button[1][1] + 15))
            else:
                display.blit(text, (button[1][0] + 35, button[1][1] + 15))

        clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
                        
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
    
        pygame.display.update() #updates the display
        clock.tick(60)
 