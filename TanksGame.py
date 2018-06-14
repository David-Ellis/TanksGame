# -*- coding: utf-8 -*-
""" Basic Tanks Game

Created on Sat Dec 17 18:53:44 2016

Bugs:
    - Bug with the player change yet to be fixed [FIXED 03/01/17]
    - If bullet goes out of range it can't hit the floor
    - Wind is still broken

To Add:
    - Green floor
        1. Flat ground
        2. Variable hills
    - blue sky [DONE 03/01/17] 
    - Limitied movement
    - Start angle at same position as last turn with that tank [DONE 03/01/17]
    - Variable weapons
        ~ Might be able to change the max and minimum speeds depending on weapon
        ~ Need to show ammo specific to each player
        ~ Maybe some indication of the destruction level of the weapon on the
            weapon axes
        ~ left and right buttons to scroll through weapons
        ~ Blast radius
    - Random wind
        1. Plot left/right arrow to show dirrection 
        2. Add text to show magnitude
    - Sound effects
    - Pop up box asking for number of players
    - Pop up box asking if you want to play again
        Both of these can be done by generating new figures using Matplotlib
        (I think)
    - Stop tanks from going off the edge of the screen
    - Find a way to prevent multiple shots before the first is finished
            maybe use if self.firing == False:
    - Pick up bonuses:
        ~ Air strike attack

@author: David Ellis
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.gridspec as gridspec
import ctypes

#v = np.array([self.speed1*np.sin(AimAngle1.val*(2*np.pi/360)),
#              self.speed1*np.cos(AimAngle1.val*(2*np.pi/360))])
#g = np.array([0, self.grav])
#k = np.array([0, self.wind])

def func(v, g, k):
    drag = 0.01*np.array([((v[0]-k[0])/abs(v[0]-k[0]))*(v[0]-k[0])**2, v[1]**2])
    return (g - drag)

plt.close('all')
fig = plt.figure('Tanks', figsize = (10,7), facecolor = '#a5a5a5')

gs = gridspec.GridSpec(16,16)
ax1 = plt.subplot(gs[0:10, 0:16])
ax1.set_title('Tanks', size = 24);ax1.set_xticks([],[]); ax1.set_yticks([],[])
ax1.patch.set_facecolor('#b3cffc') # blue sky

#rect = 0.14, 0.73, 0.2, 0.15
#weapons = fig.add_axes(rect, frameon=True)
#weapons.set_xticks([],[]); weapons.set_yticks([],[])
#weapons.text(0.2, 0.75,'Weapons', size = 16)

ax_angle1 = plt.subplot(gs[11,5:11])
ax_power1 = plt.subplot(gs[12,5:11])
ax_fire1 = plt.subplot(gs[14,5:11])
ax_left = plt.subplot(gs[13,6:8])
ax_right = plt.subplot(gs[13,8:10])

AimAngle1 = Slider(ax_angle1, '', -90, 90, valinit = 45, color='k')
Speed1 = Slider(ax_power1, '', 0, 15, valinit = 3, color='k')
left = Button(ax_left,'Left')
right = Button(ax_right,'Right')
fire1 = Button(ax_fire1, 'Fire!')

players = 4
health1 = plt.subplot(gs[12, 0:4]);plt.xticks([],[]); plt.yticks([],[])
health1.set_title('Player 1')
health2 = plt.subplot(gs[15, 0:4]);plt.xticks([],[]); plt.yticks([],[])
health2.set_title('Player 2')
if players > 2:
    health3 = plt.subplot(gs[12, 12:16]);plt.xticks([],[]); plt.yticks([],[])
    health3.set_title('Player 3')
if players > 3:
    health4 = plt.subplot(gs[15, 12:16]);plt.xticks([],[]); plt.yticks([],[])
    health4.set_title('Player 4')
    

class Tanks(object):
    
    players = np.array([])
    NumberOfPlayers = 0
    xposns = np.array([])    
    healths = np.array([])
    
    alive = np.array([])
    
    bL = 0.7
    bw = 0.2
    x0 = 0
    y0 = 0
    
    barrelx = np.array([])
    barrely =  np.array([])
    
    angles = np.array([])
    speeds = np.array([])    
    
    # Flat ground
    hillx = np.array([])
    hilly = np.array([])    
    
    MaxDamage = 20
    
    tw = 0.6
    th = 0.4
    tankx = np.array([]) 
    tanky = np.array([])     
    
    colors = np.array(['b','g','r','m'])
    
    leftArrowX = np.array([13, 13, 12, 13, 13, 14, 14, 13])-1.6
    leftArrowY = np.array([8.7, 8.5, 8.9, 9.3, 9.1, 9.1, 8.7, 8.7])
    
    rightArrowX = np.array([13, 13, 14, 13, 13, 12, 12, 13])-1.6
    rightArrowY = np.array([8.7, 8.5, 8.9, 9.3, 9.1, 9.1, 8.7, 8.7])   
    
    wind = 10 - 20*np.random.rand(1)
    speed1 = Speed1.val
    grav = -10
    
    activePlayer = 0
    
    def __init__(self, NumberOfPlayers):
        
        ########### Create landscape ############
        print("Does this work?")
        # plot sky
        groundX = np.concatenate(([-15], np.arange(-15, 15.2, 0.2),[15]))

        numberOfHills = np.random.randint(1, 4)
        HillWidths = 1 + 4*np.random.rand(numberOfHills)
        HillHeight = 3*np.random.rand(numberOfHills)
        HillCentre = 12 - 24*np.random.rand(numberOfHills)
        
        self.hilly = np.zeros(len(groundX))+0.5
        for hill in range(numberOfHills):
            self.hilly += HillHeight[hill]*np.exp(-((groundX-HillCentre[hill])**2)/(2*HillWidths[hill]**2))
        
        self.hilly = np.concatenate(([0], self.hilly, [0]))
        self.hillx = np.concatenate(([-15], groundX, [15]))        
                
        ax1.fill(self.hillx, self.hilly,'#06d100')               
        ########### Create tanks ############
        
        self.NumberOfPlayers = NumberOfPlayers
        self.players = np.arange(0,NumberOfPlayers)
        
        self.indices = np.random.randint(0.1*len(self.hillx), 0.9*len(self.hillx),self.NumberOfPlayers)
        self.xposns = self.hillx[self.indices+1]
        self.yposns = self.hilly[self.indices+1]
        
        self.barrelx = np.zeros([4,NumberOfPlayers])
        self.barrely = np.zeros([4,NumberOfPlayers])
        
        self.tankx = np.zeros([4,NumberOfPlayers])
        self.tanky = np.zeros([4,NumberOfPlayers])
        
        self.healths = np.zeros([NumberOfPlayers]) + 100
        self.alive = np.zeros([NumberOfPlayers]) + 1        
        
        self.angles = np.zeros([NumberOfPlayers]) + AimAngle1.val
        self.speeds = np.zeros([NumberOfPlayers]) + Speed1.val
        
        print(self.players)
        print(self.xposns)
        
        if self.wind > 0:
            ax1.fill(self.rightArrowX, self.rightArrowY, 'w')
        elif self.wind < 0:
            ax1.fill(self.leftArrowX, self.leftArrowY, 'w')
        ax1.text(8, 8, 'Wind Speed: {0:.2f}'.format(float(self.wind)), size=14,
                 color='k')
        
        for player in self.players:
            self.tankx[:,player] = self.xposns[player] + \
                    np.array([self.x0-self.tw, self.x0-self.tw, 
                              self.x0+self.tw, self.x0+self.tw])         
                      
            self.tanky[:,player] = np.array([0, self.th, self.th, 0]) + self.yposns[player]     
            
            self.barrelx[:,player] = self.xposns[player] + np.array([self.x0-self.bw/2,
                -self.bw/2 + self.bL*np.sin(AimAngle1.val*(2*np.pi/360)),
                -self.bw/2 + self.bL*np.sin(AimAngle1.val*(2*np.pi/360)) 
                                    + self.bw*np.cos(AimAngle1.val*(2*np.pi/360)),
                -self.bw/2 + self.bw*np.cos(AimAngle1.val*(2*np.pi/360))]) 
                
            self.barrely[:, player] = self.yposns[player]+ 0.2 + np.array([self.y0,
                self.y0 + self.bL*np.cos(AimAngle1.val*(2*np.pi/360)),
                self.y0 + self.bL*np.cos(AimAngle1.val*(2*np.pi/360)) - 
                            self.bw*np.sin(AimAngle1.val*(2*np.pi/360)),
                self.y0 - self.bw*np.sin(AimAngle1.val*(2*np.pi/360))])

            
            ax1.fill(self.barrelx[:,player], self.barrely[:,player], color = 'k')
            ax1.fill(self.tankx[:,player], self.tanky[:,player], color = self.colors[player]) 
            ax1.axis([-15, 15, -0, 10]);plt.xticks([],[]); plt.yticks([],[])
        health1.axis([0, 100, 0, 0.1])
        health1.barh(0, self.healths[0], color=self.colors[0])
        health2.axis([0, 100, 0, 0.1])
        health2.barh(0, self.healths[1],color=self.colors[1])
        if self.NumberOfPlayers > 2:
            health3.axis([0, 100, 0, 0.1])
            health3.barh(0, self.healths[2],color=self.colors[2])
        if self.NumberOfPlayers > 3:
            health4.axis([0, 100, 0, 0.1])
            health4.barh(0, self.healths[3],color=self.colors[3])
        plt.pause(0.01)
        plt.show()
            

    def changePlayer(self):
        self.activePlayer += 1
        if self.activePlayer == int(self.NumberOfPlayers):
            self.activePlayer = int(0)
        if int(sum(self.alive)) >= 1:
            while self.alive[int(self.activePlayer)] == 0:
                #print('looping')
                self.activePlayer += 1
                if self.activePlayer == int(self.NumberOfPlayers):
                    #print('Inside if statement')
                    self.activePlayer = int(0)
        self.wind = 10 - 20*np.random.rand(1)
        print(self.wind)
        AimAngle1.set_val(self.angles[self.activePlayer])
        Speed1.set_val(self.speeds[self.activePlayer])
        
    def replot(self):
        ax1.cla()
        ax1.set_title('Tanks', size = 24)
        ax1.fill(self.hillx, self.hilly,'#06d100') 
        
        if self.wind > 0:
            ax1.fill(self.rightArrowX, self.rightArrowY, 'w')
        elif self.wind < 0:
            ax1.fill(self.leftArrowX, self.leftArrowY, 'w')
        ax1.text(8, 8, 'Wind Speed: {0:.2f}'.format(float(self.wind)), size=14,
                 color='k')
        for player in self.players:       
            ax1.fill(self.barrelx[:,player], self.barrely[:,player], color = 'k')
            ax1.fill(self.tankx[:,player], self.tanky[:,player], color = self.colors[player]) 
            ax1.axis([-15, 15, -0, 10]);ax1.set_xticks([],[]); ax1.set_yticks([],[])
        ax1.patch.set_facecolor('#b3cffc') # blue sky
        plt.xticks([],[]); plt.yticks([],[])
        self.progectileTrace()
        plt.show()      
        
    def aim(self, event): 
        self.angles[self.activePlayer] = AimAngle1.val      
        self.speeds[self.activePlayer] = Speed1.val
        
        if AimAngle1.val >= 0:
            self.barrelx[:,self.activePlayer] =  self.xposns[self.activePlayer] + \
            np.array([-self.bw/2, 
                      -self.bw/2 + self.bL*np.sin(AimAngle1.val*(2*np.pi/360)),
                      -self.bw/2 + self.bL*np.sin(AimAngle1.val*(2*np.pi/360)) + self.bw*np.cos(AimAngle1.val*(2*np.pi/360)),
                      -self.bw/2 + self.bw*np.cos(AimAngle1.val*(2*np.pi/360))]) 
                      
            self.barrely[:, self.activePlayer] = self.tanky[1,self.activePlayer] - self.th/2 + np.array([0,
                 self.bL*np.cos(AimAngle1.val*(2*np.pi/360)),
                 self.bL*np.cos(AimAngle1.val*(2*np.pi/360)) - self.bw*np.sin(AimAngle1.val*(2*np.pi/360)),
                 -self.bw*np.sin(AimAngle1.val*(2*np.pi/360))])
                 
        # IS A BIT WRONG
        elif AimAngle1.val < 0:
            self.barrelx[:,self.activePlayer] = self.xposns[self.activePlayer] + \
            np.array([self.bw/2 - self.bw*np.cos(AimAngle1.val*(2*np.pi/360)), 
                      self.bw/2 + self.bL*np.sin(AimAngle1.val*(2*np.pi/360)) - self.bw*np.cos(AimAngle1.val*(2*np.pi/360)),
                      self.bw/2 + self.bL*np.sin(AimAngle1.val*(2*np.pi/360)),
                      self.bw/2]) 
            self.barrely[:, self.activePlayer] =  self.tanky[1,self.activePlayer] - self.th/2 +  np.array([self.bw*np.sin(AimAngle1.val*(2*np.pi/360)),
                self.bL*np.cos(AimAngle1.val*(2*np.pi/360)) + self.bw*np.sin(AimAngle1.val*(2*np.pi/360)),
                + self.bL*np.cos(AimAngle1.val*(2*np.pi/360)), 0])
                
        self.replot()
        plt.pause(0.01)
                                    
    def progectileTrace(self):
        #x and y vals of barrel end
        self.speed1 = Speed1.val
        xb_end = 0.5*(self.barrelx[2,self.activePlayer]+self.barrelx[1,self.activePlayer])
        yb_end = 0.5*(self.barrely[2,self.activePlayer]+self.barrely[1,self.activePlayer])
        t = np.linspace(0.05, 1, 10)            
        xtrace = xb_end + self.speed1*np.sin(AimAngle1.val*(2*np.pi/360)) * t
        ytrace = yb_end + self.speed1*np.cos(AimAngle1.val*(2*np.pi/360)) * t + 0.5 * self.grav * t **2
        ax1.plot(xtrace, ytrace,'.k')
        
    def damage(self, landx, landy):
        # Has anything been hit?
        for player in self.players:
            distance = np.sqrt(abs(landx-self.xposns[player])**2 + abs(landy-self.yposns[player])**2)
            if distance < 2:
                self.healths[player] -= self.MaxDamage*(2-distance)
                if self.healths[player] <= 0:
                    self.kill(player)

        self.replot()
        plt.pause(0.01)
    
    def kill(self, player):
        # Move tank off screen
        self.alive[player] = 0
        self.barrelx[:, player] = -100
        self.barrely[:, player] = -100
        self.xposns[player] = -100
        self.tankx[:,player] = -100
        # display dealth message
        dealthMessage = 'Player: {0:.0f} killed'.format(player+1)
        ctypes.windll.user32.MessageBoxW(0, dealthMessage, 'Player Killed!', 1)

        
    def fireProgectile(self, event):
        # over estimate total time
        yb_end = 0.5*(self.barrely[2,self.activePlayer]+self.barrely[1,self.activePlayer])
        xb_end = 0.5*(self.barrelx[2,self.activePlayer]+self.barrelx[1,self.activePlayer])

        v = np.array([self.speed1*np.sin(AimAngle1.val*(2*np.pi/360)),
                      self.speed1*np.cos(AimAngle1.val*(2*np.pi/360))])
        
        g = np.array([0, self.grav])
        k = np.array([self.wind[0], 0])
 
        
        r = np.array([xb_end,yb_end])
        del_t = 0.02
        
        groundIndex = np.searchsorted(self.hillx, int(round(r[0])/0.2)*0.2)
        floorY = self.hilly[groundIndex]
        while r[1]>floorY:
                rh = r + del_t*v/2
                vh = v + del_t*func(v, g, k)

                # full step:
                r = rh + del_t*vh/2
                v = v + del_t*func(vh, g, k)
                print(func(v, g, k))
                # Calculate corresponding ground Y 
                groundIndex = np.searchsorted(self.hillx, int(round(r[0])/0.2)*0.2)
                floorY = self.hilly[groundIndex]                
                
                self.replot()
                ax1.plot(r[0], r[1],'ob')
                plt.pause(0.01)
                plt.show()
        for a in np.arange(1,30, 2):
            ax1.plot(r[0], r[1],'or', markersize=a)
            plt.pause(0.001)
        self.damage(r[0], floorY)
        self.changePlayer() 
        self.replot()
        health1.cla();health1.axis([0, 100, 0, 0.1])
        health1.barh(0, self.healths[0], color=self.colors[0])
        health1.set_xticks([],[]); health1.set_yticks([],[])
        health1.set_title('Player 1')
        health2.cla();health2.axis([0, 100, 0, 0.1])
        health2.barh(0, self.healths[1],color=self.colors[1])
        health2.set_xticks([],[]); health2.set_yticks([],[])
        health2.set_title('Player 2')
        if self.NumberOfPlayers > 2:
            health3.cla();health3.axis([0, 100, 0, 0.1])
            health3.barh(0, self.healths[2],color=self.colors[2])
            health3.set_xticks([],[]); health3.set_yticks([],[])
            health3.set_title('Player 3')
        if self.NumberOfPlayers > 3:
            health4.cla();health4.axis([0, 100, 0, 0.1])
            health4.barh(0, self.healths[3],color=self.colors[3])
            health4.set_xticks([],[]); health4.set_yticks([],[])
            health4.set_title('Player 4')
        
        if int(sum(self.alive))==1:
            winner = self.players[self.alive==1]+1
            WinMessage = 'Player: {0:.0f} Wins!'.format(winner[0])
            ctypes.windll.user32.MessageBoxW(0, WinMessage, 'Game Over!', 1)
        elif int(sum(self.alive))==0:
            DrawMessage = 'It\'s a draw!'
            ctypes.windll.user32.MessageBoxW(0, DrawMessage, 'Game Over!', 1)
        
        if int(sum(self.alive))<2:
            plt.close('all')
        plt.pause(0.01)    
        
    def moveRight(self, event):
        self.indices[self.activePlayer] += 1
        self.xposns[self.activePlayer] = self.hillx[self.indices[self.activePlayer]]
        self.yposns[self.activePlayer] = self.hilly[self.indices[self.activePlayer]]
        
        self.tankx[:,self.activePlayer] = self.xposns[self.activePlayer] + \
             np.array([self.x0-self.tw, self.x0-self.tw, 
                       self.x0+self.tw, self.x0+self.tw])         
                      
        self.tanky[:,self.activePlayer] = self.yposns[self.activePlayer] + np.array([0, self.th, self.th, 0])            
        if AimAngle1.val >= 0:
            self.barrelx[:,self.activePlayer] =  self.xposns[self.activePlayer] + \
            np.array([-self.bw/2, 
                      -self.bw/2 + self.bL*np.sin(AimAngle1.val*(2*np.pi/360)),
                      -self.bw/2 + self.bL*np.sin(AimAngle1.val*(2*np.pi/360)) + self.bw*np.cos(AimAngle1.val*(2*np.pi/360)),
                      -self.bw/2 + self.bw*np.cos(AimAngle1.val*(2*np.pi/360))]) 
                      
            self.barrely[:, self.activePlayer] = self.tanky[1,self.activePlayer] - self.th/2 + np.array([0,
                 self.bL*np.cos(AimAngle1.val*(2*np.pi/360)),
                 self.bL*np.cos(AimAngle1.val*(2*np.pi/360)) - self.bw*np.sin(AimAngle1.val*(2*np.pi/360)),
                 -self.bw*np.sin(AimAngle1.val*(2*np.pi/360))])
                 
        elif AimAngle1.val < 0:
            self.barrelx[:,self.activePlayer] = self.xposns[self.activePlayer] + \
            np.array([self.bw/2 - self.bw*np.cos(AimAngle1.val*(2*np.pi/360)), 
                      self.bw/2 + self.bL*np.sin(AimAngle1.val*(2*np.pi/360)) - self.bw*np.cos(AimAngle1.val*(2*np.pi/360)),
                      self.bw/2 + self.bL*np.sin(AimAngle1.val*(2*np.pi/360)),
                      self.bw/2]) 
            self.barrely[:, self.activePlayer] =  self.tanky[1,self.activePlayer] - self.th/2 +  np.array([self.bw*np.sin(AimAngle1.val*(2*np.pi/360)),
                self.bL*np.cos(AimAngle1.val*(2*np.pi/360)) + self.bw*np.sin(AimAngle1.val*(2*np.pi/360)),
                + self.bL*np.cos(AimAngle1.val*(2*np.pi/360)), 0])

        self.replot()
        plt.pause(0.01)

    def moveLeft(self, event):
        self.indices[self.activePlayer] -= 1
        self.xposns[self.activePlayer] = self.hillx[self.indices[self.activePlayer]]
        self.yposns[self.activePlayer] = self.hilly[self.indices[self.activePlayer]]
        
        self.tankx[:,self.activePlayer] = self.xposns[self.activePlayer] + \
             np.array([self.x0-self.tw, self.x0-self.tw, 
                       self.x0+self.tw, self.x0+self.tw])         
                      
        self.tanky[:,self.activePlayer] = self.yposns[self.activePlayer] + np.array([0, self.th, self.th, 0])            
        if AimAngle1.val >= 0:
            self.barrelx[:,self.activePlayer] = self.xposns[self.activePlayer] + \
            np.array([-self.bw/2, 
                      -self.bw/2 + self.bL*np.sin(AimAngle1.val*(2*np.pi/360)),
                      -self.bw/2 + self.bL*np.sin(AimAngle1.val*(2*np.pi/360)) + self.bw*np.cos(AimAngle1.val*(2*np.pi/360)),
                      -self.bw/2 + self.bw*np.cos(AimAngle1.val*(2*np.pi/360))])  
                      
            self.barrely[:, self.activePlayer] = self.tanky[1,self.activePlayer] - self.th/2 + np.array([0,
                 self.bL*np.cos(AimAngle1.val*(2*np.pi/360)),
                 self.bL*np.cos(AimAngle1.val*(2*np.pi/360)) - self.bw*np.sin(AimAngle1.val*(2*np.pi/360)),
                 -self.bw*np.sin(AimAngle1.val*(2*np.pi/360))])
        
        # STILL MIGHT BE WRONG
        elif AimAngle1.val < 0:
            self.barrelx[:,self.activePlayer] = self.xposns[self.activePlayer] + \
            np.array([self.bw/2 - self.bw*np.cos(AimAngle1.val*(2*np.pi/360)), 
                      self.bw/2 + self.bL*np.sin(AimAngle1.val*(2*np.pi/360)) - self.bw*np.cos(AimAngle1.val*(2*np.pi/360)),
                      self.bw/2 + self.bL*np.sin(AimAngle1.val*(2*np.pi/360)),
                      self.bw/2]) 
                      
            self.barrely[:, self.activePlayer] =  self.tanky[1,self.activePlayer] - self.th/2 +  np.array([self.bw*np.sin(AimAngle1.val*(2*np.pi/360)),
                self.bL*np.cos(AimAngle1.val*(2*np.pi/360)) + self.bw*np.sin(AimAngle1.val*(2*np.pi/360)),
                + self.bL*np.cos(AimAngle1.val*(2*np.pi/360)), 0])


        self.replot()
        plt.pause(0.01)


callback = Tanks(players)

AimAngle1.on_changed(callback.aim)
Speed1.on_changed(callback.aim)
left.on_clicked(callback.moveLeft)
right.on_clicked(callback.moveRight)
fire1.on_clicked(callback.fireProgectile)

plt.show()