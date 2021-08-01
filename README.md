This is the repository for the 2018+ GUI.

Contributors:
Jack Taliercio
Alex Philpott
Alex Davenport
Elham Islam
Samantha Liu
Firuz Sharipov

This GUI will be written in Python using PyQT.
It will be suplemented by MATLAB.

Please make changes on the develop branch. Master branch is for validated, tested and ready to be used code.This is the repository for the 2018+ GUI. Contributors: Jack Taliercio Alex Philpott Alex Davenport Elham Islam Samantha Liu Firuz Sharipov

This GUI will be written in Python using PyQT. It will be suplemented by MATLAB.

Please make changes on the develop branch. Master branch is for validated, tested and ready to be used code.

# Setting up the GUI
## Cloning the repo
Open the terminal to the desired directory and then clone the repository into that directory by copying the clone url and running a similar command in the terminal: 

```
git clone git@gitlab.eecs.umich.edu:masa/avionics/gui.git
```

## Opening the GUI
In order to run the gui, it is recommended that you have python3 which you can install using [this guide](https://realpython.com/installing-python/).  Once that is done, please run  the following from the `gui` directory:

```pip install -r requirements.txt``` 

 This will install all the necessary python packages to run the GUI. Forgoing this step is the most common cause for not being able to launch the gui so do not forget this. If you notice a version is out of date, feel free to update it in requirements.txt.
 
Once this is done, you can launch the gui by running `python3 Python/gui.py` from the `gui` directory. 

When opening for the first time, you will be prompted to select a directory to store any gui configurations made. You should select the existing directory `Configurations` directory.

## Branching
Untested changes should be made on their own branches. These are then merged into  `develop` for integration testing. `Master`  is for validated, tested and ready to be used code.

The general naming convention for branches should be:
`feature-name_here`

When you wish to create a new branch, first checkout the branch you want to branch from using  `git pull origin branch_that_you_want_to_branch_off` and pull the latest changes using `git pull`. 

It is recommended that you brench off the `develop` branch as it will have the latest version for the gui that has been validated for normal use cases (be warned that they may still be some edge case bugs).

You can create a new branch using the command:

`git checkout -b <name-of-your-branch>`

When you have finished making your changes, remember to push your changes to the remote repo using `git push <name-of-your-branch>`. And feel free to make a merge request into `dev` by going into the merge requests section in the left sidebar on gitlab.

### Checking out a remote branch
If you want access to a branch that is on the remote repo but not on your local repo. You can run the following:
```
git fetch // retrieves changes from remote to local
git checkout <desired-branch> // switches into branch
```


# Information about operators/new members
![image/20210801152044.png](images/20210801152044.png)


## Setting up a configuration
In order to add components, enter edit mode using `ctrl + E` where you can then right-click in the edit area to add, connect and set up various components. When you have completing the config, you can then exit using `ctrl + shift + E`. If it is a new configuration, you will be prompted to save and name it. 

Here is an example of how it could be set up:
![image/20210801152906.png](images/20210801152906.png)

Clicking on various components oustide edit mode can allow you to edit various attributes (e.g. changing setpoints on motors).  Selecting most components in edit mode will provide graphical information, as well as the board and channel they belong to.

## Setting up boards on the GUI
![image/20210801152735.png](images/20210801152735.png)
In order to add a board to the gui, go into `run -> add avionics` and select the specific board. You will then see a board widget pop up in the side bar with various information about the board including the:
- state
- Ebatt
- I-batt
- Flash
- ADC rate
- Tx rate

The GUI also enables operators to send a command to change a boards state as seen above. The GUI is designed to only enable the necessary buttons based on the boards current state.

## Abort 
In order to enable the abort button, click the `Abort Button` action in the toolbar open a window to connect/enable the hardware and software abort buttons. This should then enable a clear red abort button for ermergencies:
![image/20210801154206.png](images/20210801154206.png)

When the abort button is enabled, the sidebar will become red alongside the state indication at the top to emphasize the current systems status to the operator: ![[images/20210801154426.png]]

## Flash
## Connecting to the server
In order to connect to the server, press the `connection` action in the toolbar. This will then open a window that allows you connect and take control of the server (i.e. send commands). Make sure you have the right ip address and port in order to connect to ther sever. The server currently only allows for one client to command the server at any given time.

## Other features
### Limits
![image/20210801155749.png](images/20210801155749.png)
When pressing the `Limits` action in the toolbar, a checklist that contains the necessary conditions before beginning a test. This helps to ensure that sensors are reading values in the appropriate ranges. A condition met is indicated by the light on the left.
### Textbox
There is a textbox on the side bar to store any notes related to the test. When saving, you will be prompted to save these notes in a seperate text file in addition to the config file.


# Section for developers
## Testing 
To be updated.

# Sections to be documented/implemented
## Debug Mode
## Level Sensing
## Autosequence manager
## Ducer Calibrations

[Please document issues and feature requests here.](https://docs.google.com/document/u/1/d/1WmYvYzNJm1WY62pQbBBs2LYiohTocQXqx2uKusf8IV8/edit#heading=h.9vix6k8uwaab)

Last updated: August 1, 2021 
Author: Elham Islam